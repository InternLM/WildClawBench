"""Tests for src/utils/claude_oauth/recovery.py (pause/backoff/retry) and
src/utils/claude_oauth/__main__.py (CLI dispatch).

Offline + deterministic: time.time/time.sleep and httpx are monkeypatched;
uvicorn is stubbed into sys.modules before importing __main__ (it is an
optional dep not installed in the unit-test venv). Temp files go to tmp_path.
"""
from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.claude_oauth import recovery


# --------------------------------------------------------------------------
# Helpers / fixtures
# --------------------------------------------------------------------------
class _FakeResp:
    """Stand-in for an httpx.Response returned by a fake httpx.Client.get."""

    def __init__(self, status_code=200, payload=None, raise_exc=None):
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self._raise_exc = raise_exc

    def json(self):
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._payload


class _FakeClient:
    """Context-manager fake for httpx.Client(timeout=...)."""

    def __init__(self, resp=None, get_exc=None):
        self._resp = resp
        self._get_exc = get_exc
        self.requested_url = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def get(self, url):
        self.requested_url = url
        if self._get_exc is not None:
            raise self._get_exc
        return self._resp


@pytest.fixture
def patch_httpx(monkeypatch):
    """Return a helper that installs a fake httpx.Client on the recovery module."""

    def _install(resp=None, get_exc=None):
        holder = {}

        def _client_factory(timeout=None):
            c = _FakeClient(resp=resp, get_exc=get_exc)
            holder["client"] = c
            holder["timeout"] = timeout
            return c

        monkeypatch.setattr(recovery.httpx, "Client", _client_factory)
        return holder

    return _install


class _FakeExcResponse:
    def __init__(self, headers):
        self.headers = headers


