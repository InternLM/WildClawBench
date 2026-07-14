"""Behavioral tests for src/utils/s3_artifacts.py.

Covers the deliverable-file collector, template filtering, and the full
upload_output_artifacts orchestration with boto3 fully mocked (no network,
no AWS creds, no real S3). We monkeypatch the module-level ``boto3`` import
(via sys.modules) and the ``import boto3`` inside upload_output_artifacts.

Tested surfaces:
  * _collect_deliverable_files  — subdir walking, top-level files, dedup,
    non-dir roots, ordering.
  * _is_template_or_input_file  — persona-scaffolding filter.
  * upload_output_artifacts     — key layout (prefix / no-prefix), record
    schema, MIME + artifact_type classification, URL formatting, and every
    early-return / error path (no bucket, empty task_id, no candidates,
    boto3 ImportError, client-init failure, per-file read OSError,
    per-file put_object failure).
"""

from __future__ import annotations

import builtins
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils import s3_artifacts  # noqa: E402
from src.utils.s3_artifacts import (  # noqa: E402
    _collect_deliverable_files,
    _is_template_or_input_file,
    upload_output_artifacts,
)


# ---------------------------------------------------------------------------
# Test doubles
# ---------------------------------------------------------------------------


class _FakeConfig:
    """Minimal stand-in for src.utils.config.Config (only the fields the
    uploader reads via getattr / attribute access)."""

    def __init__(
        self,
        *,
        s3_bucket="",
        s3_prefix="WildClaw",
        s3_region="us-east-1",
        s3_access_key_id="",
        s3_secret_access_key="",
    ):
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.s3_region = s3_region
        self.s3_access_key_id = s3_access_key_id
        self.s3_secret_access_key = s3_secret_access_key


class _FakeS3Client:
    """Records every put_object call; optionally raises on selected keys."""

    def __init__(self, *, fail_on=None, raise_cls=RuntimeError):
        self.puts = []
        self._fail_on = set(fail_on or ())
        self._raise_cls = raise_cls

    def put_object(self, *, Bucket, Key, Body, ContentType):
        if Key in self._fail_on:
            raise self._raise_cls("simulated S3 failure for %s" % Key)
        self.puts.append(
            {
                "Bucket": Bucket,
                "Key": Key,
                "Body": Body,
                "ContentType": ContentType,
            }
        )


class _FakeBoto3:
    """Stand-in for the boto3 module. Records client() kwargs and hands back
    a preconfigured fake client (or raises on client init)."""

    def __init__(self, client_obj=None, *, init_error=None):
        self._client_obj = client_obj if client_obj is not None else _FakeS3Client()
        self._init_error = init_error
        self.client_calls = []

    def client(self, service_name, **kwargs):
        self.client_calls.append((service_name, kwargs))
        if self._init_error is not None:
            raise self._init_error
        return self._client_obj


@pytest.fixture
def install_fake_boto3(monkeypatch):
    """Install a fake boto3 into sys.modules so the ``import boto3`` inside
    upload_output_artifacts resolves to it. Returns a setter."""

    def _install(fake):
        monkeypatch.setitem(sys.modules, "boto3", fake)
        return fake

    return _install


def _make_workspace(tmp_path, layout):
    """layout: {relative_path: bytes}. Creates files under tmp_path."""
    root = tmp_path / "workspace_full"
    for rel, data in layout.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
    return root


# ---------------------------------------------------------------------------
# _is_template_or_input_file
# ---------------------------------------------------------------------------


class TestIsTemplateFile:
    @pytest.mark.parametrize(
        "name",
        ["IDENTITY.md", "BOOTSTRAP.md", "HEARTBEAT.md", "USER.md",
         "SOUL.md", "AGENTS.md", "TOOLS.md", "AGENT.md", "MEMORY.md"],
    )
    def test_persona_scaffolding_names_are_templates(self, name):
        assert _is_template_or_input_file(Path("/some/dir") / name) is True

    def test_regular_output_file_is_not_template(self):
        assert _is_template_or_input_file(Path("/x/report.csv")) is False

    def test_match_is_by_basename_not_path(self):
        # A file literally named MEMORY.md anywhere is filtered; a differently
        # named file in a dir called MEMORY.md is not.
        assert _is_template_or_input_file(Path("/deep/nested/MEMORY.md")) is True
        assert _is_template_or_input_file(Path("/MEMORY.md/data.json")) is False

    def test_case_sensitive(self):
        # Filter is exact-name; lowercase variant is a real artifact.
        assert _is_template_or_input_file(Path("/x/memory.md")) is False


