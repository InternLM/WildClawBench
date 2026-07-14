"""Behavioral unit tests for the src/utils/testgen/ package.

Covers the pure/deterministic logic of the test-generation pipeline:
  - constants.py invariants (ALLOWED_WEIGHTS / FALLBACK_WEIGHTS)
  - sanitize.py     (strip duplicate imports/helpers/env constants)
  - repair.py       (auto-close truncated strings/brackets so code parses)
  - wrapper.py      (assemble the wrapper prefix + <SVC>_URL constants)
  - intent.py       (_extract_python_code, _load_intent_system_prompt, flow)
  - bedrock.py      (call_bedrock_converse with httpx + eventstream mocked)
  - generator.py    (_strip_code_fences, _extract_json_object, _clean_weights,
                     _derive_task_output_format, _build_user_message, and the
                     full generate_task_tests happy/fallback paths)

All tests are offline & deterministic: the only network client (httpx) and
the Bedrock eventstream parser are monkeypatched. Temp files go to tmp_path.

Some assertions pin CURRENT behavior that looks defective — those carry the
comment: # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.utils.config import Config  # noqa: E402
from src.utils.testgen import bedrock as bedrock_mod  # noqa: E402
from src.utils.testgen import generator as gen_mod  # noqa: E402
from src.utils.testgen import intent as intent_mod  # noqa: E402
from src.utils.testgen.constants import (  # noqa: E402
    ALLOWED_WEIGHTS,
    FALLBACK_WEIGHTS,
    MAX_TESTGEN_ATTEMPTS,
    SAFE_FALLBACK_STUB,
)
from src.utils.testgen.generator import (  # noqa: E402
    TestGenResult as _TestGenResult,  # aliased so pytest doesn't collect it
    _build_user_message,
    _clean_weights,
    _derive_task_output_format,
    _extract_json_object,
    _strip_code_fences,
    generate_task_tests,
)
from src.utils.testgen.intent import (  # noqa: E402
    _DEFAULT_INTENT_PROMPT,
    _extract_python_code,
    _load_intent_system_prompt,
    generate_intent_tests,
)
from src.utils.testgen.repair import auto_repair_truncated_python  # noqa: E402
from src.utils.testgen.sanitize import sanitize_llm_test_code  # noqa: E402
from src.utils.testgen.wrapper import build_wrapper_prefix  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def _make_env_dir(tmp_path: Path, services: dict | None = None) -> Path:
    """Create a minimal environment/ tree with one or more <name>-api/service.toml.

    services maps api_name -> (port, env_var). Defaults to a single amazon
    seller API. Returns the env dir Path.
    """
    if services is None:
        services = {"amazon-seller-api": (9001, "AMAZON_SELLER_API_URL")}
    env_dir = tmp_path / "environment"
    env_dir.mkdir()
    for name, (port, env_var) in services.items():
        svc = env_dir / name
        svc.mkdir()
        (svc / "service.toml").write_text(
            '[service]\n'
            'name = "%s"\n'
            'port = %d\n'
            'env_var_name = "%s"\n'
            'healthcheck_path = "/health"\n' % (name, port, env_var)
        )
    return env_dir


def _cfg(env_dir: Path | None = None) -> Config:
    cfg = Config(
        bedrock_inference_arn="arn:aws:bedrock:ap-south-1::inference-profile/x",
        bedrock_region="ap-south-1",
        aws_bearer_token="test-token",
    )
    if env_dir is not None:
        cfg.environment_dir = env_dir
    return cfg


# ---------------------------------------------------------------------------
# constants.py invariants
# ---------------------------------------------------------------------------

class TestConstantsInvariants:
    def test_allowed_weights_exact_set(self):
        assert ALLOWED_WEIGHTS == frozenset({5, 3, 1, -1, -3, -5})

    def test_allowed_weights_excludes_zero_and_two(self):
        assert 0 not in ALLOWED_WEIGHTS
        assert 2 not in ALLOWED_WEIGHTS
        assert -2 not in ALLOWED_WEIGHTS

    def test_allowed_weights_symmetric(self):
        # every magnitude has both a positive and negative form
        for w in (1, 3, 5):
            assert w in ALLOWED_WEIGHTS
            assert -w in ALLOWED_WEIGHTS

    def test_fallback_weights_are_all_allowed(self):
        assert FALLBACK_WEIGHTS  # non-empty
        for w in FALLBACK_WEIGHTS.values():
            assert w in ALLOWED_WEIGHTS

    def test_fallback_weights_have_positive_and_negative(self):
        vals = list(FALLBACK_WEIGHTS.values())
        assert any(v > 0 for v in vals)
        assert any(v < 0 for v in vals)

    def test_max_attempts_positive_int(self):
        assert isinstance(MAX_TESTGEN_ATTEMPTS, int)
        assert MAX_TESTGEN_ATTEMPTS >= 1

    def test_safe_fallback_stub_parses_as_python(self):
        # The fallback stub must be valid Python so the assembled file is runnable.
        ast.parse(SAFE_FALLBACK_STUB)


# ---------------------------------------------------------------------------
# sanitize.py
# ---------------------------------------------------------------------------

class TestSanitize:
    def test_strips_import_lines(self):
        code = "import os\nfrom urllib.request import urlopen\nx = 1"
        out = sanitize_llm_test_code(code)
        assert "import os" not in out
        assert "from urllib.request" not in out
        assert "x = 1" in out

    def test_strips_env_url_constants(self):
        code = 'AMAZON_SELLER_API_URL = os.environ.get("X", "http://y")\nz = 2'
        out = sanitize_llm_test_code(code)
        assert "AMAZON_SELLER_API_URL" not in out
        assert "z = 2" in out

    def test_strips_duplicate_helper_defs(self):
        code = (
            "def api_get(base, ep):\n"
            "    return 1\n"
            "\n"
            "class TestFoo:\n"
            "    def test_a(self):\n"
            "        assert 1\n"
        )
        out = sanitize_llm_test_code(code)
        assert "def api_get" not in out
        assert "class TestFoo" in out
        assert "def test_a" in out

    def test_collapses_excess_blank_lines(self):
        code = "class A:\n    pass\n\n\n\n\n\nclass B:\n    pass"
        out = sanitize_llm_test_code(code)
        assert "\n\n\n\n" not in out

    def test_preserves_test_body_and_strips_whitespace(self):
        code = "\n\n  class TestKeep:\n      def test_it(self):\n          assert True\n\n"
        out = sanitize_llm_test_code(code)
        assert out.startswith("class TestKeep") or out.startswith("  class TestKeep")
        # .strip() removes leading/trailing blank lines
        assert not out.startswith("\n")
        assert not out.endswith("\n")

    def test_empty_input_returns_empty(self):
        assert sanitize_llm_test_code("") == ""

    def test_keeps_a_test_function_after_import_removal(self):
        code = (
            "import json\n"
            "import os\n"
            "def test_something():\n"
            "    assert api_get(URL, '/x')['ok']\n"
        )
        out = sanitize_llm_test_code(code)
        assert "import json" not in out
        assert "def test_something" in out


# ---------------------------------------------------------------------------
# repair.py
# ---------------------------------------------------------------------------

class TestAutoRepair:
    def test_none_for_empty_string(self):
        assert auto_repair_truncated_python("") is None

    def test_valid_code_returned_unchanged(self):
        code = "x = 1\ndef test_a():\n    assert x == 1\n"
        assert auto_repair_truncated_python(code) == code

    def test_closes_unbalanced_paren(self):
        repaired = auto_repair_truncated_python("def t():\n    assert foo(1, 2\n")
        assert repaired is not None
        ast.parse(repaired)  # must now parse

    def test_closes_unbalanced_bracket(self):
        repaired = auto_repair_truncated_python("x = [1, 2, 3\n")
        assert repaired is not None
        ast.parse(repaired)
        assert repaired.rstrip().endswith("]")

    def test_closes_unbalanced_brace(self):
        repaired = auto_repair_truncated_python('x = {"a": 1\n')
        assert repaired is not None
        ast.parse(repaired)

    def test_closes_single_quoted_string(self):
        repaired = auto_repair_truncated_python('x = "hello')
        assert repaired is not None
        ast.parse(repaired)
        assert repaired.endswith('"')

    def test_closes_triple_quoted_string(self):
        repaired = auto_repair_truncated_python('x = """hello world')
        assert repaired is not None
        ast.parse(repaired)
        assert repaired.endswith('"""')

    def test_truncated_inside_string_backtracks_to_start(self):
        # An unclosed string mid-list: repair backtracks to string start,
        # trims trailing comma, and closes brackets.
        repaired = auto_repair_truncated_python('x = [1, 2,\n    "unclosed')
        assert repaired is not None
        ast.parse(repaired)

    def test_unrepairable_garbage_returns_none(self):
        assert auto_repair_truncated_python("def (((:::\n    @@@ %%% ^^^") is None

    def test_comment_only_line_is_not_treated_as_string(self):
        # '#' starts a comment; a '"' inside it must not open a string.
        code = "x = 1  # a \" quote in a comment\ndef test_a():\n    assert x\n"
        assert auto_repair_truncated_python(code) == code

    def test_closed_triple_string_then_truncated_bracket(self):
        # A fully closed triple-quoted docstring followed by a truncated call —
        # exercises the triple-close branch in _scan then bracket balancing.
        repaired = auto_repair_truncated_python('x = """doc"""\ny = foo(1\n')
        assert repaired is not None
        ast.parse(repaired)

    def test_escaped_quote_inside_unclosed_string(self):
        # Backslash-escaped quote must not prematurely close the string; the
        # repair still closes it at EOF.
        repaired = auto_repair_truncated_python('x = "a\\"b')
        assert repaired is not None
        ast.parse(repaired)

    def test_string_terminated_by_newline_is_unrepairable(self):
        # A single-quoted string closed by a raw newline mid-statement leaves a
        # syntax error the close-quote/bracket heuristic cannot fix -> None.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        code = 'x = "abc\ndef test():\n    assert foo(1\n'
        assert auto_repair_truncated_python(code) is None

    def test_comment_then_truncated_bracket(self):
        # A trailing comment before a truncated list — comment scan must skip to
        # newline, then bracket balancing closes the list.
        repaired = auto_repair_truncated_python('x = 1  # hello\ny = [1, 2\n')
        assert repaired is not None
        ast.parse(repaired)

    def test_backtrack_closes_string_and_open_paren(self):
        # Unclosed string that itself contains an open paren: repair closes the
        # string and then the enclosing call paren.
        repaired = auto_repair_truncated_python(
            'result = compute(\n    "unclosed string with (paren'
        )
        assert repaired is not None
        ast.parse(repaired)

    def test_backtrack_trims_unclosed_string_line(self):
        # Naively closing the string ('2 "abc"') would still be a SyntaxError, so
        # the second branch backtracks to before the string start, trims the
        # trailing token, and closes the outer bracket -> 'z = [1,\n2]'.
        repaired = auto_repair_truncated_python('z = [1,\n2 "abc')
        assert repaired is not None
        ast.parse(repaired)
        assert repaired.rstrip().endswith("]")

    def test_unrepairable_after_backtrack_returns_none(self):
        # Even after backtracking, the remaining prefix has an unbalanced,
        # unfixable structure -> None.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        assert auto_repair_truncated_python('w = (1,\n2 3 "abc') is None