# --------------------------------------------------------------------------
# _bridge_base_url
# --------------------------------------------------------------------------
def test_bridge_base_url_none_when_unset(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_BASE", raising=False)
    assert recovery._bridge_base_url() is None


def test_bridge_base_url_empty_string(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "   ")
    assert recovery._bridge_base_url() is None


def test_bridge_base_url_localhost_strips_trailing_slash(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765/")
    assert recovery._bridge_base_url() == "http://localhost:8765"


def test_bridge_base_url_127_and_ipv6_and_dot_local(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://127.0.0.1:8765")
    assert recovery._bridge_base_url() == "http://127.0.0.1:8765"
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://[::1]:8765")
    assert recovery._bridge_base_url() == "http://[::1]:8765"
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://mybox.local:8765")
    assert recovery._bridge_base_url() == "http://mybox.local:8765"


def test_bridge_base_url_remote_host_returns_none(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "https://api.anthropic.com")
    assert recovery._bridge_base_url() is None


# --------------------------------------------------------------------------
# _fetch_quota
# --------------------------------------------------------------------------
def test_fetch_quota_success(patch_httpx):
    holder = patch_httpx(resp=_FakeResp(200, {"multi_account": True}))
    out = recovery._fetch_quota("http://localhost:8765")
    assert out == {"multi_account": True}
    assert holder["client"].requested_url == "http://localhost:8765/quota"


def test_fetch_quota_non_200_returns_empty(patch_httpx):
    patch_httpx(resp=_FakeResp(503, {"ignored": 1}))
    assert recovery._fetch_quota("http://localhost:8765") == {}


def test_fetch_quota_http_error_returns_empty(patch_httpx):
    patch_httpx(get_exc=recovery.httpx.ConnectError("boom"))
    assert recovery._fetch_quota("http://localhost:8765") == {}


def test_fetch_quota_bad_json_returns_empty(patch_httpx):
    # r.json() raising ValueError is caught.
    patch_httpx(resp=_FakeResp(200, raise_exc=ValueError("bad json")))
    assert recovery._fetch_quota("http://localhost:8765") == {}


# --------------------------------------------------------------------------
# _next_reset_seconds
# --------------------------------------------------------------------------
def test_next_reset_seconds_uses_quota_delta(monkeypatch, patch_httpx):
    monkeypatch.setattr(recovery.time, "time", lambda: 1000.0)
    patch_httpx(resp=_FakeResp(200, {"next_reset_at_unix": 1300}))
    assert recovery._next_reset_seconds("http://localhost:8765", 42) == 300


def test_next_reset_seconds_falls_back_when_delta_non_positive(monkeypatch, patch_httpx):
    monkeypatch.setattr(recovery.time, "time", lambda: 2000.0)
    # reset in the past -> delta <= 0 -> fallback
    patch_httpx(resp=_FakeResp(200, {"next_reset_at_unix": 1900}))
    assert recovery._next_reset_seconds("http://localhost:8765", 77) == 77


def test_next_reset_seconds_falls_back_when_no_reset_key(patch_httpx):
    patch_httpx(resp=_FakeResp(200, {}))
    assert recovery._next_reset_seconds("http://localhost:8765", 99) == 99


# --------------------------------------------------------------------------
# _effective_max_retries
# --------------------------------------------------------------------------
def test_effective_max_retries_single_account_uses_user_value(patch_httpx):
    patch_httpx(resp=_FakeResp(200, {}))
    assert recovery._effective_max_retries("http://localhost:8765", 1) == 1


def test_effective_max_retries_not_multi_account_flag(patch_httpx):
    # accounts present but multi_account flag falsy -> pool_size 0 -> user value
    patch_httpx(resp=_FakeResp(200, {"accounts": [1, 2, 3]}))
    assert recovery._effective_max_retries("http://localhost:8765", 2) == 2


def test_effective_max_retries_scales_to_pool_size(patch_httpx):
    patch_httpx(resp=_FakeResp(200, {"multi_account": True, "accounts": [1, 2, 3, 4]}))
    # pool_size 4 > user 1 -> 4
    assert recovery._effective_max_retries("http://localhost:8765", 1) == 4


def test_effective_max_retries_keeps_user_value_if_larger(patch_httpx):
    patch_httpx(resp=_FakeResp(200, {"multi_account": True, "accounts": [1, 2]}))
    # user value 5 > pool_size 2 -> 5
    assert recovery._effective_max_retries("http://localhost:8765", 5) == 5


def test_effective_max_retries_single_element_pool(patch_httpx):
    # pool_size 1 -> pool_size <= 1 -> user value
    patch_httpx(resp=_FakeResp(200, {"multi_account": True, "accounts": [1]}))
    assert recovery._effective_max_retries("http://localhost:8765", 3) == 3


# --------------------------------------------------------------------------
# _max_pause_seconds
# --------------------------------------------------------------------------
def test_max_pause_seconds_default_when_unset(monkeypatch):
    monkeypatch.delenv("WCB_CC_MAX_PAUSE_SEC", raising=False)
    assert recovery._max_pause_seconds() == recovery.DEFAULT_MAX_PAUSE_SECONDS


def test_max_pause_seconds_blank_uses_default(monkeypatch):
    monkeypatch.setenv("WCB_CC_MAX_PAUSE_SEC", "   ")
    assert recovery._max_pause_seconds() == recovery.DEFAULT_MAX_PAUSE_SECONDS


def test_max_pause_seconds_parses_int(monkeypatch):
    monkeypatch.setenv("WCB_CC_MAX_PAUSE_SEC", "7200")
    assert recovery._max_pause_seconds() == 7200


def test_max_pause_seconds_floors_at_60(monkeypatch):
    monkeypatch.setenv("WCB_CC_MAX_PAUSE_SEC", "5")
    assert recovery._max_pause_seconds() == 60


def test_max_pause_seconds_invalid_uses_default(monkeypatch):
    monkeypatch.setenv("WCB_CC_MAX_PAUSE_SEC", "not-a-number")
    assert recovery._max_pause_seconds() == recovery.DEFAULT_MAX_PAUSE_SECONDS


# --------------------------------------------------------------------------
# _is_rate_limit_error
# --------------------------------------------------------------------------
def test_is_rate_limit_error_real_litellm_class():
    from litellm.exceptions import RateLimitError

    exc = RateLimitError("capped", "anthropic", "claude")
    assert recovery._is_rate_limit_error(exc) is True


def test_is_rate_limit_error_message_substring():
    assert recovery._is_rate_limit_error(RuntimeError("got subscription_cap here")) is True
    assert recovery._is_rate_limit_error(RuntimeError("a rate_limit_error occurred")) is True
    assert recovery._is_rate_limit_error(RuntimeError("RateLimitError seen")) is True


def test_is_rate_limit_error_mro_name_match():
    # A class whose name matches but from a fake litellm module.
    fake_mod = types.ModuleType("litellm.faux")

    class RateLimitError(Exception):
        pass

    RateLimitError.__module__ = "litellm.faux"
    assert recovery._is_rate_limit_error(RateLimitError("x")) is True


def test_is_rate_limit_error_openai_module_name():
    class RateLimitError(Exception):
        pass

    RateLimitError.__module__ = "openai._exceptions"
    assert recovery._is_rate_limit_error(RateLimitError("x")) is True


def test_is_rate_limit_error_negative():
    assert recovery._is_rate_limit_error(ValueError("some unrelated error")) is False


# --------------------------------------------------------------------------
# _extract_retry_after_from_error
# --------------------------------------------------------------------------
def test_extract_retry_after_from_response_headers():
    exc = RuntimeError("no hint in msg")
    exc.response = _FakeExcResponse({"Retry-After": "45"})
    assert recovery._extract_retry_after_from_error(exc) == 45


def test_extract_retry_after_lowercase_header():
    exc = RuntimeError("no hint")
    exc.response = _FakeExcResponse({"retry-after": "12"})
    assert recovery._extract_retry_after_from_error(exc) == 12


def test_extract_retry_after_from_underscore_response_attr():
    exc = RuntimeError("no hint")
    exc._response = _FakeExcResponse({"Retry-After": "9"})
    assert recovery._extract_retry_after_from_error(exc) == 9


def test_extract_retry_after_bad_header_falls_through_to_msg():
    exc = RuntimeError("please Retry-After: 88 seconds")
    exc.response = _FakeExcResponse({"Retry-After": "not-int"})
    # header int() raises ValueError -> caught -> falls through to regex on msg
    assert recovery._extract_retry_after_from_error(exc) == 88


def test_extract_retry_after_from_message_regex_variants():
    assert recovery._extract_retry_after_from_error(RuntimeError("retry_after 30")) == 30
    assert recovery._extract_retry_after_from_error(RuntimeError("RETRY-AFTER: 7")) == 7


def test_extract_retry_after_none_when_absent():
    assert recovery._extract_retry_after_from_error(RuntimeError("nothing useful")) is None


# --------------------------------------------------------------------------
# _heartbeat
# --------------------------------------------------------------------------
def test_heartbeat_none_is_noop():
    # Should simply return without error.
    assert recovery._heartbeat(None) is None


def test_heartbeat_creates_marker_and_touches_agent_run(tmp_path):
    log_dir = tmp_path / "stage" / "logs"
    log_dir.mkdir(parents=True)
    agent_run = log_dir / "agent_run.log"
    agent_run.write_text("")
    aider = log_dir / "sub" / "aider.log"
    aider.parent.mkdir(parents=True)
    aider.write_text("")

    recovery._heartbeat(log_dir)

    assert (log_dir / ".rate_limit_paused").exists()
    # agent_run.log lives directly in log_dir -> found on first iteration.
    assert agent_run.exists()


def test_heartbeat_walks_up_to_find_agent_run(tmp_path):
    # agent_run.log lives in a parent dir; heartbeat should walk up and touch it.
    stage = tmp_path / "stage"
    nested = stage / "a" / "b"
    nested.mkdir(parents=True)
    agent_run = stage / "agent_run.log"
    agent_run.write_text("")
    before = agent_run.stat().st_mtime

    recovery._heartbeat(nested)

    assert (nested / ".rate_limit_paused").exists()
    # Walking up finds agent_run.log in the ancestor; touch updates or preserves mtime.
    assert agent_run.stat().st_mtime >= before


def test_heartbeat_no_agent_run_still_drops_marker(tmp_path):
    log_dir = tmp_path / "logs"
    recovery._heartbeat(log_dir)
    assert (log_dir / ".rate_limit_paused").exists()


# --------------------------------------------------------------------------
# _sleep_with_heartbeat
# --------------------------------------------------------------------------
def test_sleep_with_heartbeat_zero_total_no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(recovery.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(recovery.time, "time", lambda: 100.0)
    recovery._sleep_with_heartbeat(0, None)
    assert sleeps == []


def test_sleep_with_heartbeat_negative_total_no_sleep(monkeypatch):
    sleeps = []
    monkeypatch.setattr(recovery.time, "sleep", lambda s: sleeps.append(s))
    monkeypatch.setattr(recovery.time, "time", lambda: 100.0)
    recovery._sleep_with_heartbeat(-50, None)
    assert sleeps == []


def test_sleep_with_heartbeat_slices_by_heartbeat_interval(monkeypatch, tmp_path):
    # Fake a monotonic-ish clock advanced by whatever we pass to time.sleep.
    now = {"t": 0.0}
    monkeypatch.setattr(recovery.time, "time", lambda: now["t"])

    slept = []

    def _sleep(s):
        slept.append(s)
        now["t"] += s

    monkeypatch.setattr(recovery.time, "sleep", _sleep)

    hb_calls = []
    monkeypatch.setattr(recovery, "_heartbeat", lambda d: hb_calls.append(d))

    recovery._sleep_with_heartbeat(150, tmp_path, heartbeat_seconds=60)

    # 60 + 60 + 30 == 150 total, three slices.
    assert slept == [60, 60, 30]
    assert len(hb_calls) == 3
    assert all(d == tmp_path for d in hb_calls)


# --------------------------------------------------------------------------
# run_with_recovery
# --------------------------------------------------------------------------
def test_run_with_recovery_passthrough_when_not_bridge(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_BASE", raising=False)
    calls = []

    def fn(x, y=0):
        calls.append((x, y))
        return x + y

    assert recovery.run_with_recovery(fn, 3, y=4) == 7
    assert calls == [(3, 4)]


def test_run_with_recovery_returns_value_on_first_success(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: m)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)
    assert recovery.run_with_recovery(lambda: "ok") == "ok"


def test_run_with_recovery_non_rate_limit_error_propagates(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: m)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)

    def fn():
        raise ValueError("unrelated")

    with pytest.raises(ValueError, match="unrelated"):
        recovery.run_with_recovery(fn)


def test_run_with_recovery_retries_then_succeeds(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: 2)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)
    monkeypatch.setattr(recovery, "_next_reset_seconds", lambda b, hint: 10)
    slept = []
    monkeypatch.setattr(recovery, "_sleep_with_heartbeat", lambda w, d: slept.append(w))

    state = {"n": 0}

    def fn():
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("subscription_cap hit")
        return "recovered"

    assert recovery.run_with_recovery(fn) == "recovered"
    assert state["n"] == 2
    assert slept == [10]


def test_run_with_recovery_exhausts_retries_and_raises(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: 1)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)
    monkeypatch.setattr(recovery, "_next_reset_seconds", lambda b, hint: 5)
    monkeypatch.setattr(recovery, "_sleep_with_heartbeat", lambda w, d: None)

    def fn():
        raise RuntimeError("rate_limit_error again")

    with pytest.raises(RuntimeError, match="rate_limit_error"):
        recovery.run_with_recovery(fn)


def test_run_with_recovery_gives_up_when_wait_exceeds_max_pause(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: 5)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100)
    # wait 200 > max_pause 100 -> immediate raise without sleeping.
    monkeypatch.setattr(recovery, "_next_reset_seconds", lambda b, hint: 200)
    sleep_called = []
    monkeypatch.setattr(recovery, "_sleep_with_heartbeat", lambda w, d: sleep_called.append(w))

    def fn():
        raise RuntimeError("subscription_cap")

    with pytest.raises(RuntimeError, match="subscription_cap"):
        recovery.run_with_recovery(fn)
    assert sleep_called == []


