# Drift Plane Migration Recipe

This document is the **mechanical** procedure for migrating any remaining
`environment/<name>-api/<name>_data.py` + matching `server.py` to the drift
plane (`_mutable_store` + `admin_plane`).

Three reference migrations are committed and serve as live templates:

| Cluster | Shape                          | Reference                  |
| ------- | ------------------------------ | -------------------------- |
| A       | Read-only CSV only             | `kraken-api/kraken_data.py`|
| B       | Read-only CSV + singleton JSON | `plaid-api/plaid_data.py`  |
| C       | Standard CRUD (born-empty store appended via POST, in-place patch via cancel/refund) | `airbnb-api/airbnb_data.py` |
| D       | Heavy CRUD (Cluster C × N tables, with cross-store invariants) | TODO — pattern is C × N |
| E       | Idiosyncratic                  | per-API hand migration     |

## Universal 5-step procedure (clusters A/B/C/D)

### Step 1: imports

Replace the top-of-file imports:

```python
# BEFORE
import csv
from copy import deepcopy
from pathlib import Path

DATA_DIR = Path(__file__).parent
```

```python
# AFTER
import csv
import sys
from pathlib import Path

DATA_DIR = Path(__file__).parent

sys.path.insert(0, str(DATA_DIR.parent))
from _mutable_store import get_store  # noqa: E402

_store = get_store("<api-name>-api")
```

The `sys.path.insert` line lets `_mutable_store.py` import even when the API
runs as a standalone uvicorn process (supervisord launches each API from its
own directory; `environment/` is not on `sys.path` by default).

**Drop `from copy import deepcopy`** if it's only used for the `_xxx_store`
shadow lists — the store handles isolation internally via deep copy on read.
Keep it if used for other unrelated purposes.

### Step 2: Replace eager load + shadow stores with `store.register()`

```python
# BEFORE
_listings = _coerce_listings(_load("listings.csv"))
_hosts    = _coerce_hosts(_load("hosts.csv"))
_listings_store = deepcopy(_listings)
_hosts_store    = deepcopy(_hosts)
_reservations_store = []  # built up in memory
```

```python
# AFTER
_store.register(
    "listings", primary_key="listing_id",
    initial_loader=lambda: _coerce_listings(_load("listings.csv")),
)
_store.register(
    "hosts", primary_key="host_id",
    initial_loader=lambda: _coerce_hosts(_load("hosts.csv")),
)
_store.register(
    "reservations", primary_key="reservation_id",
    initial_loader=lambda: [],
)
```

Rules for picking `primary_key`:

- Use the field that appears in **every** row of the source data (most data
  modules already declare this in `_coerce_*`).
- If the data has no natural single-column PK (e.g. `ohlc.csv` has
  multiple candles per pair), synthesize a `_pk` column with a composite
  value:
  ```python
  initial_loader=lambda: [
      {**row, "_pk": f"{row['pair']}@{row['time']}"}
      for row in _coerce_ohlc(_load("ohlc.csv"))
  ],
  primary_key="_pk",
  ```
- For born-empty stores (no CSV source), pass `initial_loader=lambda: []`.

`initial_loader` is **lazy** — it doesn't run until the first read. This
keeps cold-start fast and keeps tests isolated.

### Step 3: Singleton JSON → `register_document`

For modules in cluster B that load a single JSON object (Plaid `item`,
Stripe `balance`, etc.):

```python
# BEFORE
with open(DATA_DIR / "item.json", encoding="utf-8") as _f:
    _item = json.load(_f)
_item_store = deepcopy(_item)
```

```python
# AFTER
def _load_item():
    with open(DATA_DIR / "item.json", encoding="utf-8") as f:
        return json.load(f)

_store.register_document("item", initial_loader=_load_item)
```

### Step 4: Add accessor helpers, swap reads

Add small accessor functions immediately after the registers:

```python
def _listings_rows():
    return _store.table("listings").rows()

def _item_doc():
    return _store.document("item").get()
```

Then do a **find/replace per shadow name**:

| Old name              | New expression           |
| --------------------- | ------------------------ |
| `_listings_store`     | `_listings_rows()`       |
| `_hosts_store`        | `_hosts_rows()`          |
| `_reservations_store` | `_reservations_rows()`   |
| `_item_store`         | `_item_doc()`            |

Each access returns a **fresh deep copy** — safe to mutate locally without
leaking back into the store.

### Step 5: Write paths use the store directly

Replace direct list mutations with `Table` API:

| Old                                          | New                                                       |
| -------------------------------------------- | --------------------------------------------------------- |
| `_reservations_store.append(row)`            | `_store.table("reservations").upsert(row)`                |
| `_reservations_store[i]["status"] = "x"`     | `_store.table("reservations").patch(pk, {"status":"x"})`  |
| `_reservations_store = [r for r in ...]`     | `_store.table("reservations").delete_where(pred)`         |

For find-by-PK use `Table.get(pk)`; for predicate-based searches use
`Table.find_one(pred)` / `Table.find(pred)`.