# ---------------------------------------------------------------------------
# _collect_deliverable_files
# ---------------------------------------------------------------------------


class TestCollectDeliverableFiles:
    def test_empty_when_no_roots(self):
        assert _collect_deliverable_files([]) == []

    def test_skips_non_directory_roots(self, tmp_path):
        missing = tmp_path / "does_not_exist"
        a_file = tmp_path / "afile.txt"
        a_file.write_text("x")
        # Neither a missing path nor a file (non-dir) root yields anything.
        assert _collect_deliverable_files([missing, a_file]) == []

    def test_collects_files_from_deliverable_subdirs(self, tmp_path):
        root = _make_workspace(
            tmp_path,
            {
                "results/r.csv": b"a",
                "deliverables/d.json": b"b",
                "output/o.txt": b"c",
                "out/x.md": b"d",
                "artifacts/y.png": b"e",
            },
        )
        found = _collect_deliverable_files([root])
        names = {p.name for p in found}
        assert names == {"r.csv", "d.json", "o.txt", "x.md", "y.png"}

    def test_recurses_into_nested_deliverable_dirs(self, tmp_path):
        root = _make_workspace(
            tmp_path, {"results/sub/deep/nested.csv": b"a"}
        )
        found = _collect_deliverable_files([root])
        assert [p.name for p in found] == ["nested.csv"]

    def test_ignores_non_deliverable_subdirs(self, tmp_path):
        # A random subdir that is NOT in _DELIVERABLE_DIR_NAMES is not walked
        # recursively — only top-level files at the root are picked up.
        root = _make_workspace(
            tmp_path, {"random_dir/buried.csv": b"a", "toplevel.csv": b"b"}
        )
        found = _collect_deliverable_files([root])
        names = {p.name for p in found}
        # toplevel.csv is collected (root-level iterdir); buried.csv is not.
        assert "toplevel.csv" in names
        assert "buried.csv" not in names

    def test_collects_top_level_files_at_root(self, tmp_path):
        root = _make_workspace(tmp_path, {"foo.csv": b"a", "bar.txt": b"b"})
        found = _collect_deliverable_files([root])
        assert {p.name for p in found} == {"foo.csv", "bar.txt"}

    def test_top_level_dirs_are_not_returned_as_files(self, tmp_path):
        root = _make_workspace(tmp_path, {"results/inside.csv": b"a"})
        found = _collect_deliverable_files([root])
        # Only the inner file, never the 'results' directory itself.
        assert all(p.is_file() for p in found)
        assert [p.name for p in found] == ["inside.csv"]

    def test_dedups_across_multiple_roots_by_resolved_path(self, tmp_path):
        root = _make_workspace(tmp_path, {"results/r.csv": b"a"})
        # Pass the same root twice; the resolved-path seen-set must dedup.
        found = _collect_deliverable_files([root, root])
        assert len(found) == 1
        assert found[0].name == "r.csv"

    def test_dedups_file_reachable_via_subdir_and_toplevel(self, tmp_path):
        # A file that lives directly under root inside a deliverable dir named
        # 'output' is reached by the subdir walk; a plain top-level file should
        # only appear once even though iterdir also visits the deliverable dir.
        root = _make_workspace(tmp_path, {"output/only.csv": b"a", "plain.csv": b"b"})
        found = _collect_deliverable_files([root])
        names = [p.name for p in found]
        assert names.count("only.csv") == 1
        assert names.count("plain.csv") == 1

    def test_multiple_valid_roots_are_all_walked(self, tmp_path):
        root_a = tmp_path / "a"
        root_b = tmp_path / "b"
        (root_a / "results").mkdir(parents=True)
        (root_b / "results").mkdir(parents=True)
        (root_a / "results" / "one.csv").write_bytes(b"1")
        (root_b / "results" / "two.csv").write_bytes(b"2")
        found = _collect_deliverable_files([root_a, root_b])
        assert {p.name for p in found} == {"one.csv", "two.csv"}


