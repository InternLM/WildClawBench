"""Convert DSH session.v3 events to OpenClaw chat.jsonl for grading/usage.

Standalone (stdlib only): docker cp'd into the container and run there.
Mirrors src/agents/hermesagent/compat_transcript.py conventions.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

DEFAULT_SESSIONS_ROOT = "/root/.dsh/sessions"
OUTPUT_TRANSCRIPT_PATH = "/root/.openclaw/agents/main/sessions/chat.jsonl"


def _blocks_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts = [str(b.get("text", "")) for b in content
             if isinstance(b, dict) and b.get("type") == "text"] \
            if isinstance(content, list) else []
    return "\n".join(parts)


def _assistant_entry(data: dict) -> dict:
    msg = data.get("message", {})
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    blocks: list[dict] = []
    content = msg.get("content", [])
    if isinstance(content, str):
        if content.strip():
            blocks.append({"type": "text", "text": content})
    elif isinstance(content, list):
        for b in content:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "text":
                blocks.append({"type": "text", "text": str(b.get("text", ""))})
            elif b.get("type") == "tool-call":
                args = b.get("arguments", {})
                if isinstance(args, str):
                    try:
                        args = json.loads(args)
                    except Exception:
                        pass
                blocks.append({"type": "tool_use", "name": str(b.get("name", "")),
                               "input": args, "id": str(b.get("id", ""))})
    return {"type": "message", "message": {
        "role": "assistant", "content": blocks,
        "usage": {"input": usage.get("inputTokens", 0),
                  "output": usage.get("outputTokens", 0),
                  "cacheRead": usage.get("cacheReadTokens", 0),
                  "cacheWrite": usage.get("cacheWriteTokens", 0),
                  "totalTokens": usage.get("totalTokens", 0),
                  "cost": usage.get("cost", {})}}}


def _user_entry(data: dict) -> dict:
    return {"type": "message", "message": {"role": "user",
            "content": _blocks_text(data.get("content", []))}}


def _tool_entry(data: dict) -> dict:
    msg = data.get("message", {})
    call_id, text = "", ""
    content = msg.get("content")
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool-result":
                call_id = str(b.get("toolCallId", ""))
                text = _blocks_text(b.get("content", []))
    return {"type": "toolResult",
            "toolResult": {"content": text, "tool_call_id": call_id}}


def convert_events(lines: list[str]) -> list[dict]:
    out: list[dict] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        t, data = e.get("type"), e.get("data", {})
        if t == "user/message":
            out.append(_user_entry(data))
        elif t == "assistant/message":
            out.append(_assistant_entry(data))
        elif t == "tool/result":
            out.append(_tool_entry(data))
    return out


def _find_latest_session(root: str) -> Path | None:
    try:
        if not Path(root).is_dir():
            return None
        cands = [(p.stat().st_mtime_ns, p)
                 for p in Path(root).rglob("session.v3.jsonl.zstd")
                 if p.exists()]
    except OSError:
        return None
    return max(cands)[1] if cands else None


def _read_lines(zst: "Path | None", uncompressed: str) -> list[str]:
    if uncompressed:
        p = Path(uncompressed)
        return p.read_text(errors="ignore").splitlines() if p.exists() else []
    if zst is None:
        return []
    try:
        r = subprocess.run(["zstd", "-dc", str(zst)], capture_output=True, check=True)
    except (OSError, subprocess.CalledProcessError):
        return []
    return r.stdout.decode("utf-8", "ignore").splitlines()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sessions-root", default=DEFAULT_SESSIONS_ROOT)
    ap.add_argument("--out", default=OUTPUT_TRANSCRIPT_PATH)
    ap.add_argument("--uncompressed-file", default="")
    a = ap.parse_args(argv)
    entries = convert_events(_read_lines(_find_latest_session(a.sessions_root),
                                         a.uncompressed_file))
    out_path = Path(a.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries),
        encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