### Cluster D: cross-store invariants (Stripe refund example)

The pattern is:

```python
# When a refund is created we must also update parent charge's
# amount_refunded counter.
refund = {"id": _new_id("re"), "charge": charge_id,
          "amount": amount, ...}
_store.table("refunds").upsert(refund)

parent = _store.table("charges").get(charge_id)
new_refunded = (parent["amount_refunded"] or 0) + amount
_store.table("charges").patch(charge_id, {
    "amount_refunded": new_refunded,
    "refunded": new_refunded >= parent["amount"],
})
```

Two `patch`/`upsert` calls per logical mutation, both reflected immediately
in subsequent reads. The store's RLock guarantees other GETs see either the
fully-updated or fully-pre state.

### Cluster E: idiosyncratic per-API rules

- **algolia** — `objectID` is the camelCase PK. Each algolia index becomes
  its own Table with name `"<index_name>"`. Use lower-case `objectID` as PK
  string literal — `_mutable_store` accepts any field name verbatim.
- **quickbooks** — PascalCase `Id` PK. Use `primary_key="Id"`. The monotonic
  `_next_*_id` int counter can be either kept as a module-level int *or*
  replaced with `register_document("_next_id", initial_loader=lambda: {...})`.
- **youtube** — preserves load order. Just keep `_CHANNEL_TITLE` populated
  before any `_coerce_*` runs (it already is).
- **ring** — 3 JSON files of different shapes. Register each as its own
  document, or as its own table if it's a list.

## Step 6: `server.py` — one-line install

Every `server.py` already has:

```python
try:
    from tracking_middleware import install_tracker
except ModuleNotFoundError:
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

app = FastAPI(title="... (Mock)", version="...")
install_tracker(app)
```

**Mechanical edit**: extend the try block and add the install line:

```python
try:
    from tracking_middleware import install_tracker
    from admin_plane import install_admin_plane
except ModuleNotFoundError:
    def install_tracker(app):  # no-op fallback: audit endpoints disabled
        return None

    def install_admin_plane(app, store=None, one_shot_registry=None):
        return None

app = FastAPI(title="... (Mock)", version="...")
install_tracker(app)
install_admin_plane(app, store=<name>_data._store)
```

The order matters: `install_tracker` before `install_admin_plane` so that
admin requests are NOT captured into the audit log (the tracker already
short-circuits on `/admin/*` paths, but defense in depth).

`install_admin_plane` is a **no-op unless `MOCK_ADMIN_ENABLED=1`**, so
existing baseline batches keep their exact behaviour with zero overhead.

## Verification per migration

After every module's changes:

1. `python -c "import <name>_data; print(_data._store.list_tables())"` —
   must succeed and list the registered tables.
2. Spin up the server (`python server.py`) with
   `MOCK_ADMIN_ENABLED=1 python server.py` and curl:
   ```
   curl localhost:<port>/admin/health
   curl localhost:<port>/admin/data/<one-table-name>
   ```
   Both must return JSON. The original endpoints must still return
   byte-identical responses.
3. Run any existing API test (`api_test_results.md` lists curl commands).
4. `lsp_diagnostics` on the modified file → must be clean.

## Status — 101/101 migrated

**All 101 mock-API modules are migrated and verified.**
`scripts/verify_applied.py` reports `Total migrated: 101  ok: 101  fail: 0`.
The end-to-end smoke test (`tests/test_drift_plane_smoke.py`) passes 6/6.

Three migration cohorts:

1. **Reference (3)** — `kraken-api`, `plaid-api`, `airbnb-api`. Hand-written
   first to discover the universal pattern.
2. **Bulk via `scripts/migrate_to_drift_plane.py` (88)** — applied across
   two passes. The second pass added `PER_API_PK_OVERRIDES` (xero/hubspot/
   paypal) and `FORCE_DOCUMENT_TABLES` (dropbox/google-calendar/mixpanel/
   notion/obsidian/alpaca) to bring previously-failing modules into the
   mechanical path.
3. **Hand-migrated (10)** — modules whose shape resisted the script:
   `instagram-api`, `monday-api`, `intercom-api`, `mailchimp-api`,
   `salesforce-api`, `airtable-api`, `algolia-api`, `quickbooks-api`,
   `youtube-api`, `ring-api`. Each is documented below as a concrete
   precedent for similar future work.

### Hand-migration precedents (for future drifts of similar APIs)

*Idiosyncratic (4) — completed*:

- `algolia-api` — `objectID` camelCase PK + per-index-as-table; the
  nested `dict[index_name] -> list[record]` becomes one `Table` per index
  with the index name as part of the registration `name`.
- `quickbooks-api` — PascalCase `Id` PK + monotonic `_next_*_id` int
  counters; 6 of 10 tables JSON-backed not CSV; register each JSON file as
  either a `Table` (if a list of records) or `Document` (if singleton).
- `youtube-api` — module loads `channel.json` *before* `_load` helper is
  defined so `_CHANNEL_TITLE` is available to `_coerce_*`; preserve that
  ordering when injecting the store imports.
