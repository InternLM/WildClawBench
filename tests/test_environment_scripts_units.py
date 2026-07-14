"""Unit tests for the standalone maintenance scripts under ``environment/``.

Covers the *pure logic* of the four operator scripts plus the trivially-
loadable helpers of ``environment/test_all_apis.py``:

  * environment/scripts/audit_data_formats.py   -> classify_file, _non_string_cells, audit_dir
  * environment/scripts/migrate_csv_to_json.py  -> migrate_one, derive_loaded_set, _strip, _canon
  * environment/scripts/wiring_report.py        -> kind_of, load_endpoint_results
  * environment/smoke_eager_load.py             -> _module_name
  * environment/test_all_apis.py                -> parse_service_toml, _iter_items,
                                                   load_endpoints, _path_only, encode_url

These modules are NOT importable packages (no ``__init__.py`` under
``environment/``; ``migrate_csv_to_json.py`` does ``import _mutable_store as ms``
at top level). They are loaded via ``importlib.util.spec_from_file_location``
with ``environment/`` prepended to ``sys.path`` -- the same pattern used by
tests/test_repackage_bundle_ground_truth.py to load ``script/`` files.

Everything here runs OFFLINE and deterministically: no docker, no network, no
subprocess boot. ``derive_loaded_set`` / ``migrate_one`` operate over fake
service trees built in ``tmp_path``; the scripts' module-level ``ROOT`` is
monkeypatched to the tmp tree where the code globs the real environment.

Behaviours are PINNED as-is: where a script does something arguably surprising
(e.g. ``_path_only`` eating a hostname with no leading slash, short CSV rows
becoming ``null`` cells, ``index.csv`` counting as an orphan), the test asserts
the CURRENT output rather than the "ideal" one.
"""

from __future__ import annotations

import glob
import importlib.util
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_ENV_DIR = _REPO_ROOT / "environment"


# ---------------------------------------------------------------------------
# Module loading (standalone scripts -> importlib, environment/ on sys.path)
# ---------------------------------------------------------------------------

