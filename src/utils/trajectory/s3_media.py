"""Optional S3 uploader for inline trajectory media.

Mirrors `_replace_inline_media_with_s3` from kensei2_sandbox.py L3088.
Same three storage formats as `local_media.py`; the difference is the
output URL is an HTTPS S3 link rather than `file://`.
"""

from __future__ import annotations

import base64
import logging
import re
import uuid
from typing import List, Mapping, Optional

_logger = logging.getLogger(__name__)

_MEDIA_BLOCK_TYPES = {"image", "video", "audio", "input_image"}
_DATA_URI_RE = re.compile(r"^data:([^;]+);base64,(.+)$", re.DOTALL)

_MIME_EXT_MAP = {
    "image/png": "png",
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/webp": "webp",
    "image/svg+xml": "svg",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "audio/mp3": "mp3",
    "audio/mpeg": "mp3",
    "audio/wav": "wav",
    "audio/x-wav": "wav",
    "audio/ogg": "ogg",
    # See local_media.py for the .m4a MIME-fragmentation rationale; the
    # two tables must stay in sync so trajectories saved locally vs to S3
    # land on identical file extensions.
    "audio/mp4": "m4a",
    "audio/mp4a-latm": "m4a",
    "audio/x-m4a": "m4a",
    "audio/aac": "aac",
    "audio/x-aac": "aac",
    "application/pdf": "pdf",
}


def _ext_for(mime: str) -> str:
    if not mime:
        return "bin"
    return _MIME_EXT_MAP.get(mime.lower(), mime.split("/")[-1] or "bin")


class _S3Uploader:
    def __init__(
        self,
        bucket: str,
        prefix: str,
        region: str,
        access_key: str = "",
        secret_key: str = "",
    ):
        try:
            import boto3
            from botocore.config import Config as BotoConfig
        except ImportError as exc:
            raise RuntimeError(
                "boto3 is required for S3 media upload — install with `pip install boto3`"
            ) from exc
        kwargs = {"region_name": region, "config": BotoConfig(retries={"max_attempts": 3, "mode": "adaptive"})}
        if access_key and secret_key:
            kwargs["aws_access_key_id"] = access_key
            kwargs["aws_secret_access_key"] = secret_key
        self.client = boto3.client("s3", **kwargs)
        self.bucket = bucket
        self.prefix = (prefix or "").strip("/")
        self.region = region

    def put(self, task_id: str, data: bytes, mime: str) -> str:
        ext = _ext_for(mime)
        key = "%s/output/tasks/%s/%s.%s" % (
            self.prefix, task_id, uuid.uuid4().hex[:12], ext,
        )
        params = {"Bucket": self.bucket, "Key": key, "Body": data}
        if mime:
            params["ContentType"] = mime
        self.client.put_object(**params)
        return "https://%s.s3.%s.amazonaws.com/%s" % (self.bucket, self.region, key)


def _rewrite_block(block: dict, task_id: str, uploader: _S3Uploader) -> None:
    if not isinstance(block, dict) or block.get("type") not in _MEDIA_BLOCK_TYPES:
        return
    mime = block.get("mimeType") or block.get("mediaType") or ""

    if isinstance(block.get("data"), str) and block["data"]:
        try:
            raw = base64.b64decode(block["data"])
        except (ValueError, TypeError):
            return
        url = uploader.put(task_id, raw, mime)
        block.pop("data", None)
        block["source"] = url
        if mime:
            block["mimeType"] = mime
        return

    src = block.get("source")
    if isinstance(src, dict):
        if src.get("type") == "base64" and isinstance(src.get("data"), str):
            mime = src.get("media_type") or mime
            try:
                raw = base64.b64decode(src["data"])
            except (ValueError, TypeError):
                return
            block["source"] = uploader.put(task_id, raw, mime)
            if mime and not block.get("mimeType"):
                block["mimeType"] = mime
        elif src.get("type") == "url" and isinstance(src.get("url"), str):
            block["source"] = src["url"]
        return

    if isinstance(src, str):
        m = _DATA_URI_RE.match(src)
        if m:
            mime = m.group(1) or mime
            try:
                raw = base64.b64decode(m.group(2))
            except (ValueError, TypeError):
                return
            block["source"] = uploader.put(task_id, raw, mime)
            if mime and not block.get("mimeType"):
                block["mimeType"] = mime


def _walk_content(content, task_id: str, uploader: _S3Uploader) -> None:
    if isinstance(content, list):
        for block in content:
            if isinstance(block, dict):
                _rewrite_block(block, task_id, uploader)
                inner = block.get("content")
                if isinstance(inner, list):
                    _walk_content(inner, task_id, uploader)


def replace_inline_media_with_s3(
    messages: List[dict],
    task_id: str,
    bucket: str,
    prefix: str,
    region: str,
    access_key: str = "",
    secret_key: str = "",
) -> List[dict]:
    """Upload inline media to S3, rewriting trajectory message `source` fields."""
    if not bucket:
        return messages
    uploader = _S3Uploader(bucket, prefix, region, access_key, secret_key)
    for msg in messages:
        if not isinstance(msg, dict):
            continue
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
            _walk_content(inner.get("content"), task_id, uploader)
    return messages