# ---------------------------------------------------------------------------
# wrapper.py
# ---------------------------------------------------------------------------

class TestBuildWrapperPrefix:
    def test_empty_services_still_emits_helpers(self):
        prefix = build_wrapper_prefix({})
        assert "def api_get" in prefix
        assert "def api_post" in prefix
        assert "def read_file" in prefix
        assert "def file_exists" in prefix
        assert "def _request" in prefix
        # no env constants when there are no services
        assert "_URL = os.environ" not in prefix

    def test_emits_url_constant_for_service(self):
        services = {"amazon-seller-api": {"env_var": "AMAZON_SELLER_API_URL", "port": 9001}}
        prefix = build_wrapper_prefix(services)
        assert 'AMAZON_SELLER_API_URL = os.environ.get("AMAZON_SELLER_API_URL", "http://localhost:9001")' in prefix

    def test_const_name_derived_from_service_name(self):
        services = {"quick-books-api": {"env_var": "QB_URL", "port": 8080}}
        prefix = build_wrapper_prefix(services)
        # constant name uses uppercased service name with hyphens -> underscores + _URL
        assert "QUICK_BOOKS_API_URL = os.environ.get" in prefix

    def test_scoped_apis_filters_constants(self):
        services = {
            "wanted-api": {"env_var": "WANTED_URL", "port": 1000},
            "other-api": {"env_var": "OTHER_URL", "port": 2000},
        }
        prefix = build_wrapper_prefix(services, scoped_apis=["wanted-api"])
        assert "WANTED_API_URL = os.environ.get" in prefix
        assert "OTHER_API_URL = os.environ.get" not in prefix

    def test_scoped_none_emits_all(self):
        services = {
            "a-api": {"env_var": "A_URL", "port": 1},
            "b-api": {"env_var": "B_URL", "port": 2},
        }
        prefix = build_wrapper_prefix(services, scoped_apis=None)
        assert "A_API_URL = os.environ.get" in prefix
        assert "B_API_URL = os.environ.get" in prefix

    def test_empty_scope_emits_no_constants(self):
        services = {"a-api": {"env_var": "A_URL", "port": 1}}
        prefix = build_wrapper_prefix(services, scoped_apis=[])
        # empty (but not None) scope filters out every service
        assert "A_API_URL = os.environ.get" not in prefix
        # helpers still present
        assert "def api_get" in prefix

    def test_prefix_is_valid_python(self):
        services = {"amazon-seller-api": {"env_var": "AMAZON_SELLER_API_URL", "port": 9001}}
        prefix = build_wrapper_prefix(services)
        ast.parse(prefix)