def _load_script(unique_name: str, rel_path: str):
    path = _REPO_ROOT / rel_path
    assert path.exists(), f"script missing: {path}"
    # migrate_csv_to_json imports `_mutable_store` at top level; the shared
    # plane lives in environment/, so make it importable before exec.
    env_str = str(_ENV_DIR)
    if env_str not in sys.path:
        sys.path.insert(0, env_str)
    spec = importlib.util.spec_from_file_location(unique_name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[unique_name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def audit_mod():
    return _load_script("_test_audit_data_formats", "environment/scripts/audit_data_formats.py")


@pytest.fixture(scope="module")
def migrate_mod():
    return _load_script("_test_migrate_csv_to_json", "environment/scripts/migrate_csv_to_json.py")


@pytest.fixture(scope="module")
def wiring_mod():
    return _load_script("_test_wiring_report", "environment/scripts/wiring_report.py")


@pytest.fixture(scope="module")
def smoke_mod():
    return _load_script("_test_smoke_eager_load", "environment/smoke_eager_load.py")


@pytest.fixture(scope="module")
def testall_mod():
    return _load_script("_test_test_all_apis", "environment/test_all_apis.py")


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


# ===========================================================================
# audit_data_formats.py
# ===========================================================================

class TestClassifyFile:
    def test_seed_table_array_of_objects_strings(self, audit_mod, tmp_path):
        p = _write(tmp_path / "seed.json", '[{"a": "1"}, {"a": "2"}]\n')
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-table"
        assert "2 rows" in detail
        assert "trailing_nl=True" in detail
        assert "NON-STRING" not in detail

    def test_seed_table_non_string_cells_flagged(self, audit_mod, tmp_path):
        # numeric cell + no trailing newline -> both notes appear in detail
        p = _write(tmp_path / "s.json", '[{"a": 1, "b": "x"}]')
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-table"
        assert "trailing_nl=False" in detail
        assert "NON-STRING cells in ['a']" in detail

    def test_none_cell_is_not_non_string(self, audit_mod, tmp_path):
        # explicit JSON null is exempted from the string-fidelity contract
        p = _write(tmp_path / "s.json", '[{"a": null, "b": "x"}]')
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-table"
        assert "NON-STRING" not in detail

    def test_empty_array(self, audit_mod, tmp_path):
        p = _write(tmp_path / "e.json", "[]")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-empty"
        assert "empty array" in detail

    def test_object_document(self, audit_mod, tmp_path):
        p = _write(tmp_path / "doc.json", '{"x": 1}')
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-doc"
        assert detail.startswith("dict")

    def test_array_not_all_objects_is_doc(self, audit_mod, tmp_path):
        p = _write(tmp_path / "mixed.json", "[1, 2, 3]")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-doc"
        assert "array (not all objects)" in detail

    def test_scalar_document(self, audit_mod, tmp_path):
        p = _write(tmp_path / "n.json", "42")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "data-json-doc"
        assert detail.startswith("int")

    def test_invalid_json_flagged_bad(self, audit_mod, tmp_path):
        p = _write(tmp_path / "bad.json", "{oops not json")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "BAD-JSON"
        assert "invalid json" in detail

    def test_postman_collection_is_config_json(self, audit_mod, tmp_path):
        p = _write(tmp_path / "svc_postman_collection.json", "{}")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "config-json"
        assert detail == "postman collection"

    @pytest.mark.parametrize(
        "name",
        ["server.py", "requirements.txt", "service.toml", "Dockerfile", "notes.md"],
    )
    def test_known_non_data_files_are_config(self, audit_mod, tmp_path, name):
        p = _write(tmp_path / name, "whatever")
        cat, _ = audit_mod.classify_file(p)
        assert cat == "config"

    def test_leftover_csv_is_non_json_data(self, audit_mod, tmp_path):
        # a .csv sitting in an api dir is flagged as "other format"
        p = _write(tmp_path / "leftover.csv", "a,b\n1,2\n")
        # NOTE: .csv is not in NON_DATA_SUFFIX, so it is treated as data.
        cat, detail = audit_mod.classify_file(p)
        assert cat == "NON-JSON-DATA"
        assert detail == ".csv"

    def test_extensionless_file_is_non_json_data(self, audit_mod, tmp_path):
        p = _write(tmp_path / "somefile", "raw bytes here")
        cat, detail = audit_mod.classify_file(p)
        assert cat == "NON-JSON-DATA"
        assert detail == "no-ext"


class TestNonStringCells:
    def test_collects_columns_with_non_string_values(self, audit_mod):
        rows = [{"a": "s", "b": 1}, {"a": "t", "c": True}]
        assert audit_mod._non_string_cells(rows) == {"b", "c"}

    def test_none_and_all_strings_yield_empty(self, audit_mod):
        rows = [{"a": "s", "b": None}, {"a": "t"}]
        assert audit_mod._non_string_cells(rows) == set()


class TestAuditDir:
    def test_classifies_all_files_and_skips_subdirs(self, audit_mod, tmp_path):
        api = tmp_path / "demo-api"
        _write(api / "seed.json", '[{"id": "1"}]\n')
        _write(api / "server.py", "x = 1")
        _write(api / "leftover.csv", "a\n1\n")
        # __pycache__ is a skipped dir; a stray file inside must not surface
        _write(api / "__pycache__" / "x.pyc", "")
        files = audit_mod.audit_dir(api)
        by_name = {f["file"]: f["category"] for f in files}
        assert by_name == {
            "seed.json": "data-json-table",
            "server.py": "config",
            "leftover.csv": "NON-JSON-DATA",
        }
        # results are sorted by filename
        assert [f["file"] for f in files] == sorted(by_name)


# ===========================================================================
# migrate_csv_to_json.py
# ===========================================================================

class TestMigrateStripAndCanon:
    def test_strip_removes_ctx_keys(self, migrate_mod):
        row = {
            "a": "1",
            "__api__": "x",
            "__table__": "t",
            "__file__": "f",
            "__row_index__": 0,
        }
        assert migrate_mod._strip(row) == {"a": "1"}

    def test_canon_is_key_order_independent(self, migrate_mod):
        assert migrate_mod._canon({"b": 1, "a": 2}) == migrate_mod._canon({"a": 2, "b": 1})


class TestMigrateOne:
    def test_dry_run_writes_json_and_keeps_csv(self, migrate_mod, tmp_path):
        csvp = _write(tmp_path / "t.csv", "a,b,c\n1,2,3\n4,5,6\n")
        status, path, detail = migrate_mod.migrate_one(csvp, apply=False)
        assert status == "OK"
        assert "2 row(s)" in detail
        assert csvp.exists()  # dry-run never deletes
        jp = csvp.with_suffix(".json")
        assert json.loads(jp.read_text(encoding="utf-8")) == [
            {"a": "1", "b": "2", "c": "3"},
            {"a": "4", "b": "5", "c": "6"},
        ]
        # trailing newline convention preserved
        assert jp.read_text(encoding="utf-8").endswith("\n")

    def test_short_rows_become_null_cells(self, migrate_mod, tmp_path):
        # NOTE: pins current behavior -- read_csv_with_ctx fills short rows
        # with None (not rejected); the JSON round-trips those as null.
        csvp = _write(tmp_path / "t.csv", "a,b,c\n1,2\n")
        status, _, _ = migrate_mod.migrate_one(csvp, apply=False)
        assert status == "OK"
        rows = json.loads(csvp.with_suffix(".json").read_text(encoding="utf-8"))
        assert rows == [{"a": "1", "b": "2", "c": None}]

    def test_empty_file_yields_empty_array(self, migrate_mod, tmp_path):
        csvp = _write(tmp_path / "empty.csv", "")
        status, _, detail = migrate_mod.migrate_one(csvp, apply=False)
        assert status == "OK"
        assert "0 row(s)" in detail
        assert json.loads(csvp.with_suffix(".json").read_text(encoding="utf-8")) == []

    def test_apply_deletes_csv_after_roundtrip(self, migrate_mod, tmp_path):
        csvp = _write(tmp_path / "apply.csv", "x\n9\n")
        status, _, detail = migrate_mod.migrate_one(csvp, apply=True)
        assert status == "OK-APPLIED"
        assert "csv deleted" in detail
        assert not csvp.exists()
        assert csvp.with_suffix(".json").exists()

    def test_missing_file_reported_not_converted(self, migrate_mod, tmp_path):
        status, _, detail = migrate_mod.migrate_one(tmp_path / "nope.csv", apply=False)
        assert status == "MISSING"
        assert "not on disk" in detail
        assert not (tmp_path / "nope.json").exists()

    def test_ragged_row_raises_coerce_error(self, migrate_mod, tmp_path):
        # A row with MORE fields than the header (unquoted comma) is rejected
        # by read_csv_with_ctx -> CoerceError propagates out of migrate_one.
        # NOTE: pins current behavior -- migrate_one does not catch this.
        csvp = _write(tmp_path / "ragged.csv", "a,b\n1,2,3\n")
        import _mutable_store as ms  # already importable via env on sys.path

        with pytest.raises(ms.CoerceError):
            migrate_mod.migrate_one(csvp, apply=False)


class TestDeriveLoadedSet:
    def test_static_dynamic_and_orphans(self, migrate_mod, tmp_path, monkeypatch):
        api = tmp_path / "foo-api"
        # static: two filename literals in the data module
        _write(
            api / "foo_data.py",
            'x = _load("listings.csv")\nM = {"Account": "accounts.csv"}\n',
        )
        _write(api / "listings.csv", "id\n1\n")
        _write(api / "accounts.csv", "id\n2\n")
        # dynamic: an index csv naming a per-table records file
        _write(api / "index.csv", "records_csv\nrecs.csv\n")
        _write(api / "recs.csv", "id\n4\n")
        # a csv referenced by nothing
        _write(api / "orphan.csv", "id\n3\n")

        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        loaded = {p.name for p in migrate_mod.derive_loaded_set()}
        assert loaded == {"listings.csv", "accounts.csv", "recs.csv"}

        on_disk = {Path(p).resolve() for p in glob.glob(str(tmp_path / "*-api" / "*.csv"))}
        orphans = {p.name for p in (on_disk - migrate_mod.derive_loaded_set())}
        # index.csv is itself never loaded (it is the record index), and
        # orphan.csv is referenced by nothing -> both are orphans.
        assert orphans == {"index.csv", "orphan.csv"}

    def test_literal_only_acted_on_if_csv_exists(self, migrate_mod, tmp_path, monkeypatch):
        # A ".json" literal (already-converted) with no sibling .csv is excluded.
        api = tmp_path / "bar-api"
        _write(api / "bar_data.py", 'x = _load("balance.json")\n')
        # no balance.csv on disk
        monkeypatch.setattr(migrate_mod, "ROOT", tmp_path)
        assert migrate_mod.derive_loaded_set() == set()


# ===========================================================================
# wiring_report.py
# ===========================================================================

class TestKindOf:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("svc_postman_collection.json", "postman"),
            ("seed.json", "data-json"),
            ("foo_data.py", "code"),
            ("service.toml", "config"),
            ("Dockerfile", "config"),
            ("requirements.txt", "config"),
            ("README.md", "config"),
            ("notes.log", "config"),
            ("random.bin", "other"),
            ("noext", "other"),
        ],
    )
    def test_kind_classification(self, wiring_mod, name, expected):
        assert wiring_mod.kind_of(name) == expected

    def test_postman_beats_data_json(self, wiring_mod):
        # a *postman_collection.json is postman, not data-json (order matters)
        assert wiring_mod.kind_of("x_postman_collection.json") == "postman"


