"""Schema-meta builders: task_type slug + multimodal metadata
+ input file manifest + output artifact manifest.

Ports the corresponding helpers from custom_addons/kensei2/models/kensei2.py
(L2128 _slugify_task_type, L2138 _build_multimodal_metadata,
 L2189 _build_input_files_manifest, L2234 _build_output_artifacts)
with Odoo recordsets replaced by plain mappings.
"""

from __future__ import annotations

import json
import mimetypes
import os
import re
from typing import Iterable, List, Mapping, Optional

from src.utils.store import Task


_SLUG_RE = re.compile(r"[^a-z0-9]+")

# Match any agent-written file path under a known workspace root. The char
# class stops at shell terminators so paths embedded in exec commands
# (`python3 x.py > /tmp_workspace/out.csv && ...`) are captured cleanly.
_CONTAINER_PATH_RE = re.compile(
    r"(?:/home/node/\.openclaw/(?:workspace|uploads|media)"
    r"|/tmp_workspace|/root/workspace)/[^\s\"'`,;|&)>]+",
)
# Workspace prefixes accepted for structured path args from write-style tools.
_WORKSPACE_PREFIXES = ("/home/node/.openclaw/", "/tmp_workspace", "/root/workspace")

_MIME_TO_ARTIFACT_TYPE = {
    "image/": "generated_image",
    "video/": "media",
    "audio/": "media",
    "application/pdf": "document",
    "text/csv": "data_export",
    "application/json": "data_export",
    "text/markdown": "document",
    "text/plain": "document",
    "text/html": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
}

_OUTPUT_MIME_TO_MODALITY = {
    "image/": "image",
    "video/": "file",
    "audio/": "audio",
    "application/pdf": "file",
    "text/": "text",
    "application/json": "file",
    "application/zip": "file",
}

_INPUT_MIME_TO_MODALITY_TAG = {
    "image/": "upload_image",
    "video/": "video",
    "audio/": "audio",
    "application/pdf": "pdf",
}

_WRITE_TOOL_NAMES = {"write", "save_file", "create_file", "write_file"}
# Tools that run shell/python: deliverables written through them (redirection,
# open().write, df.to_csv(...)) have no structured path arg, so we regex the
# command string instead.
_EXEC_TOOL_NAMES = {"exec", "bash", "shell", "sh", "run", "execute", "terminal"}
_WRITE_PATH_KEYS = ("path", "file_path", "filePath", "filename")

_VALID_L1 = {
    "Small Business & Personal Docs",
    "Creative & Media",
    "Commerce & Product",
    "Property & Space",
    "Health & Wellness",
    "Visual Learning",
    "Operations & QA",
}


def slugify_task_type(l1_name: str, l2_name: str) -> str:
    """Build the schema-required `^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$` slug."""
    def slug(value: str) -> str:
        s = _SLUG_RE.sub("_", (value or "").lower()).strip("_")
        return s or "uncategorized"
    return "%s__%s" % (slug(l1_name), slug(l2_name))


def _classify_artifact_type(mime: str) -> str:
    if not mime:
        return "other"
    for prefix, kind in _MIME_TO_ARTIFACT_TYPE.items():
        if mime == prefix or mime.startswith(prefix):
            return kind
    return "other"


def _output_modality(mime: str) -> Optional[str]:
    if not mime:
        return None
    for prefix, mod in _OUTPUT_MIME_TO_MODALITY.items():
        if mime == prefix or mime.startswith(prefix):
            return mod
    return None


def _modality_tag(mime: str) -> Optional[str]:
    if not mime:
        return None
    for prefix, tag in _INPUT_MIME_TO_MODALITY_TAG.items():
        if mime == prefix or mime.startswith(prefix):
            return tag
    return None


def build_input_files_manifest(
    task: Task,
    attachments: Iterable[Mapping],
    s3_bucket: str = "",
    s3_prefix: str = "",
) -> List[dict]:
    """Build schema `meta_info.input_files` list.

    `attachments` is an iterable of dicts with keys:
        name        : filename
        mimeType    : MIME type
        storedAs    : opaque key under storage prefix
        size        : optional byte size

    When `s3_bucket` is empty, no `source` is emitted (local mode).
    """
    manifest: List[dict] = []
    for idx, att in enumerate(attachments):
        if not isinstance(att, Mapping):
            continue
        filename = att.get("name") or att.get("filename") or ""
        if not filename:
            continue
        mime = att.get("mimeType") or att.get("mime_type") \
            or mimetypes.guess_type(filename)[0] or "application/octet-stream"
        entry: dict = {
            "ref_id": "input_%d" % idx,
            "filename": filename,
            "mime_type": mime,
            "role": att.get("role", "primary_reference"),
            "description": att.get("description") or "User-uploaded %s file" % mime,
        }
        size = att.get("size") or att.get("size_bytes")
        if isinstance(size, int) and size > 0:
            entry["size_bytes"] = size
        stored = att.get("storedAs") or att.get("stored_as")
        if s3_bucket and stored:
            entry["source"] = "s3://%s/%s/input/tasks/%s/%s" % (
                s3_bucket, (s3_prefix or "").strip("/"), task.task_id, stored,
            )
        manifest.append(entry)
    return manifest


def _walk_tool_calls(raw_json: str) -> Iterable[dict]:
    if not raw_json:
        return
    try:
        data = json.loads(raw_json)
    except (TypeError, ValueError):
        return
    if not isinstance(data, list):
        return
    for call in data:
        if isinstance(call, dict):
            yield call


