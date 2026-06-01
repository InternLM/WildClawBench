"""Schema-meta builders for the reference trajectory contract.

Reference shape (`/Users/apple/Downloads/output.json`) — `input_files` and
`output_artifacts` live at the trajectory's TOP LEVEL (not nested under
`meta_info`). Every record must carry `ref_id`, `filename`, `mime_type`,
`size_bytes`, plus a polarity-fixed `source` field that documents WHERE
the bytes came from (S3 key path for inputs, the literal
`"agent_workspace"` tag for outputs). Ports the trimmed half of kensei2's
`_build_input_files_manifest` + `_build_output_artifacts` with Odoo
recordsets replaced by plain mappings.
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

# MIME prefix → modality_tag emitted in `trajectory.meta_info.modality_tags`.
# Reference uses processing-style verbs (image_ocr, pdf_extraction); do NOT
# revert to the older upload_image/video/audio tags — those broke schema
# parity with the canonical reference output.
_INPUT_MIME_TO_MODALITY_TAG = {
    "image/": "image_ocr",
    "video/": "video_analysis",
    "audio/": "audio_transcription",
    "application/pdf": "pdf_extraction",
}

# Modality-fusion bucket. PDFs and image-bearing types collapse to "image"
# because the agent's downstream processing fuses them with text reasoning.
_INPUT_MIME_TO_FUSED = {
    "image/": "image",
    "video/": "video",
    "audio/": "audio",
    "application/pdf": "image",
    "text/csv": "text",
    "text/": "text",
    "application/json": "text",
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

_WRITE_TOOL_NAMES = {"write", "save_file", "create_file", "write_file"}
# Tools that run shell/python: deliverables written through them (redirection,
# open().write, df.to_csv(...)) have no structured path arg, so we regex the
# command string instead.
_EXEC_TOOL_NAMES = {"exec", "bash", "shell", "sh", "run", "execute", "terminal"}
_WRITE_PATH_KEYS = ("path", "file_path", "filePath", "filename")


def slugify_task_type(l1_name: str, l2_name: str) -> str:
    """Build the schema-required `^[a-z][a-z0-9_]*__[a-z][a-z0-9_]*$` slug."""
    def slug(value: str) -> str:
        s = _SLUG_RE.sub("_", (value or "").lower()).strip("_")
        return s or "uncategorized"
    return "%s__%s" % (slug(l1_name), slug(l2_name))


def slug_taxonomy_l2(l2_name: str) -> str:
    return _SLUG_RE.sub("_", (l2_name or "").lower()).strip("_")


def input_modality_tag(mime: str) -> Optional[str]:
    if not mime:
        return None
    for prefix, tag in _INPUT_MIME_TO_MODALITY_TAG.items():
        if mime == prefix or mime.startswith(prefix):
            return tag
    return None


def fused_modality(mime: str) -> Optional[str]:
    if not mime:
        return None
    for prefix, mod in _INPUT_MIME_TO_FUSED.items():
        if mime == prefix or mime.startswith(prefix):
            return mod
    return None


def output_modality(mime: str) -> Optional[str]:
    if not mime:
        return None
    for prefix, mod in _OUTPUT_MIME_TO_MODALITY.items():
        if mime == prefix or mime.startswith(prefix):
            return mod
    return None


def build_input_files_manifest(
    task: Task,
    attachments: Iterable[Mapping],
    s3_bucket: str = "",
    s3_prefix: str = "",
) -> List[dict]:
    """Build top-level `input_files` list matching reference schema.

    Reference fields per entry: ref_id, filename, mime_type, role,
    description, size_bytes, source. ALL six are always present.

    `source` is a RELATIVE key path (`input/tasks/<task_id>_<filename>`),
    never an `s3://` URL — the bucket/region are implicit from harness
    config; consumers reconstruct the full S3 URL on demand. `s3_bucket`
    and `s3_prefix` kwargs are accepted but unused (kept for caller
    compat; future may use them to override the key prefix).
    """
    del s3_bucket, s3_prefix
    manifest: List[dict] = []
    task_id = task.task_id or task.id or "task"
    for idx, att in enumerate(attachments or []):
        if not isinstance(att, Mapping):
            continue
        filename = att.get("name") or att.get("filename") or ""
        if not filename:
            continue
        mime = (
            att.get("mimeType")
            or att.get("mime_type")
            or mimetypes.guess_type(filename)[0]
            or "application/octet-stream"
        )
        size_raw = att.get("size") or att.get("size_bytes") or 0
        try:
            size_bytes = int(size_raw or 0)
        except (TypeError, ValueError):
            size_bytes = 0
        manifest.append({
            "ref_id": "input_%d" % idx,
            "filename": filename,
            "mime_type": mime,
            "role": att.get("role") or "primary",
            "description": att.get("description") or "",
            "size_bytes": size_bytes,
            "source": "input/tasks/%s_%s" % (task_id, filename),
        })
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
    """Walk turns for agent-written file paths; emit trimmed records.

    Each turn is a Mapping with keys: response, tool_calls (JSON str),
    trajectory_messages (JSON str). Missing keys are tolerated.

    Reference fields per entry: ref_id, path, filename, mime_type,
    size_bytes, source. `source` is the literal `"agent_workspace"`.

    `input_filenames` are the task's supplied input files (attachments). Paths
    whose basename matches an input are skipped — the agent READING an input is
    not an output artifact. Extensionless paths (e.g. `mkdir`'d directories) are
    also skipped so only concrete files are emitted.

    Most artifacts are added by the caller in `run_batch.py` after the
    workspace is collected (this scanner only catches paths explicitly
    mentioned in tool calls / chat transcript). When turns is empty,
    returns [].
    """
    del s3_bucket, s3_prefix, s3_region, task_id
    input_set = {os.path.basename(str(n)) for n in (input_filenames or []) if n}
    artifacts: List[dict] = []
    seen_paths: set[str] = set()

    def push(container_path: str) -> None:
        if not container_path or container_path in seen_paths:
            return
        filename = os.path.basename(container_path)
        if filename in input_set:        # the agent READING an input is not an output
            return
        if "." not in filename:          # skip directories / extensionless paths
            return
        seen_paths.add(container_path)
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        artifacts.append({
            "ref_id": "artifact_%d" % (len(artifacts)),
            "path": container_path,
            "filename": filename,
            "mime_type": mime,
            "size_bytes": 0,
            "source": "agent_workspace",
        })

    for turn in turns or []:
        if not isinstance(turn, Mapping):
            continue
        response_text = turn.get("response") or ""
        if isinstance(response_text, str):
            for m in _CONTAINER_PATH_RE.findall(response_text):
                push(m)
        # tool_calls JSON — extract paths from write-style AND exec/shell tools
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
                # No structured path arg — recover any workspace path mentioned
                # in the serialized command (redirections, to_csv, open().write).
                for m in _CONTAINER_PATH_RE.findall(raw_args_str):
                    push(m)
        # trajectory_messages JSON — same regex sweep
        traj_json = turn.get("trajectory_messages") or ""
        if isinstance(traj_json, str) and traj_json:
            for m in _CONTAINER_PATH_RE.findall(traj_json):
                push(m)

    return artifacts


def build_trajectory_meta_info(
    task: Task,
    input_files: List[dict],
    output_artifacts: List[dict],
) -> dict:
    """Build the `trajectory.meta_info` block.

    Reference shape (exact 5 keys): platform, modality_tags, taxonomy_l1,
    taxonomy_l2, modalities_fused. `platform` is always "linux" (containers
    run linux). taxonomy_l1 preserves the original L1 string (case +
    punctuation); taxonomy_l2 is the snake_case slug of L2.
    """
    modality_tags: List[str] = []
    fused: List[str] = []
    for f in input_files or []:
        if not isinstance(f, Mapping):
            continue
        mime = f.get("mime_type", "")
        tag = input_modality_tag(mime)
        if tag and tag not in modality_tags:
            modality_tags.append(tag)
        bucket = fused_modality(mime)
        if bucket and bucket not in fused:
            fused.append(bucket)
    for a in output_artifacts or []:
        if not isinstance(a, Mapping):
            continue
        mime = a.get("mime_type", "")
        bucket = fused_modality(mime)
        if bucket and bucket not in fused:
            fused.append(bucket)
    if not fused:
        fused = ["text"]

    return {
        "platform": "linux",
        "modality_tags": modality_tags,
        "taxonomy_l1": task.l1 or "",
        "taxonomy_l2": slug_taxonomy_l2(task.l2 or ""),
        "modalities_fused": fused,
    }


def build_input_modalities(input_files: List[dict]) -> List[str]:
    seen: List[str] = []
    for f in input_files or []:
        if not isinstance(f, Mapping):
            continue
        mime = f.get("mime_type", "")
        if mime and mime not in seen:
            seen.append(mime)
    return seen


def build_output_modalities(output_artifacts: List[dict]) -> List[str]:
    seen: List[str] = []
    for a in output_artifacts or []:
        if not isinstance(a, Mapping):
            continue
        mod = output_modality(a.get("mime_type", ""))
        if mod and mod not in seen:
            seen.append(mod)
    if not seen:
        seen = ["text"]
    return seen


def build_multimodal_metadata(
    task: Task,
    attachments: Iterable[Mapping],
    output_artifacts: Iterable[Mapping],
) -> dict:
    """DEPRECATED: legacy nested metadata block; no longer emitted in the
    reference schema. Retained for import-compat only. New code should
    call `build_trajectory_meta_info` + `build_input_modalities` +
    `build_output_modalities` directly.
    """
    del task, attachments, output_artifacts
    return {}


def _classify_artifact_type(mime: str) -> str:
    """Backward-compat helper (still referenced by s3_artifacts.py).

    Maps a MIME type to a kensei2-style artifact_type bucket. This field
    is no longer part of the persisted trajectory schema, but the
    upload module keeps a rich internal record for debug/logging.
    """
    if not mime:
        return "other"
    table = {
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
    for prefix, kind in table.items():
        if mime == prefix or mime.startswith(prefix):
            return kind
    return "other"
