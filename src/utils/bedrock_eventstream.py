"""
Minimal pure-Python parser for AWS vnd.amazon.eventstream binary frames.

Used by the Bedrock converse-stream callers (`src/utils/testgen/bedrock.py`
and `src/utils/grading.py:_call_judge_bedrock`). We avoid pulling botocore
just for this so boto3 stays an OPTIONAL dependency (lazy-loaded only by
`src/utils/s3_artifacts.py`).

Frame layout (all integers big-endian):
    [4B total_length]
    [4B headers_length]
    [4B prelude_crc]   -- skipped; we trust the bedrock-runtime endpoint
    [headers_length bytes]   -- key/value pairs, see below
    [payload]                -- JSON event body
    [4B message_crc]   -- skipped

Header entry layout:
    [1B name_length]
    [name_length bytes]
    [1B type]              -- 7 = utf-8 string (the only type bedrock emits)
    [2B value_length]
    [value_length bytes]

The only header we extract is `:event-type` (e.g. 'contentBlockDelta',
'metadata', 'messageStop'). Payloads are JSON dicts whose schema depends
on the event type.
"""
from __future__ import annotations

import base64
import json
from typing import Iterator, Tuple


def iter_eventstream(stream_bytes_iter: Iterator[bytes]) -> Iterator[Tuple[str, dict]]:
    """Yield ``(event_type, payload_dict)`` tuples from a stream of byte chunks.

    Buffers incomplete frames across chunk boundaries. Skips CRC validation;
    Bedrock connections terminate over TLS so corruption is rejected at the
    transport layer.
    """
    buf = bytearray()
    for chunk in stream_bytes_iter:
        if not chunk:
            continue
        buf.extend(chunk)
        while True:
            if len(buf) < 12:
                break
            total_len = int.from_bytes(buf[0:4], "big")
            headers_len = int.from_bytes(buf[4:8], "big")
            if total_len < 16 or len(buf) < total_len:
                break
            headers_start = 12
            payload_start = headers_start + headers_len
            payload_end = total_len - 4
            evt_type = _extract_event_type(bytes(buf[headers_start:payload_start]))
            try:
                payload = json.loads(buf[payload_start:payload_end].decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                payload = {}
            if isinstance(payload, dict) and "bytes" in payload and isinstance(payload["bytes"], str):
                try:
                    inner = base64.b64decode(payload["bytes"])
                    payload = json.loads(inner.decode("utf-8"))
                except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
                    pass
            yield evt_type, payload if isinstance(payload, dict) else {}
            del buf[:total_len]


def _extract_event_type(headers_bytes: bytes) -> str:
    pos = 0
    n = len(headers_bytes)
    while pos < n:
        if pos + 1 > n:
            break
        name_len = headers_bytes[pos]
        pos += 1
        if pos + name_len + 1 > n:
            break
        name = headers_bytes[pos:pos + name_len].decode("utf-8", errors="replace")
        pos += name_len
        type_byte = headers_bytes[pos]
        pos += 1
        if type_byte != 7:
            break
        if pos + 2 > n:
            break
        val_len = int.from_bytes(headers_bytes[pos:pos + 2], "big")
        pos += 2
        if pos + val_len > n:
            break
        value = headers_bytes[pos:pos + val_len].decode("utf-8", errors="replace")
        pos += val_len
        if name == ":event-type":
            return value
    return ""