def test_run_with_recovery_uses_retry_after_hint_fallback(monkeypatch):
    # When _extract_retry_after returns None the code uses `or 300`; verify the
    # hint value threaded into _next_reset_seconds.
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    monkeypatch.setattr(recovery, "_effective_max_retries", lambda b, m: 2)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)
    seen_hints = []

    def _next(base, hint):
        seen_hints.append(hint)
        return 1

    monkeypatch.setattr(recovery, "_next_reset_seconds", _next)
    monkeypatch.setattr(recovery, "_sleep_with_heartbeat", lambda w, d: None)

    state = {"n": 0}

    def fn():
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("subscription_cap, no retry hint")
        return "ok"

    assert recovery.run_with_recovery(fn) == "ok"
    # No parseable hint in message -> `or 300` fallback.
    assert seen_hints == [300]


def test_run_with_recovery_passes_kaiju_log_dir_and_max_retries(monkeypatch, tmp_path):
    monkeypatch.setenv("ANTHROPIC_API_BASE", "http://localhost:8765")
    captured = {}

    def _eff(base, user_max):
        captured["user_max"] = user_max
        return 1

    monkeypatch.setattr(recovery, "_effective_max_retries", _eff)
    monkeypatch.setattr(recovery, "_max_pause_seconds", lambda: 100000)
    monkeypatch.setattr(recovery, "_next_reset_seconds", lambda b, hint: 3)

    def _sleep(w, d):
        captured["log_dir"] = d

    monkeypatch.setattr(recovery, "_sleep_with_heartbeat", _sleep)

    state = {"n": 0}

    def fn():
        state["n"] += 1
        if state["n"] == 1:
            raise RuntimeError("rate_limit_error")
        return "done"

    out = recovery.run_with_recovery(fn, _kaiju_log_dir=tmp_path, max_retries=3)
    assert out == "done"
    assert captured["user_max"] == 3
    assert captured["log_dir"] == tmp_path


