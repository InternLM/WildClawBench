"""S3 upload for agent-generated output artifacts.

Mirrors the kensei2 canonical `_persist_output_artifacts_to_s3`
(custom_addons/kensei2/models/kensei2_sandbox.py L5099-5146): walks the
task's collected workspace for files written under any of the
deliverable-dir-name conventions, then uploads each one to
`s3://<bucket>/<prefix>/output/tasks/<task_id>/<filename>` and returns
manifest records that match the schema produced by
`src.utils.trajectory.multimodal_meta.build_output_artifacts`.

The upload step is REQUIRED for `meta_info.output_artifacts` to contain
real S3 URLs: `build_output_artifacts` only synthesizes URL strings from
chat-content regex matches, it never moves bytes. Without this module
the synthesized URLs would point at S3 keys that don't exist.
"""

from __future__ import annotations

import logging
import mimetypes
from pathlib import Path
from typing import Iterable, List, Sequence

from src.utils.config import Config
from src.utils.trajectory.multimodal_meta import _classify_artifact_type

logger = logging.getLogger(__name__)

# Must match src/utils/grading.py:_DELIVERABLE_DIR_NAMES — both lists encode
# the same cross-file invariant (the verifier judges files under these
# subdirs, the uploader pushes the SAME files to S3). Changing one without
# the other would silently desync uploaded artifacts from judged content.
_DELIVERABLE_DIR_NAMES = ("results", "deliverables", "output", "out", "artifacts")


def _collect_deliverable_files(workspace_roots: Sequence[Path]) -> List[Path]:
    seen: set[Path] = set()
    found: List[Path] = []
    for root in workspace_roots:
        if not root.is_dir():
            continue
        for name in _DELIVERABLE_DIR_NAMES:
            subdir = root / name
            if not subdir.is_dir():
                continue
            for path in sorted(subdir.rglob("*")):
                if path.is_file():
                    resolved = path.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        found.append(path)
        # Top-level files at the root itself (some tasks write directly
        # to workspace_full/foo.csv without a deliverable subdir).
        for path in sorted(root.iterdir()):
            if path.is_file():
                resolved = path.resolve()
                if resolved not in seen:
                    seen.add(resolved)
                    found.append(path)
    return found


# Filenames in the openclaw persona-scaffolding set get re-copied into
# workspace_full on every task and would show up as fake "agent-generated"
# artifacts in every trajectory if we didn't filter them out here.
_TEMPLATE_FILE_NAMES = frozenset({
    "IDENTITY.md", "BOOTSTRAP.md", "HEARTBEAT.md", "USER.md",
    "SOUL.md", "AGENTS.md", "TOOLS.md", "AGENT.md", "MEMORY.md",
})


def _is_template_or_input_file(path: Path) -> bool:
    return path.name in _TEMPLATE_FILE_NAMES


def upload_output_artifacts(
    config: Config,
    task_id: str,
    workspace_roots: Iterable[Path],
    *,
    include_template_files: bool = False,
) -> List[dict]:
    """Upload each agent-written deliverable to S3 and return artifact records.

    Returns `[]` silently when `config.s3_bucket` is empty (the "no S3
    configured" baseline). On any other failure (boto3 missing, creds
    invalid, bucket-access denied, individual file read/upload errors)
    logs a WARN and skips the affected file, never raises.

    Each returned dict matches the schema produced by
    `src.utils.trajectory.multimodal_meta.build_output_artifacts`, with
    the addition of a real `size_bytes` field harvested from the file.
    """
    if not config or not getattr(config, "s3_bucket", ""):
        return []
    if not task_id:
        logger.warning("S3 upload skipped: empty task_id")
        return []

    candidates = _collect_deliverable_files(list(workspace_roots))
    if not include_template_files:
        candidates = [p for p in candidates if not _is_template_or_input_file(p)]
    if not candidates:
        return []

    try:
        import boto3  # type: ignore[import-untyped]
    except ImportError:
        logger.warning(
            "[%s] S3 upload skipped: boto3 not installed (pip install boto3)",
            task_id,
        )
        return []

    init_kwargs: dict = {"region_name": config.s3_region or "us-east-1"}
    if getattr(config, "s3_access_key_id", ""):
        init_kwargs["aws_access_key_id"] = config.s3_access_key_id
    if getattr(config, "s3_secret_access_key", ""):
        init_kwargs["aws_secret_access_key"] = config.s3_secret_access_key
    try:
        client = boto3.client("s3", **init_kwargs)
    except Exception as exc:  # noqa: BLE001 - boto3 error class hierarchy is dynamic
        logger.warning("[%s] S3 client init failed: %s", task_id, exc)
        return []

    bucket = config.s3_bucket
    prefix = (config.s3_prefix or "").strip("/")
    region = config.s3_region or "us-east-1"
    records: List[dict] = []
    uploaded = 0
    failed = 0

    for path in candidates:
        filename = path.name
        mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        if prefix:
            key = "%s/output/tasks/%s/%s" % (prefix, task_id, filename)
        else:
            key = "output/tasks/%s/%s" % (task_id, filename)

        try:
            data = path.read_bytes()
        except OSError as exc:
            logger.warning("[%s] read failed %s: %s", task_id, path, exc)
            failed += 1
            continue

        try:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=mime,
            )
        except Exception as exc:  # noqa: BLE001 - any client error
            logger.warning("[%s] S3 upload failed for %s: %s", task_id, filename, exc)
            failed += 1
            continue

        uploaded += 1
        records.append({
            "filename": filename,
            "mime_type": mime,
            "artifact_type": _classify_artifact_type(mime),
            "description": "Agent-generated %s output" % (
                path.suffix.lstrip(".") or "file"
            ),
            "container_path": str(path),
            "size_bytes": len(data),
            "source": "s3://%s/%s" % (bucket, key),
            "s3_url": "https://%s.s3.%s.amazonaws.com/%s" % (bucket, region, key),
        })

    if uploaded or failed:
        logger.info(
            "[%s] S3 artifact upload complete: %d uploaded, %d failed to s3://%s/%s/output/tasks/%s/",
            task_id, uploaded, failed, bucket, prefix or "(root)", task_id,
        )
    return records
