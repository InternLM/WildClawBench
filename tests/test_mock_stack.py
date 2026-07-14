"""Behavioral tests for src/utils/mock_stack.py.

Covers the pure/decision logic of the mock-image lifecycle without ever
spawning docker or touching the network:

- _compute_mock_content_hash: (relpath, size, mtime) manifest hash over an
  environment/ tree, builder-version folding, empty-on-missing-dir.
- _image_content_hash: label extraction via `docker image inspect`.
- read_api_ports / _extract_port: service.toml [service] port discovery.
- _generate_ports_manifest / _generate_dockerfile: baked artifacts.
- _mock_build_lock: cross-process flock context manager.
- build_mock_image_if_needed / _build_mock_image_locked: the rebuild-vs-reuse
  decision (content-hash match, KENSEI_MOCK_REBUILD=1, force=True, stale tag,
  missing env_dir, no APIs, docker-build failure).
- start_mock_stack: docker-run argv assembly (overlays, enabled_apis,
  admin_env, publish_ports) + failure surfacing.
- get_published_ports / get_network_gateway: docker-output parsing.
- wait_for_mock_stack_healthy / wait_for_ports_healthy / stop_mock_stack.

Every subprocess.run is monkeypatched; every filesystem write goes to
tmp_path. time.sleep is stubbed so timeout loops don't actually wait.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import mock_stack  # noqa: E402


# ---------------------------------------------------------------------------
# Fakes & fixtures
# ---------------------------------------------------------------------------


class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


@pytest.fixture
def capture_run(monkeypatch):
    """Record every subprocess.run argv; return a default success result."""
    calls: list[list[str]] = []

    def fake_run(cmd, *args, **kwargs):
        calls.append(list(cmd))
        return _FakeCompleted()

    monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
    return calls


def _make_env(tmp_path: Path, spec: dict[str, str | None]) -> Path:
    """Build a fake environment/ tree.

    spec maps '<api-dir>' -> service.toml text, or None to create the dir
    WITHOUT a service.toml.
    """
    env = tmp_path / "environment"
    env.mkdir()
    for name, toml in spec.items():
        d = env / name
        d.mkdir()
        if toml is not None:
            (d / "service.toml").write_text(toml, encoding="utf-8")
    return env


def _service_toml(port: int) -> str:
    return f'[service]\nname = "svc"\nport = {port}\n'


# ---------------------------------------------------------------------------
# _compute_mock_content_hash
# ---------------------------------------------------------------------------


class TestComputeContentHash:
    def test_missing_dir_returns_empty_string(self, tmp_path):
        assert mock_stack._compute_mock_content_hash(tmp_path / "nope") == ""

    def test_file_path_not_dir_returns_empty(self, tmp_path):
        f = tmp_path / "afile"
        f.write_text("x")
        assert mock_stack._compute_mock_content_hash(f) == ""

    def test_hash_is_16_hex_chars(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h = mock_stack._compute_mock_content_hash(env)
        assert len(h) == 16
        assert all(c in "0123456789abcdef" for c in h)

    def test_deterministic_for_identical_tree(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 == h2

    def test_accepts_str_path(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        assert mock_stack._compute_mock_content_hash(str(env)) == (
            mock_stack._compute_mock_content_hash(env)
        )

    def test_empty_dir_hash_differs_from_missing(self, tmp_path):
        env = tmp_path / "environment"
        env.mkdir()
        # No files: manifest is [] but builder version still folds in => non-empty,
        # and distinct from the "" returned for a missing dir.
        h = mock_stack._compute_mock_content_hash(env)
        assert h != ""
        assert len(h) == 16

    def test_size_change_changes_hash(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        (env / "a-api" / "service.toml").write_text(
            _service_toml(8000) + "# extra padding line to change size\n",
            encoding="utf-8",
        )
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 != h2

    def test_mtime_change_changes_hash(self, tmp_path):
        import os as _os

        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        f = env / "a-api" / "service.toml"
        st = f.stat()
        _os.utime(f, (st.st_atime, st.st_mtime + 100))
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 != h2

    def test_adding_file_changes_hash(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        (env / "a-api" / "data.py").write_text("X = 1\n", encoding="utf-8")
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 != h2

    def test_nested_subdirs_included(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        nested = env / "a-api" / "mock_data" / "deep"
        nested.mkdir(parents=True)
        (nested / "row.csv").write_text("id\n1\n", encoding="utf-8")
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 != h2

    def test_builder_version_folds_into_hash(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        monkeypatch.setattr(mock_stack, "_BUILDER_VERSION", "different-recipe-2")
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 != h2

    def test_directories_do_not_contribute_only_files(self, tmp_path):
        # An empty subdirectory (no files under it) must not change the hash,
        # because the manifest only includes is_file() entries.
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        h1 = mock_stack._compute_mock_content_hash(env)
        (env / "a-api" / "empty_subdir").mkdir()
        h2 = mock_stack._compute_mock_content_hash(env)
        assert h1 == h2

    def test_stat_oserror_file_is_skipped(self, tmp_path, monkeypatch):
        # The manifest builder wraps the explicit `path.stat()` in try/except
        # OSError and skips that file. is_file() (which also stats) must still
        # succeed, so we let the FIRST stat on ghost pass (is_file) and raise on
        # the SECOND (the explicit size/mtime read).
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        (env / "a-api" / "ghost").write_text("boo", encoding="utf-8")
        real_stat = Path.stat
        seen = {"ghost_calls": 0}

        def flaky_stat(self, *a, **kw):
            if self.name == "ghost":
                seen["ghost_calls"] += 1
                if seen["ghost_calls"] >= 2:
                    raise OSError("gone")
            return real_stat(self, *a, **kw)

        monkeypatch.setattr(Path, "stat", flaky_stat)
        # ghost is skipped by the OSError guard; hashing still succeeds and the
        # explicit stat on ghost did raise (proving the except branch ran).
        h = mock_stack._compute_mock_content_hash(env)
        assert len(h) == 16
        assert seen["ghost_calls"] >= 2


# ---------------------------------------------------------------------------
# _image_content_hash
# ---------------------------------------------------------------------------


class TestImageContentHash:
    def test_returns_label_on_success(self, monkeypatch):
        def fake_run(cmd, *a, **kw):
            assert cmd[:3] == ["docker", "image", "inspect"]
            return _FakeCompleted(returncode=0, stdout="abcd1234\n")

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        assert mock_stack._image_content_hash("kensei3-mocks:v1") == "abcd1234"

    def test_returns_empty_on_nonzero_exit(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=1, stdout="junk"),
        )
        assert mock_stack._image_content_hash("missing:tag") == ""

    def test_strips_whitespace(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="  hh  \n"),
        )
        assert mock_stack._image_content_hash("i") == "hh"

    def test_none_stdout_returns_empty(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout=None),
        )
        assert mock_stack._image_content_hash("i") == ""

    def test_uses_content_hash_label_in_format(self, monkeypatch):
        captured = {}

        def fake_run(cmd, *a, **kw):
            captured["cmd"] = cmd
            return _FakeCompleted(returncode=0, stdout="")

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        mock_stack._image_content_hash("i")
        assert mock_stack._CONTENT_HASH_LABEL in " ".join(captured["cmd"])


# ---------------------------------------------------------------------------
# _extract_port / read_api_ports
# ---------------------------------------------------------------------------


class TestExtractPort:
    def test_reads_port_in_service_section(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text("[service]\nport = 8123\n", encoding="utf-8")
        assert mock_stack._extract_port(p) == 8123

    def test_strips_double_quotes(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text('[service]\nport = "8200"\n', encoding="utf-8")
        assert mock_stack._extract_port(p) == 8200

    def test_strips_single_quotes(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text("[service]\nport = '8201'\n", encoding="utf-8")
        assert mock_stack._extract_port(p) == 8201

    def test_ignores_port_outside_service_section(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text("[other]\nport = 9999\n", encoding="utf-8")
        assert mock_stack._extract_port(p) is None

    def test_only_reads_service_section_port(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text(
            "[other]\nport = 1111\n[service]\nport = 8300\n", encoding="utf-8"
        )
        assert mock_stack._extract_port(p) == 8300

    def test_skips_comments_and_blank_lines(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text(
            "# a comment\n\n[service]\n# inline comment line\nport = 8400\n",
            encoding="utf-8",
        )
        assert mock_stack._extract_port(p) == 8400

    def test_non_integer_port_returns_none(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text("[service]\nport = notanumber\n", encoding="utf-8")
        assert mock_stack._extract_port(p) is None

    def test_no_port_key_returns_none(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text('[service]\nname = "x"\n', encoding="utf-8")
        assert mock_stack._extract_port(p) is None

    def test_lines_without_equals_skipped(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text("[service]\nbarewords here\nport = 8500\n", encoding="utf-8")
        assert mock_stack._extract_port(p) == 8500

    def test_switching_out_of_service_section_stops_matching(self, tmp_path):
        p = tmp_path / "service.toml"
        p.write_text(
            '[service]\nname = "x"\n[env]\nport = 7000\n', encoding="utf-8"
        )
        assert mock_stack._extract_port(p) is None


class TestReadApiPorts:
    def test_missing_env_dir_returns_empty(self, tmp_path):
        assert mock_stack.read_api_ports(tmp_path / "nope") == {}

    def test_discovers_multiple_apis_sorted(self, tmp_path):
        env = _make_env(
            tmp_path,
            {
                "b-api": _service_toml(8001),
                "a-api": _service_toml(8000),
                "c-api": _service_toml(8002),
            },
        )
        ports = mock_stack.read_api_ports(env)
        assert ports == {"a-api": 8000, "b-api": 8001, "c-api": 8002}

    def test_skips_dirs_without_service_toml(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000), "notes": None})
        assert mock_stack.read_api_ports(env) == {"a-api": 8000}

    def test_skips_files_at_top_level(self, tmp_path):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        (env / "README.md").write_text("hi", encoding="utf-8")
        assert mock_stack.read_api_ports(env) == {"a-api": 8000}

    def test_dir_with_unparseable_port_is_omitted(self, tmp_path):
        env = _make_env(
            tmp_path,
            {"a-api": _service_toml(8000), "bad-api": "[service]\nport = xx\n"},
        )
        assert mock_stack.read_api_ports(env) == {"a-api": 8000}

    def test_env_dir_is_file_returns_empty(self, tmp_path):
        f = tmp_path / "afile"
        f.write_text("x")
        assert mock_stack.read_api_ports(f) == {}


# ---------------------------------------------------------------------------
# _generate_ports_manifest
# ---------------------------------------------------------------------------


class TestGeneratePortsManifest:
    def test_sorted_json_with_int_values(self):
        out = mock_stack._generate_ports_manifest({"b-api": 8001, "a-api": 8000})
        data = json.loads(out)
        assert data == {"a-api": 8000, "b-api": 8001}
        assert list(data.keys()) == ["a-api", "b-api"]

    def test_empty_map_is_empty_json_object(self):
        assert json.loads(mock_stack._generate_ports_manifest({})) == {}

    def test_string_port_coerced_to_int(self):
        out = mock_stack._generate_ports_manifest({"a-api": "8000"})
        assert json.loads(out)["a-api"] == 8000
        assert isinstance(json.loads(out)["a-api"], int)


# ---------------------------------------------------------------------------
# _generate_dockerfile
# ---------------------------------------------------------------------------


class TestGenerateDockerfile:
    def test_base_image_is_digest_pinned(self):
        df = mock_stack._generate_dockerfile(["a-api"])
        assert "FROM python:3.11-slim@sha256:" in df

    def test_creates_non_root_app_user_and_switches(self):
        df = mock_stack._generate_dockerfile(["a-api"])
        assert "useradd -r -g app" in df
        assert "USER app" in df

    def test_require_hashes_locked_install(self):
        df = mock_stack._generate_dockerfile(["a-api"])
        assert "--require-hashes" in df
        assert "requirements-locked.txt" in df

    def test_healthcheck_present(self):
        df = mock_stack._generate_dockerfile(["a-api"])
        assert "HEALTHCHECK" in df
        assert "/healthcheck.sh" in df

    def test_output_ignores_api_dirs_arg_content(self):
        # The generated Dockerfile is COPY-based (COPY env_dir/) and does not
        # inline per-API names, so passing a different list yields identical text.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        assert mock_stack._generate_dockerfile(["a-api"]) == (
            mock_stack._generate_dockerfile(["x-api", "y-api"])
        )


# ---------------------------------------------------------------------------
# _mock_build_lock
# ---------------------------------------------------------------------------


class TestMockBuildLock:
    def test_acquires_and_releases_flock(self, monkeypatch, tmp_path):
        import fcntl as _f

        events: list[str] = []

        def fake_flock(fd, op):
            events.append("lock" if op == _f.LOCK_EX else "unlock")

        monkeypatch.setattr(mock_stack.fcntl, "flock", fake_flock)
        monkeypatch.setattr(mock_stack.tempfile, "gettempdir", lambda: str(tmp_path))
        with mock_stack._mock_build_lock():
            events.append("body")
        assert events == ["lock", "body", "unlock"]

    def test_unlocks_even_if_body_raises(self, monkeypatch, tmp_path):
        import fcntl as _f

        events: list[str] = []

        def fake_flock(fd, op):
            events.append("lock" if op == _f.LOCK_EX else "unlock")

        monkeypatch.setattr(mock_stack.fcntl, "flock", fake_flock)
        monkeypatch.setattr(mock_stack.tempfile, "gettempdir", lambda: str(tmp_path))
        with pytest.raises(RuntimeError):
            with mock_stack._mock_build_lock():
                raise RuntimeError("boom")
        assert events == ["lock", "unlock"]

    def test_open_failure_yields_without_locking(self, monkeypatch, tmp_path):
        # Best-effort: if the lock file can't be opened, the CM still yields and
        # never calls flock.
        called = {"flock": False}

        def bad_open(*a, **kw):
            raise OSError("no fs")

        monkeypatch.setattr(mock_stack.tempfile, "gettempdir", lambda: str(tmp_path))
        monkeypatch.setattr("builtins.open", bad_open)
        monkeypatch.setattr(
            mock_stack.fcntl, "flock",
            lambda fd, op: called.__setitem__("flock", True),
        )
        with mock_stack._mock_build_lock():
            pass
        assert called["flock"] is False


# ---------------------------------------------------------------------------
# build_mock_image_if_needed / _build_mock_image_locked (decision logic)
# ---------------------------------------------------------------------------


class _ScriptedDocker:
    """subprocess.run stand-in returning per-argv scripted results.

    Match on a substring of the joined argv; first match wins. Records all
    calls for assertions. Unmatched calls default to success (rc=0).
    """

    def __init__(self, rules: list[tuple[str, _FakeCompleted]]):
        self.rules = rules
        self.calls: list[list[str]] = []

    def __call__(self, cmd, *a, **kw):
        self.calls.append(list(cmd))
        joined = " ".join(str(c) for c in cmd)
        # The content-hash label probe is `docker image inspect <img> --format
        # {{ ... Config.Labels ... }}`; it also contains the substring
        # "image inspect <img>". To disambiguate, a Config.Labels rule wins over
        # a bare "image inspect" rule whenever the command is the label probe.
        if "Config.Labels" in joined:
            for needle, result in self.rules:
                if needle == "Config.Labels":
                    return result
        for needle, result in self.rules:
            if needle in joined:
                return result
        return _FakeCompleted(returncode=0)

    def ran(self, needle: str) -> bool:
        return any(needle in " ".join(str(c) for c in cmd) for cmd in self.calls)


class TestBuildDecision:
    @pytest.fixture(autouse=True)
    def _no_lock(self, monkeypatch):
        """Neutralize the cross-process flock (no real lock files) for this class."""
        import contextlib

        @contextlib.contextmanager
        def _noop():
            yield

        monkeypatch.setattr(mock_stack, "_mock_build_lock", _noop)
        monkeypatch.delenv("KENSEI_MOCK_REBUILD", raising=False)

    def test_reuses_when_hash_matches(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        expected = mock_stack._compute_mock_content_hash(env)
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=0)),
                ("Config.Labels", _FakeCompleted(returncode=0, stdout=expected)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        # Reuse path: never rmi, never build.
        assert not scripted.ran("rmi")
        assert not scripted.ran("build")

    def test_rebuilds_when_hash_stale(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=0)),
                ("Config.Labels", _FakeCompleted(returncode=0, stdout="STALEHASH")),
                ("build", _FakeCompleted(returncode=0)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        assert scripted.ran("rmi")  # stale tag removed
        assert scripted.ran("build")

    def test_builds_when_image_absent(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=1)),
                ("build", _FakeCompleted(returncode=0)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        assert scripted.ran("build")

    def test_force_true_rebuilds_and_removes_tag(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        scripted = _ScriptedDocker([("build", _FakeCompleted(returncode=0))])
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env, force=True) is True
        assert scripted.ran("rmi")
        assert scripted.ran("build")
        # Force path skips the image-inspect staleness probe entirely.
        assert not scripted.ran("image inspect")

    def test_kensei_mock_rebuild_env_forces(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        monkeypatch.setenv("KENSEI_MOCK_REBUILD", "1")
        scripted = _ScriptedDocker([("build", _FakeCompleted(returncode=0))])
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        assert scripted.ran("rmi")
        assert not scripted.ran("image inspect")

    @pytest.mark.parametrize("val", ["1", "true", "TRUE", "Yes", " yes "])
    def test_rebuild_env_truthy_variants(self, tmp_path, monkeypatch, val):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        monkeypatch.setenv("KENSEI_MOCK_REBUILD", val)
        scripted = _ScriptedDocker([("build", _FakeCompleted(returncode=0))])
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        assert not scripted.ran("image inspect")

    @pytest.mark.parametrize("val", ["0", "false", "no", "", "off"])
    def test_rebuild_env_falsy_variants_take_cache_path(
        self, tmp_path, monkeypatch, val
    ):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        monkeypatch.setenv("KENSEI_MOCK_REBUILD", val)
        expected = mock_stack._compute_mock_content_hash(env)
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=0)),
                ("Config.Labels", _FakeCompleted(returncode=0, stdout=expected)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        # Falsy env => normal cache-check path runs (image inspect happens).
        assert scripted.ran("image inspect")
        assert not scripted.ran("build")

    def test_missing_env_dir_returns_false(self, tmp_path, monkeypatch):
        scripted = _ScriptedDocker(
            [("image inspect kensei3-mocks", _FakeCompleted(returncode=1))]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(tmp_path / "nope") is False
        assert not scripted.ran("build")

    def test_no_apis_returns_false(self, tmp_path, monkeypatch):
        env = tmp_path / "environment"
        env.mkdir()
        (env / "just-notes").mkdir()
        scripted = _ScriptedDocker(
            [("image inspect kensei3-mocks", _FakeCompleted(returncode=1))]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is False
        assert not scripted.ran("build")

    def test_docker_build_failure_returns_false(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=1)),
                ("build", _FakeCompleted(returncode=1, stderr="boom build error")),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is False
        assert scripted.ran("build")

    def test_build_command_carries_content_hash_label(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        expected = mock_stack._compute_mock_content_hash(env)
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=1)),
                ("build", _FakeCompleted(returncode=0)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        mock_stack.build_mock_image_if_needed(env)
        build_cmd = next(c for c in scripted.calls if "build" in c)
        assert "--label" in build_cmd
        label = build_cmd[build_cmd.index("--label") + 1]
        assert label == f"{mock_stack._CONTENT_HASH_LABEL}={expected}"

    def test_build_writes_all_context_files(self, tmp_path, monkeypatch):
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        seen = {}

        def fake_run(cmd, *a, **kw):
            joined = " ".join(str(c) for c in cmd)
            if "image inspect kensei3-mocks" in joined:
                return _FakeCompleted(returncode=1)
            if "build" in joined:
                cwd = Path(kw["cwd"])
                seen["files"] = sorted(p.name for p in cwd.iterdir())
                return _FakeCompleted(returncode=0)
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        assert mock_stack.build_mock_image_if_needed(env) is True
        for name in (
            "Dockerfile",
            "mock_ports.json",
            "gen_supervisord.py",
            "start.sh",
            "healthcheck.sh",
            "env_dir",
        ):
            assert name in seen["files"], seen["files"]

    def test_empty_cached_label_forces_rebuild(self, tmp_path, monkeypatch):
        # If current_hash is non-empty but cached label is empty, image is
        # treated as stale (empty != current) => rebuild.
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=0)),
                ("Config.Labels", _FakeCompleted(returncode=0, stdout="")),
                ("build", _FakeCompleted(returncode=0)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env) is True
        assert scripted.ran("build")

    def test_if_needed_delegates_through_lock(self, tmp_path, monkeypatch):
        # build_mock_image_if_needed must run the locked body. With the flock
        # neutralized by _no_lock, a matched cache hit returns True.
        env = _make_env(tmp_path, {"a-api": _service_toml(8000)})
        expected = mock_stack._compute_mock_content_hash(env)
        scripted = _ScriptedDocker(
            [
                ("image inspect kensei3-mocks", _FakeCompleted(returncode=0)),
                ("Config.Labels", _FakeCompleted(returncode=0, stdout=expected)),
            ]
        )
        monkeypatch.setattr(mock_stack.subprocess, "run", scripted)
        assert mock_stack.build_mock_image_if_needed(env, image=mock_stack.MOCK_IMAGE) is True


# ---------------------------------------------------------------------------
# start_mock_stack
# ---------------------------------------------------------------------------


class TestStartMockStack:
    @staticmethod
    def _run_cmd(calls):
        return next(c for c in calls if len(c) >= 2 and c[1] == "run")

    def test_minimal_run_argv(self, capture_run):
        mock_stack.start_mock_stack("mock-c", "kensei-net")
        # First call is the rm -f cleanup.
        assert capture_run[0][:3] == ["docker", "rm", "-f"]
        run_cmd = self._run_cmd(capture_run)
        assert run_cmd[:3] == ["docker", "run", "-d"]
        assert run_cmd[run_cmd.index("--name") + 1] == "mock-c"
        assert run_cmd[run_cmd.index("--network") + 1] == "kensei-net"
        assert run_cmd[-1] == mock_stack.MOCK_IMAGE

    def test_custom_image_is_last_token(self, capture_run):
        mock_stack.start_mock_stack("mock-c", "net", image="custom:tag")
        run_cmd = self._run_cmd(capture_run)
        assert run_cmd[-1] == "custom:tag"

    def test_enabled_apis_adds_sorted_csv_env(self, capture_run):
        mock_stack.start_mock_stack(
            "mock-c", "net", enabled_apis={"c-api", "a-api", "b-api"}
        )
        run_cmd = self._run_cmd(capture_run)
        idx = run_cmd.index("MOCK_ENABLED_APIS=a-api,b-api,c-api")
        assert run_cmd[idx - 1] == "-e"

    def test_enabled_apis_empty_set_omits_env(self, capture_run):
        mock_stack.start_mock_stack("mock-c", "net", enabled_apis=set())
        run_cmd = self._run_cmd(capture_run)
        assert not any("MOCK_ENABLED_APIS" in tok for tok in run_cmd)

    def test_overlays_produce_readonly_mounts(self, capture_run):
        mock_stack.start_mock_stack(
            "mock-c", "net", overlays={"figma-api": {"data.py": "/host/data.py"}}
        )
        run_cmd = self._run_cmd(capture_run)
        mount = "/host/data.py:/opt/mocks/figma-api/data.py:ro"
        idx = run_cmd.index(mount)
        assert run_cmd[idx - 1] == "-v"

    def test_overlays_non_dict_files_skipped(self, capture_run):
        # A non-dict overlay value must be ignored (no mount, no crash).
        mock_stack.start_mock_stack(
            "mock-c", "net", overlays={"figma-api": "not-a-dict"}
        )
        run_cmd = self._run_cmd(capture_run)
        assert "-v" not in run_cmd

    def test_admin_env_vars_appended(self, capture_run):
        mock_stack.start_mock_stack(
            "mock-c",
            "net",
            admin_env={"MOCK_ADMIN_TOKEN": "secret", "MOCK_ADMIN_ENABLED": "1"},
        )
        run_cmd = self._run_cmd(capture_run)
        assert "MOCK_ADMIN_TOKEN=secret" in run_cmd
        assert "MOCK_ADMIN_ENABLED=1" in run_cmd

    def test_publish_ports_bind_localhost(self, capture_run):
        mock_stack.start_mock_stack("mock-c", "net", publish_ports=[8000, 8001])
        run_cmd = self._run_cmd(capture_run)
        assert "127.0.0.1::8000" in run_cmd
        assert "127.0.0.1::8001" in run_cmd
        for spec in ("127.0.0.1::8000", "127.0.0.1::8001"):
            assert run_cmd[run_cmd.index(spec) - 1] == "-p"

    def test_run_failure_raises_runtimeerror(self, monkeypatch):
        def fake_run(cmd, *a, **kw):
            if len(cmd) >= 2 and cmd[1] == "run":
                return _FakeCompleted(returncode=1, stderr="cannot start")
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        with pytest.raises(RuntimeError, match="mock-stack start failed"):
            mock_stack.start_mock_stack("mock-c", "net")

    def test_combined_options_all_present(self, capture_run):
        mock_stack.start_mock_stack(
            "mock-c",
            "net",
            image="img:1",
            overlays={"a-api": {"f.py": "/h/f.py"}},
            admin_env={"MOCK_ADMIN_ENABLED": "1"},
            publish_ports=[9000],
            enabled_apis=["a-api"],
        )
        run_cmd = self._run_cmd(capture_run)
        assert "/h/f.py:/opt/mocks/a-api/f.py:ro" in run_cmd
        assert "MOCK_ENABLED_APIS=a-api" in run_cmd
        assert "MOCK_ADMIN_ENABLED=1" in run_cmd
        assert "127.0.0.1::9000" in run_cmd
        assert run_cmd[-1] == "img:1"


# ---------------------------------------------------------------------------
# get_published_ports
# ---------------------------------------------------------------------------


class TestGetPublishedPorts:
    def test_parses_host_port_from_docker_port(self, monkeypatch):
        def fake_run(cmd, *a, **kw):
            internal = cmd[-1]
            mapping = {"8000": "0.0.0.0:49001", "8001": "127.0.0.1:49002"}
            return _FakeCompleted(returncode=0, stdout=mapping[internal] + "\n")

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        out = mock_stack.get_published_ports("mock-c", [8000, 8001])
        assert out == {8000: 49001, 8001: 49002}

    def test_unmapped_port_omitted(self, monkeypatch):
        def fake_run(cmd, *a, **kw):
            if cmd[-1] == "8000":
                return _FakeCompleted(returncode=0, stdout="0.0.0.0:49001\n")
            return _FakeCompleted(returncode=1)  # not published

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        out = mock_stack.get_published_ports("mock-c", [8000, 8001])
        assert out == {8000: 49001}

    def test_empty_stdout_omitted(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="\n\n"),
        )
        assert mock_stack.get_published_ports("mock-c", [8000]) == {}

    def test_unparseable_host_part_omitted(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="0.0.0.0:notaport\n"),
        )
        assert mock_stack.get_published_ports("mock-c", [8000]) == {}

    def test_ipv6_style_takes_last_colon_segment(self, monkeypatch):
        # rsplit(":", 1) takes the trailing port even with an IPv6 host.
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="[::]:49010\n"),
        )
        assert mock_stack.get_published_ports("mock-c", [8000]) == {8000: 49010}

    def test_empty_internal_ports_returns_empty(self, monkeypatch):
        called = {"n": 0}

        def fake_run(*a, **kw):
            called["n"] += 1
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        assert mock_stack.get_published_ports("mock-c", []) == {}
        assert called["n"] == 0


# ---------------------------------------------------------------------------
# get_network_gateway
# ---------------------------------------------------------------------------


class TestGetNetworkGateway:
    def test_returns_first_gateway(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(
                returncode=0, stdout="172.20.0.1 172.21.0.1 \n"
            ),
        )
        assert mock_stack.get_network_gateway("kensei-net") == "172.20.0.1"

    def test_nonzero_exit_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run", lambda *a, **kw: _FakeCompleted(returncode=1)
        )
        assert mock_stack.get_network_gateway("nope") is None

    def test_empty_output_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="   \n"),
        )
        assert mock_stack.get_network_gateway("net") is None


# ---------------------------------------------------------------------------
# wait_for_mock_stack_healthy
# ---------------------------------------------------------------------------


@pytest.fixture
def no_sleep(monkeypatch):
    monkeypatch.setattr(mock_stack.time, "sleep", lambda *a, **kw: None)


class TestWaitForMockStackHealthy:
    def test_returns_true_when_healthy(self, monkeypatch, no_sleep):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="healthy\n"),
        )
        assert mock_stack.wait_for_mock_stack_healthy("c", timeout=5) is True

    def test_returns_false_when_unhealthy(self, monkeypatch, no_sleep):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="unhealthy\n"),
        )
        assert mock_stack.wait_for_mock_stack_healthy("c", timeout=5) is False

    def test_times_out_when_stuck_starting(self, monkeypatch):
        # 'starting' never resolves -> loop exits at deadline -> False. Drive the
        # clock forward via a fake time.time so no real waiting occurs.
        clock = {"t": 1000.0}
        monkeypatch.setattr(mock_stack.time, "time", lambda: clock["t"])
        monkeypatch.setattr(
            mock_stack.time, "sleep",
            lambda _s: clock.__setitem__("t", clock["t"] + 3),
        )
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout="starting\n"),
        )
        assert mock_stack.wait_for_mock_stack_healthy("c", timeout=6) is False

    def test_becomes_healthy_after_starting(self, monkeypatch):
        clock = {"t": 1000.0}
        monkeypatch.setattr(mock_stack.time, "time", lambda: clock["t"])
        monkeypatch.setattr(
            mock_stack.time, "sleep",
            lambda _s: clock.__setitem__("t", clock["t"] + 3),
        )
        seq = iter(["starting\n", "starting\n", "healthy\n"])
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0, stdout=next(seq)),
        )
        assert mock_stack.wait_for_mock_stack_healthy("c", timeout=60) is True


# ---------------------------------------------------------------------------
# wait_for_ports_healthy
# ---------------------------------------------------------------------------


class TestWaitForPortsHealthy:
    def test_empty_ports_returns_true_without_docker(self, monkeypatch):
        called = {"n": 0}
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: called.__setitem__("n", called["n"] + 1)
            or _FakeCompleted(),
        )
        assert mock_stack.wait_for_ports_healthy("c", []) is True
        assert called["n"] == 0

    def test_returns_true_on_first_success(self, monkeypatch, no_sleep):
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=0),
        )
        assert mock_stack.wait_for_ports_healthy("c", [8000], timeout=5) is True

    def test_curl_command_covers_all_ports(self, monkeypatch, no_sleep):
        captured = {}

        def fake_run(cmd, *a, **kw):
            captured["cmd"] = cmd
            return _FakeCompleted(returncode=0)

        monkeypatch.setattr(mock_stack.subprocess, "run", fake_run)
        mock_stack.wait_for_ports_healthy("c", [8000, 8001], timeout=5)
        script = captured["cmd"][-1]
        assert "8000 8001" in script
        assert "/health" in script

    def test_times_out_when_never_healthy(self, monkeypatch):
        clock = {"t": 500.0}
        monkeypatch.setattr(mock_stack.time, "time", lambda: clock["t"])
        monkeypatch.setattr(
            mock_stack.time, "sleep",
            lambda _s: clock.__setitem__("t", clock["t"] + 2),
        )
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=1, stderr="down"),
        )
        assert mock_stack.wait_for_ports_healthy("c", [8000], timeout=4) is False


# ---------------------------------------------------------------------------
# stop_mock_stack
# ---------------------------------------------------------------------------


class TestStopMockStack:
    def test_issues_rm_force(self, capture_run):
        mock_stack.stop_mock_stack("mock-c")
        assert capture_run == [["docker", "rm", "-f", "mock-c"]]

    def test_swallows_docker_result(self, monkeypatch):
        # Even a non-zero rm result must not raise (capture_output, no check).
        monkeypatch.setattr(
            mock_stack.subprocess, "run",
            lambda *a, **kw: _FakeCompleted(returncode=1, stderr="no such container"),
        )
        assert mock_stack.stop_mock_stack("mock-c") is None