# ---------------------------------------------------------------------------
# upload_output_artifacts — early returns / guard clauses
# ---------------------------------------------------------------------------


class TestUploadEarlyReturns:
    def test_no_config_returns_empty(self, tmp_path):
        assert upload_output_artifacts(None, "task-1", [tmp_path]) == []

    def test_empty_bucket_returns_empty(self, tmp_path):
        cfg = _FakeConfig(s3_bucket="")
        assert upload_output_artifacts(cfg, "task-1", [tmp_path]) == []

    def test_empty_task_id_returns_empty_and_warns(self, tmp_path, caplog):
        cfg = _FakeConfig(s3_bucket="my-bucket")
        with caplog.at_level("WARNING"):
            out = upload_output_artifacts(cfg, "", [tmp_path])
        assert out == []
        assert any("empty task_id" in r.message for r in caplog.records)

    def test_no_candidate_files_returns_empty(self, tmp_path, install_fake_boto3):
        # Bucket + task_id set but the workspace has no deliverable files.
        cfg = _FakeConfig(s3_bucket="my-bucket")
        empty_root = tmp_path / "empty_ws"
        empty_root.mkdir()
        fake = _FakeBoto3()
        install_fake_boto3(fake)
        out = upload_output_artifacts(cfg, "task-1", [empty_root])
        assert out == []
        # boto3.client must not even be constructed when there are no candidates.
        assert fake.client_calls == []

    def test_only_template_files_returns_empty_when_excluded(
        self, tmp_path, install_fake_boto3
    ):
        cfg = _FakeConfig(s3_bucket="my-bucket")
        root = _make_workspace(tmp_path, {"results/MEMORY.md": b"x"})
        fake = _FakeBoto3()
        install_fake_boto3(fake)
        out = upload_output_artifacts(cfg, "task-1", [root])
        assert out == []
        assert fake.client_calls == []


# ---------------------------------------------------------------------------
# upload_output_artifacts — boto3 / client failures
# ---------------------------------------------------------------------------


class TestUploadBotoFailures:
    def test_boto3_import_error_returns_empty(self, tmp_path, monkeypatch, caplog):
        cfg = _FakeConfig(s3_bucket="my-bucket")
        root = _make_workspace(tmp_path, {"results/r.csv": b"data"})

        # Force ``import boto3`` inside the function to raise ImportError.
        monkeypatch.delitem(sys.modules, "boto3", raising=False)
        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "boto3":
                raise ImportError("no boto3")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)
        with caplog.at_level("WARNING"):
            out = upload_output_artifacts(cfg, "task-1", [root])
        assert out == []
        assert any("boto3 not installed" in r.message for r in caplog.records)

    def test_client_init_failure_returns_empty(self, tmp_path, install_fake_boto3, caplog):
        cfg = _FakeConfig(s3_bucket="my-bucket")
        root = _make_workspace(tmp_path, {"results/r.csv": b"data"})
        fake = _FakeBoto3(init_error=RuntimeError("bad creds"))
        install_fake_boto3(fake)
        with caplog.at_level("WARNING"):
            out = upload_output_artifacts(cfg, "task-1", [root])
        assert out == []
        assert any("S3 client init failed" in r.message for r in caplog.records)


# ---------------------------------------------------------------------------
# upload_output_artifacts — client init kwargs
# ---------------------------------------------------------------------------


