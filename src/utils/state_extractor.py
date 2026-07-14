"""Assemble the post-run ``agent_state.json`` consumed by fixture-based suites.

Persona/inject tasks ship a deterministic CHECKERS module (``task.py``) whose
lambdas query a single ``state`` dict with three kinds of evidence:

  * ``state["audit"]``           — the agent-visible API call log, keyed by
                                    service: ``{"<api>": {"total_requests": N,
                                    "endpoints": {"<METHOD path>": {"count": N,
                                    "statuses": {...}}}}}`` (from each mock
                                    service's ``/audit/summary``).
  * ``state["<api>"]``           — that service's final store contents, in the
                                    shape the helpers read (``events``,
                                    ``messages``/``drafts``, ``files``,
                                    ``documents``, ``contacts``, sheets...).
  * ``state["last_response"]``   — the agent's natural-language output (the
                                    concatenated assistant transcript, so the
                                    turn-agnostic ``_semantic_check`` calls can
                                    find keywords anywhere in the run).

Previously the shipped ``agent_state.json`` was a golden steer-flow summary with
empty service sections (IAN report Pointer 2), so deployed checkers had nothing
real to evaluate. This module rebuilds a faithful state from live run artifacts:
the mock-store snapshot (``snapshot_state`` dump), the live ``/audit/summary``
feed, and the agent transcript.

Best-effort by design: ``audit`` and ``last_response`` are exact; per-service
reshaping maps common store-table names to the keys the helpers read and always
keeps the raw rows so blob-level checks still see the data. A service shape the
mapper does not recognize still appears under its raw table names.
"""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

logger = logging.getLogger(__name__)

# store-table name (lowercased) -> checker-facing alias key on state["<api>"]
_TABLE_ALIASES = {
    "events": "events",
    "calendar_events": "events",
    "files": "files",
    "drive_files": "files",
    "messages": "messages",
    "emails": "messages",
    "drafts": "drafts",
    "contacts": "contacts",
    "people": "contacts",
}


def _csv_cell(value: str) -> Any:
    """Decode one CSV cell back to a Python value. Cells that the snapshot
    writer JSON-encoded (nested objects/arrays) are parsed back; everything
    else is kept as the raw string, matching the CSV-seeded store shape."""
    if value and value[0] in "[{":
        try:
            return json.loads(value)
        except (json.JSONDecodeError, ValueError):
            return value
    return value


def _read_table_csv(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                rows.append({k: _csv_cell(v) for k, v in row.items() if k is not None})
    except OSError:
        return []
    return rows


def _load_store_snapshot(snapshot_dir: Path) -> Dict[str, Dict[str, Any]]:
    """Read a ``snapshot_state`` dump into ``{api: {tables:{...}, documents:{...}}}``.

    The current layout mirrors the seed ``mock_data/`` (``<api>/<table>.csv`` +
    ``<api>/<doc>.json``); the older nested layout (``<api>/tables/<t>.json`` +
    ``<api>/documents/<d>.json``) is still read for backward compatibility."""
    out: Dict[str, Dict[str, Any]] = {}
    if not snapshot_dir or not snapshot_dir.is_dir():
        return out
    for api_dir in sorted(snapshot_dir.iterdir()):
        if not api_dir.is_dir() or api_dir.name.startswith("_"):
            continue
        tables: Dict[str, Any] = {}
        documents: Dict[str, Any] = {}
        # New flat layout: tables as CSV, documents as JSON, side by side.
        for csvf in sorted(api_dir.glob("*.csv")):
            tables[csvf.stem] = _read_table_csv(csvf)
        for jf in sorted(api_dir.glob("*.json")):
            try:
                documents[jf.stem] = json.loads(jf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
        # Legacy nested layout fallback.
        tdir = api_dir / "tables"
        if tdir.is_dir():
            for tf in sorted(tdir.glob("*.json")):
                try:
                    blob = json.loads(tf.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
                rows = blob.get("rows") if isinstance(blob, dict) else blob
                tables[tf.stem] = rows if isinstance(rows, list) else []
        ddir = api_dir / "documents"
        if ddir.is_dir():
            for df in sorted(ddir.glob("*.json")):
                try:
                    documents[df.stem] = json.loads(df.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    continue
        out[api_dir.name] = {"tables": tables, "documents": documents}
    return out


def _reshape_service(api: str, tables: Dict[str, Any], documents: Dict[str, Any]) -> Dict[str, Any]:
    """Project a service's raw store tables/documents onto the keys the CHECKER
    helpers read, while keeping the raw rows accessible for blob checks."""
    svc: Dict[str, Any] = {}
    # raw tables under their own names (so str(state[api]) blob checks see them)
    for tname, rows in tables.items():
        svc[tname] = rows
        alias = _TABLE_ALIASES.get(tname.lower())
        if alias and alias not in svc:
            svc[alias] = rows
    # gmail: split messages into sent vs draft views the helpers expect
    if "messages" in svc and "drafts" not in svc:
        msgs = svc.get("messages") or []
        svc["drafts"] = [m for m in msgs
                         if isinstance(m, dict)
                         and str(m.get("status", "draft")).lower() == "draft"]
    # docs: helpers read state["<docs>"]["documents"] as {doc_id: body}
    if documents:
        svc["documents"] = documents
    return svc


def build_agent_state(
    *,
    audit: Optional[Dict[str, Any]] = None,
    store_snapshot_dir: Optional[Path] = None,
    last_response: str = "",
    extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Assemble the ``state`` dict the deterministic CHECKERS consume."""
    state: Dict[str, Any] = {}
    state["audit"] = audit or {}
    state["last_response"] = last_response or ""
    store = _load_store_snapshot(Path(store_snapshot_dir)) if store_snapshot_dir else {}
    for api, blob in store.items():
        state[api] = _reshape_service(api, blob.get("tables", {}), blob.get("documents", {}))
    if extra:
        for k, v in extra.items():
            state.setdefault(k, v)
    return state


def extract_assistant_text(transcript_paths: Iterable[Path], max_chars: int = 2_000_000) -> str:
    """Concatenate every assistant/agent text block from one or more JSONL
    transcripts into a single string for ``state["last_response"]``.

    Defensive across transcript dialects: handles OpenClaw chat.jsonl rows
    (``{"message": {"role": "assistant", "content": ...}}``), flat
    ``{"role": "assistant", "content": ...}`` rows, and content that is either a
    string or a list of ``{"type": "text", "text": ...}`` blocks.
    """
    chunks: list[str] = []
    total = 0

    def _emit(text: str) -> bool:
        nonlocal total
        if not text:
            return True
        chunks.append(text)
        total += len(text)
        return total < max_chars

    def _content_text(content: Any) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts = []
            for blk in content:
                if isinstance(blk, dict):
                    if blk.get("type") in (None, "text") and isinstance(blk.get("text"), str):
                        parts.append(blk["text"])
                    elif isinstance(blk.get("content"), str):
                        parts.append(blk["content"])
                elif isinstance(blk, str):
                    parts.append(blk)
            return "\n".join(parts)
        return ""

    for path in transcript_paths:
        try:
            p = Path(path)
            if not p.is_file():
                continue
            for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                msg = row.get("message") if isinstance(row, dict) else None
                if not isinstance(msg, dict):
                    msg = row if isinstance(row, dict) else {}
                role = str(msg.get("role") or row.get("role") or "").lower()
                if role not in ("assistant", "agent", "model"):
                    continue
                if not _emit(_content_text(msg.get("content"))):
                    return "\n".join(chunks)
        except OSError as exc:
            logger.debug("transcript read failed (%s): %s", path, exc)
    return "\n".join(chunks)
