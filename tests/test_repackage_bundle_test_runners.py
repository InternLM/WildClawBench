"""Invariant tests pinning the 4-file emission contract added to
script/repackage_to_bundle.py:

    bundle/data/tests/test_outputs.py     (copied from input/<task>/)
    bundle/data/tests/test_weights.json   (copied from input/<task>/)
    bundle/data/tests/test.sh             (generated, verbatim Harbor template)
    bundle/data/solution/solve.sh         (generated from discovered env_vars)

These were silently lost during the b1 refactor that routed auto-bundle through
the standalone stdlib script. Restored 2026-06-27 per user request: "Combine
both paths to make sure everything is fulfilled and add it to bundle.py file."

The tests are static (no docker, no network). They cover:
  1. test.sh byte-equal with src/utils/harbor/test_sh.py::_TEST_SH.
  2. solve.sh byte-equal with src/utils/harbor/solve_sh.py::generate_harbor_solve_sh.
  3. End-to-end convert_task emits all 4 files in canonical paths.
  4. solve.sh contains one os.environ.get per discovered service env_var.
  5. test_outputs.py / test_weights.json sources are at input/<task>/ ROOT
     (NOT under data/tests/) - this matches src/utils/task_parser.py loading.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_repackage_module():
    spec = importlib.util.spec_from_file_location(
        "_rp_test", REPO_ROOT / "script" / "repackage_to_bundle.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_harbor_test_sh():
    sys.path.insert(0, str(REPO_ROOT / "src" / "utils" / "harbor"))
    try:
        from test_sh import generate_harbor_test_sh
        return generate_harbor_test_sh
    finally:
        sys.path.pop(0)


def _load_harbor_solve_sh():
    sys.path.insert(0, str(REPO_ROOT / "src" / "utils" / "harbor"))
    try:
        from solve_sh import generate_harbor_solve_sh
        return generate_harbor_solve_sh
    finally:
        sys.path.pop(0)


def test_test_sh_byte_equal_with_harbor():
    rp = _load_repackage_module()
    harbor = _load_harbor_test_sh()
    assert rp._generate_test_sh() == harbor(), (
        "test.sh has drifted from src/utils/harbor/test_sh.py::_TEST_SH. "
        "Both must stay byte-equal; update both files together."
    )


def test_solve_sh_byte_equal_with_harbor_empty():
    rp = _load_repackage_module()
    harbor = _load_harbor_solve_sh()
    assert rp._generate_solve_sh({}) == harbor({})
    assert rp._generate_solve_sh(None) == harbor(None)


def test_solve_sh_byte_equal_with_harbor_populated():
    rp = _load_repackage_module()
    harbor = _load_harbor_solve_sh()
    env_vars = {
        "GMAIL_API_URL": "http://gmail-api:8017",
        "XERO_API_URL": "http://xero-api:8088",
        "QUICKBOOKS_API_URL": "http://quickbooks-api:8041",
    }
    assert rp._generate_solve_sh(env_vars) == harbor(env_vars)


def _stage_minimal_task(tmp_path: Path, task_id: str = "ben_cox_8fc24d4b") -> tuple[Path, Path, Path]:
    src_root = tmp_path / "output_root"
    dst_root = tmp_path / "dest_root"
    inp_root = tmp_path / "input_root"
    task_src = src_root / task_id
    task_inp = inp_root / task_id

    (task_src / "trajectories" / "claude" / "run_1").mkdir(parents=True)
    (task_src / "trajectories" / "claude" / "run_1" / "output.json").write_text("{}")
    (task_src / "rubric.json").write_text('{"criteria": []}')

    env_dir = task_src / "data" / "environment"
    (env_dir / "gmail-api").mkdir(parents=True)
    (env_dir / "gmail-api" / "service.toml").write_text(
        '[service]\nname = "gmail-api"\nport = 8017\nenv_var_name = "GMAIL_API_URL"\n'
    )
    (env_dir / "xero-api").mkdir(parents=True)
    (env_dir / "xero-api" / "service.toml").write_text(
        '[service]\nname = "xero-api"\nport = 8088\nenv_var_name = "XERO_API_URL"\n'
    )

    task_inp.mkdir(parents=True)
    (task_inp / "prompt.txt").write_text("dummy prompt\n")
    (task_inp / "test_outputs.py").write_text(
        "import pytest\n\nclass TestFoo:\n    def test_bar(self):\n        assert True\n"
    )
    (task_inp / "test_weights.json").write_text(json.dumps({"test_bar": 5}))

    return src_root, dst_root, inp_root


def test_convert_task_emits_all_four_files(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None, "convert_task returned None"

    test_outputs = bundle / "data" / "tests" / "test_outputs.py"
    test_weights = bundle / "data" / "tests" / "test_weights.json"
    test_sh = bundle / "data" / "tests" / "test.sh"
    solve_sh = bundle / "data" / "solution" / "solve.sh"

    assert test_outputs.is_file(), f"missing {test_outputs}"
    assert test_weights.is_file(), f"missing {test_weights}"
    assert test_sh.is_file(), f"missing {test_sh}"
    assert solve_sh.is_file(), f"missing {solve_sh}"


def test_convert_task_test_outputs_source_is_input_root(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    src_text = (inp_root / task_id / "test_outputs.py").read_text()
    src_weights = (inp_root / task_id / "test_weights.json").read_text()

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None

    assert (bundle / "data" / "tests" / "test_outputs.py").read_text() == src_text
    assert (bundle / "data" / "tests" / "test_weights.json").read_text() == src_weights


def test_convert_task_accepts_legacy_test_output_singular_filename(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    canonical = inp_root / task_id / "test_outputs.py"
    legacy = inp_root / task_id / "test_output.py"
    legacy_content = canonical.read_text()
    canonical.unlink()
    legacy.write_text(legacy_content)

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None
    dst = bundle / "data" / "tests" / "test_outputs.py"
    assert dst.is_file(), (
        "legacy singular-typo test_output.py at input root must still produce "
        "canonical bundle/data/tests/test_outputs.py (mirrors task_parser.py:190 "
        "which accepts both names)"
    )
    assert dst.read_text() == legacy_content


def test_resolve_test_outputs_source_prefers_canonical_when_both_present(tmp_path):
    rp = _load_repackage_module()
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    (task_dir / "test_outputs.py").write_text("# canonical")
    (task_dir / "test_output.py").write_text("# legacy")
    resolved = rp._resolve_test_outputs_source(task_dir)
    assert resolved is not None
    assert resolved.name == "test_outputs.py"
    assert resolved.read_text() == "# canonical"


def test_resolve_test_outputs_source_falls_back_to_legacy(tmp_path):
    rp = _load_repackage_module()
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    (task_dir / "test_output.py").write_text("# legacy only")
    resolved = rp._resolve_test_outputs_source(task_dir)
    assert resolved is not None
    assert resolved.name == "test_output.py"


def test_resolve_test_outputs_source_returns_none_when_absent(tmp_path):
    rp = _load_repackage_module()
    task_dir = tmp_path / "task"
    task_dir.mkdir()
    assert rp._resolve_test_outputs_source(task_dir) is None


def test_solve_sh_references_discovered_env_vars(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    solve = (bundle / "data" / "solution" / "solve.sh").read_text()
    assert "GMAIL_API_URL" in solve
    assert "XERO_API_URL" in solve
    assert "http://gmail-api:8017" in solve
    assert "http://xero-api:8088" in solve


def test_test_sh_and_solve_sh_emit_even_when_input_root_missing(tmp_path):
    rp = _load_repackage_module()
    src_root = tmp_path / "src"
    dst_root = tmp_path / "dst"
    inp_root = tmp_path / "input_does_not_match"
    inp_root.mkdir()

    task_id = "orphan_task_001"
    task_src = src_root / task_id
    (task_src / "trajectories" / "claude" / "run_1").mkdir(parents=True)
    (task_src / "trajectories" / "claude" / "run_1" / "output.json").write_text("{}")
    (task_src / "rubric.json").write_text('{"criteria": []}')

    bundle = rp.convert_task(
        task_dir=task_src,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None
    assert (bundle / "data" / "tests" / "test.sh").is_file(), (
        "test.sh must emit unconditionally (no input dir dependency)"
    )
    assert (bundle / "data" / "solution" / "solve.sh").is_file(), (
        "solve.sh must emit unconditionally (no input dir dependency)"
    )
    assert not (bundle / "data" / "tests" / "test_outputs.py").exists(), (
        "test_outputs.py must NOT emit when input/<task>/ is unmatched"
    )
    assert not (bundle / "data" / "tests" / "test_weights.json").exists(), (
        "test_weights.json must NOT emit when input/<task>/ is unmatched"
    )


def test_discover_service_env_vars_returns_dict(tmp_path):
    rp = _load_repackage_module()
    env_dir = tmp_path / "environment"
    (env_dir / "alpha").mkdir(parents=True)
    (env_dir / "alpha" / "service.toml").write_text(
        '[service]\nname = "alpha"\nport = 9000\nenv_var_name = "ALPHA_URL"\n'
    )
    (env_dir / "beta-svc").mkdir(parents=True)
    (env_dir / "beta-svc" / "service.toml").write_text(
        '[service]\nname = "beta-svc"\nport = 9001\nenv_var_name = "BETA_URL"\n'
    )
    out = rp._discover_service_env_vars(env_dir)
    assert out == {
        "ALPHA_URL": "http://alpha:9000",
        "BETA_URL": "http://beta-svc:9001",
    }


def test_discover_service_env_vars_respects_enabled_filter(tmp_path):
    rp = _load_repackage_module()
    env_dir = tmp_path / "environment"
    for n, p, v in [("alpha", 9000, "ALPHA_URL"), ("beta", 9001, "BETA_URL")]:
        d = env_dir / n
        d.mkdir(parents=True)
        (d / "service.toml").write_text(
            f'[service]\nname = "{n}"\nport = {p}\nenv_var_name = "{v}"\n'
        )
    out = rp._discover_service_env_vars(env_dir, enabled_apis={"alpha"})
    assert out == {"ALPHA_URL": "http://alpha:9000"}


def test_discover_service_env_vars_skips_missing_toml(tmp_path):
    rp = _load_repackage_module()
    env_dir = tmp_path / "environment"
    (env_dir / "no-toml").mkdir(parents=True)
    out = rp._discover_service_env_vars(env_dir)
    assert out == {}


def test_per_rep_logs_verifier_has_test_sources(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None
    verifier = bundle / "trajectories" / "Claude Opus 4.7" / "run_1" / "logs" / "verifier"
    assert (verifier / "test.sh").is_file(), (
        "test.sh must mirror into each per-rep logs/verifier/ next to the run outputs"
    )
    assert (verifier / "test_outputs.py").is_file(), (
        "test_outputs.py must mirror into each per-rep logs/verifier/ from input root"
    )
    assert (verifier / "test_weights.json").is_file(), (
        "test_weights.json must mirror into each per-rep logs/verifier/ from input root"
    )


def test_per_rep_logs_verifier_test_sh_byte_equal_with_harbor(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    verifier_test_sh = (
        bundle / "trajectories" / "Claude Opus 4.7" / "run_1" / "logs" / "verifier" / "test.sh"
    ).read_text()
    harbor_test_sh = _load_harbor_test_sh()()
    assert verifier_test_sh == harbor_test_sh, (
        "per-rep logs/verifier/test.sh must stay byte-equal with src/utils/harbor/test_sh.py"
    )


def test_per_rep_logs_verifier_test_outputs_byte_equal_with_input(tmp_path):
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    verifier_dir = bundle / "trajectories" / "Claude Opus 4.7" / "run_1" / "logs" / "verifier"
    src_outputs = (inp_root / task_id / "test_outputs.py").read_bytes()
    src_weights = (inp_root / task_id / "test_weights.json").read_bytes()
    assert (verifier_dir / "test_outputs.py").read_bytes() == src_outputs
    assert (verifier_dir / "test_weights.json").read_bytes() == src_weights


# ---- stage_output_data parity tests ----
#
# These pin the output/<task>/data parity contract added 2026-06-27 per user
# request: "There is a mismatch between data folder in output and output_bundle"
# (m0835) and user-chosen Option 1 (m0838): "Mirror EVERYTHING into output/".
# The orchestrator stage_output_data() is invoked by eval/run_batch.py via
# subprocess (--stage-output-data flag) BEFORE the bundle subprocess call,
# so output/<task>/data/ ends up matching bundle/<task>/data/ modulo the 3
# by-design strips (_overlay_manifest.json, _meta.json, skills/*/_meta.json).
# See script/AGENTS.md "stage-output-data" invariant for the full contract.


def test_stage_output_data_emits_5_artifacts_into_source(tmp_path):
    """stage_output_data writes persona/, artifacts/, 3 harness .py, tests/, solution/
    into task_dir/data/ (the SOURCE output/<task>/, not a bundle/)."""
    rp = _load_repackage_module()
    src_root, _dst, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"
    task_dir = src_root / task_id

    # Stage persona + harness env source files so the staging helpers have inputs.
    (inp_root / task_id / "persona").mkdir(exist_ok=True)
    (inp_root / task_id / "persona" / "SOUL.md").write_text("# persona\n")
    (inp_root / task_id / "data").mkdir(exist_ok=True)
    (inp_root / task_id / "data" / "input.txt").write_text("artifact body\n")

    ok = rp.stage_output_data(task_dir=task_dir, input_root=inp_root, verbose=False)
    assert ok is True

    data = task_dir / "data"
    assert (data / "tests" / "test.sh").is_file(), "test.sh missing in output/<task>/data/tests/"
    assert (data / "tests" / "test_outputs.py").is_file(), "test_outputs.py missing"
    assert (data / "tests" / "test_weights.json").is_file(), "test_weights.json missing"
    assert (data / "solution" / "solve.sh").is_file(), "solve.sh missing"


def test_stage_output_data_still_emits_test_sh_when_input_missing(tmp_path):
    """test.sh + solve.sh are zero-dep on input/; they emit even when no input dir matches."""
    rp = _load_repackage_module()
    src_root = tmp_path / "src"
    inp_root = tmp_path / "input_does_not_match"
    inp_root.mkdir()
    task_id = "orphan_task"
    task_dir = src_root / task_id
    (task_dir / "data" / "environment").mkdir(parents=True)

    ok = rp.stage_output_data(task_dir=task_dir, input_root=inp_root, verbose=False)
    assert ok is True

    assert (task_dir / "data" / "tests" / "test.sh").is_file()
    assert (task_dir / "data" / "solution" / "solve.sh").is_file()


def test_stage_output_data_then_convert_task_parity(tmp_path):
    """End-to-end: after stage_output_data writes into output/<task>/data/,
    a subsequent convert_task on that task produces bundle/data/ that matches
    output/<task>/data/ for the 5 staged artifact paths."""
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"
    task_dir = src_root / task_id

    (inp_root / task_id / "persona").mkdir(exist_ok=True)
    (inp_root / task_id / "persona" / "SOUL.md").write_text("# persona\n")
    (inp_root / task_id / "data").mkdir(exist_ok=True)
    (inp_root / task_id / "data" / "input.txt").write_text("artifact body\n")

    assert rp.stage_output_data(task_dir=task_dir, input_root=inp_root, verbose=False)

    bundle = rp.convert_task(
        task_dir=task_dir,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None

    # The 5 mirrored artifacts must appear in BOTH trees.
    for rel in (
        "data/tests/test.sh",
        "data/tests/test_outputs.py",
        "data/tests/test_weights.json",
        "data/solution/solve.sh",
    ):
        assert (task_dir / rel).is_file(), f"output side missing {rel}"
        assert (bundle / rel).is_file(), f"bundle side missing {rel}"
        assert (task_dir / rel).read_bytes() == (bundle / rel).read_bytes(), (
            f"output/{rel} differs from bundle/{rel}"
        )


def test_stage_output_data_cli_flag_in_argparse():
    """The --stage-output-data flag must be exposed via the CLI so eval/run_batch.py
    can invoke it via subprocess. AST-level check on the module source."""
    src = (REPO_ROOT / "script" / "repackage_to_bundle.py").read_text()
    assert "--stage-output-data" in src, (
        "--stage-output-data flag missing from script/repackage_to_bundle.py argparse; "
        "eval/run_batch.py subprocess invocation will fail."
    )
    assert "def stage_output_data" in src, (
        "stage_output_data() orchestrator missing from script/repackage_to_bundle.py"
    )


# ============================================================================
# Harbor-parity emitters: instruction.md, Dockerfile, docker-compose.yaml, task.toml
# Pins the 4 emissions added 2026-06-27 after user m0899 reported these files
# missing from output_bundle. All 4 emit into bundle/data/ (and into output/<task>/data/
# via --stage-output-data). Each test ensures byte-equal with Harbor source-of-truth
# generators (src/utils/harbor/{dockerfile.py,compose.py,task_toml.py}) where applicable.
# ============================================================================


def _load_harbor_dockerfile():
    spec = importlib.util.spec_from_file_location(
        "harbor_dockerfile", REPO_ROOT / "src" / "utils" / "harbor" / "dockerfile.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.generate_harbor_dockerfile


def _load_harbor_compose_gen():
    """Load Harbor compose generator via a sys.path-aware loader.

    compose.py uses package-relative imports (`from .compose import ...`),
    so we import the parent harbor package first.
    """
    import sys as _sys
    if str(REPO_ROOT) not in _sys.path:
        _sys.path.insert(0, str(REPO_ROOT))
    from src.utils.harbor.compose import generate_harbor_compose  # type: ignore
    return generate_harbor_compose


def test_dockerfile_byte_equal_with_harbor_all_combinations():
    """Dockerfile must be byte-equal with src/utils/harbor/dockerfile.py across
    all 8 (has_skills, has_persona, has_artifacts) boolean combinations."""
    import itertools
    rp = _load_repackage_module()
    harbor_gen = _load_harbor_dockerfile()
    for s, p, a in itertools.product([False, True], repeat=3):
        harbor = harbor_gen(has_skills=s, has_persona=p, has_artifacts=a)
        local = rp._generate_environment_dockerfile(has_skills=s, has_persona=p, has_artifacts=a)
        assert harbor == local, (
            f"Dockerfile drift at has_skills={s} has_persona={p} has_artifacts={a}"
        )


def test_compose_byte_equal_with_harbor(tmp_path):
    """docker-compose.yaml must be byte-equal with src/utils/harbor/compose.py
    when given the same env_dir (here: a minimal env with 2 services)."""
    rp = _load_repackage_module()
    harbor_compose = _load_harbor_compose_gen()
    env_dir = tmp_path / "env"
    env_dir.mkdir()
    for name, port, env_var in (
        ("gmail-api", 8017, "GMAIL_API_URL"),
        ("xero-api", 8087, "XERO_API_URL"),
    ):
        svc_dir = env_dir / name
        svc_dir.mkdir()
        (svc_dir / "service.toml").write_text(
            f'[service]\nname = "{name}"\nport = {port}\nenv_var_name = "{env_var}"\nhealthcheck_path = "/health"\n'
        )
    harbor = harbor_compose(env_dir)
    local = rp._generate_environment_compose(env_dir)
    assert harbor == local, "compose byte-equal drift"


def test_instruction_md_emitted_with_workspace_hint_when_attachments(tmp_path):
    """When input task has attachments (persona/home or data files),
    instruction.md = prompt.txt + workspace_hint suffix."""
    rp = _load_repackage_module()
    input_task_dir = tmp_path / "task_with_attachments"
    input_task_dir.mkdir()
    (input_task_dir / "prompt.txt").write_text("Solve this puzzle.\n")
    (input_task_dir / "data").mkdir()
    (input_task_dir / "data" / "input.txt").write_text("payload\n")

    bundle = tmp_path / "bundle_a"
    assert rp._stage_data_instruction(input_task_dir, bundle, verbose=False)
    text = (bundle / "data" / "instruction.md").read_text()
    assert text.startswith("Solve this puzzle.")
    assert "Workspace inputs" in text
    assert "/root/workspace/" in text


def test_instruction_md_no_workspace_hint_when_no_attachments(tmp_path):
    """When the task has no persona/home and no data files, instruction.md is
    prompt.txt verbatim (no workspace hint appended)."""
    rp = _load_repackage_module()
    input_task_dir = tmp_path / "task_no_attachments"
    input_task_dir.mkdir()
    (input_task_dir / "prompt.txt").write_text("Just answer in words.\n")

    bundle = tmp_path / "bundle_b"
    assert rp._stage_data_instruction(input_task_dir, bundle, verbose=False)
    text = (bundle / "data" / "instruction.md").read_text()
    assert text == "Just answer in words.\n"
    assert "Workspace inputs" not in text


def test_dockerfile_and_compose_emitted_from_bundle_env_dir(tmp_path):
    """Dockerfile + docker-compose.yaml emit into bundle/data/environment/ when
    env_dir is present. has_persona/has_artifacts conditionals work."""
    rp = _load_repackage_module()
    bundle = tmp_path / "bundle_c"
    env_dir = bundle / "data" / "environment"
    env_dir.mkdir(parents=True)
    (env_dir / "persona").mkdir()
    (env_dir / "persona" / "SOUL.md").write_text("# persona\n")
    svc_dir = env_dir / "gmail-api"
    svc_dir.mkdir()
    (svc_dir / "service.toml").write_text(
        '[service]\nname = "gmail-api"\nport = 8017\nenv_var_name = "GMAIL_API_URL"\n'
    )
    wrote_d, wrote_c = rp._stage_environment_dockerfile_and_compose(bundle, verbose=False)
    assert wrote_d is True and wrote_c is True
    dockerfile_text = (env_dir / "Dockerfile").read_text()
    assert "FROM ubuntu:24.04" in dockerfile_text
    assert "COPY persona /root/.openclaw/persona" in dockerfile_text
    assert "COPY artifacts/inputs/files" not in dockerfile_text
    compose_text = (env_dir / "docker-compose.yaml").read_text()
    assert "services:" in compose_text
    assert "gmail-api:" in compose_text
    assert "litellm-proxy:4000" in compose_text


def test_task_toml_required_skills_from_mock_data(tmp_path):
    """task.toml required_skills must be derived from input/<task>/mock_data/<api>/
    dir names (with -connector suffix), sorted."""
    rp = _load_repackage_module()
    input_task_dir = tmp_path / "task_with_overlay"
    input_task_dir.mkdir()
    (input_task_dir / "prompt.txt").write_text("Use gmail and xero.\n")
    mock_data = input_task_dir / "mock_data"
    mock_data.mkdir()
    (mock_data / "gmail-api").mkdir()
    (mock_data / "xero-api").mkdir()

    bundle = tmp_path / "bundle_d"
    env_dir = bundle / "data" / "environment"
    env_dir.mkdir(parents=True)
    for name, port, env_var in (
        ("gmail-api", 8017, "GMAIL_API_URL"),
        ("xero-api", 8087, "XERO_API_URL"),
        ("github-api", 8088, "GITHUB_API_URL"),
    ):
        sd = env_dir / name
        sd.mkdir()
        (sd / "service.toml").write_text(
            f'[service]\nname = "{name}"\nport = {port}\nenv_var_name = "{env_var}"\n'
        )

    assert rp._stage_task_toml(input_task_dir, bundle, verbose=False)
    toml_text = (bundle / "data" / "task.toml").read_text()
    assert 'required_skills = ["gmail-api-connector", "xero-api-connector"]' in toml_text
    assert "github-api-connector" in toml_text
    idx_required = toml_text.find("required_skills =")
    idx_distractor = toml_text.find("distractor_skills =")
    assert idx_required != -1 and idx_distractor != -1
    distractor_line = toml_text[idx_distractor : toml_text.find("\n", idx_distractor)]
    assert "github-api-connector" in distractor_line


def test_task_toml_env_vars_and_healthcheck_chain(tmp_path):
    """task.toml [environment.env] must contain per-service URL env vars +
    runtime_env_defaults; [environment.healthcheck] command must chain
    curl probes per service."""
    rp = _load_repackage_module()
    input_task_dir = tmp_path / "task_e"
    input_task_dir.mkdir()
    (input_task_dir / "prompt.txt").write_text("Use gmail.\n")
    mock_data = input_task_dir / "mock_data"
    mock_data.mkdir()
    (mock_data / "gmail-api").mkdir()

    bundle = tmp_path / "bundle_e"
    env_dir = bundle / "data" / "environment"
    env_dir.mkdir(parents=True)
    sd = env_dir / "gmail-api"
    sd.mkdir()
    (sd / "service.toml").write_text(
        '[service]\nname = "gmail-api"\nport = 8017\nenv_var_name = "GMAIL_API_URL"\n'
    )

    assert rp._stage_task_toml(input_task_dir, bundle, verbose=False)
    toml_text = (bundle / "data" / "task.toml").read_text()
    assert 'GMAIL_API_URL = "http://gmail-api:8017"' in toml_text
    assert 'LITELLM_BASE_URL = "http://litellm-proxy:4000"' in toml_text
    assert 'TEST_DIR = "/tests"' in toml_text
    assert "curl -f http://localhost:8017/health" in toml_text


def test_convert_task_emits_all_four_harbor_files(tmp_path):
    """End-to-end: convert_task emits instruction.md + Dockerfile + docker-compose.yaml + task.toml."""
    rp = _load_repackage_module()
    src_root, dst_root, inp_root = _stage_minimal_task(tmp_path)
    task_id = "ben_cox_8fc24d4b"

    bundle = rp.convert_task(
        task_dir=src_root / task_id,
        dest_root=dst_root,
        input_root=inp_root,
        infer_meta=False,
        verbose=False,
    )
    assert bundle is not None
    for rel in (
        "data/instruction.md",
        "data/environment/Dockerfile",
        "data/environment/docker-compose.yaml",
        "data/task.toml",
    ):
        assert (bundle / rel).is_file(), f"convert_task did not emit {rel}"