class TestLoadEndpointResults:
    def test_missing_file_returns_empty(self, wiring_mod, tmp_path, monkeypatch):
        monkeypatch.setattr(wiring_mod, "ROOT", tmp_path)  # no api_test_responses.json here
        assert wiring_mod.load_endpoint_results() == {}

    def test_parses_environments_keyed_by_name(self, wiring_mod, tmp_path, monkeypatch):
        payload = {
            "environments": [
                {
                    "name": "stripe",
                    "server": "server.py",
                    "counts": {"PASS": 3, "WARN": 1, "FAIL": 0, "SKIP": 2},
                    "dir": "/abs/stripe-api",
                }
            ]
        }
        _write(tmp_path / "api_test_responses.json", json.dumps(payload))
        monkeypatch.setattr(wiring_mod, "ROOT", tmp_path)
        out = wiring_mod.load_endpoint_results()
        assert out["stripe"]["server"] == "server.py"
        assert out["stripe"]["counts"]["PASS"] == 3
        # dir is reduced to its basename
        assert out["stripe"]["dir"] == "stripe-api"


# ===========================================================================
# smoke_eager_load.py
# ===========================================================================

class TestModuleName:
    @pytest.mark.parametrize(
        "dirname,expected",
        [
            ("stripe-api", "stripe_data"),
            ("google-drive-api", "google_drive_data"),
            ("github-api", "github_data"),
            # trailing "-api" -> "_api" is stripped; internal dashes -> underscore
            ("multi-word-thing-api", "multi_word_thing_data"),
        ],
    )
    def test_dir_to_data_module_name(self, smoke_mod, dirname, expected):
        assert smoke_mod._module_name(Path("/x") / dirname) == expected


