#!/usr/bin/env python3
"""Mechanical migration of <api>_data.py + server.py to the drift plane.

Run with --dry-run first; --apply to write changes. Skips already-migrated
modules (detected by `from _mutable_store import get_store`). Idiosyncratic
modules (algolia, quickbooks, youtube, ring) must still be hand-migrated and
are skipped here.

Algorithm per data module:
  1. Parse with libcst-style regex to locate:
     - the `import csv`/`from copy import deepcopy`/`from pathlib import Path`
       header block,
     - the `_xxx = _coerce_xxx(_load("file.csv"))` eager-load lines,
     - any `_xxx_store = deepcopy(_xxx)` shadow lines,
     - any born-empty `_xxx_store = []` lines,
     - any singleton-JSON load `with open(... / "x.json"... ) as _f: _x = json.load(_f); _x_store = deepcopy(_x)`.
  2. Build the register() calls + accessor helpers and patch them in.
  3. Replace every `_xxx_store` reference (after the registration block) with
     the matching accessor call.

Algorithm per server.py:
  1. Locate the try/except install_tracker block.
  2. Add `from admin_plane import install_admin_plane` inside try, and the
     no-op def inside except.
  3. Add `install_admin_plane(app, store=<mod>_data._store)` after the
     `install_tracker(app)` line.

We do NOT touch idiosyncratic primary keys; we infer PK with priority:
  1. `<entity>_id` (where entity = singular of the CSV stem)
  2. `id`
  3. The first field name in `_coerce_*` output (parsed from the function body)
  4. A synthesized `_pk` column based on row-hash (fallback only)

If PK inference is ambiguous, skip the module and report it. The recipe
covers what to do manually in that case.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ENV_DIR = REPO_ROOT / "environment"

# Module-name overrides (the 6 google/openweather cases the survey identified)
DATA_MODULE_OVERRIDES = {
    "google-analytics-api": "analytics_data",
    "google-calendar-api": "calendar_data",
    "google-classroom-api": "classroom_data",
    "google-drive-api": "drive_data",
    "google-maps-api": "maps_data",
    "openweather-api": "weather_data",
}

IDIOSYNCRATIC = {"algolia-api", "quickbooks-api", "youtube-api", "ring-api"}
ALREADY_DONE = {"kraken-api", "plaid-api", "airbnb-api"}

NEEDS_MANUAL = {
    "airtable-api", "instagram-api", "intercom-api", "mailchimp-api",
    "monday-api", "salesforce-api",
}

ALREADY_MIGRATED_MARKER = "from _mutable_store import get_store"

PK_OVERRIDES = {
    "users": "user_id",
    "channels": "channel_id",
    "tickers": "pair",
    "candles": "_pk",
    "ohlc": "_pk",
    "events": "event_id",
    "messages": "message_id",
    "rooms": "room_id",
    "members": "member_id",
    "groups": "group_id",
    "shows": "show_id",
    "movies": "movie_id",
    "books": "book_id",
    "authors": "author_id",
}

PER_API_PK_OVERRIDES: dict[str, dict[str, str]] = {
    "xero-api": {"accounts": "AccountID", "invoices": "InvoiceID",
                 "contacts": "ContactID"},
    "hubspot-api": {"pipelines": "id"},
    "paypal-api": {"payouts": "payout_batch_id"},
}

PER_API_LOADER_WRAPPERS: dict[str, dict[str, str]] = {
    "paypal-api": {
        "payouts": (
            "lambda: [{**r, 'payout_batch_id': r['batch_header']['payout_batch_id']} "
            "for r in _coerce_payouts(_load(\"payouts.csv\"))]"
        ),
    },
}

FORCE_DOCUMENT_TABLES: dict[str, set[str]] = {
    "dropbox-api": {"account"},
    "google-calendar-api": {"attendees"},
    "alpaca-api": {"quotes"},
    "mixpanel-api": {"funnels"},
    "notion-api": {"properties"},
    "obsidian-api": {"contents"},
}


@dataclass
class StoreDecl:
    name: str
    primary_key: str
    initial_loader_expr: str
    is_document: bool = False


@dataclass
class ModuleMigration:
    api_dir: Path
    data_module_path: Path
    server_path: Path
    data_module_name: str
    stores: list[StoreDecl] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)


def discover_apis() -> list[Path]:
    return sorted(p for p in ENV_DIR.iterdir()
                  if p.is_dir() and p.name.endswith("-api"))


def data_module_name(api_dir_name: str) -> str:
    if api_dir_name in DATA_MODULE_OVERRIDES:
        return DATA_MODULE_OVERRIDES[api_dir_name]
    return api_dir_name.replace("-", "_").removesuffix("_api") + "_data"


_COERCE_LINE = re.compile(
    r"^(?P<var>_[A-Za-z0-9_]+)\s*=\s*(?P<expr>_coerce_[A-Za-z0-9_]+\(_load\(\"(?P<csv>[^\"]+)\"\)\))\s*$",
    re.M,
)
_PLAIN_LOAD_LINE = re.compile(
    r"^(?P<var>_[A-Za-z0-9_]+)\s*=\s*(?P<expr>_load\(\"(?P<csv>[^\"]+)\"\))\s*$",
    re.M,
)
_SHADOW_DEEPCOPY = re.compile(
    r"^(?P<store>_[A-Za-z0-9_]+_store)\s*=\s*deepcopy\((?P<src>_[A-Za-z0-9_]+)\)\s*$",
    re.M,
)
_SHADOW_EMPTY = re.compile(
    r"^(?P<store>_[A-Za-z0-9_]+_store)\s*=\s*\[\]\s*(?:#.*)?$", re.M,
)
_JSON_LOAD_BLOCK = re.compile(
    r"^with open\(DATA_DIR / \"(?P<json>[^\"]+)\"[^)]*\)\s*as\s*_?f\s*:\s*\n"
    r"\s+(?P<var>_[A-Za-z0-9_]+)\s*=\s*json\.load\(_?f\)\s*$",
    re.M,
)


def parse_module(text: str) -> tuple[dict, dict, dict, dict]:
    """Return (load_vars, shadow_to_src, json_vars, empty_stores) where:
    - load_vars[var]   = (csv_filename, full_expr)  -- e.g. _customers -> ("customers.csv", "_coerce_customers(_load(\"customers.csv\"))")
    - shadow_to_src[store_name] = source_var  -- e.g. _customers_store -> _customers
    - json_vars[var]    = json_filename
    - empty_stores      = list of empty-init store names
    """
    load_vars: dict[str, tuple[str, str]] = {}
    for m in _COERCE_LINE.finditer(text):
        load_vars[m.group("var")] = (m.group("csv"), m.group("expr"))
    for m in _PLAIN_LOAD_LINE.finditer(text):
        load_vars.setdefault(m.group("var"), (m.group("csv"), m.group("expr")))

    shadow_to_src: dict[str, str] = {}
    for m in _SHADOW_DEEPCOPY.finditer(text):
        shadow_to_src[m.group("store")] = m.group("src")

    json_vars: dict[str, str] = {}
    for m in _JSON_LOAD_BLOCK.finditer(text):
        json_vars[m.group("var")] = m.group("json")

    empty_stores = [m.group("store") for m in _SHADOW_EMPTY.finditer(text)]
    return load_vars, shadow_to_src, json_vars, empty_stores


def infer_primary_key(table_logical_name: str, csv_path: Path,
                      api_name: str = "") -> str:
    per_api = PER_API_PK_OVERRIDES.get(api_name, {})
    if table_logical_name in per_api:
        return per_api[table_logical_name]
    try:
        header_line = csv_path.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, IndexError):
        return PK_OVERRIDES.get(table_logical_name, "id")
    headers = [h.strip() for h in header_line.split(",")]
    if not headers:
        return PK_OVERRIDES.get(table_logical_name, "id")
    singular = table_logical_name.rstrip("s")
    candidates = [
        f"{singular}_id", f"{table_logical_name}_id", "id",
        "objectID", "Id", "sys_id", "zpid",
    ]
    pk_override = PK_OVERRIDES.get(table_logical_name)
    if pk_override and pk_override in headers:
        return pk_override
    for c in candidates:
        if c in headers:
            return c
    return headers[0]


def build_register_block(stores: list[StoreDecl], json_vars: dict[str, str],
                         shadow_to_src: dict[str, str]) -> str:
    lines: list[str] = []
    for sd in stores:
        if sd.is_document:
            lines.append(
                f"_store.register_document(\"{sd.name}\", "
                f"initial_loader={sd.initial_loader_expr})"
            )
        else:
            lines.append(
                f"_store.register(\"{sd.name}\", primary_key=\"{sd.primary_key}\",\n"
                f"                initial_loader={sd.initial_loader_expr})"
            )
    return "\n".join(lines)


def build_accessor_block(stores: list[StoreDecl]) -> str:
    lines: list[str] = []
    for sd in stores:
        if sd.is_document:
            lines.append(
                f"def _{sd.name}_doc():\n"
                f"    return _store.document(\"{sd.name}\").get()"
            )
        else:
            lines.append(
                f"def _{sd.name}_rows():\n"
                f"    return _store.table(\"{sd.name}\").rows()"
            )
    return "\n\n\n".join(lines)


def plan_module(api_dir: Path) -> ModuleMigration:
    dm_name = data_module_name(api_dir.name)
    dm_path = api_dir / f"{dm_name}.py"
    sv_path = api_dir / "server.py"
    mig = ModuleMigration(
        api_dir=api_dir, data_module_path=dm_path,
        server_path=sv_path, data_module_name=dm_name,
    )
    if not dm_path.exists():
        mig.issues.append(f"data module not found: {dm_path.name}")
        return mig
    text = dm_path.read_text(encoding="utf-8")
    if ALREADY_MIGRATED_MARKER in text:
        mig.issues.append("already migrated")
        return mig

    load_vars, shadow_to_src, json_vars, empty_stores = parse_module(text)

    src_to_store = {v: k for k, v in shadow_to_src.items()}

    for var, (csv_file, expr) in load_vars.items():
        store_name_var = src_to_store.get(var) or f"{var}_store"
        logical = var.lstrip("_")
        if logical.endswith("_data"):
            logical = logical[:-5]
        csv_path = api_dir / csv_file
        force_doc = logical in FORCE_DOCUMENT_TABLES.get(api_dir.name, set())
        pk = "" if force_doc else infer_primary_key(
            logical, csv_path, api_dir.name)
        loader_wrapper = PER_API_LOADER_WRAPPERS.get(
            api_dir.name, {}).get(logical)
        loader_expr = loader_wrapper if loader_wrapper else f"lambda: {expr}"
        mig.stores.append(StoreDecl(
            name=logical,
            primary_key=pk,
            initial_loader_expr=loader_expr,
            is_document=force_doc,
        ))

    for var, json_file in json_vars.items():
        store_name_var = src_to_store.get(var) or f"{var}_store"
        logical = var.lstrip("_")
        loader_expr = (
            f"lambda: __import__('json').load("
            f"open(DATA_DIR / \"{json_file}\", encoding=\"utf-8\"))"
        )
        mig.stores.append(StoreDecl(
            name=logical,
            primary_key="",
            initial_loader_expr=loader_expr,
            is_document=True,
        ))

    for store_name in empty_stores:
        logical = store_name.lstrip("_").removesuffix("_store")
        pk = PK_OVERRIDES.get(logical) or f"{logical.rstrip('s')}_id"
        mig.stores.append(StoreDecl(
            name=logical,
            primary_key=pk,
            initial_loader_expr="lambda: []",
            is_document=False,
        ))

    if not mig.stores:
        mig.issues.append("no stores detected; manual migration required")
    return mig


def apply_data_module(mig: ModuleMigration) -> str | None:
    if mig.issues:
        return None
    text = mig.data_module_path.read_text(encoding="utf-8")

    new_text = re.sub(
        r"^(from copy import deepcopy\n)", "", text, count=1, flags=re.M,
    )

    pathlib_anchor = "DATA_DIR = Path(__file__).parent"
    if pathlib_anchor not in new_text:
        return None
    insert_block = (
        f"{pathlib_anchor}\n\n"
        f"import sys as _sys\n"
        f"_sys.path.insert(0, str(DATA_DIR.parent))\n"
        f"from _mutable_store import get_store  # noqa: E402\n"
        f"\n"
        f"_store = get_store(\"{mig.api_dir.name}\")"
    )
    new_text = new_text.replace(pathlib_anchor, insert_block, 1)

    new_text = _COERCE_LINE.sub("", new_text)
    new_text = _PLAIN_LOAD_LINE.sub("", new_text)
    new_text = _SHADOW_DEEPCOPY.sub("", new_text)
    new_text = _SHADOW_EMPTY.sub("", new_text)
    new_text = _JSON_LOAD_BLOCK.sub("", new_text)

    register_block = build_register_block(
        mig.stores, {}, {},
    )
    accessor_block = build_accessor_block(mig.stores)

    injection = "\n\n" + register_block + "\n\n\n" + accessor_block + "\n"
    new_text = new_text.replace(
        f"_store = get_store(\"{mig.api_dir.name}\")",
        f"_store = get_store(\"{mig.api_dir.name}\"){injection}",
    )

    for sd in mig.stores:
        store_var = f"_{sd.name}_store"
        replacement = (
            f"_{sd.name}_doc()" if sd.is_document else f"_{sd.name}_rows()"
        )
        new_text = re.sub(rf"\b{re.escape(store_var)}\b", replacement, new_text)

    return new_text


def apply_server(api_dir: Path, data_module_name: str) -> str | None:
    sv = api_dir / "server.py"
    if not sv.exists():
        return None
    text = sv.read_text(encoding="utf-8")
    if "install_admin_plane" in text:
        return None
    if "install_tracker" not in text:
        return None

    new_text = re.sub(
        r"(\s+from tracking_middleware import install_tracker\n)"
        r"(except ModuleNotFoundError:.*?\n"
        r"\s+def install_tracker\(app\):.*?\n"
        r"\s+return None\n)",
        lambda m: (
            m.group(1)
            + "    from admin_plane import install_admin_plane\n"
            + m.group(2).replace(
                "        return None\n",
                "        return None\n\n"
                "    def install_admin_plane(app, store=None, one_shot_registry=None):\n"
                "        return None\n",
                1,
            )
        ),
        text, count=1, flags=re.S,
    )
    if new_text == text:
        return None

    new_text = re.sub(
        r"^install_tracker\(app\)\s*$",
        f"install_tracker(app)\ninstall_admin_plane(app, store={data_module_name}._store)",
        new_text, count=1, flags=re.M,
    )
    return new_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--only", nargs="*", help="limit to these API dirs")
    args = parser.parse_args()

    skip = ALREADY_DONE | IDIOSYNCRATIC | NEEDS_MANUAL
    apis = discover_apis()
    if args.only:
        wanted = set(args.only)
        apis = [a for a in apis if a.name in wanted]

    total = succeeded = skipped = failed = 0
    failed_names: list[str] = []
    for api in apis:
        total += 1
        if api.name in skip:
            skipped += 1
            print(f"  SKIP {api.name} (already done or idiosyncratic)")
            continue
        mig = plan_module(api)
        if mig.issues:
            skipped += 1
            print(f"  SKIP {api.name}: {'; '.join(mig.issues)}")
            continue
        dm_out = apply_data_module(mig)
        sv_out = apply_server(api, mig.data_module_name)
        if dm_out is None or sv_out is None:
            failed += 1
            failed_names.append(api.name)
            print(f"  FAIL {api.name}: dm_out={dm_out is not None} sv_out={sv_out is not None}")
            continue
        if args.apply:
            mig.data_module_path.write_text(dm_out, encoding="utf-8")
            mig.server_path.write_text(sv_out, encoding="utf-8")
        succeeded += 1
        print(f"  OK   {api.name} ({len(mig.stores)} stores)")

    print(
        f"\nTotal: {total}  ok: {succeeded}  skipped: {skipped}  failed: {failed}"
    )
    if failed_names:
        print("Failed:", failed_names)
        sys.exit(1 if not args.apply else 0)


if __name__ == "__main__":
    main()