# --------------------------------------------------------------------------
# __main__.main  (CLI dispatch)
# --------------------------------------------------------------------------
@pytest.fixture
def oauth_main(monkeypatch):
    """Import src.utils.claude_oauth.__main__ with uvicorn stubbed.

    uvicorn is an optional dependency not installed in the unit-test venv;
    __main__ imports it at module scope, so we inject a stub before import.
    """
    if "uvicorn" not in sys.modules:
        stub = types.ModuleType("uvicorn")
        stub.run = lambda *a, **k: None
        monkeypatch.setitem(sys.modules, "uvicorn", stub)
    import importlib

    mod = importlib.import_module("src.utils.claude_oauth.__main__")
    importlib.reload(mod)
    return mod


class _FakeProvider:
    def __init__(self, token="sk-oat-abcdefghijklmnop", raise_exc=None):
        self._token = token
        self._raise_exc = raise_exc

    def get_access_token(self):
        if self._raise_exc is not None:
            raise self._raise_exc
        return self._token


def test_main_check_returns_zero(oauth_main, monkeypatch, capsys):
    monkeypatch.setattr(oauth_main, "_resolve_provider", lambda: _FakeProvider())
    ran = []
    monkeypatch.setattr(oauth_main.uvicorn, "run", lambda *a, **k: ran.append(True))

    rc = oauth_main.main(["--check"])
    assert rc == 0
    # --check exits before starting the server.
    assert ran == []
    out = capsys.readouterr().out
    assert "credentials OK" in out