# ===========================================================================
# test_all_apis.py (standalone runner -- pure helpers only)
# ===========================================================================

class TestParseServiceToml:
    def test_reads_service_section_only(self, testall_mod, tmp_path):
        toml = _write(
            tmp_path / "service.toml",
            "[service]\n"
            'name = "foo"\n'
            "port = 8123\n"
            'healthcheck_path = "/hc"\n'
            "[other]\n"
            "port = 999\n",  # must be ignored (outside [service])
        )
        assert testall_mod.parse_service_toml(toml) == ("foo", 8123, "/hc")

    def test_defaults_health_and_tolerates_bad_port(self, testall_mod, tmp_path):
        toml = _write(
            tmp_path / "service.toml",
            "[service]\nname = 'bar'\nport = notanint\n",
        )
        # bad port -> None; missing healthcheck_path -> "/health"
        assert testall_mod.parse_service_toml(toml) == ("bar", None, "/health")

    def test_comments_and_blank_lines_ignored(self, testall_mod, tmp_path):
        toml = _write(
            tmp_path / "service.toml",
            "[service]\n# a comment line\n\nname = \"baz\"\nport = 42\n",
        )
        assert testall_mod.parse_service_toml(toml) == ("baz", 42, "/health")


class TestIterItems:
    def test_recurses_folders_and_yields_leaf_requests(self, testall_mod):
        items = [
            {"name": "folder", "item": [
                {"name": "r1", "request": {"method": "GET"}},
                {"name": "sub", "item": [{"name": "r2", "request": {"method": "POST"}}]},
            ]},
            {"name": "r3", "request": {"method": "GET"}},
            {"name": "not-a-request"},  # neither item nor request -> skipped
        ]
        got = [it["name"] for it in testall_mod._iter_items(items)]
        assert got == ["r1", "r2", "r3"]

    def test_none_input_yields_nothing(self, testall_mod):
        assert list(testall_mod._iter_items(None)) == []