# ---------------------------------------------------------------------------
# generator.py — pure helpers
# ---------------------------------------------------------------------------

class TestStripCodeFences:
    def test_strips_python_fence(self):
        assert _strip_code_fences("```python\nfoo\nbar\n```") == "foo\nbar"

    def test_strips_bare_fence(self):
        assert _strip_code_fences("```\nfoo\n```") == "foo"

    def test_passthrough_without_fence(self):
        assert _strip_code_fences("just text") == "just text"

    def test_fence_open_without_newline(self):
        # startswith ``` but no newline -> ValueError path leaves text as-is
        assert _strip_code_fences("```nolineafterfence") == "```nolineafterfence"

    def test_strips_surrounding_whitespace(self):
        assert _strip_code_fences("   plain   ") == "plain"


class TestExtractJsonObject:
    def test_extracts_from_fenced_json(self):
        out = _extract_json_object('```json\n{"code": "x", "weights": {"a": 1}}\n```')
        assert out == {"code": "x", "weights": {"a": 1}}

    def test_extracts_first_brace_block(self):
        out = _extract_json_object('prefix {"k": 1} suffix')
        assert out == {"k": 1}

    def test_returns_none_when_no_brace(self):
        assert _extract_json_object("no json here at all") is None

    def test_returns_none_on_invalid_json(self):
        assert _extract_json_object("{not valid json}") is None

    def test_returns_none_for_json_list(self):
        # a bare list is valid JSON but not a dict -> None
        assert _extract_json_object("[1, 2, 3]") is None

    def test_greedy_match_spans_nested_braces(self):
        out = _extract_json_object('{"outer": {"inner": 2}}')
        assert out == {"outer": {"inner": 2}}


class TestCleanWeights:
    def test_keeps_only_allowed_int_weights(self):
        raw = {"a": 5, "b": 3, "c": 1, "neg": -3}
        assert _clean_weights(raw) == raw

    def test_drops_out_of_range_weights(self):
        assert _clean_weights({"a": 5, "b": 2, "c": 0, "d": 7}) == {"a": 5}

    def test_drops_non_int_values(self):
        assert _clean_weights({"a": 5, "b": "3", "c": 1.0}) == {"a": 5}

    def test_drops_non_string_keys(self):
        assert _clean_weights({1: 5, "ok": 3}) == {"ok": 3}

    def test_non_dict_returns_empty(self):
        assert _clean_weights("nope") == {}
        assert _clean_weights(None) == {}
        assert _clean_weights([("a", 5)]) == {}

    def test_bool_true_is_dropped_current_behavior(self):
        # bool is an int subclass; True == 1 which is in ALLOWED_WEIGHTS, so the
        # isinstance(w, int) + membership check keeps it.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        assert _clean_weights({"a": True}) == {"a": True}