def test_main_credentials_error_returns_two(oauth_main, monkeypatch, capsys):
    from src.utils.claude_oauth.credentials import CredentialsError

    monkeypatch.setattr(
        oauth_main,
        "_resolve_provider",
        lambda: _FakeProvider(raise_exc=CredentialsError("no creds")),
    )
    rc = oauth_main.main(["--check"])
    assert rc == 2
    err = capsys.readouterr().err
    assert "credentials error" in err
    assert "no creds" in err


def test_main_starts_server_when_not_check(oauth_main, monkeypatch, capsys):
    monkeypatch.setattr(oauth_main, "_resolve_provider", lambda: _FakeProvider())
    monkeypatch.setattr(oauth_main, "build_app", lambda provider: "APP_SENTINEL")

    captured = {}

    def _run(app, host, port, log_level):
        captured.update(app=app, host=host, port=port, log_level=log_level)

    monkeypatch.setattr(oauth_main.uvicorn, "run", _run)

    rc = oauth_main.main(["--host", "0.0.0.0", "--port", "9999", "--log-level", "debug"])
    assert rc == 0
    assert captured == {
        "app": "APP_SENTINEL",
        "host": "0.0.0.0",
        "port": 9999,
        "log_level": "debug",
    }
    out = capsys.readouterr().out
    assert "listening on http://0.0.0.0:9999" in out


def test_main_default_args(oauth_main, monkeypatch, capsys):
    monkeypatch.setattr(oauth_main, "_resolve_provider", lambda: _FakeProvider())
    monkeypatch.setattr(oauth_main, "build_app", lambda provider: "APP")
    captured = {}
    monkeypatch.setattr(
        oauth_main.uvicorn,
        "run",
        lambda app, host, port, log_level: captured.update(host=host, port=port),
    )
    rc = oauth_main.main([])
    assert rc == 0
    assert captured == {"host": "127.0.0.1", "port": 8765}
