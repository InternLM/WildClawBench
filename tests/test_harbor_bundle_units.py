"""Unit coverage for the Harbor bundle-assembly modules.

Covers src/utils/harbor/{bundle,compose,task_toml,dockerfile,solve_sh}.py by
materializing a real bundle from a fake graded-run tree into tmp_path and
asserting the on-disk layout + rendered file contents. Everything runs
offline: no docker, no network, no AWS. The mock-API "environment" is a tiny
2-service fake dir under tmp_path (via config.environment_dir), so we never
touch the real 101-service environment/ tree.

Import bootstrapping mirrors tests/test_docker_env_validation.py (sys.path
insert of the repo root before `from src...`).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.utils.config import Config  # noqa: E402
from src.utils.store import Sandbox, Store, Task  # noqa: E402
from src.utils.harbor import bundle as bundle_mod  # noqa: E402
from src.utils.harbor.bundle import write_bundle  # noqa: E402
from src.utils.harbor.compose import (  # noqa: E402
    _compose_mem,
    _healthcheck_cmd,
    _parse_service_toml,
    _parse_service_toml_fallback,
    discover_services,
    generate_harbor_compose,
    runtime_env_defaults,
)
from src.utils.harbor.dockerfile import (  # noqa: E402
    _AGENT_SKILL_DIRS,
    generate_harbor_dockerfile,
)
from src.utils.harbor.solve_sh import generate_harbor_solve_sh  # noqa: E402
from src.utils.harbor.task_toml import (  # noqa: E402
    _arr_authors,
    _arr_strs,
    _q,
    _truncate_for_description,
    build_task_toml,
)


# --------------------------------------------------------------------------
# Fixtures — tiny fake environment/ tree + a Store + Config
# --------------------------------------------------------------------------

def _write_service_toml(env_dir: Path, name: str, port: int,
                        env_var_name: str, *, mem_limit: str = "256Mi",
                        healthcheck_path: str = "/health") -> None:
    svc = env_dir / name
    svc.mkdir(parents=True, exist_ok=True)
    (svc / "service.toml").write_text(
        f'[service]\n'
        f'name = "{name}"\n'
        f'port = {port}\n'
        f'env_var_name = "{env_var_name}"\n'
        f'healthcheck_path = "{healthcheck_path}"\n'
        f'\n[k8s]\n'
        f'image = ""\n'
        f'cpu_request = "25m"\n'
        f'memory_request = "128Mi"\n'
        f'memory_limit = "{mem_limit}"\n',
        encoding="utf-8",
    )


@pytest.fixture
def fake_env_dir(tmp_path: Path) -> Path:
    """A minimal environment/ dir with two real mock services + skills tree."""
    env_dir = tmp_path / "environment"
    env_dir.mkdir()
    _write_service_toml(env_dir, "orders-api", 8010, "ORDERS_API_URL")
    _write_service_toml(env_dir, "billing-api", 8011, "BILLING_API_URL")
    # A skills/ tree with connectors + multimodal helpers + noise to be filtered
    skills = env_dir / "skills"
    skills.mkdir()
    for sk in (
        "orders-api-connector",
        "billing-api-connector",
        "unrelated-api-connector",
        "video-frames",
        "audio-extract",
    ):
        d = skills / sk
        d.mkdir()
        (d / "SKILL.md").write_text(f"skill {sk}\n", encoding="utf-8")
    (skills / "README.md").write_text("top-level skills readme\n", encoding="utf-8")
    # A top-level KEEP file + a persona dir.
    (env_dir / "API_DOCUMENTATION.md").write_text("docs\n", encoding="utf-8")
    persona = env_dir / "persona"
    persona.mkdir()
    (persona / "MEMORY.md").write_text("persona memory\n", encoding="utf-8")
    return env_dir


@pytest.fixture
def store(tmp_path: Path) -> Store:
    s = Store(tmp_path / "state.db")
    yield s
    s.close()


@pytest.fixture
def config(fake_env_dir: Path, tmp_path: Path) -> Config:
    return Config(environment_dir=fake_env_dir, output_dir=tmp_path / "out")


def _make_task(**overrides) -> Task:
    base = dict(
        id="pk-1",
        task_id="alden_croft_01",
        persona="",
        initial_prompt="Reconcile the orders-api ledger against billing-api.",
        rubrics_json=json.dumps([
            {"label": "Posted the refund", "is_positive": True, "score": 3},
            {"criterion": "No duplicate charge", "is_positive": False,
             "type": "guardrail", "importance": "critical", "score": -5},
            "not-a-dict-row",  # exercised skip branch
        ]),
        test_code="def test_ok():\n    assert True\n",
        test_weights=json.dumps({"test_ok": 5}),
        task_type="finance",
        difficulty="hard",
        l1="reconciliation",
        l2="ledger",
        extra={"required_apis": ["orders-api", "billing-api"],
               "distractor_apis": []},
    )
    base.update(overrides)
    return Task(**base)


# ==========================================================================
# task_toml.py
# ==========================================================================

class TestTaskTomlHelpers:
    def test_q_escapes_backslash_quote_newline(self):
        assert _q('a"b') == '"a\\"b"'
        assert _q("c\\d") == '"c\\\\d"'
        # newline collapses to a space
        assert _q("e\nf") == '"e f"'

    def test_q_none_becomes_empty_string(self):
        assert _q(None) == '""'

    def test_q_coerces_non_string(self):
        assert _q(42) == '"42"'

    def test_arr_strs_empty(self):
        assert _arr_strs([]) == "[]"

    def test_arr_strs_multi(self):
        assert _arr_strs(["a", "b"]) == '["a", "b"]'

    def test_arr_authors_empty(self):
        assert _arr_authors([]) == "[]"

    def test_arr_authors_maps_name(self):
        out = _arr_authors([{"name": "Ada"}, {"name": "Bo"}])
        assert out == '[{ name = "Ada" }, { name = "Bo" }]'

    def test_arr_authors_non_mapping_stringified(self):
        # a plain string author -> str(a) is used as the name
        out = _arr_authors(["Solo"])
        assert out == '[{ name = "Solo" }]'

    def test_truncate_collapses_newlines(self):
        assert _truncate_for_description("a\r\nb\nc\rd") == "a b c d"

    def test_truncate_respects_limit_with_ellipsis(self):
        out = _truncate_for_description("abcdef", limit=4)
        assert out == "abc…"
        assert len(out) == 4

    def test_truncate_none_input(self):
        assert _truncate_for_description(None) == ""


class TestBuildTaskToml:
    def test_section_order_is_strict(self):
        task = _make_task()
        toml = build_task_toml(
            task, required_skills=["orders-api-connector"],
            distractor_skills=[],
        )
        order = [
            "[task]", "[metadata]", "[verifier]", "[verifier.env]",
            "[agent]", "[environment]", "[environment.env]",
            "[environment.healthcheck]", "[solution.env]",
            "[multimodal]", "[evaluation]", "[dimensions]",
        ]
        positions = [toml.index(sec) for sec in order]
        assert positions == sorted(positions), "section order not strictly increasing"

    def test_schema_version_and_name_wiring(self):
        task = _make_task()
        toml = build_task_toml(task, [], [])
        assert 'schema_version = "1.1"' in toml
        assert 'name = "alden_croft_01"' in toml
        assert 'task_id = "alden_croft_01"' in toml
        assert 'category = "finance"' in toml
        assert 'difficulty = "hard"' in toml

    def test_keywords_from_task_type_and_difficulty(self):
        task = _make_task()
        toml = build_task_toml(task, [], [])
        assert 'keywords = ["finance", "hard"]' in toml

    def test_name_falls_back_to_id_then_default(self):
        # task_id empty -> id used
        t = _make_task(task_id="", id="pk-x")
        toml = build_task_toml(t, [], [])
        assert 'name = "pk-x"' in toml
        # both empty -> literal default
        t2 = _make_task(task_id="", id="")
        toml2 = build_task_toml(t2, [], [])
        assert 'name = "kensei2-task"' in toml2

    def test_env_vars_rendered_in_sections(self):
        task = _make_task()
        toml = build_task_toml(
            task, [], [],
            env_vars={"ORDERS_API_URL": "http://orders-api:8010"},
            verifier_env={"TEST_DIR": "/tests"},
            solution_env={"FOO": "bar"},
        )
        assert "ORDERS_API_URL = \"http://orders-api:8010\"" in toml
        assert 'TEST_DIR = "/tests"' in toml
        assert 'FOO = "bar"' in toml

    def test_pass_at_k_override_and_default(self):
        task = _make_task()
        assert "pass_at_k = 4" in build_task_toml(task, [], [], pass_at_k=4)
        # default is 8
        assert "pass_at_k = 8" in build_task_toml(task, [], [])
        # 0 falls back to default (int(0 or default))
        assert "pass_at_k = 8" in build_task_toml(task, [], [], pass_at_k=0)

    def test_healthcheck_command_override_and_default(self):
        task = _make_task()
        toml = build_task_toml(task, [], [], healthcheck_command="curl -f http://x/health")
        assert 'command = "curl -f http://x/health"' in toml
        toml_def = build_task_toml(task, [], [])
        assert 'command = "curl -f http://localhost:8000/health"' in toml_def

    def test_optional_metadata_lines_conditional(self):
        task = _make_task()
        # trajectory_modifier + safety_critical (non-N/A) emitted
        toml = build_task_toml(
            task, [], [], trajectory_modifier="mod-x", safety_critical="high",
        )
        assert 'trajectory_modifier = "mod-x"' in toml
        assert 'safety_critical = "high"' in toml
        # N/A safety_critical suppressed
        toml2 = build_task_toml(task, [], [], safety_critical="N/A")
        assert "safety_critical" not in toml2

    def test_dimensions_default_and_multimodal_override(self):
        task = _make_task()
        toml = build_task_toml(task, [], [], dimensions={"multimodal": "true"})
        assert 'multimodal = "true"' in toml
        assert 'objective = "true"' in toml  # default carried through

    def test_dependency_tags_rendered(self):
        task = _make_task()
        toml = build_task_toml(task, [], [], dependency_tags=["a", "b"])
        assert 'dependency_tags = ["a", "b"]' in toml

    def test_required_and_distractor_skills_rendered(self):
        task = _make_task()
        toml = build_task_toml(
            task, ["orders-api-connector"], ["noise-api-connector"],
        )
        assert 'required_skills = ["orders-api-connector"]' in toml
        assert 'distractor_skills = ["noise-api-connector"]' in toml


# ==========================================================================
# compose.py
# ==========================================================================

class TestComposeHelpers:
    def test_runtime_env_defaults_keys(self):
        env = runtime_env_defaults()
        assert env["LITELLM_BASE_URL"] == "http://litellm-proxy:4000"
        assert env["OPENAI_API_BASE"] == "http://litellm-proxy:4000/v1"
        assert env["OPENAI_API_KEY"] == "placeholder"
        assert env["CURRENT_DATE"] == "2026-05-28"
        # secret must NOT be present here
        assert "LLAMA_API_KEY" not in env

    def test_compose_mem_strips_k8s_binary_suffix(self):
        assert _compose_mem("256Mi") == "256M"
        assert _compose_mem("1Gi") == "1G"
        assert _compose_mem("512Ki") == "512K"
        # bare compose suffix passes through unchanged
        assert _compose_mem("256M") == "256M"
        assert _compose_mem(" 128M ") == "128M"

    def test_healthcheck_cmd_embeds_port_and_path(self):
        cmd = _healthcheck_cmd(8010, "/health")
        assert "http://localhost:8010/health" in cmd
        assert "urllib.request.urlopen" in cmd
        assert "timeout=3" in cmd

    def test_parse_service_toml_reads_fields(self, fake_env_dir):
        svc = _parse_service_toml(fake_env_dir / "orders-api" / "service.toml")
        assert svc["name"] == "orders-api"
        assert svc["port"] == 8010
        assert svc["env_var_name"] == "ORDERS_API_URL"
        assert svc["memory_limit"] == "256Mi"

    def test_parse_service_toml_fallback_parses_sections(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text(
            "# comment\n"
            "[service]\n"
            'name = "widget-api"\n'
            "port = 8099\n"
            'env_var_name = "WIDGET_API_URL"\n'
            'healthcheck_path = "/ping"\n'
            "[k8s]\n"
            'image = "img:1"\n'
            'memory_limit = "512Mi"\n',
            encoding="utf-8",
        )
        d = _parse_service_toml_fallback(p)
        assert d["name"] == "widget-api"
        assert d["port"] == 8099
        assert d["env_var_name"] == "WIDGET_API_URL"
        assert d["healthcheck_path"] == "/ping"
        assert d["k8s_image"] == "img:1"
        assert d["memory_limit"] == "512Mi"

    def test_parse_service_toml_fallback_missing_file(self, tmp_path):
        d = _parse_service_toml_fallback(tmp_path / "nope.toml")
        # returns the defaults, name from parent dir
        assert d["port"] == 8000
        assert d["healthcheck_path"] == "/health"

    def test_parse_service_toml_fallback_bad_port_ignored(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text('[service]\nport = notanumber\n', encoding="utf-8")
        d = _parse_service_toml_fallback(p)
        assert d["port"] == 8000  # default retained on ValueError

    def test_discover_services_sorted(self, fake_env_dir):
        svcs = discover_services(fake_env_dir)
        names = [s["name"] for s in svcs]
        assert names == ["billing-api", "orders-api"]  # sorted, skills/ has no service.toml

    def test_discover_services_missing_dir(self, tmp_path):
        assert discover_services(tmp_path / "does-not-exist") == []


class TestGenerateCompose:
    def test_main_service_block_and_depends_on(self, fake_env_dir):
        yaml = generate_harbor_compose(fake_env_dir)
        assert yaml.startswith("services:\n")
        assert "  main:\n" in yaml
        assert 'command: ["sleep", "infinity"]' in yaml
        assert "image: harbor-main:local" in yaml
        # depends_on lists both services as healthy gates
        assert "billing-api:\n        condition: service_healthy" in yaml
        assert "orders-api:\n        condition: service_healthy" in yaml
        # runtime env + secret substitution
        assert "LITELLM_BASE_URL=http://litellm-proxy:4000" in yaml
        assert "LLAMA_API_KEY=${LLAMA_API_KEY}" in yaml
        assert "TEST_DIR=${TEST_DIR:-/tests}" in yaml

    def test_env_vars_default_from_services(self, fake_env_dir):
        yaml = generate_harbor_compose(fake_env_dir)
        assert "ORDERS_API_URL=http://orders-api:8010" in yaml
        assert "BILLING_API_URL=http://billing-api:8011" in yaml

    def test_explicit_env_vars_override(self, fake_env_dir):
        yaml = generate_harbor_compose(
            fake_env_dir, env_vars={"CUSTOM_URL": "http://c:1"},
        )
        assert "CUSTOM_URL=http://c:1" in yaml
        # default derivation suppressed when env_vars supplied
        assert "ORDERS_API_URL=http://orders-api:8010" not in yaml

    def test_per_service_healthcheck_and_mem_limit(self, fake_env_dir):
        yaml = generate_harbor_compose(fake_env_dir)
        assert "  orders-api:\n" in yaml
        assert "context: ./orders-api" in yaml
        assert "image: harbor-orders-api:local" in yaml
        assert 'expose:\n      - "8010"' in yaml
        assert "http://localhost:8010/health" in yaml
        # k8s Mi suffix -> M
        assert "memory: 256M" in yaml

    def test_no_services_no_depends_on(self, tmp_path):
        empty_env = tmp_path / "empty"
        empty_env.mkdir()
        yaml = generate_harbor_compose(empty_env, services=[])
        assert "depends_on" not in yaml
        assert yaml.rstrip().endswith("memory: \"${MEMORY:-4096M}\"")

    def test_trailing_newline(self, fake_env_dir):
        assert generate_harbor_compose(fake_env_dir).endswith("\n")


# ==========================================================================
# dockerfile.py
# ==========================================================================

class TestDockerfile:
    def test_base_image_and_apt_packages(self):
        df = generate_harbor_dockerfile()
        assert df.startswith("FROM ubuntu:24.04")
        for pkg in ("curl", "jq", "python3", "ffmpeg", "poppler-utils"):
            assert pkg in df
        assert "pip install --no-cache-dir --break-system-packages pymupdf pillow" in df
        assert df.rstrip().endswith("WORKDIR /app")

    def test_no_conditional_copies_by_default(self):
        df = generate_harbor_dockerfile()
        assert "COPY skills" not in df
        assert "COPY persona" not in df
        assert "COPY artifacts" not in df

    def test_skills_copy_fans_out_to_all_agent_dirs(self):
        df = generate_harbor_dockerfile(has_skills=True)
        first, *rest = _AGENT_SKILL_DIRS
        assert "COPY skills %s" % first in df
        # a single mkdir + cp fan-out RUN line covers the remaining dirs
        for d in rest:
            assert d in df
        assert "cp -a %s/. " % first in df

    def test_persona_copy_conditional(self):
        df = generate_harbor_dockerfile(has_persona=True)
        assert "COPY persona /root/.openclaw/persona" in df

    def test_artifacts_copy_conditional(self):
        df = generate_harbor_dockerfile(has_artifacts=True)
        assert "COPY artifacts/inputs/files /app/artifacts/inputs/files" in df


# ==========================================================================
# solve_sh.py
# ==========================================================================

class TestSolveSh:
    def test_no_env_vars_placeholder_only(self):
        sh = generate_harbor_solve_sh()
        assert sh.startswith("#!/usr/bin/env bash")
        assert "Solution not yet implemented" in sh
        assert sh.endswith("PY\n")
        assert "os.environ.get" not in sh

    def test_env_vars_emitted_sorted_lowercased(self):
        sh = generate_harbor_solve_sh({
            "ZED_API_URL": "http://zed:2",
            "ALPHA_API_URL": "http://alpha:1",
        })
        # sorted by KEY -> alpha before zed
        i_alpha = sh.index("alpha_api_url = os.environ.get('ALPHA_API_URL'")
        i_zed = sh.index("zed_api_url = os.environ.get('ZED_API_URL'")
        assert i_alpha < i_zed
        assert ".rstrip('/')" in sh

    def test_trailing_newline(self):
        assert generate_harbor_solve_sh({"X_URL": "http://x"}).endswith("\n")


# ==========================================================================
# bundle.py — full assembly into tmp_path
# ==========================================================================

def _read_json(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


class TestWriteBundleLayout:
    def test_full_bundle_layout_written(self, tmp_path, store, config):
        task = _make_task(
            golden_trajectory=json.dumps([{"role": "assistant", "content": "hi"}]),
        )
        out_dir = tmp_path / "bundle"
        manifest = write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"session_id": "s1"}]},
            pass_at_k=4,
        )

        # top-level files
        assert (out_dir / "prompt.txt").read_text() == task.initial_prompt
        assert (out_dir / "rubric.json").is_file()
        assert (out_dir / "golden_trajectory.json").is_file()

        data = out_dir / "data"
        assert (data / "instruction.md").read_text() == task.initial_prompt
        assert (data / "task.toml").is_file()
        assert (data / "tests" / "test.sh").is_file()
        assert (data / "tests" / "test_outputs.py").read_text() == task.test_code
        assert (data / "tests" / "test_weights.json").read_text() == task.test_weights
        assert (data / "solution" / "solve.sh").is_file()

        env_out = data / "environment"
        assert (env_out / "Dockerfile").is_file()
        assert (env_out / "docker-compose.yaml").is_file()
        # both required services copied verbatim
        assert (env_out / "orders-api" / "service.toml").is_file()
        assert (env_out / "billing-api" / "service.toml").is_file()

        # manifest
        assert manifest["out_dir"] == str(out_dir)
        assert manifest["models"] == ["claude"]
        assert set(manifest["required_skills"]) == {
            "orders-api-connector", "billing-api-connector",
        }
        assert manifest["distractor_skills"] == []

    def test_rubric_transform_shape(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        rubric = _read_json(out_dir / "rubric.json")
        # 2 dict rows kept, the bare string row dropped
        assert len(rubric) == 2
        assert rubric[0]["criterion"] == "Posted the refund"
        assert rubric[0]["is_positive"] is True
        assert rubric[0]["number"] == "R1"
        assert rubric[1]["criterion"] == "No duplicate charge"
        assert rubric[1]["is_positive"] is False
        assert rubric[1]["number"] == "R2"

    def test_golden_trajectory_first_entry_only(self, tmp_path, store, config):
        task = _make_task(
            golden_trajectory=json.dumps([{"n": 1}, {"n": 2}]),
        )
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        doc = _read_json(out_dir / "golden_trajectory.json")
        assert doc == {"n": 1}

    def test_golden_trajectory_empty_when_absent(self, tmp_path, store, config):
        task = _make_task(golden_trajectory="")
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        assert _read_json(out_dir / "golden_trajectory.json") == {}

    def test_skills_filtered_to_required_plus_multimodal(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        skills = out_dir / "data" / "environment" / "skills"
        kept = {p.name for p in skills.iterdir() if p.is_dir()}
        assert "orders-api-connector" in kept
        assert "billing-api-connector" in kept
        assert "video-frames" in kept
        assert "audio-extract" in kept
        # unrelated connector filtered out
        assert "unrelated-api-connector" not in kept
        # top-level non-dir files inside skills/ are copied verbatim
        assert (skills / "README.md").is_file()

    def test_persona_kept_via_keep_top_level(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        env_out = out_dir / "data" / "environment"
        assert (env_out / "persona" / "MEMORY.md").is_file()
        # Dockerfile picks up persona presence
        df = (env_out / "Dockerfile").read_text()
        assert "COPY persona" in df

    def test_task_toml_has_required_skills_wired(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        toml = (out_dir / "data" / "task.toml").read_text()
        assert "orders-api-connector" in toml
        assert "billing-api-connector" in toml
        # per-service healthcheck chained
        assert "curl -f http://localhost:8010/health" in toml
        assert "curl -f http://localhost:8011/health" in toml

    def test_empty_test_weights_defaults_to_brace(self, tmp_path, store, config):
        task = _make_task(test_weights="")
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        assert (out_dir / "data" / "tests" / "test_weights.json").read_text() == "{}"


class TestWriteBundleTrajectories:
    def test_run_index_honored_over_enumerate(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        # explicit __run_index__ = 3 should place output at run_3, not run_1
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"__run_index__": 3, "sid": "x"}]},
        )
        run_dir = out_dir / "trajectories" / "claude" / "run_3"
        assert (run_dir / "output.json").is_file()
        assert not (out_dir / "trajectories" / "claude" / "run_1").exists()
        # internal keys stripped from output.json; the entry is normalized
        # into the published-trajectory shape (messages + meta_info) by
        # build_published_trajectory rather than copied through raw.
        out = _read_json(run_dir / "output.json")
        assert "__run_index__" not in out
        assert "sid" not in out
        assert "messages" in out and "meta_info" in out

    def test_verifier_files_from_pytest_result(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        tr = {
            "tests_total": 2,
            "tests_passed": 2,
            "tests_failed": 0,
            "test_scores": json.dumps({"test_ok": "passed", "test_two": "passed"}),
        }
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"__test_result__": tr}]},
        )
        vdir = out_dir / "trajectories" / "claude" / "run_1" / "task_output" / "logs" / "verifier"
        reward = float((vdir / "reward.txt").read_text().strip())
        # test_weights = {"test_ok": 5}; test_ok passed -> full reward 1.0
        assert reward == pytest.approx(1.0)
        ctrf = _read_json(vdir / "ctrf.json")
        assert ctrf["results"]["summary"]["overall_score"] == pytest.approx(1.0)
        assert (vdir / "test_weights.json").is_file()
        assert (vdir / "test_outputs.py").is_file()

    def test_rubric_only_falls_back_to_canonical_reward(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        # No test_scores => fall back to canonical_reward (rubric grade)
        tr = {"canonical_reward": 0.8378}
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"__test_result__": tr}]},
        )
        vdir = out_dir / "trajectories" / "claude" / "run_1" / "task_output" / "logs" / "verifier"
        reward = float((vdir / "reward.txt").read_text().strip())
        assert reward == pytest.approx(0.8378)

    def test_pass_summary_average(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [
                {"__run_index__": 1,
                 "__test_result__": {"tests_total": 1, "tests_passed": 1,
                                     "test_scores": json.dumps({"test_ok": "passed"})}},
                {"__run_index__": 2,
                 "__test_result__": {"tests_total": 1, "tests_passed": 0,
                                     "test_scores": json.dumps({"test_ok": "failed"})}},
            ]},
        )
        summary = _read_json(
            out_dir / "trajectories" / "claude" / "pass_summary.json"
        )
        assert summary["runs"] == 2
        # rewards 1.0 and 0.0 -> average 0.5
        assert summary["average_reward"] == pytest.approx(0.5)
        assert summary["model"] == "claude"

    def test_run_index_above_8_skips_verifier_dir(self, tmp_path, store, config):
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [
                {"__run_index__": 9,
                 "__test_result__": {"tests_total": 1, "tests_passed": 1,
                                     "test_scores": json.dumps({"test_ok": "passed"})}},
            ]},
        )
        run_dir = out_dir / "trajectories" / "claude" / "run_9"
        assert (run_dir / "output.json").is_file()
        # verifier dir only written for run_index <= 8
        assert not (run_dir / "task_output").exists()

    def test_trajectories_fall_back_to_task_extra(self, tmp_path, store, config):
        task = _make_task(
            extra={
                "required_apis": ["orders-api", "billing-api"],
                "distractor_apis": [],
                "claude_trajectory": json.dumps([{"from": "extra"}]),
            },
        )
        out_dir = tmp_path / "b"
        # trajectories_by_model omitted -> writer reads task.extra[<model>_trajectory]
        manifest = write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
        )
        assert manifest["models"] == ["claude"]
        out = _read_json(
            out_dir / "trajectories" / "claude" / "run_1" / "output.json"
        )
        # Normalized into the published-trajectory shape (messages + meta_info),
        # not the raw task.extra entry.
        assert "messages" in out and "meta_info" in out


class TestWriteBundleDiscoveryFallback:
    def test_prompt_keyword_discovery_when_extra_absent(self, tmp_path, config, store, monkeypatch):
        """When Task.extra carries no required/distractor lists, write_bundle
        discovers APIs via _discover_used_apis + compute_distractor_skills.
        Patch those two so the test stays independent of the real inference
        catalog."""
        monkeypatch.setattr(
            bundle_mod, "infer_required_apis", lambda *a, **k: ["orders-api"],
        )
        monkeypatch.setattr(
            bundle_mod, "compute_distractor_skills", lambda *a, **k: ["billing-api"],
        )
        task = _make_task(extra={})  # no required/distractor keys
        out_dir = tmp_path / "b"
        manifest = write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
        )
        # orders-api discovered as required; billing-api as distractor
        assert "orders-api-connector" in manifest["required_skills"]
        assert manifest["distractor_skills"] == ["billing-api-connector"]

    def test_mock_data_overlays_from_task_dir(self, tmp_path, store, config):
        """Overlay files under <task_dir>/mock_data/<api>/ get copied into the
        bundle environment dir."""
        task_dir = tmp_path / "input" / "alden"
        overlay = task_dir / "mock_data" / "orders-api"
        overlay.mkdir(parents=True)
        (overlay / "seed.json").write_text('{"seeded": true}', encoding="utf-8")
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            task_dir=task_dir,
        )
        copied = out_dir / "data" / "environment" / "orders-api" / "seed.json"
        assert copied.is_file()
        assert _read_json(copied) == {"seeded": True}

    def test_no_required_apis_copies_full_environment(self, tmp_path, store, config):
        """When required+distractor resolve to the empty set, the whole
        environment/ tree is copied verbatim (skills still filtered)."""
        task = _make_task(extra={"required_apis": [], "distractor_apis": []})
        out_dir = tmp_path / "b"
        write_bundle(task=task, out_dir=out_dir, store=store, config=config)
        env_out = out_dir / "data" / "environment"
        # both services copied even though none were "required"
        assert (env_out / "orders-api" / "service.toml").is_file()
        assert (env_out / "billing-api" / "service.toml").is_file()
        # top-level keep file present
        assert (env_out / "API_DOCUMENTATION.md").is_file()

    def test_task_dir_tests_and_solution_subdirs_copied(self, tmp_path, store, config):
        """<task_dir>/tests/** and <task_dir>/solution/** are merged into
        data/tests and data/solution, skipping dotfiles."""
        task_dir = tmp_path / "input" / "alden"
        (task_dir / "tests").mkdir(parents=True)
        (task_dir / "tests" / "helper.py").write_text("# helper\n", encoding="utf-8")
        (task_dir / "tests" / "fixtures").mkdir()
        (task_dir / "tests" / "fixtures" / "data.txt").write_text("x", encoding="utf-8")
        (task_dir / "tests" / ".hidden").write_text("skip me", encoding="utf-8")
        (task_dir / "solution").mkdir()
        (task_dir / "solution" / "notes.md").write_text("notes", encoding="utf-8")
        task = _make_task()
        out_dir = tmp_path / "b"
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            task_dir=task_dir,
        )
        data = out_dir / "data"
        assert (data / "tests" / "helper.py").is_file()
        assert (data / "tests" / "fixtures" / "data.txt").is_file()
        assert not (data / "tests" / ".hidden").exists()  # dotfile skipped
        assert (data / "solution" / "notes.md").is_file()

    def test_malformed_test_scores_falls_back(self, tmp_path, store, config):
        """A non-JSON test_scores blob must not raise; has_pytest_results is
        False so the run falls back to canonical_reward."""
        task = _make_task()
        out_dir = tmp_path / "b"
        tr = {"test_scores": "{not valid json", "canonical_reward": 0.42}
        write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"__test_result__": tr}]},
        )
        vdir = out_dir / "trajectories" / "claude" / "run_1" / "task_output" / "logs" / "verifier"
        reward = float((vdir / "reward.txt").read_text().strip())
        assert reward == pytest.approx(0.42)


class TestWriteBundleStoreResults:
    def test_store_test_results_are_read_numeric_sandbox_id(self, tmp_path, store, config):
        """When the store holds sandbox+test_result rows keyed by a numeric-
        string sandbox id, write_bundle reads them without error
        (store.list_test_results path + int(sid) coercion)."""
        task = _make_task()
        store.upsert_task(task)
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        # bundle.py:383 does int(sandbox_id); only numeric-string ids survive.
        store.upsert_sandbox(
            Sandbox(id="42", task_pk=task.id, model_type="claude", run_index=1),
        )
        store.insert_test_result(
            "42", "claude", 0,
            {"status": "passed", "tests_total": 1, "tests_passed": 1,
             "test_scores": {"test_ok": "passed"}},
        )
        out_dir = tmp_path / "b"
        # Should complete and read the stored results without raising.
        manifest = write_bundle(
            task=task, out_dir=out_dir, store=store, config=config,
            trajectories_by_model={"claude": [{"sid": "x"}]},
        )
        assert (out_dir / "data" / "task.toml").is_file()
        assert manifest["models"] == ["claude"]

    def test_non_numeric_sandbox_id_raises_value_error(self, tmp_path, store, config):
        """NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        sandbox.id is a TEXT column, but bundle.py:383 coerces it with
        int(sid). A non-numeric id (the real default, e.g. a uuid/'sb-1')
        makes write_bundle raise ValueError instead of skipping the row."""
        task = _make_task()
        store.upsert_task(task)
        store.upsert_sandbox(
            Sandbox(id="sb-1", task_pk=task.id, model_type="claude", run_index=1),
        )
        store.insert_test_result(
            "sb-1", "claude", 0,
            {"status": "passed", "tests_total": 1, "tests_passed": 1},
        )
        out_dir = tmp_path / "b"
        with pytest.raises(ValueError):
            write_bundle(
                task=task, out_dir=out_dir, store=store, config=config,
                trajectories_by_model={"claude": [{"sid": "x"}]},
            )

    def test_store_list_results_exception_is_swallowed(self, tmp_path, config):
        """A store whose list_test_results raises must not break bundling."""
        class _BoomStore:
            def list_test_results(self, _pk):
                raise RuntimeError("db gone")
        task = _make_task()
        out_dir = tmp_path / "b"
        manifest = write_bundle(
            task=task, out_dir=out_dir, store=_BoomStore(), config=config,
            trajectories_by_model={"claude": [{"sid": "x"}]},
        )
        assert (out_dir / "prompt.txt").is_file()
        assert manifest["models"] == ["claude"]