class TestDeriveTaskOutputFormat:
    def test_non_list_is_unknown(self):
        assert _derive_task_output_format("notlist") == "unknown"
        assert _derive_task_output_format(None) == "unknown"

    def test_empty_list_is_unknown(self):
        assert _derive_task_output_format([]) == "unknown"

    def test_no_evaluation_targets_is_unknown(self):
        assert _derive_task_output_format([{"foo": "bar"}]) == "unknown"

    def test_dominant_final_answer_no_file(self):
        rubrics = [{"evaluation_target": "final_answer"}, {"evaluation_target": "final_answer"}]
        assert _derive_task_output_format(rubrics) == "final_answer"

    def test_dominant_workspace_artifact_no_text(self):
        rubrics = [{"evaluation_target": "workspace_artifact"}]
        assert _derive_task_output_format(rubrics) == "workspace_artifact"

    def test_file_output_dominant_maps_to_workspace_artifact(self):
        rubrics = [{"evaluation_target": "file_output"}, {"evaluation_target": "file_output"}]
        assert _derive_task_output_format(rubrics) == "workspace_artifact"

    def test_final_answer_with_file_is_mixed(self):
        rubrics = [
            {"evaluation_target": "final_answer"},
            {"evaluation_target": "workspace_artifact"},
        ]
        assert _derive_task_output_format(rubrics) == "mixed"

    def test_file_dominant_with_text_is_mixed(self):
        rubrics = [
            {"evaluation_target": "workspace_artifact"},
            {"evaluation_target": "workspace_artifact"},
            {"evaluation_target": "final_answer"},
        ]
        assert _derive_task_output_format(rubrics) == "mixed"

    def test_state_change_only_falls_through_to_mixed(self):
        # state_change is neither a file target nor final_answer, and dominant
        # doesn't match the two special cases, so it returns "mixed".
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        rubrics = [{"evaluation_target": "state_change"}]
        assert _derive_task_output_format(rubrics) == "mixed"

    def test_ignores_non_dict_and_blank_targets(self):
        rubrics = ["notadict", {"evaluation_target": ""}, {"evaluation_target": "final_answer"}]
        assert _derive_task_output_format(rubrics) == "final_answer"


class TestBuildUserMessage:
    def _base_kwargs(self):
        return dict(
            prompt="Do the thing.",
            task_toml="",
            services={},
            required_apis=[],
            distractor_apis=[],
            api_docs="",
            data_snapshot="",
            lint_failures=[],
            attempt=1,
        )

    def test_includes_prompt_and_no_services_notice(self):
        msg = _build_user_message(**self._base_kwargs())
        assert "Do the thing." in msg
        assert "No API services configured." in msg

    def test_final_answer_format_adds_text_only_block(self):
        kw = self._base_kwargs()
        kw["task_output_format"] = "final_answer"
        msg = _build_user_message(**kw)
        assert "TEXT-ONLY" in msg

    def test_workspace_artifact_format_adds_file_block(self):
        kw = self._base_kwargs()
        kw["task_output_format"] = "workspace_artifact"
        msg = _build_user_message(**kw)
        assert "FILE DELIVERABLES" in msg

    def test_mixed_format_block(self):
        kw = self._base_kwargs()
        kw["task_output_format"] = "mixed"
        msg = _build_user_message(**kw)
        assert "MIXED" in msg

    def test_required_and_distractor_tags(self):
        kw = self._base_kwargs()
        kw["services"] = {
            "req-api": {"env_var": "REQ_URL", "port": 100},
            "dist-api": {"env_var": "DIST_URL", "port": 200},
        }
        kw["required_apis"] = ["req-api"]
        kw["distractor_apis"] = ["dist-api"]
        msg = _build_user_message(**kw)
        assert "REQUIRED" in msg
        assert "DISTRACTOR" in msg
        assert "REQ_API_URL" in msg
        assert "DIST_API_URL" in msg

    def test_task_toml_embedded(self):
        kw = self._base_kwargs()
        kw["task_toml"] = "name = 'x'"
        msg = _build_user_message(**kw)
        assert "task.toml" in msg
        assert "name = 'x'" in msg

    def test_lint_failures_included(self):
        kw = self._base_kwargs()
        kw["lint_failures"] = ["L1: missing assert"]
        msg = _build_user_message(**kw)
        assert "LINT FAILURES" in msg
        assert "L1: missing assert" in msg

    def test_retry_banner_on_attempt_two(self):
        kw = self._base_kwargs()
        kw["lint_failures"] = ["L1: missing assert"]
        kw["attempt"] = 2
        msg = _build_user_message(**kw)
        assert "RETRY 2/" in msg

    def test_api_docs_and_snapshot_included(self):
        kw = self._base_kwargs()
        kw["api_docs"] = "GET /widgets"
        kw["data_snapshot"] = "widget_id=42"
        msg = _build_user_message(**kw)
        assert "GET /widgets" in msg
        assert "widget_id=42" in msg


# ---------------------------------------------------------------------------
# intent.py
# ---------------------------------------------------------------------------