class TestClientInitKwargs:
    def test_region_only_when_no_creds(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_region="eu-west-1")
        root = _make_workspace(tmp_path, {"results/r.csv": b"d"})
        fake = _FakeBoto3()
        install_fake_boto3(fake)
        upload_output_artifacts(cfg, "task-1", [root])
        service, kwargs = fake.client_calls[0]
        assert service == "s3"
        assert kwargs == {"region_name": "eu-west-1"}

    def test_region_defaults_to_us_east_1_when_blank(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_region="")
        root = _make_workspace(tmp_path, {"results/r.csv": b"d"})
        fake = _FakeBoto3()
        install_fake_boto3(fake)
        upload_output_artifacts(cfg, "task-1", [root])
        _, kwargs = fake.client_calls[0]
        assert kwargs["region_name"] == "us-east-1"

    def test_creds_forwarded_when_present(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(
            s3_bucket="b",
            s3_access_key_id="AKIA123",
            s3_secret_access_key="secretxyz",
        )
        root = _make_workspace(tmp_path, {"results/r.csv": b"d"})
        fake = _FakeBoto3()
        install_fake_boto3(fake)
        upload_output_artifacts(cfg, "task-1", [root])
        _, kwargs = fake.client_calls[0]
        assert kwargs["aws_access_key_id"] == "AKIA123"
        assert kwargs["aws_secret_access_key"] == "secretxyz"


# ---------------------------------------------------------------------------
# upload_output_artifacts — key layout & record schema (happy path)
# ---------------------------------------------------------------------------


class TestKeyLayoutAndSchema:
    def test_key_includes_prefix(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="mybucket", s3_prefix="WildClaw", s3_region="us-east-1")
        root = _make_workspace(tmp_path, {"results/report.csv": b"col1,col2\n"})
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "task-abc", [root])

        assert len(records) == 1
        assert len(client.puts) == 1
        put = client.puts[0]
        assert put["Bucket"] == "mybucket"
        assert put["Key"] == "WildClaw/output/tasks/task-abc/report.csv"
        assert put["Body"] == b"col1,col2\n"
        assert put["ContentType"] == "text/csv"

    def test_key_without_prefix(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="mybucket", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/report.csv": b"x"})
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        upload_output_artifacts(cfg, "task-abc", [root])
        assert client.puts[0]["Key"] == "output/tasks/task-abc/report.csv"

    def test_prefix_surrounding_slashes_are_stripped(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="mybucket", s3_prefix="/foo/bar/")
        root = _make_workspace(tmp_path, {"results/r.csv": b"x"})
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        upload_output_artifacts(cfg, "task-1", [root])
        assert client.puts[0]["Key"] == "foo/bar/output/tasks/task-1/r.csv"

    def test_record_schema_full(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="mybucket", s3_prefix="P", s3_region="us-west-2")
        root = _make_workspace(tmp_path, {"results/report.csv": b"12345"})
        install_fake_boto3(_FakeBoto3(_FakeS3Client()))
        records = upload_output_artifacts(cfg, "task-abc", [root])

        rec = records[0]
        assert set(rec.keys()) == {
            "filename", "mime_type", "artifact_type", "description",
            "container_path", "size_bytes", "source", "s3_url",
        }
        assert rec["filename"] == "report.csv"
        assert rec["mime_type"] == "text/csv"
        assert rec["artifact_type"] == "data_export"
        assert rec["description"] == "Agent-generated csv output"
        assert rec["container_path"].endswith("report.csv")
        assert rec["size_bytes"] == 5
        assert rec["source"] == "s3://mybucket/P/output/tasks/task-abc/report.csv"
        assert rec["s3_url"] == (
            "https://mybucket.s3.us-west-2.amazonaws.com/P/output/tasks/task-abc/report.csv"
        )

    def test_s3_url_uses_config_region(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="bkt", s3_prefix="", s3_region="ap-south-1")
        root = _make_workspace(tmp_path, {"results/r.csv": b"x"})
        install_fake_boto3(_FakeBoto3(_FakeS3Client()))
        records = upload_output_artifacts(cfg, "t", [root])
        assert records[0]["s3_url"] == (
            "https://bkt.s3.ap-south-1.amazonaws.com/output/tasks/t/r.csv"
        )

    def test_unknown_extension_gets_octet_stream_mime(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/blob.weirdext": b"raw"})
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "t", [root])
        assert client.puts[0]["ContentType"] == "application/octet-stream"
        assert records[0]["mime_type"] == "application/octet-stream"
        assert records[0]["artifact_type"] == "other"

    def test_file_with_no_suffix_description_says_file(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/README": b"hello"})
        install_fake_boto3(_FakeBoto3(_FakeS3Client()))
        records = upload_output_artifacts(cfg, "t", [root])
        # No extension -> description falls back to "file".
        assert records[0]["description"] == "Agent-generated file output"

    def test_image_artifact_type(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/chart.png": b"\x89PNG"})
        install_fake_boto3(_FakeBoto3(_FakeS3Client()))
        records = upload_output_artifacts(cfg, "t", [root])
        assert records[0]["mime_type"] == "image/png"
        assert records[0]["artifact_type"] == "generated_image"

    def test_empty_file_uploads_with_zero_size(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/empty.csv": b""})
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "t", [root])
        assert records[0]["size_bytes"] == 0
        assert client.puts[0]["Body"] == b""


# ---------------------------------------------------------------------------
# upload_output_artifacts — template inclusion toggle
# ---------------------------------------------------------------------------


class TestTemplateInclusion:
    def test_template_files_excluded_by_default(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(
            tmp_path, {"results/MEMORY.md": b"x", "results/real.csv": b"y"}
        )
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "t", [root])
        uploaded = {r["filename"] for r in records}
        assert uploaded == {"real.csv"}

    def test_template_files_included_when_flag_set(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(
            tmp_path, {"results/MEMORY.md": b"x", "results/real.csv": b"y"}
        )
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(
            cfg, "t", [root], include_template_files=True
        )
        uploaded = {r["filename"] for r in records}
        assert uploaded == {"MEMORY.md", "real.csv"}


# ---------------------------------------------------------------------------
# upload_output_artifacts — per-file error resilience
# ---------------------------------------------------------------------------


class TestPerFileErrorResilience:
    def test_put_object_failure_skips_file_and_continues(
        self, tmp_path, install_fake_boto3, caplog
    ):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(
            tmp_path, {"results/good.csv": b"1", "results/bad.csv": b"2"}
        )
        # Make the upload of bad.csv raise; good.csv must still succeed.
        client = _FakeS3Client(fail_on={"output/tasks/t/bad.csv"})
        install_fake_boto3(_FakeBoto3(client))
        with caplog.at_level("WARNING"):
            records = upload_output_artifacts(cfg, "t", [root])
        names = {r["filename"] for r in records}
        assert names == {"good.csv"}
        assert {p["Key"] for p in client.puts} == {"output/tasks/t/good.csv"}
        assert any("S3 upload failed" in r.message for r in caplog.records)

    def test_read_oserror_skips_file_and_continues(
        self, tmp_path, install_fake_boto3, monkeypatch, caplog
    ):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(
            tmp_path, {"results/good.csv": b"1", "results/unreadable.csv": b"2"}
        )
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))

        real_read_bytes = Path.read_bytes

        def flaky_read_bytes(self):
            if self.name == "unreadable.csv":
                raise OSError("permission denied")
            return real_read_bytes(self)

        monkeypatch.setattr(Path, "read_bytes", flaky_read_bytes)
        with caplog.at_level("WARNING"):
            records = upload_output_artifacts(cfg, "t", [root])
        names = {r["filename"] for r in records}
        assert names == {"good.csv"}
        # The unreadable file never reached put_object.
        assert {p["Key"] for p in client.puts} == {"output/tasks/t/good.csv"}
        assert any("read failed" in r.message for r in caplog.records)

    def test_all_files_fail_returns_empty_list(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/a.csv": b"1", "results/b.csv": b"2"})
        client = _FakeS3Client(
            fail_on={"output/tasks/t/a.csv", "output/tasks/t/b.csv"}
        )
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "t", [root])
        assert records == []
        assert client.puts == []


# ---------------------------------------------------------------------------
# upload_output_artifacts — multi-file ordering & completeness
# ---------------------------------------------------------------------------


class TestMultiFileUpload:
    def test_multiple_files_all_uploaded(self, tmp_path, install_fake_boto3):
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(
            tmp_path,
            {
                "results/a.csv": b"1",
                "deliverables/b.json": b"2",
                "top.txt": b"3",
            },
        )
        client = _FakeS3Client()
        install_fake_boto3(_FakeBoto3(client))
        records = upload_output_artifacts(cfg, "task-9", [root])
        assert len(records) == 3
        assert {r["filename"] for r in records} == {"a.csv", "b.json", "top.txt"}
        assert len(client.puts) == 3

    def test_accepts_iterable_generator_of_roots(self, tmp_path, install_fake_boto3):
        # workspace_roots is declared as Iterable[Path]; the function calls
        # list() on it, so a one-shot generator must work.
        cfg = _FakeConfig(s3_bucket="b", s3_prefix="")
        root = _make_workspace(tmp_path, {"results/r.csv": b"x"})
        install_fake_boto3(_FakeBoto3(_FakeS3Client()))
        records = upload_output_artifacts(cfg, "t", (p for p in [root]))
        assert len(records) == 1