class TestPathOnly:
    def test_strips_scheme_and_host(self, testall_mod):
        assert testall_mod._path_only("http://host:8/a/b?q=1") == "/a/b?q=1"

    def test_empty_url_returns_empty(self, testall_mod):
        assert testall_mod._path_only("") == ""

    def test_host_without_leading_slash_is_consumed(self, testall_mod):
        # NOTE: pins current behavior -- the regex ^https?://[^/]+ eats
        # everything up to the first '/', so a path glued to the host
        # (no separating slash) loses its leading segment.
        assert testall_mod._path_only("http://127.0.0.1:8080v1/x") == "/x"


class TestEncodeUrl:
    def test_encodes_spaces_in_path_and_query(self, testall_mod):
        assert testall_mod.encode_url("http://h/a b?q=1 2") == "http://h/a%20b?q=1%202"

    def test_preexisting_escapes_not_double_encoded(self, testall_mod):
        # '%' is in the safe set, so %3D stays %3D (not %253D)
        assert testall_mod.encode_url("http://h/a?jql=x%3Dy") == "http://h/a?jql=x%3Dy"


class TestLoadEndpoints:
    def _collection(self):
        return {
            "variable": [{"key": "baseUrl", "value": "http://localhost:9/"}],
            "item": [
                {"name": "ok", "request": {
                    "method": "get",  # lowercased method -> uppercased
                    "url": {"raw": "{{baseUrl}}v1/x"},
                    "header": [{"key": "H", "value": "v"}, {"key": None, "value": "z"}],
                    "body": {"mode": "raw", "raw": '{"a": 1}'},
                }},
                {"name": "missing", "request": {
                    "method": "POST",
                    "url": "{{baseUrl}}z/{{unknown}}",
                }},
                {"name": "folder", "item": [
                    {"name": "nested", "request": {"method": "GET", "url": "{{baseUrl}}n"}},
                ]},
            ],
        }

    def test_resolves_vars_uppercases_method_and_rewrites_localhost(self, testall_mod, tmp_path):
        cp = _write(tmp_path / "c_postman_collection.json", json.dumps(self._collection()))
        endpoints, skipped = testall_mod.load_endpoints(cp, 8080)

        names = {e["name"]: e for e in endpoints}
        assert set(names) == {"ok", "nested"}

        ok = names["ok"]
        # localhost -> the port the server binds; method uppercased
        assert ok["method"] == "GET"
        assert ok["url"] == "http://127.0.0.1:8080v1/x"
        # header with a None key is dropped; only "H" survives
        assert ok["headers"] == {"H": "v"}
        assert ok["body"] == '{"a": 1}'

    def test_unresolved_variable_is_skipped_with_name(self, testall_mod, tmp_path):
        cp = _write(tmp_path / "c_postman_collection.json", json.dumps(self._collection()))
        _, skipped = testall_mod.load_endpoints(cp, 8080)
        assert [s["name"] for s in skipped] == ["missing"]
        assert skipped[0]["missing_var"] == "unknown"

    def test_default_base_url_var_when_absent(self, testall_mod, tmp_path):
        # no "variable" block at all -> baseUrl/base_url default to the local port
        coll = {"item": [{"name": "r", "request": {"method": "GET", "url": "{{baseUrl}}/ping"}}]}
        cp = _write(tmp_path / "c_postman_collection.json", json.dumps(coll))
        endpoints, skipped = testall_mod.load_endpoints(cp, 7000)
        assert skipped == []
        assert endpoints[0]["url"] == "http://127.0.0.1:7000/ping"
        assert endpoints[0]["path"] == "/ping"
