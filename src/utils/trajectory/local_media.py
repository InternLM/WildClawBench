"""Rewrite inline media in trajectory messages to file:// URLs on disk.

Local-only replacement for `_replace_inline_media_with_s3` from
kensei2_sandbox.py. Handles the three image storage formats produced by
OpenClaw clients:
1. OpenClaw direct: `{type:image, data:<b64>, mimeType:...}`
2. Anthropic dict source: `{type:image, source:{type:base64, media_type, data}}`
3. String source: `data:image/...;base64,...` URI or
   `/home/node/.openclaw/...` container path
"""

from __future__ import annotations

import base64
import logging
import os
import re
import uuid
from pathlib import Path
from typing import List, Mapping, Optional

_logger = logging.getLogger(__name__)

_MEDIA_BLOCK_TYPES = {"image", "video", "audio", "input_image"}

_DATA_URI_RE = re.compile(r"^data:([^;]+);base64,(.+)$", re.DOTALL)
_CONTAINER_PATH_RE = re.compile(
    r"^/home/node/\.openclaw/(?:workspace|uploads|media)/.+"
)

_MIME_EXT_MAP = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/bmp": "bmp",
    "image/svg+xml": "svg",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "audio/mp3": "mp3",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/ogg": "ogg",
    "application/pdf": "pdf",
}


def _ext_for(mime: str) -> str:
    if not mime:
        return "bin"
    return _MIME_EXT_MAP.get(mime.lower(), mime.split("/")[-1] or "bin")


def _write_bytes(artifacts_root: Path, task_id: str, data: bytes, mime: str) -> Path:
    out_dir = artifacts_root / task_id
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = "%s.%s" % (uuid.uuid4().hex[:12], _ext_for(mime))
    path = out_dir / fname
    path.write_bytes(data)
    return path


def _to_url(path: Path, base_url: Optional[str], task_id: str) -> str:
    if base_url:
        return "%s/%s/%s" % (base_url.rstrip("/"), task_id, path.name)
    return "file://%s" % path.resolve()


def _rewrite_block(
    block: dict, task_id: str, artifacts_root: Path, base_url: Optional[str]
) -> None:
    if not isinstance(block, dict):
        return
    btype = block.get("type")
    if btype not in _MEDIA_BLOCK_TYPES:
        return

    mime = block.get("mimeType") or block.get("mediaType") or ""

    # Format 1: OpenClaw direct {type, data, mimeType}
    if isinstance(block.get("data"), str) and block.get("data"):
        try:
            raw = base64.b64decode(block["data"])
        except (ValueError, TypeError):
            return
        path = _write_bytes(artifacts_root, task_id, raw, mime)
        block.pop("data", None)
        block.pop("mimeType", None)
        block["source"] = _to_url(path, base_url, task_id)
        if mime:
            block["mimeType"] = mime
        return

    src = block.get("source")
    # Format 2: Anthropic dict source {type:base64, media_type, data}
    if isinstance(src, dict):
        if src.get("type") == "base64" and isinstance(src.get("data"), str):
            mime = src.get("media_type") or mime
            try:
                raw = base64.b64decode(src["data"])
            except (ValueError, TypeError):
                return
            path = _write_bytes(artifacts_root, task_id, raw, mime)
            block["source"] = _to_url(path, base_url, task_id)
            if mime and not block.get("mimeType"):
                block["mimeType"] = mime
        elif src.get("type") == "url" and isinstance(src.get("url"), str):
            block["source"] = src["url"]
        return

    # Format 3: String source — data: URI or container path
    if isinstance(src, str):
        m = _DATA_URI_RE.match(src)
        if m:
            mime = m.group(1) or mime
            try:
                raw = base64.b64decode(m.group(2))
            except (ValueError, TypeError):
                return
            path = _write_bytes(artifacts_root, task_id, raw, mime)
            block["source"] = _to_url(path, base_url, task_id)
            if mime and not block.get("mimeType"):
                block["mimeType"] = mime
            return
        if _CONTAINER_PATH_RE.match(src):
            # Container-only path — keep as a relative reference; we cannot
            # read it from outside the sandbox at this point.  The caller
            # is expected to have copied it out before invoking this pass.
            return


def _walk_content(
    content, task_id: str, artifacts_root: Path, base_url: Optional[str]
) -> None:
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                _rewrite_block(block, task_id, artifacts_root, base_url)
                inner = block.get("content")
                if isinstance(inner, list):
                    _walk_content(inner, task_id, artifacts_root, base_url)


def replace_inline_media_with_files(
    messages: List[dict],
    task_id: str,
    artifacts_dir: Path,
    base_url: Optional[str] = None,
) -> List[dict]:
    """Walk messages and rewrite any inline media to local files.

    `artifacts_dir` is a base directory; files are written under
    `artifacts_dir/<task_id>/`. `base_url` overrides the URL prefix
    (e.g. for a local HTTP server); when omitted, `file://` URLs are used.
    """
    artifacts_root = Path(artifacts_dir)
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        # Handle wrapped envelopes (is_accepted/hints/message)
        envelope = msg
        while (
            isinstance(envelope, dict)
            and "message" in envelope
            and isinstance(envelope["message"], dict)
            and "role" not in envelope["message"]
            and "content" not in envelope["message"]
        ):
            envelope = envelope["message"]
        inner = envelope.get("message") if isinstance(envelope, dict) else None
        if isinstance(inner, dict):
            _walk_content(inner.get("content"), task_id, artifacts_root, base_url)
    return messages
