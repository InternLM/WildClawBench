"""
WildClawBench InjectDirector: Talos-style staged, inject-between-turns.

This is the second silent-injection model in WildClawBench (alongside the
``stage_director`` / ``stages.yaml`` model). It consumes the richer Talos
``inject/stageN/mutations.json`` layout shipped by tasks like
``LAYLA_001_october_grant_crunch`` and applies each stage's *silent* mutations
between agent turns, while the agent is idle, via each mock API's ``/admin/*``
admin plane (so the change never appears in the agent-visible ``/audit/*`` feed).

Why a separate module from ``stage_director``
---------------------------------------------
* ``stages.yaml`` expresses mutations directly as admin-plane ops
  (``{api, op: data.patch, table, pk, fields}``) and uses ``1 + len(stages)``
  turns with a single neutral nudge.
* The Talos ``inject/`` format expresses mutations as **service REST calls**
  (``{service, method, path, body}``), drives a fixed 50-turn script from
  ``prompts.txt``, and applies each ``stageN`` between specific turn boundaries
  (e.g. ``applies_between_turns: ["T12", "T13"]``).

Design choices
--------------
* **Baseline already seeded.** The task's ``mock_data/`` overlays already
  contain the canonical pre-T0 state, so the *stage0* ``loud`` API mutations are
  NOT replayed by default (they would only re-assert state already present and
  would pollute the audit feed). Only stage0 ``filesystem`` drops are seeded
  (optional, requires a workspace copy hook). Set ``replay_loud=True`` to also
  replay ``loud`` ops as visible seed history. This gating applies ONLY to the
  seed stage; ``loud`` ops in a mid-run stage (>= 1) have no overlay redundancy
  and ARE applied by ``apply_stage`` as visible (silent=False) mutations.
* **Apply-time resolution.** The Talos mutations carry unresolved placeholders
  (``{rec_UDI-2026-007}``, ``{page_id_...}``) and field-name casing that may not
  match the live store columns. Rather than trust the literal path/body, the
  applier reads the live admin state (``GET /admin/data/<table>``), locates the
  target row by its embedded business key, and maps fields case-insensitively
  before issuing a ``PATCH /admin/data/<table>/<pk>``. Anything it cannot
  resolve is logged to the timeline as ``unresolved`` rather than silently
  dropped.
* **Silent vs loud at apply time.** Mutations flagged ``silent: true`` (or every
  entry in the ``silent`` array) are applied through ``/admin/*`` and are
  invisible to the agent. ``loud`` mutations in a mid-run stage go through the
  same admin plane but are recorded silent=False (agent-visible: a new
  email/event/row it will read through normal API calls). At the *seed* stage,
  ``loud`` is gated by ``replay_loud`` and ``filesystem`` drops are skipped when
  the container is not yet up (the baseline mount carries that state instead).

Turn model
----------
``turn_messages(...)`` returns the full per-turn wake-up list parsed from
``prompts.txt``. ``stage_for_boundary(turn_index)`` returns the stage that must
be applied *before* running turn ``turn_index`` (i.e. the stage whose
``applies_between_turns`` ends at that turn). run_batch wires this into the
openclaw runner's ``before_turn`` hook.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests

LOG = logging.getLogger("wildclaw.inject")


class InjectConfigError(Exception):
    """Raised for a malformed inject/ directory."""


# ---------------------------------------------------------------------------
# Script model
# ---------------------------------------------------------------------------

def _turn_to_index(token: Any) -> Optional[int]:
    """Parse a turn token like ``"T13"`` / ``13`` / ``null`` -> int or None."""
    if token is None:
        return None
    if isinstance(token, int):
        return token
    m = re.match(r"\s*T?(\d+)\s*$", str(token))
    return int(m.group(1)) if m else None


@dataclass
class InjectStage:
    index: int
    name: str
    # (from_turn, to_turn): the mutation is applied AFTER from_turn and BEFORE
    # to_turn. from_turn is None for the pre-T0 seed stage.
    from_turn: Optional[int]
    to_turn: Optional[int]
    filesystem: List[Dict[str, Any]] = field(default_factory=list)
    loud: List[Dict[str, Any]] = field(default_factory=list)
    silent: List[Dict[str, Any]] = field(default_factory=list)
    source: str = ""

    @property
    def is_seed(self) -> bool:
        return self.from_turn is None


def _coerce_mutation_buckets(raw_muts: Any) -> Tuple[list, list, list]:
    """Return (filesystem, loud, silent) from a stage's ``mutations`` value.

    Tolerates two on-disk shapes seen in the Talos export:
      * dict form: ``{"filesystem": [...], "loud": [...], "silent": [...]}``
      * list form: a flat list of op dicts, each optionally carrying
        ``silent: true`` / ``kind`` / ``bucket`` to classify it.
    Unknown shapes yield three empty lists (logged by the caller).
    """
    if isinstance(raw_muts, dict):
        return (
            list(raw_muts.get("filesystem") or []),
            list(raw_muts.get("loud") or []),
            list(raw_muts.get("silent") or []),
        )
    if isinstance(raw_muts, list):
        fs: list = []
        loud: list = []
        silent: list = []
        for op in raw_muts:
            if not isinstance(op, dict):
                continue
            bucket = op.get("bucket") or op.get("kind")
            if op.get("silent") is True or bucket == "silent":
                silent.append(op)
            elif "action" in op or bucket == "filesystem":
                fs.append(op)
            elif op.get("service") or op.get("path"):
                # An API op with no explicit silent flag in list form: treat as
                # loud (visible) by default — silent must be opted into.
                loud.append(op)
        return fs, loud, silent
    return [], [], []


@dataclass
class InjectScript:
    description: str
    stages: List[InjectStage] = field(default_factory=list)

    @classmethod
    def load(cls, inject_dir: Path | str) -> "InjectScript":
        d = Path(inject_dir)
        if not d.is_dir():
            raise InjectConfigError(f"inject dir not found: {d}")
        stage_dirs = sorted(
            (p for p in d.iterdir() if p.is_dir() and re.match(r"stage\d+$", p.name)),
            key=lambda p: int(re.match(r"stage(\d+)$", p.name).group(1)),
        )
        if not stage_dirs:
            raise InjectConfigError(f"no stageN/ dirs under {d}")
        stages: List[InjectStage] = []
        for sd in stage_dirs:
            mf = sd / "mutations.json"
            if not mf.is_file():
                LOG.warning("inject: %s has no mutations.json; skipping", sd.name)
                continue
            try:
                raw = json.loads(mf.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise InjectConfigError(f"{mf}: {exc}") from exc
            idx = int(re.match(r"stage(\d+)$", sd.name).group(1))
            between = (
                raw.get("applies_between_turns")
                or raw.get("applied_between")
                or [None, None]
            )
            from_turn = _turn_to_index(between[0]) if len(between) > 0 else None
            to_turn = _turn_to_index(between[1]) if len(between) > 1 else None
            fs, loud, silent = _coerce_mutation_buckets(raw.get("mutations"))
            if not (fs or loud or silent):
                LOG.warning("inject: %s mutations had no recognized ops "
                            "(shape=%s)", sd.name, type(raw.get("mutations")).__name__)
            stages.append(InjectStage(
                index=idx,
                name=str(raw.get("stage_name") or sd.name),
                from_turn=from_turn,
                to_turn=to_turn,
                filesystem=fs,
                loud=loud,
                silent=silent,
                source=str(mf),
            ))
        return cls(description=f"inject:{d.name}", stages=stages)

    def seed_stage(self) -> Optional[InjectStage]:
        for s in self.stages:
            if s.is_seed:
                return s
        return None

    def stage_for_boundary(self, turn_index: int) -> Optional[InjectStage]:
        """The non-seed stage that must be applied BEFORE running ``turn_index``.

        A stage with ``applies_between_turns: ["T12", "T13"]`` is returned when
        ``turn_index == 13`` (its ``to_turn``).
        """
        for s in self.stages:
            if not s.is_seed and s.to_turn == turn_index:
                return s
        return None


# ---------------------------------------------------------------------------
# prompts.txt parsing (50-turn wake-up script)
# ---------------------------------------------------------------------------

# The ``T`` before the turn number is optional: both ``--- TURN T1 ... ---``
# (canonical) and ``--- TURN 1 ... ---`` are accepted. This mirrors the
# multi-agent header detector (_multi_agent_config_from_complex_turns uses
# ``TURN\s+T?(\d+)``); keeping the two in sync prevents a task from passing
# multi-agent detection while its prompt body silently fails to parse (which
# yields an empty --message and an immediate agent crash).
_TURN_RE = re.compile(r"^---\s*TURN\s+T?(\d+)\b.*?---\s*$", re.IGNORECASE)


def parse_prompts_file(path: Path | str) -> List[str]:
    """Parse a ``prompts.txt`` into an ordered list of per-turn wake-up messages.

    Recognizes block headers of the form ``--- TURN T<n> (...) ---``; the body
    is every non-comment, non-blank line until the next header. Leading ``#``
    banner/comment lines (before the first TURN header, and full-line ``#``
    comments) are ignored. Turns are returned ordered by their T-index.
    """
    text = Path(path).read_text(encoding="utf-8")
    turns: Dict[int, List[str]] = {}
    current: Optional[int] = None
    for line in text.splitlines():
        m = _TURN_RE.match(line.strip())
        if m:
            current = int(m.group(1))
            turns.setdefault(current, [])
            continue
        if current is None:
            continue
        if line.strip().startswith("#"):
            continue
        turns[current].append(line)
    ordered = []
    for idx in sorted(turns):
        body = "\n".join(turns[idx]).strip()
        ordered.append(body)
    return ordered


# ---------------------------------------------------------------------------
# Applier
# ---------------------------------------------------------------------------

# Map a Talos ``service`` name -> the admin-plane store table(s) to search and
# the columns that hold a human/business key we can match a placeholder against.
# Each entry: (candidate_table_prefixes, business_key_columns).
_SERVICE_RESOLUTION = {
    "airtable-api": (("records_",), ("PlotID", "plot_id", "Name", "name", "id")),
    "notion-api": (("pages",), ("title", "Name", "name", "id")),
    "confluence-api": (("pages",), ("title", "Name", "name", "id")),
}


class InjectApplier:
    """Applies a stage's silent mutations through each API's ``/admin/*`` plane.

    ``host_api_to_url`` maps api-name -> ``http://127.0.0.1:<published-port>``
    (the same map the DriftDirector / StageApplier use). Every applied or
    skipped mutation is appended to ``inject_timeline.jsonl``.

    ``copy_into_workspace`` (optional) is ``fn(host_src: Path, container_dst:
    str) -> bool`` used to seed stage0 filesystem drops; when absent, filesystem
    ops are logged as ``skipped``.
    """

    def __init__(
        self,
        host_api_to_url: Dict[str, str],
        admin_token: Optional[str],
        timeline_path: Path,
        inject_root: Optional[Path] = None,
        copy_into_workspace=None,
        replay_loud: bool = False,
    ):
        self._urls = dict(host_api_to_url)
        self._token = admin_token
        self._timeline_path = Path(timeline_path)
        self._timeline_path.parent.mkdir(parents=True, exist_ok=True)
        self._inject_root = Path(inject_root) if inject_root else None
        self._copy = copy_into_workspace
        self._replay_loud = replay_loud
        self._session = requests.Session()

    # -- public API ---------------------------------------------------------

    def seed(self, script: InjectScript) -> None:
        stage = script.seed_stage()
        if stage is None:
            return
        self._append({"type": "inject.seed.start", "ts": time.time(),
                      "stage": stage.name,
                      "fs": len(stage.filesystem), "loud": len(stage.loud)})
        for op in stage.filesystem:
            self._apply_filesystem(op, stage)
        if self._replay_loud:
            for op in stage.loud:
                self._apply_api_mutation(op, stage, turn_index=0, silent=False)
        self._append({"type": "inject.seed.done", "ts": time.time(),
                      "stage": stage.name})

    def apply_stage(self, stage: InjectStage, turn_index: int) -> List[Dict[str, Any]]:
        outcomes: List[Dict[str, Any]] = []
        for op in stage.silent:
            outcomes.append(self._apply_api_mutation(op, stage, turn_index, silent=True))
        # Mid-run `loud` ops are VISIBLE API mutations applied between turns: a new
        # email/event/row the agent will discover through normal API reads. Unlike
        # the stage0 (seed) loud ops — which describe pre-T0 baseline state already
        # carried by the mock_data overlays and are therefore gated behind
        # `replay_loud` to avoid double-application — a loud op in a stage >= 1 has
        # no overlay redundancy, so it must fire here. Applied with silent=False so
        # the timeline records it as agent-visible (no /admin stealth semantics).
        # NOTE: to INSERT a brand-new row (e.g. a phishing email) the op must carry
        # an explicit ``admin`` block with ``op: upsert``; a bare REST POST with no
        # admin block resolves no existing target and is logged ``unresolved``.
        for op in stage.loud:
            outcomes.append(self._apply_api_mutation(op, stage, turn_index, silent=False))
        # list-form stages may also carry filesystem drops mid-run
        for op in stage.filesystem:
            outcomes.append(self._apply_filesystem(op, stage))
        self._append({
            "type": "inject.stage.applied",
            "ts": time.time(),
            "stage": stage.name,
            "applied_before_turn": turn_index,
            "silent_ops": len(stage.silent),
            "loud_ops": len(stage.loud),
            "outcomes": outcomes,
        })
        LOG.info("inject stage '%s' applied before turn %d: %d silent op(s), %d loud op(s)",
                 stage.name, turn_index, len(stage.silent), len(stage.loud))
        return outcomes

    def close(self) -> None:
        self._session.close()

    # -- full-state snapshot ------------------------------------------------

    def snapshot_state(self, dest_dir: Path | str, label: str = "") -> Dict[str, Any]:
        """Dump the FULL live state of every mock API into ``dest_dir``.

        Walks each API's ``/admin/*`` plane and writes, per service, every
        registered table's rows and every document. Used to capture a
        before-injection and an after-injection picture of the data the agent
        sees, so a reviewer can diff exactly what the silent mutations changed.

        The on-disk layout mirrors the task's own ``mock_data/`` overlays —
        tables as flat CSV, documents as flat JSON — so a reviewer can diff the
        before/after snapshot against the seed data in the exact same format::

            <dest_dir>/
                _manifest.json                 # which apis/tables/docs, row counts
                <api>/<table>.csv              # header row + one row per record
                <api>/<doc>.json               # the raw document value

        Returns the manifest dict (also persisted as ``_manifest.json``).
        """
        dest = Path(dest_dir)
        dest.mkdir(parents=True, exist_ok=True)
        manifest: Dict[str, Any] = {
            "label": label,
            "ts": time.time(),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "apis": {},
        }
        for api in sorted(self._urls):
            tbl_resp = self._admin_get(api, "/admin/tables")
            if isinstance(tbl_resp, dict):
                tlist = tbl_resp.get("tables", []) or []
                dlist = tbl_resp.get("documents", []) or []
            else:
                tlist = tbl_resp or []
                dlist = []
            table_names = [t.get("name") if isinstance(t, dict) else t for t in tlist]
            doc_names = [d.get("name") if isinstance(d, dict) else d for d in dlist]

            api_entry: Dict[str, Any] = {"tables": {}, "documents": {}}
            api_dir = dest / api
            for table in table_names:
                if not table:
                    continue
                rows = self._admin_get_rows(api, table)
                api_dir.mkdir(parents=True, exist_ok=True)
                self._write_rows_csv(api_dir / f"{table}.csv", rows)
                api_entry["tables"][table] = len(rows)
            for doc in doc_names:
                if not doc:
                    continue
                value = self._admin_get(api, f"/admin/doc/{doc}")
                api_dir.mkdir(parents=True, exist_ok=True)
                with open(api_dir / f"{doc}.json", "w", encoding="utf-8") as f:
                    json.dump(value, f, indent=2, default=str)
                api_entry["documents"][doc] = True
            manifest["apis"][api] = api_entry

        with open(dest / "_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, default=str)
        self._append({"type": "inject.snapshot", "label": label,
                      "dest": str(dest), "apis": list(manifest["apis"].keys()),
                      "ts": time.time()})
        LOG.info("inject snapshot '%s' written to %s (%d api(s))",
                 label, dest, len(manifest["apis"]))
        return manifest

    @staticmethod
    def _flatten_row(row: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten one store row to scalar CSV cells. Airtable-style rows nest
        their data under ``fields``; lift those to top-level columns (alongside
        ``id``/``createdTime``) so the CSV matches the seed ``mock_data`` shape.
        Non-scalar values are JSON-encoded; ``None`` becomes the empty string."""
        if not isinstance(row, dict):
            return {"value": row}
        flat: Dict[str, Any] = {}
        nested = row.get("fields") if isinstance(row.get("fields"), dict) else None
        for k, v in row.items():
            if k == "fields" and nested is not None:
                continue
            flat[k] = v
        if nested is not None:
            flat.update(nested)
        out: Dict[str, Any] = {}
        for k, v in flat.items():
            if v is None:
                out[k] = ""
            elif isinstance(v, (dict, list)):
                out[k] = json.dumps(v, ensure_ascii=False, default=str)
            elif isinstance(v, bool):
                out[k] = str(v)
            else:
                out[k] = v
        return out

    @classmethod
    def _write_rows_csv(cls, path: Path, rows: List[Dict[str, Any]]) -> None:
        """Write ``rows`` as CSV at ``path``. The header is the union of column
        names in first-seen order across all rows. An empty table still yields a
        file (header-only / empty) so before/after diffs stay aligned."""
        flat_rows = [cls._flatten_row(r) for r in (rows or [])]
        header: List[str] = []
        seen = set()
        for fr in flat_rows:
            for k in fr:
                if k not in seen:
                    seen.add(k)
                    header.append(k)
        with open(path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=header, extrasaction="ignore")
            if header:
                writer.writeheader()
            for fr in flat_rows:
                writer.writerow(fr)

    # -- filesystem ---------------------------------------------------------

    def _apply_filesystem(self, op: Dict[str, Any], stage: InjectStage) -> Dict[str, Any]:
        action = op.get("action")
        dst = op.get("dst")
        rec = {"id": op.get("id"), "action": action, "dst": dst}
        if self._copy is None or self._inject_root is None:
            rec.update(ok=False, status="skipped", reason="no workspace copy hook")
            self._append({"type": "inject.fs", **rec, "ts": time.time()})
            return rec
        if action == "mkdir":
            ok = self._copy(None, dst, mkdir=True)
            rec.update(ok=bool(ok), status="mkdir")
            self._append({"type": "inject.fs", **rec, "ts": time.time()})
            return rec
        src = op.get("src")
        if not src or not dst:
            rec.update(ok=False, status="skipped", reason="missing src/dst")
            self._append({"type": "inject.fs", **rec, "ts": time.time()})
            return rec
        stage_dir = Path(stage.source).parent
        host_src = (stage_dir / src).resolve()
        # Several Talos ops name only the bare filename in ``src`` while the file
        # actually lives in a stage subdir (grants/, family/, field/maps/, ...).
        # Fall back to a basename search within the stage dir before giving up.
        if not host_src.exists():
            hits = [p for p in stage_dir.rglob(Path(src).name)
                    if p.is_file() and "_placeholders" not in p.parts]
            if hits:
                host_src = hits[0].resolve()
        # Placeholder stand-ins are never load-bearing content; skip with a note.
        if not host_src.exists():
            rec.update(ok=False, status="missing_src", reason=str(host_src))
            self._append({"type": "inject.fs", **rec, "ts": time.time()})
            return rec
        rec["src"] = str(host_src)
        try:
            ok = self._copy(host_src, dst)
            rec.update(ok=bool(ok), status="copied")
        except Exception as exc:  # pragma: no cover - defensive
            rec.update(ok=False, status="error", reason=str(exc))
        self._append({"type": "inject.fs", **rec, "ts": time.time()})
        return rec

    # -- API mutation -------------------------------------------------------

    def _headers(self) -> Dict[str, str]:
        return {"X-Admin-Token": self._token} if self._token else {}

    def _admin_get(self, api: str, suffix: str) -> Any:
        base = self._urls.get(api)
        if not base:
            return None
        try:
            r = self._session.get(base.rstrip("/") + suffix,
                                  headers=self._headers(), timeout=5.0)
            if r.status_code == 200:
                return r.json()
        except (requests.RequestException, ValueError):
            return None
        return None

    def audit_summary(self) -> Dict[str, Any]:
        """Return the agent-visible API call audit, keyed by service name:
        ``{"<api>": {"total_requests": int, "endpoints": {"<METHOD path>":
        {"count": int, "statuses": {...}}}}}``.

        Read from each live service's ``/audit/summary`` (the same feed the
        agent's own calls land in; silent ``/admin`` injects are excluded by
        the tracking middleware). This is the ``state["audit"]`` the
        deterministic CHECKERS query via ``_api_called`` / ``_api_NOT_called``.
        """
        audit: Dict[str, Any] = {}
        for api in sorted(self._urls):
            base = self._urls.get(api)
            if not base:
                continue
            try:
                r = self._session.get(base.rstrip("/") + "/audit/summary",
                                      headers=self._headers(), timeout=5.0)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict):
                        audit[api] = data
            except (requests.RequestException, ValueError):
                continue
        return audit

    def audit_full(self) -> Dict[str, Any]:
        """Return the FULL per-service request diary (bodies included), keyed by
        service name: ``{"<api>": {"total": int, "requests": [{method, path,
        query_params, request_body, status_code, response_body, ...}, ...]}}``.

        Read from each live service's ``/audit/requests`` (the tracking
        middleware's complete log). ``audit_summary`` keeps only per-endpoint
        counts; tests that inspect ``request_body`` (e.g. "did the agent write
        Room 112?") need this full diary. Persisting it into agent_state.json
        is what lets those tests re-run OFFLINE — no live mock stack required.
        """
        full: Dict[str, Any] = {}
        for api in sorted(self._urls):
            base = self._urls.get(api)
            if not base:
                continue
            try:
                r = self._session.get(base.rstrip("/") + "/audit/requests",
                                      headers=self._headers(), timeout=10.0)
                if r.status_code == 200:
                    data = r.json()
                    if isinstance(data, dict):
                        full[api] = data
            except (requests.RequestException, ValueError):
                continue
        return full

    def _admin_patch(self, api: str, table: str, pk: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        base = self._urls.get(api)
        if not base:
            return {"ok": False, "error": "no admin URL"}
        try:
            r = self._session.patch(
                base.rstrip("/") + f"/admin/data/{table}/{pk}",
                json={"fields": fields},
                headers=self._headers(), timeout=5.0,
            )
            ctype = r.headers.get("content-type", "")
            return {"ok": r.status_code < 300, "status": r.status_code,
                    "body": r.json() if ctype.startswith("application/json") else r.text[:200]}
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}

    def _admin_post(self, api: str, suffix: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        base = self._urls.get(api)
        if not base:
            return {"ok": False, "error": "no admin URL"}
        try:
            r = self._session.post(base.rstrip("/") + suffix, json=payload,
                                   headers=self._headers(), timeout=5.0)
            ctype = r.headers.get("content-type", "")
            return {"ok": r.status_code < 300, "status": r.status_code,
                    "body": r.json() if ctype.startswith("application/json") else r.text[:200]}
        except requests.RequestException as exc:
            return {"ok": False, "error": str(exc)}

    def _list_tables(self, api: str) -> List[str]:
        resp = self._admin_get(api, "/admin/tables")
        tlist = resp.get("tables", []) if isinstance(resp, dict) else (resp or [])
        return [t.get("name") if isinstance(t, dict) else t for t in tlist]

    def _resolve_store_table(self, api: str, wanted: Optional[str]) -> Optional[str]:
        """Map a friendly table name to the real registered store table name
        (airtable registers tables as ``records_<tableId>``, etc.)."""
        if not wanted:
            return wanted
        names = self._list_tables(api)
        w = str(wanted).lower()
        for n in names:                       # exact
            if str(n).lower() == w:
                return n
        for n in names:                       # records_<wanted> / plural
            if str(n).lower() in (f"records_{w}", f"{w}s", f"records_{w}s"):
                return n
        for n in names:                       # substring either direction
            nl = str(n).lower()
            if w in nl or nl in w:
                return n
        return wanted

    def _admin_get_rows(self, api: str, table: str) -> List[Dict[str, Any]]:
        data = self._admin_get(api, f"/admin/data/{table}")
        if isinstance(data, dict):
            return data.get("rows", data.get("data", [])) or []
        return data or []

    @staticmethod
    def _row_bag(row: Dict[str, Any]) -> Dict[str, Any]:
        return row["fields"] if isinstance(row.get("fields"), dict) else row

    def _patch_row(self, api: str, table: str, row: Dict[str, Any],
                   set_: Dict[str, Any]) -> Dict[str, Any]:
        """Patch one row, nested-``fields`` aware. The admin PATCH shallow-merges
        top-level keys, so an airtable-style nested ``fields`` object must be
        resent whole (existing + overrides)."""
        pk = row.get("id") or row.get("pk")
        if pk is None:
            return {"ok": False, "error": "no pk"}
        if isinstance(row.get("fields"), dict):
            payload = {"fields": {**row["fields"], **set_}}
        else:
            payload = dict(set_)
        return self._admin_patch(api, table, str(pk), payload)

    def _apply_admin_op(self, api: str, spec: Dict[str, Any], op: Dict[str, Any],
                        silent: bool = True) -> Dict[str, Any]:
        """Apply an explicit admin-plane op. ``spec`` is the op's ``admin`` block:
          * ``{op:'patch', table, pk, set:{...}}``          -- one row
          * ``{op:'update_where', table, where:{...}, set:{...}}`` -- bulk by field
          * ``{op:'doc_set', document, path:[...], value}`` -- nested document value
        """
        kind = (spec.get("op") or "patch").lower()
        rec: Dict[str, Any] = {"id": op.get("id"), "service": api, "silent": silent,
                               "admin_op": kind}
        try:
            if kind == "patch":
                table = self._resolve_store_table(api, spec.get("table"))
                pk = str(spec.get("pk"))
                set_ = spec.get("set") or {}
                row = self._admin_get(api, f"/admin/data/{table}/{pk}")
                if not isinstance(row, dict):
                    rec.update(ok=False, status="unresolved", table=table, pk=pk,
                               reason="row not found")
                else:
                    bag = self._row_bag(row)
                    before = {k: bag.get(k) for k in set_}
                    res = self._patch_row(api, table, row, set_)
                    after = {k: v for k, v in set_.items()} if res.get("ok") else before
                    rec.update(table=table, pk=pk, ok=bool(res.get("ok")),
                               http=res.get("status"), before=before, after=after,
                               changed=res.get("ok") and before != after,
                               status="applied" if res.get("ok") else "failed")
            elif kind in ("update_where", "bulk"):
                table = self._resolve_store_table(api, spec.get("table"))
                where = spec.get("where") or {}
                set_ = spec.get("set") or {}
                rows = self._admin_get_rows(api, table)
                matched = ok = 0
                before = after = None
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    bag = self._row_bag(row)
                    if not all(self._loose_eq(bag.get(k), v) for k, v in where.items()):
                        continue
                    if before is None:
                        before = {k: bag.get(k) for k in set_}
                    res = self._patch_row(api, table, row, set_)
                    matched += 1
                    ok += 1 if res.get("ok") else 0
                after = dict(set_) if ok else before
                rec.update(table=table, matched=matched, patched=ok,
                           before=before, after=after,
                           changed=ok > 0 and before != after,
                           ok=ok > 0, status="applied" if ok else "no-match")
            elif kind == "upsert":
                # Inject a new row (an incoming email / slack message / page) so it
                # appears when the agent next READS that service — silent (no audit
                # POST). For airtable-style stores the row nests under ``fields``.
                table = self._resolve_store_table(api, spec.get("table"))
                row = dict(spec.get("row") or {})
                pk_field = spec.get("pk_field") or "id"
                pk = row.get(pk_field)
                existed = self._admin_get(api, f"/admin/data/{table}/{pk}") if pk else None
                res = self._admin_post(api, f"/admin/data/{table}", {"row": row})
                rec.update(table=table, pk=pk, ok=bool(res.get("ok")), http=res.get("status"),
                           before=None if not isinstance(existed, dict) else "exists",
                           after=pk,
                           changed=res.get("ok") and not isinstance(existed, dict),
                           status="applied" if res.get("ok") else "failed")
            elif kind in ("doc_set", "doc_merge", "doc.merge"):
                doc = spec.get("document") or spec.get("doc")
                res = self._admin_doc_set(api, doc, spec.get("path") or [], spec.get("value"))
                rec.update(document=doc, before=res.get("before"), after=res.get("after"),
                           changed=res.get("changed"), ok=res.get("ok"), http=res.get("status"),
                           status=("applied" if res.get("ok") and res.get("changed")
                                   else ("no-change" if res.get("ok") else "failed")),
                           reason=res.get("reason"))
            else:
                rec.update(ok=False, status="unresolved", reason=f"unknown admin op '{kind}'")
        except Exception as exc:  # pragma: no cover - defensive
            rec.update(ok=False, status="error", reason=str(exc))
        self._append({"type": "inject.api", **rec, "ts": time.time()})
        return rec

    def _admin_doc_set(self, api: str, doc: str, path: List[Any], value: Any) -> Dict[str, Any]:
        """Read-modify-merge a nested value in a registered document store
        (e.g. notion ``properties`` = ``{page_id:{prop:{type,value}}}``)."""
        cur = self._admin_get(api, f"/admin/doc/{doc}")
        if not isinstance(cur, dict):
            return {"ok": False, "before": None, "after": None, "changed": False,
                    "reason": f"doc '{doc}' not found"}
        if not path:
            return {"ok": False, "changed": False, "reason": "empty path"}
        node = cur
        for key in path[:-1]:
            if not isinstance(node, dict) or key not in node:
                return {"ok": False, "before": None, "after": None, "changed": False,
                        "reason": f"path {path} missing at '{key}'"}
            node = node[key]
        leaf = path[-1]
        before = node.get(leaf) if isinstance(node, dict) else None
        if before == value:
            return {"ok": True, "before": before, "after": before, "changed": False}
        node[leaf] = value
        top = path[0]
        res = self._admin_post(api, f"/admin/doc/{doc}/merge", {"fields": {top: cur[top]}})
        return {"ok": bool(res.get("ok")), "before": before,
                "after": value if res.get("ok") else before,
                "changed": bool(res.get("ok")), "status": res.get("status")}

    @staticmethod
    def _loose_eq(a: Any, b: Any) -> bool:
        if a == b:
            return True
        # tolerate bool/str ("True"/"true"/True) and numeric/str mismatches
        sa, sb = str(a).strip().lower(), str(b).strip().lower()
        return sa == sb

    def _apply_api_mutation(self, op: Dict[str, Any], stage: InjectStage,
                            turn_index: int, silent: bool) -> Dict[str, Any]:
        api = op.get("service") or op.get("api")
        rec = {"id": op.get("id"), "service": api, "method": op.get("method"),
               "path": op.get("path"), "silent": silent}
        if not api or api not in self._urls:
            rec.update(ok=False, status="unresolved", reason=f"no admin URL for {api}")
            self._append({"type": "inject.api", **rec, "ts": time.time()})
            return rec
        # Explicit admin-op form (the unambiguous representation): the op carries
        # an ``admin`` block naming the exact store table/document, pk/where/path,
        # and the values to set. Dispatched directly — no fuzzy path resolution.
        if isinstance(op.get("admin"), dict):
            return self._apply_admin_op(api, op["admin"], op, silent)
        resolved = self._resolve_target(api, op)
        if resolved is None:
            params = op.get("params") if isinstance(op.get("params"), dict) else None
            if params and params.get("filter") and not params.get("field_updates"):
                # e.g. SM8 "archive 53 rows matching <filter>": a bulk op with no
                # per-row field_updates/record_id. Not a single-row patch; the
                # archive column+value is unspecified, so we cannot apply it.
                reason = ("bulk filter op unsupported (no record_id/field_updates; "
                          f"filter={params.get('filter')!r})")
            else:
                reason = "could not locate target row in live store"
            rec.update(ok=False, status="unresolved", reason=reason)
            self._append({"type": "inject.api", **rec, "ts": time.time()})
            return rec
        table, pk, fields = resolved
        rec.update(table=table, pk=pk, fields=list(fields.keys()))
        result = self._admin_patch(api, table, pk, fields)
        rec.update(result)
        rec["status"] = rec.get("status", "applied" if result.get("ok") else "failed")
        self._append({"type": "inject.api", **rec, "ts": time.time()})
        return rec

    def _resolve_target(self, api: str, op: Dict[str, Any]
                        ) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """Resolve a Talos REST mutation to (table, pk, fields) against live state.

        Strategy: pull the flat field map from the op body (supports the airtable
        ``{fields:{...}}`` and notion/confluence ``{properties:{...}}`` shapes),
        extract the business key embedded in the path placeholder, then scan the
        candidate store tables for the matching row and map field casing to the
        row's real column names.

        Two on-disk op shapes are supported:
          * stage1/2 REST form: ``{method, path:".../{rec_KEY}", body:{fields|
            properties:{...}}}`` — key comes from the path placeholder.
          * stage3 ``params`` form: ``{action, params:{table_id, record_id,
            field_updates:{...}}}`` — record_id is the business key and
            field_updates carries the new values. Bulk/filter params with no
            ``record_id``/``field_updates`` (e.g. archive-by-filter) are not a
            single-row patch and resolve to None (logged distinctly upstream).
        """
        new_fields = self._extract_fields(op)
        if not new_fields:
            return None
        key = self._extract_key_from_op(op)
        prefixes, key_cols = _SERVICE_RESOLUTION.get(api, ((), ("id",)))
        # /admin/tables returns {"tables":[{name,...}], "documents":[...]}.
        tbl_resp = self._admin_get(api, "/admin/tables")
        tlist = tbl_resp.get("tables", []) if isinstance(tbl_resp, dict) else (tbl_resp or [])
        table_names = [t.get("name") if isinstance(t, dict) else t for t in tlist]
        candidates = [t for t in table_names
                      if any(str(t).startswith(p) for p in prefixes)] or table_names
        for table in candidates:
            # /admin/data/{table} returns {"rows":[{id, ..., fields:{...}}]}.
            data = self._admin_get(api, f"/admin/data/{table}")
            rows = data.get("rows", data.get("data", [])) if isinstance(data, dict) else (data or [])
            for row in rows:
                if not isinstance(row, dict):
                    continue
                # airtable-style rows nest the business columns under "fields";
                # other services keep them top-level. Match + patch the bag that
                # actually holds the columns.
                nested = isinstance(row.get("fields"), dict)
                bag = row["fields"] if nested else row
                pk = row.get("id") or row.get("pk")
                if pk is None:
                    continue
                if key is not None:
                    # The key may be the store pk directly (stage3 record_id,
                    # e.g. "recUDI007") or a business key in a column.
                    pk_match = str(pk).strip().lower() == key.strip().lower()
                    if not pk_match and not self._bag_matches_key(bag, key, key_cols):
                        continue
                mapped = self._map_fields_to_row(new_fields, bag)
                if not mapped:
                    continue
                if nested:
                    # Table.patch shallow-replaces top-level keys, so the nested
                    # "fields" sub-object must be resent whole (merged).
                    patch_fields = {"fields": {**row["fields"], **mapped}}
                else:
                    patch_fields = mapped
                return table, str(pk), patch_fields
        return None

    @staticmethod
    def _extract_fields(op: Dict[str, Any]) -> Dict[str, Any]:
        # stage3 params form: the new values live under params.field_updates.
        params = op.get("params")
        if isinstance(params, dict) and isinstance(params.get("field_updates"), dict):
            return {k: v for k, v in params["field_updates"].items()
                    if not str(k).startswith("_")}
        body = op.get("body") or {}
        if not isinstance(body, dict):
            return {}
        if isinstance(body.get("fields"), dict):
            flat = {k: v for k, v in body["fields"].items() if not k.startswith("_")}
            return flat
        if isinstance(body.get("properties"), dict):
            # Flatten notion/confluence property shapes to leaf scalar values.
            flat = {}
            for k, v in body["properties"].items():
                flat[k] = _flatten_property_value(v)
            return flat
        # whole-body scalar fields (rare)
        return {k: v for k, v in body.items()
                if isinstance(v, (str, int, float, bool)) and not k.startswith("_")}

    @classmethod
    def _extract_key_from_op(cls, op: Dict[str, Any]) -> Optional[str]:
        """Business key for an op: stage3 ``params.record_id`` if present, else
        the placeholder embedded in the REST path."""
        params = op.get("params")
        if isinstance(params, dict):
            rid = params.get("record_id") or params.get("page_id") or params.get("id")
            if rid:
                # record_id may itself be a store pk (recUDI007) or a business
                # key; _bag_matches_key handles both, but strip any rec_/page_ wrap.
                return re.sub(r"^(rec_|page_id_|id_|page_)", "", str(rid)).strip() or None
        return cls._extract_key_from_path(op.get("path", ""))

    @staticmethod
    def _extract_key_from_path(path: str) -> Optional[str]:
        """Pull the business key out of a path placeholder.

        ``/v0/app/Field-Trial-Udi/records/{rec_UDI-2026-007}`` -> ``UDI-2026-007``
        ``/v1/pages/{page_id_WAITA-EACRI_Proposal_v8.0}``       -> ``WAITA-EACRI_Proposal_v8.0``
        A non-placeholder trailing id is returned verbatim.
        """
        m = re.search(r"\{([^}]+)\}", path or "")
        token = m.group(1) if m else (path or "").rstrip("/").rsplit("/", 1)[-1]
        if not token:
            return None
        token = re.sub(r"^(rec_|page_id_|id_|rec|page_)", "", token)
        return token.strip() or None

    @staticmethod
    def _bag_matches_key(bag: Dict[str, Any], key: str, key_cols: Tuple[str, ...]) -> bool:
        """True if the column bag identifies the target row by its business key."""
        norm = key.replace("_", " ").replace("-", " ").lower().strip()
        for col in key_cols:
            for rk, rv in bag.items():
                if rk.lower() != col.lower():
                    continue
                if rv is None:
                    continue
                rvn = str(rv).replace("_", " ").replace("-", " ").lower().strip()
                if rvn == norm or norm in rvn or rvn in norm:
                    return True
        # also try any column equalling the raw key
        for rv in bag.values():
            if rv is not None and str(rv).strip().lower() == key.strip().lower():
                return True
        return False

    @staticmethod
    def _map_fields_to_row(fields: Dict[str, Any], row: Dict[str, Any]) -> Dict[str, Any]:
        """Map mutation field names to the row's real column casing.

        ``{"yield_kg_m2": 16.8}`` against a row with column ``Yield_kg_m2`` ->
        ``{"Yield_kg_m2": 16.8}``. Unmatched fields are passed through verbatim
        (the admin plane will add them as-is) so a deliberately new column still
        lands, but matched ones avoid creating a dead duplicate-cased column.
        """
        lower_to_real = {k.lower(): k for k in row.keys()}
        mapped: Dict[str, Any] = {}
        for k, v in fields.items():
            real = lower_to_real.get(k.lower(), k)
            mapped[real] = v
        return mapped

    # -- timeline -----------------------------------------------------------

    def _append(self, entry: Dict[str, Any]) -> None:
        entry.setdefault("ts", time.time())
        entry.setdefault("ts_iso", time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(entry.get("ts", time.time()))))
        with open(self._timeline_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")


def _flatten_property_value(v: Any) -> Any:
    """Reduce a notion/confluence property object to a representative scalar."""
    if isinstance(v, dict):
        if "email" in v:
            return v["email"]
        if "select" in v and isinstance(v["select"], dict):
            return v["select"].get("name")
        if "date" in v and isinstance(v["date"], dict):
            return v["date"].get("start")
        for key in ("title", "rich_text"):
            arr = v.get(key)
            if isinstance(arr, list) and arr:
                t = arr[0].get("text") if isinstance(arr[0], dict) else None
                if isinstance(t, dict):
                    return t.get("content")
        if "value" in v:
            return v["value"]
    return v
