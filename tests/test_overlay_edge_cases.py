"""Overlay-logic edge cases for ``_mutable_store.read_seed_with_ctx``.

The CSV-overlay-wins contract was fixed in commit 759a9cc ("Fix Q1: make CSV
overlays actually win over baked JSON"). ``test_reader_contract.py`` locks the
positive contract (CSV beats JSON, no-suffix probes CSV first, missing file
raises). This file pins the *edge cases* a real overlay author can hit:

* Empty CSV overlay (header-only) shadows a populated baked JSON --
  "overlay-zero-wins"; an author can deliberately ship an empty table.
* Empty JSON array baked baseline returns ``[]`` cleanly when no overlay.
* Explicit ``.json`` request with NO sibling CSV falls through to JSON.
* No-suffix probe with ONLY a ``.json`` present uses it (no CSV to prefer).
* Symmetric: explicit ``.csv`` does NOT silently pull a sibling ``.json``.
* CSV overlay can carry a wholly different *schema* from the baked JSON --
  the dispatcher does not enforce shape; the data module's coercer does.
* Coercion / shape errors (ragged row, duplicate header, malformed JSON,
  non-array JSON, non-object row, non-UTF-8 file) surface as ``CoerceError``
  with overlay context attached, and CSV-overlay-wins short-circuits BEFORE
  the malformed JSON is read.
* ``__file__`` context attribution always points at the file actually used,
  so an operator looking at a CoerceError can find the right file.
* UTF-8 BOM, embedded quoted commas, embedded newlines in quoted CSV cells.
* Uppercase suffixes (``.JSON`` / ``.CSV``) are accepted via the suffix
  comparison being lowercased.
* ``Path`` and ``str`` inputs behave identically.
* Real-API integration: the figma comments overlay and the instagram users
  overlay (the two callsites the production fix rewired) are exercised in a
  sandboxed copy of the real ``environment/<api>/`` directory.

Test hygiene mirrors ``test_reader_contract.py``: every test that mutates
``sys.modules`` or ``_mutable_store._STORES`` cleans up in a ``finally``
block so subsequent tests (including those in the same session) cannot see
leaked state.
"""

from __future__ import annotations

import csv
import importlib
import json
import shutil
import sys
import textwrap
from pathlib import Path

import pytest

# Same sys.path setup as test_reader_contract.py so imports resolve from
# the repo root in either pytest-from-repo-root or pytest-from-tests-dir.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "environment"))

from _mutable_store import (  # noqa: E402
    CoerceError,
    read_csv_with_ctx,
    read_json_with_ctx,
    read_seed_with_ctx,
)

_API = "test-api"
_TABLE = "widgets"
_ENV_DIR = Path(__file__).resolve().parents[1] / "environment"


# ---------------------------------------------------------------------------
# Mock data — a deliberately small but typed schema we reuse across tests.
# Mirrors the SEED_ROWS shape in test_reader_contract.py so behavior here
# composes with the reader-contract suite.
# ---------------------------------------------------------------------------

MOCK_ROWS = [
    {"id": "1", "name": "Alpha", "price": "9.99",
     "active": "true",  "tags": "a,b", "count": "10"},
    {"id": "2", "name": "Bravo", "price": "0",
     "active": "false", "tags": "",    "count": "0"},
    {"id": "3", "name": "",      "price": "42.5",
     "active": "true",  "tags": "x",   "count": "7"},
]
MOCK_COLUMNS = list(MOCK_ROWS[0].keys())