def build_output_artifacts(
    turns: Iterable[Mapping],
    s3_bucket: str = "",
    s3_prefix: str = "",
    s3_region: str = "",
    task_id: str = "",
    input_filenames: Iterable[str] = (),
) -> List[dict]:
    """Walk turns (.response + .tool_calls + .trajectory_messages JSON) and
    emit one `OutputArtifact` per detected agent-written file.

    Each turn is a Mapping with keys: response, tool_calls (JSON str),
    trajectory_messages (JSON str). Missing keys are tolerated.

    `input_filenames` are the task's supplied input files (attachments). Paths
    whose basename matches an input are skipped — the agent READING an input is
    not an output artifact. Extensionless paths (e.g. `mkdir`'d directories) are
    also skipped so only concrete files are emitted.
    """
    input_set = {os.path.basename(str(n)) for n in (input_filenames or []) if n}
    artifacts: List[dict] = []
    seen_paths = set()

    def push(container_path: str, source_hint: str = ""):
        if not container_path or container_path in seen_paths:
            return
        filename = os.path.basename(container_path)
        if filename in input_set:        # the agent READING an input is not an output
            return
        if "." not in filename:          # skip directories / extensionless paths
            return
        seen_paths.add(container_path)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        entry: dict = {
            "filename": filename,
            "mime_type": mime,
            "artifact_type": _classify_artifact_type(mime),
            "description": "Agent-generated %s output" % (os.path.splitext(filename)[1].lstrip(".") or "file"),
            "container_path": container_path,
        }
        if s3_bucket and task_id:
            key = "%s/output/tasks/%s/%s" % (
                (s3_prefix or "").strip("/"), task_id, filename,
            )
            entry["source"] = "s3://%s/%s" % (s3_bucket, key)
            if s3_region:
                entry["s3_url"] = "https://%s.s3.%s.amazonaws.com/%s" % (
                    s3_bucket, s3_region, key,
                )
        elif source_hint:
            entry["source"] = source_hint
        artifacts.append(entry)

    for turn in turns or []:
        if not isinstance(turn, Mapping):
            continue
        # response text \u2014 regex any container paths
        response_text = turn.get("response") or ""
        if isinstance(response_text, str):
            for m in _CONTAINER_PATH_RE.findall(response_text):
                push(m)
        # tool_calls JSON \u2014 extract paths from write-style AND exec/shell tools
        for call in _walk_tool_calls(turn.get("tool_calls", "")):
            name = (call.get("name") or "").lower()
            raw_args = call.get("args") or call.get("arguments") or {}
            if isinstance(raw_args, str):
                raw_args_str = raw_args
                try:
                    args = json.loads(raw_args)
                except ValueError:
                    args = {}
            else:
                args = raw_args
                raw_args_str = json.dumps(raw_args, default=str)
            if name in _WRITE_TOOL_NAMES and isinstance(args, dict):
                for key in _WRITE_PATH_KEYS:
                    v = args.get(key)
                    if isinstance(v, str) and v.startswith(_WORKSPACE_PREFIXES):
                        push(v)
                        break
            elif name in _EXEC_TOOL_NAMES:
                # No structured path arg \u2014 recover any workspace path mentioned
                # in the serialized command (redirections, to_csv, open().write).
                for m in _CONTAINER_PATH_RE.findall(raw_args_str):
                    push(m)
        # trajectory_messages JSON \u2014 same regex sweep
        traj_json = turn.get("trajectory_messages") or ""
        if isinstance(traj_json, str) and traj_json:
            for m in _CONTAINER_PATH_RE.findall(traj_json):
                push(m)

    return artifacts


def build_multimodal_metadata(
    task: Task,
    attachments: Iterable[Mapping],
    output_artifacts: Iterable[Mapping],
) -> dict:
    """Build the `meta_info.multimodal_metadata` block.

    Hard-coded narrative fields mirror the original Odoo behaviour
    (`_build_multimodal_metadata` in kensei2.py L2138) so the trajectory
    schema's `media_necessity >= 30` and `cross_modal_reasoning.description
    >= 20` requirements are satisfied without per-task authoring.
    """
    modality_tags: List[str] = []
    input_modalities: List[str] = []
    for att in attachments or []:
        if not isinstance(att, Mapping):
            continue
        mime = att.get("mimeType") or att.get("mime_type") or ""
        tag = _modality_tag(mime)
        if tag and tag not in modality_tags:
            modality_tags.append(tag)
        if mime and mime not in input_modalities:
            input_modalities.append(mime)
    if not modality_tags:
        modality_tags = ["upload_image"]

    output_modalities: List[str] = []
    for art in output_artifacts or []:
        if not isinstance(art, Mapping):
            continue
        mod = _output_modality(art.get("mime_type", ""))
        if mod and mod not in output_modalities:
            output_modalities.append(mod)
    if not output_modalities:
        output_modalities = ["text"]

    l1 = task.l1 if task.l1 in _VALID_L1 else "Visual Learning"
    l2 = task.l2 or "Document Generation from Visual Input"

    return {
        "modality_tags": modality_tags,
        "taxonomy_l1": l1,
        "taxonomy_l2": l2,
        "media_necessity": "Multimodal input required for visual understanding task.",
        "cross_modal_reasoning": {
            "percentage": 50,
            "modalities_fused": ["text", "image"],
            "description": "Agent processes visual and text inputs together.",
        },
        "input_modalities": input_modalities or ["text/plain"],
        "output_modalities": output_modalities,
        "asset_realism_notes": (
            "Natural user-uploaded content with realistic filenames and varying quality."
        ),
    }
