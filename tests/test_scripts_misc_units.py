"""Unit coverage for the standalone one-off maintenance scripts under ``script/``.

These files are utility CLIs (migrations, dry-run verifiers, bundle reconstructors,
overlay coercion checkers) that are NOT importable as a package. Like
``tests/test_repackage_bundle_ground_truth.py`` they are loaded by path via
``importlib.util.spec_from_file_location`` and their pure helper functions are
exercised over fake input trees built in ``tmp_path``.

Everything here runs OFFLINE and deterministically: no Docker, no network, no AWS.
``subprocess`` is neutralised via monkeypatch where a script shells out to git.

Where a script's *observed* behaviour is arguably surprising (e.g. a wrong sys.path
insert that makes a module un-importable in isolation, or collision-rename ordering),
the test PINS the current behaviour and says so — it is a characterization test, not
a spec. See SCORING_AUDIT_REPORT.md.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT_DIR = _REPO_ROOT / "script"


# --------------------------------------------------------------------------- #
# module loading
# --------------------------------------------------------------------------- #
def _load_script(mod_name: str, filename: str):
    """Load a script/<filename>.py as an importable module object by path."""
    path = _SCRIPT_DIR / filename
    assert path.exists(), f"script missing: {path}"
    spec = importlib.util.spec_from_file_location(mod_name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


# Scripts with clean, side-effect-free module bodies -> load once per session.
@pytest.fixture(scope="module")
def backfill():
    return _load_script("_t_backfill_connector_docs", "backfill_connector_docs.py")


@pytest.fixture(scope="module")
def migrate():
    return _load_script("_t_migrate_to_drift_plane", "migrate_to_drift_plane.py")


@pytest.fixture(scope="module")
def reconstruct_mod():
    return _load_script("_t_reconstruct_input_from_bundle", "reconstruct_input_from_bundle.py")


@pytest.fixture(scope="module")
def coerce_dryrun():
    return _load_script("_t_coerce_dryrun", "coerce_dryrun.py")


@pytest.fixture(scope="module")
def coerce_malformed():
    return _load_script("_t_coerce_malformed_test", "coerce_malformed_test.py")


@pytest.fixture(scope="module")
def extract_home():
    return _load_script("_t_extract_home_to_data", "extract_home_to_data.py")


# =========================================================================== #
# script/backfill_connector_docs.py
# =========================================================================== #
class TestBackfillConnectorDocs:
    def test_slug_normalises_and_strips(self, backfill):
        assert backfill._slug("Hello World-API!!") == "hello_world_api"
        assert backfill._slug("---A B---") == "a_b"
        assert backfill._slug("") == ""

    def test_resource_of_skips_version_and_param_segments(self, backfill):
        assert backfill._resource_of("/v1/messages/{id}") == "messages"
        # All-param / all-version path collapses to the "root" sentinel.
        assert backfill._resource_of("/{id}/{sub}") == "root"
        assert backfill._resource_of("/v3/{id}") == "root"

    def test_flag_for_is_stable_and_dedupes(self, backfill):
        seen: set[str] = set()
        assert backfill._flag_for("GET", "/v1/messages", seen) == "get_messages"
        assert backfill._flag_for("GET", "/v1/messages/{id}", seen) == "get_messages_id"
        assert backfill._flag_for("POST", "/v1/messages", seen) == "post_messages"
        # A second GET on the same path can't reuse the flag -> numeric suffix.
        assert backfill._flag_for("GET", "/v1/messages", seen) == "get_messages_2"

    def test_parse_service_toml_minimal_reader(self, backfill, tmp_path):
        svc = tmp_path / "service.toml"
        svc.write_text(
            '[service]\nenv_var_name = "GMAIL_API_URL"\nport = "8111"\n',
            encoding="utf-8",
        )
        out = backfill.parse_service_toml(svc)
        assert out["env_var_name"] == "GMAIL_API_URL"
        assert out["port"] == "8111"

    def test_parse_service_toml_missing_file_is_empty(self, backfill, tmp_path):
        assert backfill.parse_service_toml(tmp_path / "nope.toml") == {}

    def test_parse_skill_extracts_title_env_and_endpoints(self, backfill, tmp_path):
        skill = tmp_path / "SKILL.md"
        skill.write_text(
            "# Gmail API Connector\n\n"
            "Env var: `GMAIL_API_URL`\n\n"
            "| Method | Path |\n"
            "|--------|------|\n"
            "| GET | `/v1/messages` |\n"
            "| POST | `/v1/messages` |\n"
            "| DELETE | `/v1/messages/{id}` |\n",
            encoding="utf-8",
        )
        info = backfill.parse_skill(skill)
        assert info["title"] == "Gmail API Connector"
        assert info["env_var"] == "GMAIL_API_URL"
        assert info["endpoints"] == [
            ("GET", "/v1/messages"),
            ("POST", "/v1/messages"),
            ("DELETE", "/v1/messages/{id}"),
        ]

    def test_parse_skill_skips_header_and_non_path_rows(self, backfill, tmp_path):
        # Header, separator, and a row whose "path" doesn't start with / are dropped.
        skill = tmp_path / "SKILL.md"
        skill.write_text(
            "| Method | Path |\n"
            "|--------|------|\n"
            "| GET | not-a-path |\n"
            "| GET | `/ok` |\n",
            encoding="utf-8",
        )
        info = backfill.parse_skill(skill)
        assert info["endpoints"] == [("GET", "/ok")]

    def test_parse_skill_missing_file_yields_empty_shape(self, backfill, tmp_path):
        info = backfill.parse_skill(tmp_path / "missing.md")
        assert info["title"] == ""
        assert info["env_var"] == ""
        assert info["endpoints"] == []

    def test_build_reference_has_curl_and_audit_note(self, backfill):
        info = {
            "title": "Gmail API Connector",
            "env_var": "GMAIL_API_URL",
            "endpoints": [
                ("GET", "/v1/messages"),
                ("POST", "/v1/messages"),
                ("DELETE", "/v1/messages/{id}"),
            ],
        }
        ref = backfill.build_reference(info, "GMAIL_API_URL")
        assert ref.startswith("# Gmail API Connector Guide")
        assert "curl -s" in ref
        # POST endpoints use -X POST with a JSON content-type header.
        assert '-X POST "$GMAIL_API_URL/v1/messages"' in ref
        # DELETE path placeholders are rendered as <id> in the example.
        assert '-X DELETE "$GMAIL_API_URL/v1/messages/<id>"' in ref
        assert "/audit/requests" in ref

    def test_build_reference_empty_title_falls_back(self, backfill):
        ref = backfill.build_reference(
            {"title": "", "env_var": "X_API_URL", "endpoints": []}, "X_API_URL"
        )
        assert ref.startswith("# Mock API Guide")

    def test_build_script_generates_valid_python(self, backfill):
        info = {
            "title": "Gmail",
            "env_var": "GMAIL_API_URL",
            "endpoints": [
                ("GET", "/v1/messages"),
                ("GET", "/v1/messages/{id}"),
                ("POST", "/v1/messages"),
                ("DELETE", "/v1/messages/{id}"),
            ],
        }
        script = backfill.build_script(info, "gmail", "GMAIL_API_URL", "8111")
        # Must parse as Python — the generated CLI is the actual deliverable.
        import ast

        ast.parse(script)
        assert script.startswith("#!/usr/bin/env")
        assert "def main()" in script

    def test_process_connector_writes_references_and_scripts(self, backfill, tmp_path):
        # environment/ layout: <name>-api-connector/SKILL.md + <name>-api/service.toml
        env_root = tmp_path / "environment"
        conn = env_root / "skills" / "gmail-api-connector"
        conn.mkdir(parents=True)
        (conn / "SKILL.md").write_text(
            "# Gmail\n\n`GMAIL_API_URL`\n\n"
            "| Method | Path |\n|--------|------|\n| GET | `/v1/messages` |\n",
            encoding="utf-8",
        )
        api_dir = env_root / "gmail-api"
        api_dir.mkdir(parents=True)
        (api_dir / "service.toml").write_text(
            '[service]\nenv_var_name = "GMAIL_API_URL"\nport = "8111"\n',
            encoding="utf-8",
        )

        status = backfill.process_connector(conn, env_root, force=False, verbose=False)
        assert status == "written"
        assert (conn / "references" / "gmail-api-guide.md").is_file()
        assert (conn / "scripts" / "fetch_gmail_data.py").is_file()

        # Idempotent: a second run without --force skips the existing references/.
        assert backfill.process_connector(conn, env_root, force=False, verbose=False) == "skip-exists"

    def test_process_connector_status_no_skill_and_no_endpoints(self, backfill, tmp_path):
        env_root = tmp_path / "environment"
        # No SKILL.md -> skip-no-skill
        conn1 = env_root / "skills" / "empty-api-connector"
        conn1.mkdir(parents=True)
        assert backfill.process_connector(conn1, env_root, force=False, verbose=False) == "skip-no-skill"

        # SKILL.md with no endpoint rows -> skip-no-endpoints
        conn2 = env_root / "skills" / "bare-api-connector"
        conn2.mkdir(parents=True)
        (conn2 / "SKILL.md").write_text("# Bare\n\nno table here\n", encoding="utf-8")
        assert backfill.process_connector(conn2, env_root, force=False, verbose=False) == "skip-no-endpoints"

    def test_find_bundle_skill_dirs_discovers_nested_connectors(self, backfill, tmp_path):
        base = tmp_path / "bundle" / "task1" / "data" / "environment" / "skills"
        (base / "gmail-api-connector").mkdir(parents=True)
        (base / "outlook-api-connector").mkdir(parents=True)
        (base / "not-a-connector").mkdir(parents=True)  # wrong suffix -> ignored
        found = backfill.find_bundle_skill_dirs(tmp_path / "bundle")
        assert sorted(p.name for p in found) == ["gmail-api-connector", "outlook-api-connector"]


# =========================================================================== #
# script/migrate_to_drift_plane.py
# =========================================================================== #
class TestMigrateToDriftPlane:
    def test_data_module_name_default_and_override(self, migrate):
        assert migrate.data_module_name("gmail-api") == "gmail_data"
        # Curated overrides win over the mechanical rule.
        assert migrate.data_module_name("google-drive-api") == "drive_data"

    def test_data_module_name_removesuffix_only_strips_one_api(self, migrate):
        # NOTE: pins current behavior — removesuffix("_api") strips exactly one
        # occurrence, so a doubled "-api-api" leaves a stray "_api". See SCORING_AUDIT_REPORT.md.
        assert migrate.data_module_name("foo-api-api") == "foo_api_data"

    def test_parse_module_finds_loads_shadows_and_empties(self, migrate):
        text = (
            '_customers = _coerce_customers(_load("customers.csv"))\n'
            "_customers_store = deepcopy(_customers)\n"
            '_events = _load("events.csv")\n'
            "_empty_store = []\n"
        )
        load_vars, shadow_to_src, json_vars, empty_stores = migrate.parse_module(text)
        assert load_vars["_customers"] == (
            "customers.csv",
            '_coerce_customers(_load("customers.csv"))',
        )
        assert load_vars["_events"][0] == "events.csv"
        assert shadow_to_src == {"_customers_store": "_customers"}
        assert json_vars == {}
        assert empty_stores == ["_empty_store"]

    def test_infer_primary_key_prefers_singular_id_from_header(self, migrate, tmp_path):
        csv = tmp_path / "customers.csv"
        csv.write_text("customer_id,name\nc1,Bob\n", encoding="utf-8")
        assert migrate.infer_primary_key("customers", csv, "") == "customer_id"

    def test_infer_primary_key_falls_back_to_first_header(self, migrate, tmp_path):
        csv = tmp_path / "widgets.csv"
        csv.write_text("foo,bar\n1,2\n", encoding="utf-8")
        # No <singular>_id / id / objectID etc. -> first header column.
        assert migrate.infer_primary_key("widgets", csv, "") == "foo"

    def test_infer_primary_key_per_api_override(self, migrate, tmp_path):
        csv = tmp_path / "accounts.csv"
        csv.write_text("whatever,else\n1,2\n", encoding="utf-8")
        # PER_API_PK_OVERRIDES for xero-api short-circuits before any header read.
        assert migrate.infer_primary_key("accounts", csv, "xero-api") == "AccountID"

    def test_infer_primary_key_missing_file_uses_pk_overrides(self, migrate, tmp_path):
        # File cannot be read -> PK_OVERRIDES map ("users" -> "user_id").
        assert migrate.infer_primary_key("users", tmp_path / "gone.csv", "") == "user_id"
        # Unmapped logical name with no readable header -> "id".
        assert migrate.infer_primary_key("unknowns", tmp_path / "gone.csv", "") == "id"

    def test_build_register_block_table_vs_document(self, migrate):
        table = migrate.StoreDecl(
            name="customers", primary_key="customer_id",
            initial_loader_expr="lambda: []", is_document=False,
        )
        doc = migrate.StoreDecl(
            name="account", primary_key="", initial_loader_expr="lambda: {}",
            is_document=True,
        )
        block = migrate.build_register_block([table, doc], {}, {})
        assert '_store.register("customers", primary_key="customer_id"' in block
        assert '_store.register_document("account"' in block

    def test_build_accessor_block_table_vs_document(self, migrate):
        table = migrate.StoreDecl(
            name="customers", primary_key="customer_id",
            initial_loader_expr="lambda: []", is_document=False,
        )
        doc = migrate.StoreDecl(
            name="account", primary_key="", initial_loader_expr="lambda: {}",
            is_document=True,
        )
        block = migrate.build_accessor_block([table, doc])
        assert "def _customers_rows():" in block
        assert '_store.table("customers").rows()' in block
        assert "def _account_doc():" in block
        assert '_store.document("account").get()' in block

    def _mk_api(self, tmp_path: Path) -> Path:
        api = tmp_path / "widget-api"
        api.mkdir()
        (api / "customers.csv").write_text("customer_id,name\nc1,Bob\n", encoding="utf-8")
        (api / "widget_data.py").write_text(
            "from copy import deepcopy\n"
            "from pathlib import Path\n"
            "import csv\n"
            "DATA_DIR = Path(__file__).parent\n"
            "def _load(name):\n"
            "    return list(csv.DictReader(open(DATA_DIR / name)))\n"
            "def _coerce_customers(rows):\n"
            "    return rows\n"
            '_customers = _coerce_customers(_load("customers.csv"))\n'
            "_customers_store = deepcopy(_customers)\n\n"
            "def get_customers():\n"
            "    return _customers_store\n",
            encoding="utf-8",
        )
        (api / "server.py").write_text(
            "from fastapi import FastAPI\n"
            "app = FastAPI()\n"
            "try:\n"
            "    from tracking_middleware import install_tracker\n"
            "except ModuleNotFoundError:\n"
            "    def install_tracker(app):\n"
            "        return None\n"
            "install_tracker(app)\n",
            encoding="utf-8",
        )
        return api

    def test_plan_module_detects_store_and_pk(self, migrate, tmp_path, monkeypatch):
        api = self._mk_api(tmp_path)
        monkeypatch.setattr(migrate, "ENV_DIR", tmp_path)
        mig = migrate.plan_module(api)
        assert mig.issues == []
        assert mig.data_module_name == "widget_data"
        assert [(s.name, s.primary_key, s.is_document) for s in mig.stores] == [
            ("customers", "customer_id", False)
        ]

    def test_plan_module_flags_already_migrated_and_no_stores(self, migrate, tmp_path, monkeypatch):
        monkeypatch.setattr(migrate, "ENV_DIR", tmp_path)
        # already migrated marker
        done = tmp_path / "done-api"
        done.mkdir()
        (done / "done_data.py").write_text(
            "from _mutable_store import get_store\n", encoding="utf-8"
        )
        assert "already migrated" in migrate.plan_module(done).issues
        # no recognisable stores
        empty = tmp_path / "empty-api"
        empty.mkdir()
        (empty / "empty_data.py").write_text("x = 1\n", encoding="utf-8")
        issues = migrate.plan_module(empty).issues
        assert any("no stores" in i for i in issues)

    def test_apply_data_module_and_server_produce_valid_python(self, migrate, tmp_path, monkeypatch):
        import ast

        api = self._mk_api(tmp_path)
        monkeypatch.setattr(migrate, "ENV_DIR", tmp_path)
        mig = migrate.plan_module(api)
        dm_out = migrate.apply_data_module(mig)
        assert dm_out is not None
        assert "get_store(" in dm_out
        assert '_store.register("customers"' in dm_out
        assert "_customers_rows" in dm_out
        ast.parse(dm_out)

        sv_out = migrate.apply_server(api, mig.data_module_name)
        assert sv_out is not None
        assert "install_admin_plane" in sv_out
        ast.parse(sv_out)

    def test_apply_server_returns_none_when_already_has_admin_plane(self, migrate, tmp_path):
        api = tmp_path / "srv-api"
        api.mkdir()
        (api / "server.py").write_text(
            "install_admin_plane(app)\ninstall_tracker(app)\n", encoding="utf-8"
        )
        assert migrate.apply_server(api, "srv_data") is None


# =========================================================================== #
# script/reconstruct_input_from_bundle.py
# =========================================================================== #
class TestReconstructInputFromBundle:
    def test_looks_like_bundle_prompt_and_rubric(self, reconstruct_mod, tmp_path):
        b = tmp_path / "b"
        b.mkdir()
        assert reconstruct_mod._looks_like_bundle(b) is False
        (b / "prompt.txt").write_text("hi", encoding="utf-8")
        (b / "rubric.json").write_text("[]", encoding="utf-8")
        assert reconstruct_mod._looks_like_bundle(b) is True

    def test_looks_like_bundle_via_instruction_and_env(self, reconstruct_mod, tmp_path):
        b = tmp_path / "b"
        (b / "data").mkdir(parents=True)
        (b / "data" / "instruction.md").write_text("do it", encoding="utf-8")
        (b / "data" / "environment").mkdir()
        # prompt via instruction.md fallback + env dir counts as a bundle even without rubric.
        assert reconstruct_mod._looks_like_bundle(b) is True

    def test_discover_bundles_single_and_multi(self, reconstruct_mod, tmp_path):
        # single bundle at root
        single = tmp_path / "single"
        single.mkdir()
        (single / "prompt.txt").write_text("p", encoding="utf-8")
        (single / "rubric.json").write_text("[]", encoding="utf-8")
        assert [b.name for b in reconstruct_mod.discover_bundles(single)] == ["single"]

        # root containing several bundles
        root = tmp_path / "root"
        for name in ("t_a", "t_b"):
            d = root / name
            d.mkdir(parents=True)
            (d / "prompt.txt").write_text("p", encoding="utf-8")
            (d / "rubric.json").write_text("[]", encoding="utf-8")
        (root / "not_a_bundle").mkdir()
        assert sorted(b.name for b in reconstruct_mod.discover_bundles(root)) == ["t_a", "t_b"]

    def test_extract_overlays_isolates_diffs_and_new_files(self, reconstruct_mod, tmp_path):
        baseline = tmp_path / "baseline"
        (baseline / "foo-api").mkdir(parents=True)
        (baseline / "foo-api" / "seed.json").write_text('{"a":1}', encoding="utf-8")
        (baseline / "foo-api" / "same.csv").write_text("id\n1\n", encoding="utf-8")

        benv = tmp_path / "bundle" / "data" / "environment"
        (benv / "foo-api").mkdir(parents=True)
        (benv / "foo-api" / "seed.json").write_text('{"a":2}', encoding="utf-8")  # DIFFERS
        (benv / "foo-api" / "same.csv").write_text("id\n1\n", encoding="utf-8")    # identical
        (benv / "foo-api" / "new.json").write_text('{"b":9}', encoding="utf-8")     # NEW

        out = tmp_path / "outmock"
        recovered, warnings = reconstruct_mod.extract_overlays(benv, baseline, out)
        assert warnings == []
        assert (out / "foo-api" / "seed.json").is_file()   # overlay (differs)
        assert (out / "foo-api" / "new.json").is_file()    # overlay (new)
        assert not (out / "foo-api" / "same.csv").is_file()  # identical -> skipped
        reasons = " ".join(recovered["foo-api"])
        assert "differs-from-default" in reasons
        assert "new-not-in-default" in reasons

    def test_extract_overlays_warns_when_api_not_in_baseline(self, reconstruct_mod, tmp_path):
        baseline = tmp_path / "baseline"
        baseline.mkdir()  # empty baseline
        benv = tmp_path / "bundle" / "data" / "environment"
        (benv / "bar-api").mkdir(parents=True)
        (benv / "bar-api" / "seed.json").write_text('{"x":1}', encoding="utf-8")
        out = tmp_path / "outmock"
        recovered, warnings = reconstruct_mod.extract_overlays(benv, baseline, out)
        assert (out / "bar-api" / "seed.json").is_file()
        assert any("UNVERIFIED" in w for w in warnings)

    def test_extract_overlays_missing_env_dir(self, reconstruct_mod, tmp_path):
        recovered, warnings = reconstruct_mod.extract_overlays(
            tmp_path / "nope", tmp_path / "baseline", tmp_path / "out"
        )
        assert recovered == {}
        assert any("skipped mock_data" in w for w in warnings)

    def test_load_toml_missing_and_present(self, reconstruct_mod, tmp_path):
        assert reconstruct_mod._load_toml(tmp_path / "none.toml") == {}
        t = tmp_path / "task.toml"
        t.write_text('[environment]\nrequired_apis = ["foo-api"]\n', encoding="utf-8")
        assert reconstruct_mod._load_toml(t) == {"environment": {"required_apis": ["foo-api"]}}

    def test_copy_flat_dir_flattens_and_skips_junk(self, reconstruct_mod, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "a.md").write_text("a", encoding="utf-8")
        (src / ".DS_Store").write_text("junk", encoding="utf-8")
        (src / "sub").mkdir()  # subdir not descended
        (src / "sub" / "b.md").write_text("b", encoding="utf-8")
        dst = tmp_path / "dst"
        names = reconstruct_mod._copy_flat_dir(src, dst)
        assert names == ["a.md"]
        assert (dst / "a.md").is_file()
        assert not (dst / ".DS_Store").exists()

    def test_reconstruct_full_tree(self, reconstruct_mod, tmp_path):
        b = tmp_path / "bundle"
        benv = b / "data" / "environment"
        benv.mkdir(parents=True)
        (b / "prompt.txt").write_text("do it", encoding="utf-8")
        (b / "rubric.json").write_text('[{"c":1}]', encoding="utf-8")
        (benv / "persona").mkdir()
        (benv / "persona" / "MEMORY.md").write_text("mem", encoding="utf-8")
        (benv / "artifacts" / "inputs" / "files").mkdir(parents=True)
        (benv / "artifacts" / "inputs" / "files" / "input.txt").write_text("x", encoding="utf-8")
        (b / "data" / "tests").mkdir(parents=True)
        (b / "data" / "tests" / "test_outputs.py").write_text("def test(): pass", encoding="utf-8")

        out = tmp_path / "out" / "task"
        summary = reconstruct_mod.reconstruct(b, out, tmp_path / "baseline", verbose=False)
        assert summary["prompt"] is True
        assert summary["rubric"] is True
        assert summary["persona_files"] == 1
        assert summary["data_files"] == 1
        assert (out / "prompt.txt").read_text(encoding="utf-8") == "do it"
        assert (out / "persona" / "MEMORY.md").is_file()
        assert (out / "data" / "input.txt").is_file()
        assert (out / "test_outputs.py").is_file()
        assert (out / "RECONSTRUCTION_NOTES.md").is_file()

    def test_reconstruct_prompt_fallback_to_instruction_md(self, reconstruct_mod, tmp_path):
        b = tmp_path / "b2"
        (b / "data").mkdir(parents=True)
        (b / "data" / "instruction.md").write_text("fallback prompt", encoding="utf-8")
        (b / "rubric.json").write_text("[]", encoding="utf-8")
        out = tmp_path / "out2"
        reconstruct_mod.reconstruct(b, out, tmp_path / "baseline", verbose=False)
        assert (out / "prompt.txt").read_text(encoding="utf-8") == "fallback prompt"


# =========================================================================== #
# script/coerce_dryrun.py
# =========================================================================== #
class TestCoerceDryrun:
    def test_overlaid_apis_lists_sorted_subdirs(self, coerce_dryrun, tmp_path):
        task = tmp_path / "task1"
        (task / "mock_data" / "foo-api").mkdir(parents=True)
        (task / "mock_data" / "bar-api").mkdir(parents=True)
        (task / "mock_data" / "readme.txt").write_text("x", encoding="utf-8")  # file, not dir
        apis = coerce_dryrun._overlaid_apis(task)
        assert [p.name for p in apis] == ["bar-api", "foo-api"]

    def test_overlaid_apis_no_mock_data(self, coerce_dryrun, tmp_path):
        assert coerce_dryrun._overlaid_apis(tmp_path / "empty") == []

    def test_tracked_task_dirs_git_listing(self, coerce_dryrun, tmp_path, monkeypatch):
        # Two git-tracked tasks; only ones that actually have mock_data/ survive.
        inp = tmp_path / "input"
        (inp / "alpha" / "mock_data").mkdir(parents=True)
        (inp / "beta" / "mock_data").mkdir(parents=True)
        (inp / "gamma").mkdir(parents=True)  # tracked but no mock_data/
        monkeypatch.setattr(coerce_dryrun, "INPUT_DIR", inp)

        git_out = (
            "input/alpha/prompt.txt\n"
            "input/alpha/mock_data/foo-api/x.csv\n"
            "input/beta/mock_data/bar-api/y.csv\n"
            "input/gamma/prompt.txt\n"
        )

        class _Res:
            stdout = git_out

        monkeypatch.setattr(subprocess, "run", lambda *a, **k: _Res())
        dirs = coerce_dryrun._tracked_task_dirs()
        assert sorted(d.name for d in dirs) == ["alpha", "beta"]

    def test_tracked_task_dirs_falls_back_to_dir_scan(self, coerce_dryrun, tmp_path, monkeypatch):
        inp = tmp_path / "input"
        (inp / "solo" / "mock_data").mkdir(parents=True)
        (inp / "no_mock").mkdir(parents=True)
        monkeypatch.setattr(coerce_dryrun, "INPUT_DIR", inp)

        def _boom(*a, **k):
            raise OSError("git unavailable")

        monkeypatch.setattr(subprocess, "run", _boom)
        dirs = coerce_dryrun._tracked_task_dirs()
        # Fallback keeps only dirs that have a mock_data/ child.
        assert [d.name for d in dirs] == ["solo"]


# =========================================================================== #
# script/coerce_malformed_test.py
# =========================================================================== #
class TestCoerceMalformedTest:
    def test_write_roundtrips_bytes(self, coerce_malformed, tmp_path):
        p = coerce_malformed._write(tmp_path, "a.bin", b"hi")
        assert p.read_bytes() == b"hi"

    def test_expect_coerce_requires_context_tokens(self, coerce_malformed):
        CoerceError = coerce_malformed.CoerceError

        def good():
            raise CoerceError("api=x table=y file=z bad")

        def missing_ctx():
            raise CoerceError("no context here")

        def wrong_type():
            raise ValueError("nope")

        def no_raise():
            return 1

        assert coerce_malformed._expect_coerce("g", good) is True
        assert coerce_malformed._expect_coerce("b", missing_ctx) is False
        assert coerce_malformed._expect_coerce("w", wrong_type) is False
        assert coerce_malformed._expect_coerce("n", no_raise) is False

    def test_expect_ok_pass_fail_and_exception(self, coerce_malformed):
        assert coerce_malformed._expect_ok("ok", lambda: 5, lambda r: r == 5) is True
        assert coerce_malformed._expect_ok("ok", lambda: 5, lambda r: r == 6) is False

        def boom():
            raise RuntimeError("x")

        assert coerce_malformed._expect_ok("ok", boom, lambda r: True) is False

    def test_main_runs_offline_and_passes(self, coerce_malformed):
        # main() exercises the real _mutable_store coercion guards entirely offline
        # (stdlib CSV parsing, no network) and exits 0 when all checks pass.
        with pytest.raises(SystemExit) as exc:
            coerce_malformed.main()
        assert exc.value.code == 0


# =========================================================================== #
# script/extract_home_to_data.py
# =========================================================================== #
class TestExtractHomeToData:
    def test_flatten_name_joins_parts_with_double_underscore(self, extract_home):
        assert extract_home._flatten_name(Path("Library/README.md")) == "Library__README.md"
        assert extract_home._flatten_name(Path("a/b/c.txt")) == "a__b__c.txt"

    def test_extract_flattens_and_resolves_collisions(self, extract_home, tmp_path):
        task = tmp_path / "task"
        home = task / "persona" / "home"
        (home / "Library").mkdir(parents=True)
        (home / "Public").mkdir(parents=True)
        (home / "Library" / "README.md").write_text("lib", encoding="utf-8")
        (home / "Public" / "README.md").write_text("pub", encoding="utf-8")
        (home / "notes.txt").write_text("n", encoding="utf-8")

        rc = extract_home.extract(
            task, clean=True, dry_run=False, verbose=False, delete_home=False
        )
        assert rc == 0
        data = task / "data"
        names = sorted(p.name for p in data.iterdir())
        # NOTE: pins current behavior — sorted() puts "Library/README.md" first, so it
        # keeps the plain "README.md"; the later "Public/README.md" collides and is
        # flattened. See SCORING_AUDIT_REPORT.md.
        assert names == ["Public__README.md", "README.md", "notes.txt"]
        assert (data / "README.md").read_text(encoding="utf-8") == "lib"
        assert (data / "Public__README.md").read_text(encoding="utf-8") == "pub"

    def test_extract_missing_home_returns_2(self, extract_home, tmp_path):
        assert extract_home.extract(
            tmp_path / "nope", clean=True, dry_run=False, verbose=False, delete_home=False
        ) == 2

    def test_extract_empty_home_returns_2(self, extract_home, tmp_path):
        task = tmp_path / "t"
        (task / "persona" / "home").mkdir(parents=True)
        assert extract_home.extract(
            task, clean=True, dry_run=False, verbose=False, delete_home=False
        ) == 2

    def test_extract_dry_run_writes_nothing(self, extract_home, tmp_path):
        task = tmp_path / "t"
        home = task / "persona" / "home"
        home.mkdir(parents=True)
        (home / "a.txt").write_text("a", encoding="utf-8")
        rc = extract_home.extract(
            task, clean=True, dry_run=True, verbose=False, delete_home=False
        )
        assert rc == 0
        assert not (task / "data").exists()

    def test_extract_delete_home_removes_source_tree(self, extract_home, tmp_path):
        task = tmp_path / "t"
        home = task / "persona" / "home"
        home.mkdir(parents=True)
        (home / "a.txt").write_text("a", encoding="utf-8")
        extract_home.extract(
            task, clean=True, dry_run=False, verbose=False, delete_home=True
        )
        assert not home.exists()
        assert (task / "data" / "a.txt").is_file()

    def test_main_reports_missing_task_dir(self, extract_home, tmp_path):
        # main() over an argv list; a non-existent task dir yields rc 2 (no crash).
        rc = extract_home.main([str(tmp_path / "does_not_exist")])
        assert rc == 2


# =========================================================================== #
# script/verify_migration_dryrun.py + script/verify_applied.py
# =========================================================================== #
# These two do a MODULE-LEVEL `from migrate_to_drift_plane import ...` after
# inserting REPO_ROOT/"scripts" (plural) onto sys.path — but the directory is
# "script" (singular). So importing them in isolation raises ModuleNotFoundError.
# We pin that, then load them with the migrate module pre-seeded to reach the
# handful of pure helpers they define.
class TestVerifyScriptsImportContract:
    def test_verify_applied_import_fails_without_migrate_preloaded(self):
        # NOTE: pins current behavior — the script inserts REPO_ROOT/"scripts"
        # (wrong; dir is "script"), so a cold import can't resolve
        # migrate_to_drift_plane. See SCORING_AUDIT_REPORT.md.
        sys.modules.pop("migrate_to_drift_plane", None)
        with pytest.raises(ModuleNotFoundError):
            _load_script("_t_verify_applied_cold", "verify_applied.py")

    def test_verify_migration_dryrun_import_fails_without_migrate_preloaded(self):
        # NOTE: pins current behavior — same wrong sys.path insert as verify_applied.
        # See SCORING_AUDIT_REPORT.md.
        sys.modules.pop("migrate_to_drift_plane", None)
        with pytest.raises(ModuleNotFoundError):
            _load_script("_t_verify_migration_dryrun_cold", "verify_migration_dryrun.py")


class TestVerifyMigrationDryrunHelpers:
    @pytest.fixture()
    def vd(self, monkeypatch, tmp_path):
        # Pre-seed the bare "migrate_to_drift_plane" name the script imports at module
        # level, then load verify_migration_dryrun against an empty temp ENV_DIR so its
        # module-level `discover_apis()`-free body loads cleanly.
        migrate = _load_script("migrate_to_drift_plane", "migrate_to_drift_plane.py")
        monkeypatch.setattr(migrate, "ENV_DIR", tmp_path)
        vd = _load_script("_t_verify_migration_dryrun_helpers", "verify_migration_dryrun.py")
        monkeypatch.setattr(vd, "ENV_DIR", tmp_path)
        return vd

    def test_verify_one_reports_plan_issue_without_touching_fs(self, vd, tmp_path):
        # A data module with no recognisable stores -> plan issues -> early False.
        api = tmp_path / "empty-api"
        api.mkdir()
        (api / "empty_data.py").write_text("x = 1\n", encoding="utf-8")
        ok, info = vd.verify_one(api)
        assert ok is False
        assert info.startswith("PLAN:")

    def test_verify_one_reports_already_migrated(self, vd, tmp_path):
        api = tmp_path / "done-api"
        api.mkdir()
        (api / "done_data.py").write_text(
            "from _mutable_store import get_store\n", encoding="utf-8"
        )
        ok, info = vd.verify_one(api)
        assert ok is False
        assert "already migrated" in info


class TestVerifyAppliedImportSmoke:
    def test_verify_applied_loads_and_runs_when_migrate_preloaded(self):
        # verify_applied.py has no importable pure functions — its whole body is a
        # module-level scan loop over the repo's real environment/ that even calls
        # sys.exit(1) if any migrated module fails to load. With the migrate module
        # pre-seeded under its bare name, the script loads (import-smoke only) and,
        # against the committed environment/, does not raise SystemExit.
        _load_script("migrate_to_drift_plane", "migrate_to_drift_plane.py")
        mod = _load_script("_t_verify_applied_smoke", "verify_applied.py")
        # data_module_name is the sole symbol it depends on from migrate.
        assert callable(mod.data_module_name)