class TestExtractPythonCode:
    def test_strips_python_fence(self):
        assert _extract_python_code("```python\nprint(1)\n```") == "print(1)"

    def test_strips_bare_fence(self):
        assert _extract_python_code("```\nprint(2)\n```") == "print(2)"

    def test_returns_stripped_when_no_fence(self):
        assert _extract_python_code("  plain code  ") == "plain code"

    def test_extracts_first_fenced_block(self):
        text = "intro\n```python\ncode_a\n```\ntrailing"
        assert _extract_python_code(text) == "code_a"


class TestLoadIntentSystemPrompt:
    def test_returns_loaded_prompt_when_present(self, monkeypatch):
        import src.utils.prompt_loader as pl

        monkeypatch.setattr(pl, "load_prompt", lambda name: "LOADED:%s" % name)
        assert _load_intent_system_prompt() == "LOADED:testgen_intent"

    def test_falls_back_to_default_on_not_found(self, monkeypatch):
        import src.utils.prompt_loader as pl

        def boom(name):
            raise pl.PromptNotFoundError("nope")

        monkeypatch.setattr(pl, "load_prompt", boom)
        assert _load_intent_system_prompt() == _DEFAULT_INTENT_PROMPT

    def test_falls_back_to_default_on_oserror(self, monkeypatch):
        import src.utils.prompt_loader as pl

        def boom(name):
            raise OSError("disk gone")

        monkeypatch.setattr(pl, "load_prompt", boom)
        assert _load_intent_system_prompt() == _DEFAULT_INTENT_PROMPT