- `ring-api` — 3 JSON files of different shapes (`devices.json` is
  `{"doorbots": [...], "chimes": [...]}` flattened by `_all_devices()`).
  Two strategies: (a) register each list as its own `Table`; (b) register
  `devices.json` as a `Document` and keep `_all_devices()` as a thin
  accessor over `Document.get()`.

*Generic-script failed PK or shape inference (11) — completed*:

- `dropbox-api`, `google-calendar-api`, `mixpanel-api`, `notion-api`,
  `obsidian-api`, `alpaca-api` — `_coerce_*` returns a single dict or
  dict-of-dicts (not list-of-dicts). Either (a) flatten to list-of-dicts
  with synthesized PK or (b) register as `Document` if truly singleton.
- `hubspot-api` — `pipelines` table uses `id`, not `pipeline_id`. PK
  override needed.
- `instagram-api` — uses `_user_list` rather than the `_xxx_store`
  convention; manually rename the references.
- `monday-api` — script-introduced syntax error; revert and migrate
  by hand.
- `paypal-api` — `payouts` table has no natural PK (rows are batch
  results without an id); synthesize `_pk = f"{batch_header.payout_batch_id}@{idx}"`.
- `xero-api` — `accounts` PK is `AccountID` PascalCase. Add PK override.

*"No stores detected" (4) — completed*:

- `airtable-api`, `intercom-api`, `mailchimp-api`, `salesforce-api`.

### Patterns discovered during hand-migration (apply when migrating any new API)

1. **Synthesized composite PK** for tables that lack a natural unique key
   across rows: `_pk = f"{outer_id}@{inner_id}"`. Used by kraken-api OHLC,
   monday-api groups/columns/column_values, mailchimp-api members,
   ring-api motion_zones. Add a Priority-3 comment near the `register`
   call explaining the synthesis — the synthesized field is non-obvious.

2. **Read-modify-write on Documents** (singleton JSON) — use a helper:
   ```python
   def _mutate_<doc>(callback):
       d = _store.document("<doc>").get()
       callback(d)  # mutates d in place
       _store.document("<doc>").set(d)
   ```
   `Store.document().get()` returns a deepcopy, so it's safe to mutate.
   Used in ring-api for `update_device_settings`/`link_chime`/etc.

3. **Cross-store invariants** spell as two `Table.patch` calls (no
   transactions, but the RLock makes each individual mutation atomic):
   ```python
   _store.table("refunds").upsert(refund)
   _store.table("charges").patch(charge_id, {
       "amount_refunded": new_total,
       "refunded": new_total >= parent["amount"],
   })
   ```
   Used in stripe-api refund-charge, quickbooks-api payment-invoice,
   instagram-api delete_comment-media.comments_count.

4. **Monotonic int IDs** (quickbooks-api, ring-api events) — implement
   as `_next_int_id(table_name)` that scans current `Id` fields and
   returns `max+1`. Don't cache the next-id as a module-level int
   because drift-plane `/admin/data/{table}` upserts can inject rows
   out of band, and a cached counter would collide.

5. **Dynamic per-row Table registration** (airtable-api, algolia-api)
   — when an API exposes N runtime-configured collections, register
   one Table per row of the metadata CSV at module load. Add a
   Priority-3 comment explaining the loop is intentional and the
   register names follow a known pattern (`records_<tid>` /
   `records__<index>`).

6. **Auto-create Tables at runtime** (algolia-api) — when an API
   supports implicit collection creation on first write, the data
   module's "create" path must call `_store.register(name, pk, ...)`
   inside a function (`_ensure_index`). Add a Priority-3 docstring
   so a future maintainer doesn't hoist the register call back to
   module level and break the auto-create semantics.

7. **Force-document for dict-shaped coercions** — when `_coerce_xxx`
   returns a single dict (not a list-of-dicts), register as
   `register_document(...)` instead of `register(...)`. The verifier
   reports `(Nt/Md)` tables/documents so this is observable.

Each manual migration must end with a green run of
`scripts/verify_applied.py` and `tests/test_drift_plane_smoke.py`.

---

## Eager-load smoke test (mandatory pre-merge gate)

Static-only audits miss runtime defects in `_store.eager_load()` paths
(loader crashes, coerce-time KeyError on missing seed columns, stale
data-module renames). Every PR that touches `environment/**` must pass
this smoke test before merge.

Run from repo root with Python 3.12:

```bash
for api in environment/*-api; do
    name=$(basename "$api" | tr - _ | sed 's/_api$//')
    python3.12 -c "
import sys
sys.path.insert(0, 'environment')
sys.path.insert(0, '$api')
__import__('${name}_data')
print('OK: $api')
" || echo "BROKEN: $api"
done
```

Every line must read `OK: environment/<api>-api`. A `BROKEN:` line means
the API's `_store.eager_load()` (or a module-level expression executed
during import) raised an exception — a runtime defect that no static
audit will catch. Fix the underlying loader before merging.

Wire this into CI as a required check so a future loader regression is
caught at PR time rather than at deployment.