def _write_csv(path: Path, rows, columns=MOCK_COLUMNS):
    """Author the CSV the same way DictWriter would in the real fleet."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        w.writeheader()
        w.writerows(rows)


def _write_json(path: Path, rows):
    """Author the JSON the same way the environment/ tooling does: array of
    row dicts, ``null`` (None) for genuinely blank cells (mirrors the
    asymmetry locked in ``read_csv_with_ctx``)."""
    json_rows = []
    for r in rows:
        row = {k: (None if v == "" else v) for k, v in r.items()}
        json_rows.append(row)
    path.write_text(json.dumps(json_rows, indent=2), encoding="utf-8")


def _strip_ctx(rows):
    """Drop ``__api__/__table__/__file__/__row_index__`` for value equality."""
    return [
        {k: v for k, v in r.items() if not k.startswith("__")} for r in rows
    ]


# ---------------------------------------------------------------------------
# Section 1 — dispatcher precedence and probe order edge cases
# ---------------------------------------------------------------------------


def test_json_request_without_csv_sibling_uses_json(tmp_path):
    """``.json`` request, NO sibling .csv on disk -> JSON branch."""
    j = tmp_path / "widgets.json"
    _write_json(j, MOCK_ROWS)

    rows = read_seed_with_ctx(j, _API, _TABLE)
    direct = read_json_with_ctx(j, _API, _TABLE)

    assert _strip_ctx(rows) == _strip_ctx(direct)
    # __file__ attribution: every row tagged with the JSON path actually read.
    assert all(Path(r["__file__"]) == j for r in rows)


def test_csv_request_with_json_sibling_still_uses_csv(tmp_path):
    """Symmetry check: explicit .csv must not 'fall up' into a sibling .json.

    If this regressed, an author who deliberately authored a CSV overlay would
    instead silently re-read the JSON they meant to shadow.
    """
    c = tmp_path / "widgets.csv"
    j = tmp_path / "widgets.json"
    _write_csv(c, MOCK_ROWS)
    _write_json(j, [{**r, "name": "FROM_JSON"} for r in MOCK_ROWS])

    rows = read_seed_with_ctx(c, _API, _TABLE)

    assert [r["name"] for r in rows] == ["Alpha", "Bravo", None]
    assert all(Path(r["__file__"]) == c for r in rows)


def test_no_suffix_probe_falls_back_to_json_when_no_csv(tmp_path):
    """No suffix + only .json present -> JSON branch (no CSV to prefer)."""
    j = tmp_path / "widgets.json"
    _write_json(j, MOCK_ROWS)

    rows = read_seed_with_ctx(tmp_path / "widgets", _API, _TABLE)
    direct = read_json_with_ctx(j, _API, _TABLE)

    assert _strip_ctx(rows) == _strip_ctx(direct)


def test_no_suffix_probe_prefers_csv_when_both_present(tmp_path):
    """No suffix + BOTH siblings present -> CSV wins (overlay-wins semantics
    must hold whether the caller passes .json, .csv, or no suffix).
    """
    c = tmp_path / "widgets.csv"
    j = tmp_path / "widgets.json"
    _write_csv(c, MOCK_ROWS)
    # Author the JSON with deliberately different data so we can detect any
    # accidental fall-through.
    _write_json(j, [{**r, "name": f"JSON_{r['name']}"} for r in MOCK_ROWS])

    rows = read_seed_with_ctx(tmp_path / "widgets", _API, _TABLE)

    assert [r["name"] for r in rows] == ["Alpha", "Bravo", None]
    assert all(Path(r["__file__"]) == c for r in rows)


def test_missing_both_siblings_raises_coerce_error(tmp_path):
    """No .csv and no .json on disk -> CoerceError with both suffixes named.

    Lock the error message shape so operators grepping logs can find it.
    """
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(tmp_path / "ghost", _API, _TABLE)
    msg = str(excinfo.value)
    assert "seed file not found" in msg
    assert ".csv" in msg and ".json" in msg
    assert _API in msg and _TABLE in msg


def test_path_string_input_equivalent_to_path_object(tmp_path):
    """Authors pass either ``str`` or ``Path``; dispatcher must not care."""
    c = tmp_path / "widgets.csv"
    _write_csv(c, MOCK_ROWS)

    rows_str = read_seed_with_ctx(str(c), _API, _TABLE)
    rows_path = read_seed_with_ctx(c, _API, _TABLE)
    assert _strip_ctx(rows_str) == _strip_ctx(rows_path)


def test_uppercase_suffix_csv_routes_through_csv_branch(tmp_path):
    """``.CSV`` (mixed case) must be treated as CSV. ``Path.suffix.lower()``
    in the dispatcher already guarantees this; this test pins the behavior
    so a future refactor that drops ``.lower()`` would fail loudly.
    """
    upper = tmp_path / "WIDGETS.CSV"
    _write_csv(upper, MOCK_ROWS)
    rows = read_seed_with_ctx(upper, _API, _TABLE)
    assert len(rows) == len(MOCK_ROWS)
    assert rows[0]["name"] == "Alpha"


def test_uppercase_suffix_json_prefers_csv_sibling(tmp_path):
    """``.JSON`` request still triggers CSV-overlay-wins."""
    j = tmp_path / "WIDGETS.JSON"
    # Sibling probe uses ``.with_suffix('.csv')`` which keeps case of the
    # *stem* and lower-cases the suffix; the sibling we author must match.
    c_sibling = j.with_suffix(".csv")
    _write_json(j, MOCK_ROWS)
    _write_csv(c_sibling, [{**r, "name": "CSV_WINS"} for r in MOCK_ROWS])

    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert all(r["name"] == "CSV_WINS" for r in rows)


# ---------------------------------------------------------------------------
# Section 2 — empty / sparse data edge cases
# ---------------------------------------------------------------------------


def test_empty_csv_overlay_wins_over_populated_json(tmp_path):
    """An author can deliberately ship a header-only ``.csv`` to *blank out*
    a baked table. The dispatcher must honor "CSV-wins" even when the CSV
    is empty (zero rows is a valid, distinct state from "no overlay").
    """
    c = tmp_path / "widgets.csv"
    j = tmp_path / "widgets.json"
    _write_json(j, MOCK_ROWS)
    # Header-only CSV.
    with open(c, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=MOCK_COLUMNS).writeheader()

    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert rows == []


def test_empty_json_array_baseline_returns_zero_rows(tmp_path):
    """``[]`` is a valid baked JSON; with no CSV overlay, the dispatcher
    returns ``[]`` (not an error)."""
    j = tmp_path / "widgets.json"
    j.write_text("[]", encoding="utf-8")
    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert rows == []


def test_csv_with_only_header_no_overlay_branch(tmp_path):
    """Direct ``.csv`` request, header-only file -> 0 rows, no error."""
    c = tmp_path / "widgets.csv"
    with open(c, "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=MOCK_COLUMNS).writeheader()
    assert read_seed_with_ctx(c, _API, _TABLE) == []


# ---------------------------------------------------------------------------
# Section 3 — schema divergence: CSV overlay carries a different shape
# ---------------------------------------------------------------------------


def test_csv_overlay_with_different_columns_replaces_baseline(tmp_path):
    """The dispatcher does NOT enforce schema parity between CSV and JSON.
    Per the contract, it is the caller's coercer (in <api>_data.py) that
    decides whether a divergent overlay is legal. Here we verify the
    dispatcher does the dumb-pipe thing and returns the CSV columns
    verbatim when they diverge from the JSON.
    """
    j = tmp_path / "widgets.json"
    c = tmp_path / "widgets.csv"
    _write_json(j, MOCK_ROWS)
    # Overlay has only id + name (drops price/active/tags/count).
    new_cols = ["id", "name"]
    _write_csv(c, [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}], new_cols)

    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert len(rows) == 2
    # Stripped of context, only id+name remain — the JSON's other columns
    # are NOT merged in.
    stripped = _strip_ctx(rows)
    assert stripped == [{"id": "1", "name": "A"}, {"id": "2", "name": "B"}]


# ---------------------------------------------------------------------------
# Section 4 — CSV file-shape corruption surfaces as CoerceError with context
# ---------------------------------------------------------------------------


def test_ragged_csv_overlay_surfaces_coerce_error_with_context(tmp_path):
    """A ragged CSV (extra unquoted commas) surfaces as CoerceError naming
    the api, table, file, row index, and the stray values. Critically the
    error message must point at the CSV, not the (innocent) baked JSON.
    """
    j = tmp_path / "widgets.json"
    c = tmp_path / "widgets.csv"
    _write_json(j, MOCK_ROWS)
    # Hand-author the ragged file -- DictWriter would refuse to author it.
    c.write_text(
        "id,name,price\n"
        "1,Alpha,9.99\n"
        "2,Bravo with, an, unquoted comma,1.0\n",
        encoding="utf-8",
    )

    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(j, _API, _TABLE)
    msg = str(excinfo.value)
    assert "ragged row" in msg
    assert "api=test-api" in msg
    assert "table=widgets" in msg
    assert str(c) in msg, "error must attribute the CSV overlay, not the JSON"


def test_duplicate_header_csv_overlay_surfaces_coerce_error(tmp_path):
    """Duplicate header columns would silently keep-last under
    csv.DictReader; the loader rejects this at read time."""
    c = tmp_path / "widgets.csv"
    c.write_text("id,name,name\n1,A,B\n", encoding="utf-8")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(c, _API, _TABLE)
    assert "duplicate header" in str(excinfo.value)
    assert "'name'" in str(excinfo.value)


def test_non_utf8_csv_overlay_surfaces_coerce_error(tmp_path):
    """A non-UTF-8 CSV file (e.g. authored on Windows in cp1252) surfaces
    as a CoerceError naming the file, not a bare UnicodeDecodeError."""
    c = tmp_path / "widgets.csv"
    # 0xff is invalid as a UTF-8 leading byte.
    c.write_bytes(b"id,name\n1,\xff\xfe garbage\n")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(c, _API, _TABLE)
    msg = str(excinfo.value)
    assert "not valid UTF-8" in msg
    assert str(c) in msg


def test_csv_with_utf8_bom_is_accepted(tmp_path):
    """Excel and many Windows editors prepend a UTF-8 BOM. The reader uses
    ``utf-8-sig`` so the BOM is stripped and the first column name is NOT
    mangled into '\\ufeffid'."""
    c = tmp_path / "widgets.csv"
    c.write_bytes(b"\xef\xbb\xbfid,name\n1,Alpha\n")
    rows = read_seed_with_ctx(c, _API, _TABLE)
    assert len(rows) == 1
    assert "id" in rows[0]
    assert "\ufeffid" not in rows[0]
    assert rows[0]["id"] == "1"
    assert rows[0]["name"] == "Alpha"


def test_csv_quoted_comma_and_quoted_newline_parse_correctly(tmp_path):
    """A real overlay author may include text fields with embedded commas
    and newlines (think: Figma comment bodies). RFC-4180 quoting must round
    through ``csv.DictReader`` cleanly, not split the cell."""
    c = tmp_path / "widgets.csv"
    c.write_text(
        textwrap.dedent('''\
            id,name,message
            1,Alpha,"hello, world"
            2,Bravo,"line1\nline2"
            '''),
        encoding="utf-8",
    )
    rows = read_seed_with_ctx(c, _API, _TABLE)
    assert len(rows) == 2
    assert rows[0]["message"] == "hello, world"
    assert rows[1]["message"] == "line1\nline2"


# ---------------------------------------------------------------------------
# Section 5 — JSON shape corruption: only matters when CSV does NOT shadow it
# ---------------------------------------------------------------------------


def test_malformed_json_baseline_with_csv_overlay_is_ignored(tmp_path):
    """If a sibling CSV is present, the JSON is never opened -- so a
    syntactically broken JSON does not poison the read. This is a strong
    property: it means an author shipping a CSV overlay does not have to
    keep the baked JSON valid (rare but useful in panic-fix scenarios).
    """
    c = tmp_path / "widgets.csv"
    j = tmp_path / "widgets.json"
    _write_csv(c, MOCK_ROWS)
    j.write_text("{ this is not valid JSON", encoding="utf-8")

    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert len(rows) == len(MOCK_ROWS)


def test_malformed_json_without_csv_overlay_surfaces_coerce_error(tmp_path):
    """No CSV sibling, malformed JSON -> CoerceError naming the file."""
    j = tmp_path / "widgets.json"
    j.write_text("{ this is not valid JSON", encoding="utf-8")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(j, _API, _TABLE)
    msg = str(excinfo.value)
    assert "malformed JSON" in msg
    assert str(j) in msg


def test_non_array_json_baseline_surfaces_coerce_error(tmp_path):
    """Top-level JSON must be an array of row objects. An object top-level
    is rejected (a common authoring mistake when copy-pasting from a real
    API response that wraps rows in an envelope)."""
    j = tmp_path / "widgets.json"
    j.write_text(json.dumps({"rows": MOCK_ROWS}), encoding="utf-8")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(j, _API, _TABLE)
    msg = str(excinfo.value)
    assert "expected a JSON array" in msg
    assert "got dict" in msg


def test_json_non_object_row_surfaces_coerce_error(tmp_path):
    """A non-object element inside the top-level array (e.g. an author
    accidentally shipped a list of strings) is rejected with the offending
    row index named."""
    j = tmp_path / "widgets.json"
    j.write_text(json.dumps([{"id": "1"}, "oops", {"id": "3"}]), encoding="utf-8")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(j, _API, _TABLE)
    msg = str(excinfo.value)
    assert "row 1 is not an object" in msg


def test_non_utf8_json_surfaces_coerce_error(tmp_path):
    """Mirror of the CSV non-UTF-8 test for the JSON branch."""
    j = tmp_path / "widgets.json"
    j.write_bytes(b"[\xff\xfe]")
    with pytest.raises(CoerceError) as excinfo:
        read_seed_with_ctx(j, _API, _TABLE)
    assert "not valid UTF-8" in str(excinfo.value)


# ---------------------------------------------------------------------------
# Section 6 — __file__ attribution invariants
# ---------------------------------------------------------------------------


def test_file_attribution_csv_overlay_points_at_csv(tmp_path):
    """When CSV-overlay-wins fires, every row's ``__file__`` must point at
    the CSV (not the JSON). This is the contract operators rely on when
    debugging which file shaped a row."""
    j = tmp_path / "widgets.json"
    c = tmp_path / "widgets.csv"
    _write_json(j, MOCK_ROWS)
    _write_csv(c, MOCK_ROWS)
    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert rows  # non-empty
    assert all(Path(r["__file__"]) == c for r in rows)


def test_file_attribution_json_path_used_when_no_csv(tmp_path):
    """No CSV sibling -> ``__file__`` points at the JSON."""
    j = tmp_path / "widgets.json"
    _write_json(j, MOCK_ROWS)
    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert all(Path(r["__file__"]) == j for r in rows)


def test_row_index_continuous_in_csv_overlay(tmp_path):
    """The CSV branch must inject 0..N-1 row indices contiguously even
    after overlay-wins kicks in."""
    j = tmp_path / "widgets.json"
    c = tmp_path / "widgets.csv"
    _write_json(j, MOCK_ROWS)
    _write_csv(c, MOCK_ROWS)
    rows = read_seed_with_ctx(j, _API, _TABLE)
    assert [r["__row_index__"] for r in rows] == list(range(len(MOCK_ROWS)))


# ---------------------------------------------------------------------------
# Section 7 — real-API integration: figma comments + instagram users
#
# We sandbox the real environment/<api>/ directory under tmp_path so we can
# author a CSV overlay without polluting the repo, then re-import the data
# module and assert the in-memory store reflects the overlay.
# ---------------------------------------------------------------------------


def _sandbox_api(tmp_path, api_dir_name):
    """Copy environment/<api>/ to tmp_path/<api>/ for non-destructive overlay
    authoring. Returns the sandbox path. Caller is responsible for
    sys.path / sys.modules / _STORES cleanup (see fixture).
    """
    sandbox = tmp_path / api_dir_name
    shutil.copytree(_ENV_DIR / api_dir_name, sandbox)
    return sandbox


@pytest.fixture()
def isolated_api_import(monkeypatch):
    """Context manager-style fixture: yields a helper that imports a data
    module from a sandbox dir with full isolation, and cleans up _STORES +
    sys.modules in teardown so the next test sees a clean slate.

    Mirrors the symmetric setup/teardown pattern from
    test_reader_contract.test_real_api_csv_overlay_shadows_baked_json --
    must NOT evict ``_mutable_store`` itself (would re-bind CoerceError and
    break the missing-file test in test_reader_contract.py if interleaved).
    """
    import _mutable_store as _ms

    bookmarks: list[tuple[str, str]] = []

    def _import(sandbox: Path, module_name: str, api_store_key: str):
        # Drop any prior registration for this API so Store.register doesn't
        # short-circuit on a stale entry from tests/mocks/.
        _ms._STORES.pop(api_store_key, None)
        sys.modules.pop(module_name, None)
        # Prepend the sandbox AND the environment/ root (for _mutable_store
        # imports inside the data module) -- the sandbox first so its
        # <api>_data.py wins over any prior copy.
        monkeypatch.syspath_prepend(str(_ENV_DIR))
        monkeypatch.syspath_prepend(str(sandbox))
        bookmarks.append((module_name, api_store_key))
        return importlib.import_module(module_name)

    yield _import

    # Teardown: undo every import so subsequent tests see a pristine state.
    for module_name, api_store_key in bookmarks:
        _ms._STORES.pop(api_store_key, None)
        sys.modules.pop(module_name, None)


def test_real_api_figma_csv_overlay_blanks_out_comments(tmp_path, isolated_api_import):
    """Edge case end-to-end: an EMPTY (header-only) CSV overlay drops the
    comments table to zero rows even though comments.json is populated.
    This is the production analogue of test_empty_csv_overlay_wins_over...
    above, but driven through the real figma_data._store loader.
    """
    sandbox = _sandbox_api(tmp_path, "figma-api")
    # Author an empty overlay with the columns the real comments.json uses.
    header_cols = [
        "comment_id", "file_key", "user_id", "user_handle",
        "message", "node_id", "resolved", "created_at",
    ]
    with open(sandbox / "comments.csv", "w", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=header_cols).writeheader()

    figma_data = isolated_api_import(sandbox, "figma_data", "figma-api")
    rows = figma_data._store.table("comments").rows()
    assert rows == []


def test_real_api_figma_csv_overlay_does_not_leak_into_sibling_tables(
    tmp_path, isolated_api_import
):
    """Selective-overlay invariant: overlaying ``comments.csv`` must not
    perturb the sibling tables (``projects``, ``files``, ``components``)
    that were NOT overlaid. This catches a class of bugs where a globbed
    overlay collector accidentally replaces every table at once.
    """
    sandbox = _sandbox_api(tmp_path, "figma-api")
    # Baseline (no overlay) — capture counts.
    figma_baseline = isolated_api_import(sandbox, "figma_data", "figma-api")
    baseline_files = len(figma_baseline._store.table("files").rows())
    baseline_components = len(figma_baseline._store.table("components").rows())
    baseline_projects = len(figma_baseline._store.table("projects").rows())

    # Now author a single-row comments overlay in the SAME sandbox dir and
    # re-import (the fixture handles cleanup).
    overlay_row = {
        "comment_id": "EDGE_001", "file_key": "FK_EDGE", "user_id": "u-edge",
        "user_handle": "Edge", "message": "selective overlay only",
        "node_id": "0:0", "resolved": "false",
        "created_at": "2026-06-17T00:00:00Z",
    }
    with open(sandbox / "comments.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overlay_row.keys()))
        w.writeheader()
        w.writerow(overlay_row)

    figma_overlaid = isolated_api_import(sandbox, "figma_data", "figma-api")
    comments = figma_overlaid._store.table("comments").rows()
    assert len(comments) == 1
    assert comments[0]["comment_id"] == "EDGE_001"
    # Sibling tables untouched.
    assert len(figma_overlaid._store.table("files").rows()) == baseline_files
    assert len(figma_overlaid._store.table("components").rows()) == baseline_components
    assert len(figma_overlaid._store.table("projects").rows()) == baseline_projects


def test_real_api_instagram_user_csv_overlay_replaces_baked_users(
    tmp_path, isolated_api_import
):
    """The other production callsite the Q1 fix re-wired: instagram's
    ``user.json`` is now routed through ``_load`` so a sibling
    ``user.csv`` overlay wins. End-to-end edge case: a single-row CSV
    fully replaces the multi-row baked JSON.
    """
    sandbox = _sandbox_api(tmp_path, "instagram-api")
    overlay_user = {
        "id": "ig_overlay_42",
        "username": "overlay_user",
        "name": "Overlay E2E",
        "biography": "from CSV",
        "website": "",
        "followers_count": "0",
        "follows_count": "0",
        "media_count": "0",
        "profile_picture_url": "",
        "ig_id": "0",
        "account_type": "BUSINESS",
        "category": "Other",
    }
    with open(sandbox / "user.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(overlay_user.keys()))
        w.writeheader()
        w.writerow(overlay_user)

    instagram_data = isolated_api_import(
        sandbox, "instagram_data", "instagram-api",
    )
    users = instagram_data._store.table("users").rows()
    assert len(users) == 1
    assert users[0]["id"] == "ig_overlay_42"
    assert users[0]["username"] == "overlay_user"


def test_real_api_figma_ragged_csv_overlay_surfaces_coerce_error(
    tmp_path, isolated_api_import
):
    """A malformed CSV overlay must surface as CoerceError at store-load
    time, not as a downstream KeyError / IndexError when an agent
    eventually hits the route. This is the operator-visibility property
    the Q1 fix is supposed to preserve at the real-API layer.
    """
    sandbox = _sandbox_api(tmp_path, "figma-api")
    # Hand-author a ragged comments.csv (extra unquoted comma in message).
    (sandbox / "comments.csv").write_text(
        "comment_id,file_key,user_id,user_handle,message,node_id,resolved,created_at\n"
        "C1,FK,u1,Edge,oops, extra comma,0:0,false,2026-06-17T00:00:00Z\n",
        encoding="utf-8",
    )
    # NOTE: The CoerceError raised here originates from the _mutable_store that
    # figma_data resolves at (re)import time. When an earlier test in the same
    # session evicts _mutable_store from sys.modules (e.g.
    # test_drift_plane_smoke.py does exactly this in its fixture), the module
    # is re-imported under a fresh identity and its CoerceError becomes a
    # DISTINCT class object from the one bound at the top of THIS file -- so a
    # `pytest.raises(CoerceError)` keyed on the top-level import silently fails
    # to catch it (proven: the re-imported class is not even a subclass). We
    # therefore match on the exception's class NAME + message, which is robust
    # to import-order-dependent class identity. This still fully pins the
    # contract: a ragged overlay CSV must abort store load with a CoerceError
    # naming api+table.
    with pytest.raises(Exception) as excinfo:
        isolated_api_import(sandbox, "figma_data", "figma-api")
    assert type(excinfo.value).__name__ == "CoerceError", (
        f"expected CoerceError, got {type(excinfo.value).__name__}: {excinfo.value}"
    )
    msg = str(excinfo.value)
    assert "ragged row" in msg
    assert "figma-api" in msg
    assert "comments" in msg