class TestGenerateIntentTests:
    def test_no_prompt_returns_error(self, tmp_path):
        cfg = _cfg(_make_env_dir(tmp_path))
        res = generate_intent_tests({"task_id": "t"}, cfg)
        assert res.test_code == ""
        assert "no prompt" in res.error

    def test_happy_path_returns_extracted_code(self, tmp_path, monkeypatch):
        env_dir = _make_env_dir(tmp_path)
        cfg = _cfg(env_dir)

        captured = {}

        def fake_call(**kwargs):
            captured.update(kwargs)
            return "```python\ndef test_x():\n    assert True\n```", {
                "input_tokens": 3, "output_tokens": 4, "total_tokens": 7, "request_count": 1,
            }

        monkeypatch.setattr(intent_mod, "call_bedrock_converse", fake_call)
        res = generate_intent_tests(
            {"task_id": "t", "prompt": "call the seller API"}, cfg, task_toml="x=1"
        )
        assert res.error == ""
        assert res.test_code == "def test_x():\n    assert True"
        assert res.usage["total_tokens"] == 7
        # prompt + task_toml + service block make it into the user message
        assert "call the seller API" in captured["user_message"]
        assert "AMAZON_SELLER_API_URL" in captured["user_message"]
        assert "x=1" in captured["user_message"]

    def test_llm_exception_sets_error(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))

        def boom(**kwargs):
            raise RuntimeError("bedrock down")

        monkeypatch.setattr(intent_mod, "call_bedrock_converse", boom)
        res = generate_intent_tests({"task_id": "t", "prompt": "p"}, cfg)
        assert res.test_code == ""
        assert "bedrock down" in res.error

    def test_api_docs_included_in_user_message(self, tmp_path, monkeypatch):
        env_dir = _make_env_dir(tmp_path)
        (env_dir / "API_DOCUMENTATION.md").write_text("GET /seller/orders — list orders\n")
        cfg = _cfg(env_dir)

        captured = {}

        def fake_call(**kwargs):
            captured.update(kwargs)
            return "def test_x():\n    assert True\n", {
                "input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(intent_mod, "call_bedrock_converse", fake_call)
        res = generate_intent_tests({"task_id": "t", "prompt": "list orders"}, cfg)
        assert res.error == ""
        assert "Mock API Documentation" in captured["user_message"]
        assert "GET /seller/orders" in captured["user_message"]


# ---------------------------------------------------------------------------
# bedrock.py — call_bedrock_converse with httpx + eventstream mocked
# ---------------------------------------------------------------------------

class _FakeResp:
    def __init__(self, status=200, body=b"error-body"):
        self.status_code = status
        self._body = body

    def iter_bytes(self):
        # Real parsing is bypassed because iter_eventstream is monkeypatched.
        return iter([b"ignored"])

    def read(self):
        return self._body


class _FakeStreamCtx:
    def __init__(self, resp):
        self._resp = resp

    def __enter__(self):
        return self._resp

    def __exit__(self, *a):
        return False


class _FakeClient:
    captured: dict = {}

    def __init__(self, resp):
        self._resp = resp

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def stream(self, method, url, json=None, headers=None):
        _FakeClient.captured = dict(method=method, url=url, json=json, headers=headers)
        return _FakeStreamCtx(self._resp)


def _install_fake_httpx(monkeypatch, resp):
    monkeypatch.setattr(bedrock_mod.httpx, "Client", lambda **kw: _FakeClient(resp))


def _install_fake_eventstream(monkeypatch, events):
    import src.utils.bedrock_eventstream as bes

    def fake_iter(_bytes):
        for ev in events:
            yield ev

    monkeypatch.setattr(bes, "iter_eventstream", fake_iter)


class TestCallBedrockConverse:
    def test_missing_api_key_raises(self):
        with pytest.raises(RuntimeError, match="bearer token is empty"):
            bedrock_mod.call_bedrock_converse(
                api_key="", inference_arn="arn", region="r",
                system_prompt="s", user_message="u",
            )

    def test_missing_arn_raises(self):
        with pytest.raises(RuntimeError, match="inference ARN is empty"):
            bedrock_mod.call_bedrock_converse(
                api_key="k", inference_arn="", region="r",
                system_prompt="s", user_message="u",
            )

    def test_happy_path_aggregates_text_and_usage(self, monkeypatch):
        events = [
            ("contentBlockDelta", {"delta": {"text": "hello "}}),
            ("contentBlockDelta", {"delta": {"text": "world"}}),
            ("metadata", {"usage": {
                "inputTokens": 10, "outputTokens": 5,
                "cacheReadInputTokens": 2, "cacheWriteInputTokens": 3,
                "totalTokens": 20,
            }}),
        ]
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, events)

        text, usage = bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn:x", region="ap-south-1",
            system_prompt="sys", user_message="msg",
            max_tokens=100, temperature=0.5, top_p=0.9,
        )
        assert text == "hello world"
        assert usage["input_tokens"] == 10
        assert usage["output_tokens"] == 5
        assert usage["cache_read_tokens"] == 2
        assert usage["cache_write_tokens"] == 3
        assert usage["total_tokens"] == 20
        assert usage["request_count"] == 1
        # cost computed from published Opus rates
        expected = 10 * 5e-6 + 5 * 25e-6 + 2 * 5e-7 + 3 * 6.25e-6
        assert usage["cost_usd"] == pytest.approx(expected)

    def test_url_encodes_arn_into_path(self, monkeypatch):
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, [
            ("metadata", {"usage": {"inputTokens": 1, "outputTokens": 1}}),
        ])
        bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn:aws:x/y", region="ap-south-1",
            system_prompt="s", user_message="u",
        )
        url = _FakeClient.captured["url"]
        # ':' and '/' in the ARN are percent-encoded (safe="")
        assert "arn%3Aaws%3Ax%2Fy" in url
        assert url.startswith("https://bedrock-runtime.ap-south-1.amazonaws.com/model/")

    def test_system_prompt_adds_cachepoint(self, monkeypatch):
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, [
            ("metadata", {"usage": {"inputTokens": 1, "outputTokens": 1}}),
        ])
        bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn", region="r",
            system_prompt="the-system", user_message="u",
        )
        payload = _FakeClient.captured["json"]
        assert payload["system"] == [
            {"text": "the-system"},
            {"cachePoint": {"type": "default"}},
        ]

    def test_no_system_prompt_omits_system_block(self, monkeypatch):
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, [
            ("metadata", {"usage": {"inputTokens": 1, "outputTokens": 1}}),
        ])
        bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn", region="r",
            system_prompt="", user_message="u",
        )
        assert "system" not in _FakeClient.captured["json"]

    def test_temperature_and_top_p_optional(self, monkeypatch):
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, [
            ("metadata", {"usage": {"inputTokens": 1, "outputTokens": 1}}),
        ])
        bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn", region="r",
            system_prompt="s", user_message="u",
        )
        cfg = _FakeClient.captured["json"]["inferenceConfig"]
        assert "temperature" not in cfg
        assert "topP" not in cfg
        assert cfg["maxTokens"] == 4096

    def test_non_200_raises_runtime_error(self, monkeypatch):
        _install_fake_httpx(monkeypatch, _FakeResp(500, body=b"upstream boom"))
        _install_fake_eventstream(monkeypatch, [])
        with pytest.raises(RuntimeError, match="HTTP 500"):
            bedrock_mod.call_bedrock_converse(
                api_key="k", inference_arn="arn", region="r",
                system_prompt="s", user_message="u",
            )

    def test_service_exception_event_raises(self, monkeypatch):
        events = [
            ("contentBlockDelta", {"delta": {"text": "partial"}}),
            ("ThrottlingException", {"Message": "slow down"}),
        ]
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, events)
        with pytest.raises(RuntimeError, match="ThrottlingException"):
            bedrock_mod.call_bedrock_converse(
                api_key="k", inference_arn="arn", region="r",
                system_prompt="s", user_message="u",
            )

    def test_alt_cache_field_spellings_probed(self, monkeypatch):
        # snake_case cache field names should still populate cache counters.
        events = [
            ("metadata", {"usage": {
                "inputTokens": 4, "outputTokens": 2,
                "cache_read_input_tokens": 7,
                "cache_creation_input_tokens": 9,
            }}),
        ]
        _install_fake_httpx(monkeypatch, _FakeResp(200))
        _install_fake_eventstream(monkeypatch, events)
        _text, usage = bedrock_mod.call_bedrock_converse(
            api_key="k", inference_arn="arn", region="r",
            system_prompt="s", user_message="u",
        )
        assert usage["cache_read_tokens"] == 7
        assert usage["cache_write_tokens"] == 9
        # total falls back to the sum when totalTokens absent
        assert usage["total_tokens"] == 4 + 2 + 7 + 9

    def test_testgen_cost_helper_zero_tokens(self):
        assert bedrock_mod._testgen_cost_usd(0, 0, 0, 0) == 0.0

    def test_testgen_cost_helper_matches_rates(self):
        got = bedrock_mod._testgen_cost_usd(1_000_000, 0, 0, 0)
        assert got == pytest.approx(5.0)  # $5 / MTok input


# ---------------------------------------------------------------------------
# generator.py — full generate_task_tests flow
# ---------------------------------------------------------------------------

