"""
WildClawBench admin plane: out-of-band mutation surface for mock API state.

This router is installed by every ``<api>/server.py`` via the one-line call
``install_admin_plane(app, store=get_store("<api-name>"))``. It is a no-op
unless the environment variable ``MOCK_ADMIN_ENABLED=1`` is set on the mock
container --- so for normal benchmark runs (no drift) the admin plane is
absent and the container's behavior is byte-identical to today's mocks.

When enabled, the router exposes endpoints under ``/admin/*`` that let the
DriftDirector (running on the harness host) mutate the in-memory data store
mid-run, causing subsequent agent-visible responses to diverge from whatever
the persona's MEMORY.md committed to.

Security model
--------------
1. ``MOCK_ADMIN_ENABLED`` must be set to ``"1"``. Anything else (unset, "0",
   "true", "yes", etc.) leaves the router uninstalled.

2. An IP allowlist middleware blocks every ``/admin/*`` request that does not
   originate from one of the IPs in ``MOCK_ADMIN_ALLOWLIST`` (comma-separated).
   The harness sets this to the host IP visible inside the mock container's
   network (typically the Docker bridge gateway). The agent container is on
   the same Docker network but at a different IP, so it cannot reach the
   admin plane even if it discovers the routes.

   The allowlist matches the raw TCP source IP. For proxied deployments,
   set ``MOCK_ADMIN_ALLOWLIST`` to the proxy's IP, OR enable
   ``MOCK_ADMIN_TRUST_FORWARDED_FOR=1`` to parse the first IP from the
   ``X-Forwarded-For`` request header (off by default --- only enable behind
   a trusted proxy that strips client-supplied values).

3. The audit/tracking middleware that records all requests for the agent's
   visibility is configured to skip ``/admin/*`` paths (already done in
   ``tracking_middleware.py`` for ``/audit/*``; we add ``/admin/*`` to the
   same skip-list at install time). The agent therefore cannot see drift
   events even via ``/audit/requests``.

4. Every mutation is recorded twice: once in the per-store drift log
   (``GET /admin/drift/log``) and once by the host-side DriftDirector into
   ``drift_timeline.jsonl`` in the run output dir. The two logs are
   cross-checked by the grader for causality (see the design doc).

Endpoint surface
----------------
* ``GET    /admin/health``                       --- liveness probe
* ``GET    /admin/tables``                       --- list registered tables/docs
* ``GET    /admin/data/{table}``                 --- list rows
* ``GET    /admin/data/{table}/{pk}``            --- one row
* ``POST   /admin/data/{table}``                 --- upsert one row
* ``PATCH  /admin/data/{table}/{pk}``            --- patch one row
* ``DELETE /admin/data/{table}/{pk}``            --- delete one row
* ``POST   /admin/data/{table}/bulk``            --- update_where / delete_where
* ``GET    /admin/doc/{doc}``                    --- read document
* ``PUT    /admin/doc/{doc}``                    --- replace document
* ``POST   /admin/doc/{doc}/merge``              --- shallow-merge fields
* ``POST   /admin/inject/raw``                   --- batch of operations
* ``POST   /admin/inject/one_shot``              --- queue response interceptor
* ``POST   /admin/scenario/apply``               --- apply named DriftScenario
* ``GET    /admin/snapshot``                     --- snapshot current state
* ``POST   /admin/snapshot/restore``             --- restore by snapshot id
* ``GET    /admin/drift/log``                    --- ordered list of mutations
* ``POST   /admin/drift/log/clear``              --- clear drift log

The ``inject/one_shot`` mechanism is the "Position 3" interceptor: instead of
mutating store state, it registers a transformation that will be applied to
the response of the very next request matching a path pattern, then expires.
This is how a drift script causes a one-time inconsistency without changing
the underlying data --- useful for "agent sees X once, sees the real value
on every retry" scenarios.

Why a FastAPI router instead of a dedicated server?
---------------------------------------------------
Each mock API already has its own uvicorn process bound to a specific port,
and the DriftDirector needs to talk to that specific store. Embedding the
admin plane in each app means there's no extra port to manage, no extra
service discovery, and the IP allowlist applies uniformly. The cost is a
small amount of code duplication across processes, which is fine.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
import uuid
from typing import Any, Callable, Dict, List, Optional

from fastapi import APIRouter, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from _mutable_store import Store, StoreError


ENV_ENABLED = "MOCK_ADMIN_ENABLED"
ENV_ALLOWLIST = "MOCK_ADMIN_ALLOWLIST"
ENV_TOKEN = "MOCK_ADMIN_TOKEN"
ENV_TRUST_FORWARDED_FOR = "MOCK_ADMIN_TRUST_FORWARDED_FOR"

ADMIN_PREFIX = "/admin"


def admin_enabled() -> bool:
    return os.environ.get(ENV_ENABLED, "").strip() == "1"


def _allowlist_ips() -> List[str]:
    raw = os.environ.get(ENV_ALLOWLIST, "").strip()
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


def _expected_token() -> Optional[str]:
    tok = os.environ.get(ENV_TOKEN, "").strip()
    return tok or None


def _trust_forwarded_for() -> bool:
    return os.environ.get(ENV_TRUST_FORWARDED_FOR, "").strip() == "1"


def _client_ip(request: Request) -> str:
    if _trust_forwarded_for():
        xff = request.headers.get("X-Forwarded-For", "").strip()
        if xff:
            return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


class _AdminGate(BaseHTTPMiddleware):
    """Blocks /admin/* requests that fail IP allowlist or token checks.

    Returns 404 (not 403) for unauthorized requests so the existence of the
    admin plane is not leaked to the agent. The harness side knows to expect
    real responses; everyone else sees the same "not found" surface as if
    the routes weren't installed.
    """

    def __init__(self, app: ASGIApp, allowlist: List[str], token: Optional[str]):
        super().__init__(app)
        self._allowlist = set(allowlist)
        self._token = token

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        if not path.startswith(ADMIN_PREFIX):
            return await call_next(request)

        client_host = _client_ip(request)
        if self._allowlist and client_host not in self._allowlist:
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        if self._token is not None:
            supplied = request.headers.get("X-Admin-Token", "")
            if supplied != self._token:
                return JSONResponse(status_code=404, content={"detail": "Not Found"})

        return await call_next(request)


class _OneShotRegistry:
    """In-memory queue of pending response interceptors.

    Each entry: ``{id, path_regex, method, transform, expires_after}``.
    The interceptor middleware consumes one matching entry per request and
    applies its transform to the response body before returning it to the
    caller. The store data itself is unchanged --- only this single
    response is rewritten.

    Transforms are JSON-Patch-style operations on the response body
    (``set`` / ``unset`` / ``replace_path``). We deliberately do not allow
    arbitrary code execution: drift scripts declare data, not behavior.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._pending: List[Dict[str, Any]] = []

    def enqueue(self, entry: Dict[str, Any]) -> str:
        entry_id = entry.get("id") or f"os_{uuid.uuid4().hex[:10]}"
        entry["id"] = entry_id
        entry["enqueued_at"] = time.time()
        entry.setdefault("remaining", entry.get("fires", 1))
        with self._lock:
            self._pending.append(entry)
        return entry_id

    def take(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            for i, entry in enumerate(self._pending):
                if entry["method"].upper() != method.upper() and entry["method"] != "*":
                    continue
                if not re.search(entry["path_regex"], path):
                    continue
                entry["remaining"] -= 1
                if entry["remaining"] <= 0:
                    self._pending.pop(i)
                return entry
        return None

    def snapshot(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [dict(e) for e in self._pending]

    def clear(self) -> int:
        with self._lock:
            n = len(self._pending)
            self._pending.clear()
            return n


class _OneShotMiddleware(BaseHTTPMiddleware):
    """Applies pending one-shot transforms to outgoing responses.

    The middleware only rewrites bodies that are valid JSON; non-JSON
    responses (e.g. HTML errors) pass through untouched. Transforms are
    applied in registration order; only the first matching transform per
    request is consumed.
    """

    def __init__(self, app: ASGIApp, registry: _OneShotRegistry, store: Store):
        super().__init__(app)
        self._registry = registry
        self._store = store

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        if path.startswith(ADMIN_PREFIX) or path.startswith("/audit"):
            return await call_next(request)

        response = await call_next(request)
        entry = self._registry.take(request.method, path)
        if entry is None:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        try:
            payload = json.loads(body.decode("utf-8")) if body else None
        except (UnicodeDecodeError, json.JSONDecodeError):
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type,
            )

        try:
            new_payload = _apply_transform(payload, entry["transform"])
        except Exception as exc:
            self._store.record(
                "one_shot.error",
                entry_id=entry["id"],
                error=str(exc),
            )
            new_payload = payload

        new_body = json.dumps(new_payload).encode("utf-8")
        headers = dict(response.headers)
        headers.pop("content-length", None)
        headers["X-Mock-Drift-One-Shot"] = entry["id"]
        self._store.record(
            "one_shot.applied",
            entry_id=entry["id"],
            method=request.method,
            path=path,
        )
        return Response(
            content=new_body,
            status_code=response.status_code,
            headers=headers,
            media_type="application/json",
        )


def _apply_transform(payload: Any, transform: Dict[str, Any]) -> Any:
    """Apply a small declarative transform to a JSON payload.

    Supported ops, in the order they appear in ``transform["ops"]``:

    * ``set``         --- ``{"op": "set", "path": "a.b.c", "value": ...}``
    * ``unset``       --- ``{"op": "unset", "path": "a.b.c"}``
    * ``replace``     --- ``{"op": "replace", "value": <new whole body>}``
    * ``merge``       --- ``{"op": "merge", "path": "a.b", "value": {...}}``

    Paths use ``.`` for object keys and ``[N]`` for array indices, e.g.
    ``"items[0].price"``. Negative indices are not supported (drift scripts
    should be explicit). Missing intermediate keys for ``set`` are created.
    """
    if "ops" not in transform:
        if "set" in transform:
            return _apply_transform(payload, {"ops": [{"op": "set", **transform["set"]}]})
        if "replace" in transform:
            return transform["replace"]
        raise ValueError("transform must contain 'ops', 'set', or 'replace'")

    result = payload
    for op in transform["ops"]:
        kind = op["op"]
        if kind == "replace":
            result = op["value"]
            continue
        path = op.get("path", "")
        if kind == "set":
            result = _set_path(result, path, op["value"])
        elif kind == "unset":
            result = _unset_path(result, path)
        elif kind == "merge":
            target = _get_path(result, path)
            if isinstance(target, dict):
                target.update(op["value"])
            else:
                raise ValueError(f"merge target at '{path}' is not an object")
        else:
            raise ValueError(f"unknown transform op: {kind}")
    return result


_PATH_TOKEN = re.compile(r"([^.\[\]]+)|\[(\d+)\]")


def _tokenize(path: str) -> List[Any]:
    if not path:
        return []
    out: List[Any] = []
    for m in _PATH_TOKEN.finditer(path):
        key, idx = m.groups()
        if key is not None:
            out.append(key)
        else:
            out.append(int(idx))
    return out


def _get_path(obj: Any, path: str) -> Any:
    for tok in _tokenize(path):
        if isinstance(tok, int):
            obj = obj[tok]
        else:
            obj = obj[tok]
    return obj


def _set_path(obj: Any, path: str, value: Any) -> Any:
    tokens = _tokenize(path)
    if not tokens:
        return value
    cur = obj
    for tok in tokens[:-1]:
        if isinstance(tok, int):
            cur = cur[tok]
        else:
            if not isinstance(cur, dict):
                raise ValueError(f"cannot descend into non-object at '{tok}'")
            if tok not in cur:
                cur[tok] = {}
            cur = cur[tok]
    last = tokens[-1]
    if isinstance(last, int):
        cur[last] = value
    else:
        if not isinstance(cur, dict):
            raise ValueError(f"cannot set key '{last}' on non-object")
        cur[last] = value
    return obj


def _unset_path(obj: Any, path: str) -> Any:
    tokens = _tokenize(path)
    if not tokens:
        return obj
    cur = obj
    for tok in tokens[:-1]:
        if isinstance(tok, int):
            cur = cur[tok]
        else:
            cur = cur[tok]
    last = tokens[-1]
    if isinstance(last, int):
        if isinstance(cur, list) and 0 <= last < len(cur):
            cur.pop(last)
    else:
        if isinstance(cur, dict) and last in cur:
            del cur[last]
    return obj


class _RowIn(BaseModel):
    row: Dict[str, Any]


class _PatchIn(BaseModel):
    fields: Dict[str, Any]


class _BulkIn(BaseModel):
    op: str = Field(..., description="'update_where' or 'delete_where'")
    where: Dict[str, Any] = Field(default_factory=dict,
                                  description="Field-equality predicate")
    set: Dict[str, Any] = Field(default_factory=dict)


class _InjectIn(BaseModel):
    operations: List[Dict[str, Any]]


class _OneShotIn(BaseModel):
    path_regex: str
    method: str = "GET"
    transform: Dict[str, Any]
    fires: int = 1


class _DocIn(BaseModel):
    value: Any


class _DocMergeIn(BaseModel):
    fields: Dict[str, Any]


class _SnapshotRestoreIn(BaseModel):
    snapshot_id: str


def _where_to_predicate(where: Dict[str, Any]) -> Callable[[Dict[str, Any]], bool]:
    def pred(row: Dict[str, Any]) -> bool:
        for k, v in where.items():
            if row.get(k) != v:
                return False
        return True
    return pred


def install_admin_plane(
    app: FastAPI,
    store: Store,
    one_shot_registry: Optional[_OneShotRegistry] = None,
) -> Optional[_OneShotRegistry]:
    """Install the admin plane on ``app`` if ``MOCK_ADMIN_ENABLED=1``.

    Idempotent: calling twice on the same app is a no-op the second time.
    Returns the one-shot registry (so callers can inject a shared one across
    multiple apps in tests), or ``None`` if the plane wasn't installed.
    """
    if not admin_enabled():
        return None
    if getattr(app.state, "_admin_plane_installed", False):
        return getattr(app.state, "_one_shot_registry", None)

    registry = one_shot_registry or _OneShotRegistry()
    app.state._one_shot_registry = registry
    app.state._admin_plane_installed = True
    app.state._admin_store = store

    store.capture_baseline()

    app.add_middleware(
        _AdminGate,
        allowlist=_allowlist_ips(),
        token=_expected_token(),
    )
    app.add_middleware(_OneShotMiddleware, registry=registry, store=store)

    router = _build_router(store, registry)
    app.include_router(router)
    return registry


def _build_router(store: Store, registry: _OneShotRegistry) -> APIRouter:
    router = APIRouter(prefix=ADMIN_PREFIX)

    @router.get("/health")
    def health():
        return {
            "ok": True,
            "store": store.name,
            "tables": store.list_tables(),
            "documents": store.list_documents(),
            "drift_events": len(store.drift_log()),
        }

    @router.get("/tables")
    def list_tables():
        return {
            "tables": [
                {"name": t, "primary_key": store.table(t).primary_key,
                 "rows": len(store.table(t))}
                for t in store.list_tables()
            ],
            "documents": store.list_documents(),
        }

    @router.get("/data/{table}")
    def list_rows(table: str):
        try:
            return {"rows": store.table(table).rows()}
        except StoreError as e:
            raise HTTPException(404, str(e))

    @router.get("/data/{table}/{pk}")
    def get_row(table: str, pk: str):
        try:
            row = store.table(table).get(pk)
        except StoreError as e:
            raise HTTPException(404, str(e))
        if row is None:
            raise HTTPException(404, f"row '{pk}' not in table '{table}'")
        return row

    @router.post("/data/{table}")
    def upsert_row(table: str, body: _RowIn):
        try:
            t = store.table(table)
            before = t.get(body.row.get(t.primary_key)) if t.primary_key in body.row else None
            row = t.upsert(body.row)
        except StoreError as e:
            raise HTTPException(400, str(e))
        store.record("data.upsert", table=table, pk=row[t.primary_key],
                     before=before, after=row)
        return row

    @router.patch("/data/{table}/{pk}")
    def patch_row(table: str, pk: str, body: _PatchIn):
        try:
            t = store.table(table)
            before = t.get(pk)
            row = t.patch(pk, body.fields)
        except StoreError as e:
            raise HTTPException(400, str(e))
        if row is None:
            raise HTTPException(404, f"row '{pk}' not in table '{table}'")
        store.record("data.patch", table=table, pk=pk, before=before, after=row)
        return row

    @router.delete("/data/{table}/{pk}")
    def delete_row(table: str, pk: str):
        try:
            t = store.table(table)
            before = t.get(pk)
            ok = t.delete(pk)
        except StoreError as e:
            raise HTTPException(400, str(e))
        if not ok:
            raise HTTPException(404, f"row '{pk}' not in table '{table}'")
        store.record("data.delete", table=table, pk=pk, before=before)
        return {"deleted": pk}

    @router.post("/data/{table}/bulk")
    def bulk(table: str, body: _BulkIn):
        try:
            t = store.table(table)
            pred = _where_to_predicate(body.where)
            if body.op == "update_where":
                n = t.update_where(pred, body.set)
                store.record("data.update_where", table=table, where=body.where,
                             set=body.set, affected=n)
                return {"affected": n}
            if body.op == "delete_where":
                n = t.delete_where(pred)
                store.record("data.delete_where", table=table, where=body.where,
                             affected=n)
                return {"affected": n}
            raise HTTPException(400, f"unknown bulk op '{body.op}'")
        except StoreError as e:
            raise HTTPException(400, str(e))

    @router.get("/doc/{doc}")
    def get_doc(doc: str):
        try:
            return store.document(doc).get()
        except StoreError as e:
            raise HTTPException(404, str(e))

    @router.put("/doc/{doc}")
    def put_doc(doc: str, body: _DocIn):
        try:
            d = store.document(doc)
            before = d.get()
            value = d.set(body.value)
        except StoreError as e:
            raise HTTPException(404, str(e))
        store.record("doc.set", doc=doc, before=before, after=value)
        return value

    @router.post("/doc/{doc}/merge")
    def merge_doc(doc: str, body: _DocMergeIn):
        try:
            d = store.document(doc)
            before = d.get()
            value = d.merge(body.fields)
        except StoreError as e:
            raise HTTPException(400, str(e))
        store.record("doc.merge", doc=doc, before=before, after=value)
        return value

    @router.post("/inject/raw")
    def inject_raw(body: _InjectIn):
        results = []
        for op in body.operations:
            kind = op.get("op")
            try:
                if kind == "data.upsert":
                    t = store.table(op["table"])
                    before = t.get(op["row"].get(t.primary_key)) if t.primary_key in op["row"] else None
                    row = t.upsert(op["row"])
                    store.record("data.upsert", table=op["table"],
                                 pk=row[t.primary_key], before=before, after=row,
                                 source="inject.raw")
                    results.append({"ok": True, "op": kind, "row": row})
                elif kind == "data.patch":
                    t = store.table(op["table"])
                    before = t.get(op["pk"])
                    row = t.patch(op["pk"], op["fields"])
                    store.record("data.patch", table=op["table"], pk=op["pk"],
                                 before=before, after=row, source="inject.raw")
                    results.append({"ok": row is not None, "op": kind, "row": row})
                elif kind == "data.delete":
                    t = store.table(op["table"])
                    before = t.get(op["pk"])
                    ok = t.delete(op["pk"])
                    store.record("data.delete", table=op["table"], pk=op["pk"],
                                 before=before, source="inject.raw")
                    results.append({"ok": ok, "op": kind})
                elif kind == "data.update_where":
                    t = store.table(op["table"])
                    n = t.update_where(_where_to_predicate(op.get("where", {})),
                                       op.get("set", {}))
                    store.record("data.update_where", table=op["table"],
                                 where=op.get("where"), set=op.get("set"),
                                 affected=n, source="inject.raw")
                    results.append({"ok": True, "op": kind, "affected": n})
                elif kind == "data.delete_where":
                    t = store.table(op["table"])
                    n = t.delete_where(_where_to_predicate(op.get("where", {})))
                    store.record("data.delete_where", table=op["table"],
                                 where=op.get("where"), affected=n,
                                 source="inject.raw")
                    results.append({"ok": True, "op": kind, "affected": n})
                elif kind == "doc.set":
                    d = store.document(op["doc"])
                    before = d.get()
                    value = d.set(op["value"])
                    store.record("doc.set", doc=op["doc"], before=before,
                                 after=value, source="inject.raw")
                    results.append({"ok": True, "op": kind, "value": value})
                elif kind == "doc.merge":
                    d = store.document(op["doc"])
                    before = d.get()
                    value = d.merge(op["fields"])
                    store.record("doc.merge", doc=op["doc"], before=before,
                                 after=value, source="inject.raw")
                    results.append({"ok": True, "op": kind, "value": value})
                else:
                    results.append({"ok": False, "op": kind,
                                    "error": f"unknown op '{kind}'"})
            except StoreError as e:
                results.append({"ok": False, "op": kind, "error": str(e)})
        return {"results": results}

    @router.post("/inject/one_shot")
    def inject_one_shot(body: _OneShotIn):
        entry = {
            "path_regex": body.path_regex,
            "method": body.method,
            "transform": body.transform,
            "fires": max(1, body.fires),
        }
        entry_id = registry.enqueue(entry)
        store.record("one_shot.enqueued", entry_id=entry_id,
                     path_regex=body.path_regex, method=body.method,
                     fires=body.fires)
        return {"id": entry_id, "pending": len(registry.snapshot())}

    @router.get("/inject/one_shot")
    def list_one_shot():
        return {"pending": registry.snapshot()}

    @router.post("/inject/one_shot/clear")
    def clear_one_shot():
        n = registry.clear()
        store.record("one_shot.cleared", count=n)
        return {"cleared": n}

    @router.post("/scenario/apply")
    def apply_scenario(body: Dict[str, Any]):
        """Apply a named DriftScenario.

        Currently scenarios are pass-through to ``inject/raw``: the body must
        contain ``{"name": str, "operations": [...]}`` and we record the name
        on every resulting drift-log entry. This keeps room for future
        expansion (e.g. server-side templated scenarios) without changing the
        HTTP surface.
        """
        name = body.get("name", "unnamed")
        ops = body.get("operations", [])
        store.record("scenario.begin", scenario=name, ops=len(ops))
        out = inject_raw(_InjectIn(operations=ops))
        store.record("scenario.end", scenario=name)
        return {"scenario": name, **out}

    @router.get("/snapshot")
    def snapshot(label: Optional[str] = None):
        snap_id = store.snapshot(label)
        store.record("snapshot.taken", snapshot_id=snap_id)
        return {"snapshot_id": snap_id}

    @router.post("/snapshot/restore")
    def snapshot_restore(body: _SnapshotRestoreIn):
        ok = store.restore(body.snapshot_id)
        store.record("snapshot.restored", snapshot_id=body.snapshot_id, ok=ok)
        if not ok:
            raise HTTPException(404, f"unknown snapshot '{body.snapshot_id}'")
        return {"restored": body.snapshot_id}

    @router.get("/drift/log")
    def drift_log(since_ts: Optional[float] = None):
        log = store.drift_log()
        if since_ts is not None:
            log = [e for e in log if e["ts"] > since_ts]
        return {"events": log}

    @router.post("/drift/log/clear")
    def drift_log_clear():
        n = store.clear_drift_log()
        return {"cleared": n}

    return router