class TestGenerateTaskTests:
    def test_no_prompt_uses_fallback(self, tmp_path):
        cfg = _cfg(_make_env_dir(tmp_path))
        res = generate_task_tests({"task_id": "t"}, cfg)
        assert res.used_fallback is True
        assert res.error == "no prompt available for test generation"
        assert SAFE_FALLBACK_STUB in res.test_code
        assert res.test_weights == dict(FALLBACK_WEIGHTS)

    def test_system_prompt_load_failure_uses_fallback(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))

        def boom(name):
            raise FileNotFoundError("no prompt file")

        monkeypatch.setattr(gen_mod, "_load_prompt", boom)
        res = generate_task_tests({"task_id": "t", "prompt": "do it"}, cfg)
        assert res.used_fallback is True
        assert "failed to load testgen_system prompt" in res.error
        assert SAFE_FALLBACK_STUB in res.test_code

    def test_happy_path_clean_draft_no_lints(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYSTEM PROMPT")
        # a clean draft with a behavioral test + a distractor test that passes lints
        good_code = (
            "class TestBehavioralUsedSeller:\n"
            "    def test_seller_called(self):\n"
            "        reqs = api_get(AMAZON_SELLER_API_URL, '/audit/requests')\n"
            "        assert len(reqs) >= 1\n"
        )
        payload = '{"code": %r, "weights": {"test_seller_called": 5}}' % good_code

        calls = {"n": 0}

        def fake_call(**kwargs):
            calls["n"] += 1
            return payload, {"input_tokens": 1, "output_tokens": 1,
                             "total_tokens": 2, "request_count": 1, "cost_usd": 0.001}

        # force zero lints so the loop breaks after attempt 1
        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        monkeypatch.setattr(gen_mod, "self_validate_tests",
                            lambda *a, **k: [])

        res = generate_task_tests(
            {"task_id": "t", "prompt": "use the amazon seller api",
             "required_apis": ["amazon-seller-api"]},
            cfg,
        )
        assert res.used_fallback is False
        assert res.attempts == 1
        assert calls["n"] == 1
        assert "test_seller_called" in res.test_code
        assert res.test_weights == {"test_seller_called": 5}
        # wrapper prefix was prepended
        assert "def api_get" in res.test_code
        assert res.usage["total_tokens"] == 2

    def test_retries_until_attempt_budget_then_keeps_best(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        payload = '{"code": "class TestA:\\n    def test_x(self):\\n        assert 1\\n", "weights": {"test_x": 1}}'

        calls = {"n": 0}

        def fake_call(**kwargs):
            calls["n"] += 1
            return payload, {"input_tokens": 1, "output_tokens": 1,
                             "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        # always one lint failure -> never breaks early, exhausts the budget
        monkeypatch.setattr(gen_mod, "self_validate_tests",
                            lambda *a, **k: ["L1: still bad"])

        res = generate_task_tests(
            {"task_id": "t", "prompt": "p", "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=2,
        )
        assert calls["n"] == 2
        assert res.attempts == 2
        assert res.lint_failures == ["L1: still bad"]
        assert res.used_fallback is False
        assert "test_x" in res.test_code

    def test_llm_fails_after_good_draft_breaks_and_keeps_best(self, tmp_path, monkeypatch):
        # Attempt 1 returns a draft (with a lint failure so the loop continues);
        # attempt 2 raises. Because best_code is already set, the loop breaks and
        # the earlier draft is kept rather than falling back.
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        payload = (
            '{"code": "class TestA:\\n    def test_x(self):\\n        assert 1\\n",'
            ' "weights": {"test_x": 1}}'
        )
        calls = {"n": 0}

        def fake_call(**kwargs):
            calls["n"] += 1
            if calls["n"] == 1:
                return payload, {"input_tokens": 1, "output_tokens": 1,
                                 "total_tokens": 2, "request_count": 1}
            raise RuntimeError("bedrock hiccup on retry")

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        # one lint failure on attempt 1 so the loop does not break early
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: ["L1"])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "p", "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=3,
        )
        assert calls["n"] == 2  # broke out after the 2nd (failing) call
        assert res.used_fallback is False
        assert "test_x" in res.test_code

    def test_all_llm_calls_fail_uses_fallback(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")

        def boom(**kwargs):
            raise RuntimeError("bedrock unavailable")

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", boom)
        res = generate_task_tests({"task_id": "t", "prompt": "p"}, cfg, max_attempts=2)
        assert res.used_fallback is True
        assert SAFE_FALLBACK_STUB in res.test_code
        assert res.test_weights == dict(FALLBACK_WEIGHTS)

    def test_unparseable_best_draft_falls_back_at_final_repair(self, tmp_path, monkeypatch):
        # best_code gets set (sanitize keeps a `def test_`), but the code is
        # invalid python that auto_repair cannot fix, so the final-repair
        # branch swaps in SAFE_FALLBACK_STUB.
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        import json as _json
        # missing ':' after class header -> unrepairable SyntaxError
        broken = "class T\n    def test_x(self):\n        assert 1\n"
        payload = _json.dumps({"code": broken, "weights": {"test_x": 1}})

        def fake_call(**kwargs):
            return payload, {"input_tokens": 1, "output_tokens": 1,
                             "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        # accept the draft through lints so best_code is set
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: [])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "p", "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=1,
        )
        assert res.used_fallback is True
        assert SAFE_FALLBACK_STUB in res.test_code
        assert res.test_weights == dict(FALLBACK_WEIGHTS)

    def test_no_json_in_response_falls_back(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")

        def fake_call(**kwargs):
            return "sorry, no JSON here", {"input_tokens": 1, "output_tokens": 1,
                                           "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        res = generate_task_tests({"task_id": "t", "prompt": "p"}, cfg, max_attempts=1)
        # never produced usable code -> fallback
        assert res.used_fallback is True
        assert SAFE_FALLBACK_STUB in res.test_code

    def test_empty_code_in_json_falls_back(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")

        def fake_call(**kwargs):
            return '{"code": "", "weights": {}}', {
                "input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        res = generate_task_tests({"task_id": "t", "prompt": "p"}, cfg, max_attempts=1)
        assert res.used_fallback is True

    def test_raw_weight_reinstate_fallback_keeps_out_of_range_ints(self, tmp_path, monkeypatch):
        # generator.py:451-454 — when _clean_weights drops everything (all
        # weights out of the allowed set) but raw_weights is a dict, the raw
        # int weights are reinstated so downstream sees *something*.
        # NOTE: pins current behavior — see SCORING_AUDIT_REPORT.md
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        import json as _json
        good_code = "class TestA:\n    def test_x(self):\n        assert 1\n"
        # weight 7 is NOT in ALLOWED_WEIGHTS, so _clean_weights returns {}
        payload = _json.dumps({"code": good_code, "weights": {"test_x": 7}})

        def fake_call(**kwargs):
            return payload, {"input_tokens": 1, "output_tokens": 1,
                             "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: [])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "p", "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=1,
        )
        # out-of-range weight survives via the raw-weight reinstate fallback
        assert res.test_weights == {"test_x": 7}

    def test_truncated_code_is_auto_repaired(self, tmp_path, monkeypatch):
        cfg = _cfg(_make_env_dir(tmp_path))
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        import json as _json
        # Missing closing paren -> SyntaxError -> auto_repair path exercised.
        truncated = "class TestA:\n    def test_x(self):\n        assert max(1, 2\n"
        payload = _json.dumps({"code": truncated, "weights": {"test_x": 1}})

        def fake_call(**kwargs):
            return payload, {"input_tokens": 1, "output_tokens": 1,
                             "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: [])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "p", "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=1,
        )
        assert res.used_fallback is False
        # assembled file must be valid python after repair
        ast.parse(res.test_code)

    def test_required_apis_from_precomputed_list(self, tmp_path, monkeypatch):
        env_dir = _make_env_dir(tmp_path, services={
            "amazon-seller-api": (9001, "AMAZON_SELLER_API_URL"),
            "stripe-api": (9002, "STRIPE_API_URL"),
        })
        cfg = _cfg(env_dir)
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")

        seen = {}

        def fake_call(**kwargs):
            seen["user_message"] = kwargs["user_message"]
            return '{"code": "class T:\\n    def test_a(self):\\n        assert 1\\n", "weights": {"test_a": 1}}', {
                "input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: [])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "generic prompt with no api names",
             "required_apis": ["amazon-seller-api"]},
            cfg, max_attempts=1,
        )
        # precomputed required_apis should surface in the prompt as REQUIRED
        assert "REQUIRED" in seen["user_message"]
        assert "amazon-seller-api" in seen["user_message"]
        assert res.used_fallback is False


    def test_required_apis_discovered_from_mock_data_subdir(self, tmp_path, monkeypatch):
        # No precomputed required_apis and infer_required_apis returns []; the
        # last-resort scan of task_dir/mock_data/<api>/ (that matches a known
        # service) supplies the required API.
        env_dir = _make_env_dir(tmp_path)
        cfg = _cfg(env_dir)
        monkeypatch.setattr(gen_mod, "_load_prompt", lambda name: "SYS")
        monkeypatch.setattr(gen_mod, "infer_required_apis", lambda *a, **k: [])

        # build a task_dir with mock_data/amazon-seller-api/
        task_dir = tmp_path / "task"
        (task_dir / "mock_data" / "amazon-seller-api").mkdir(parents=True)

        seen = {}

        def fake_call(**kwargs):
            seen["user_message"] = kwargs["user_message"]
            return (
                '{"code": "class T:\\n    def test_a(self):\\n        assert 1\\n",'
                ' "weights": {"test_a": 1}}'
            ), {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2, "request_count": 1}

        monkeypatch.setattr(gen_mod, "call_bedrock_converse", fake_call)
        monkeypatch.setattr(gen_mod, "self_validate_tests", lambda *a, **k: [])
        res = generate_task_tests(
            {"task_id": "t", "prompt": "some prompt with no api names",
             "task_dir": str(task_dir)},
            cfg, max_attempts=1,
        )
        assert res.used_fallback is False
        # amazon-seller-api surfaced as REQUIRED via the mock_data scan
        assert "amazon-seller-api" in seen["user_message"]
        assert "REQUIRED" in seen["user_message"]


class TestLoadPrompt:
    def test_load_prompt_reads_real_testgen_system(self):
        # _load_prompt delegates to prompt_loader.load_prompt against the real
        # system_prompts/ dir; testgen_system.md ships in the repo.
        text = gen_mod._load_prompt("testgen_system")
        assert isinstance(text, str)
        assert text.strip()  # non-empty


class TestTestGenResultDataclass:
    def test_weights_json_property_serializes(self):
        r = _TestGenResult(test_code="x", test_weights={"a": 5, "b": -3})
        js = r.test_weights_json
        import json as _json
        assert _json.loads(js) == {"a": 5, "b": -3}

    def test_defaults(self):
        r = _TestGenResult(test_code="")
        assert r.attempts == 0
        assert r.used_fallback is False
        assert r.error == ""
        assert r.usage["input_tokens"] == 0
        assert r.lint_failures == []
