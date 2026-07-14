"""Tests for src/utils/claude_oauth/credentials.py — file-pool credentials."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils.claude_oauth.credentials import (
    OAuthCredentials,
    _AccountSlot,
    _FileCredentialProvider,
    MultiAccountCredentialProvider,
    load_account_pool,
)


def _write_creds(tmp_path: Path, name: str, expires_at_ms: int, access: str = "sk-oat-fresh") -> Path:
    p = tmp_path / name
    payload = {
        "claudeAiOauth": {
            "accessToken": access,
            "refreshToken": "rt_test_" + access,
            "expiresAt": expires_at_ms,
            "scopes": ["user:inference"],
            "subscriptionType": "max",
        }
    }
    p.write_text(json.dumps(payload))
    return p


def test_oauth_credentials_is_expired_when_past():
    creds = OAuthCredentials(
        access_token="a",
        refresh_token="r",
        expires_at_ms=int((time.time() - 3600) * 1000),
        scopes=(),
        subscription_type="max",
    )
    assert creds.is_expired()


def test_oauth_credentials_not_expired_when_future():
    creds = OAuthCredentials(
        access_token="a",
        refresh_token="r",
        expires_at_ms=int((time.time() + 3600) * 1000),
        scopes=(),
        subscription_type="max",
    )
    assert not creds.is_expired()


def test_oauth_credentials_expiry_leeway():
    creds = OAuthCredentials(
        access_token="a",
        refresh_token="r",
        expires_at_ms=int((time.time() + 30) * 1000),
        scopes=(),
        subscription_type="max",
    )
    assert creds.is_expired(leeway_seconds=60)


def test_file_provider_reads_valid_file(tmp_path: Path):
    p = _write_creds(tmp_path, "acct.json", int((time.time() + 3600) * 1000))
    provider = _FileCredentialProvider(str(p))
    token = provider.get_access_token()
    assert token == "sk-oat-fresh"


def test_account_slot_availability():
    class _P:
        def token_prefix(self): return "pfx"
    slot = _AccountSlot(provider=_P(), label="a")
    assert slot.is_available(time.time())
    slot.exhausted_until = time.time() + 3600
    assert not slot.is_available(time.time())
    slot.exhausted_until = 0.0
    slot.invalid = True
    assert not slot.is_available(time.time())


def test_multi_account_selects_first_available(tmp_path: Path):
    p1 = _write_creds(tmp_path, "acct1.json", int((time.time() + 3600) * 1000), "sk-oat-a")
    p2 = _write_creds(tmp_path, "acct2.json", int((time.time() + 3600) * 1000), "sk-oat-b")
    pool = load_account_pool(f"{p1}:{p2}")
    assert pool is not None
    token = pool.get_access_token()
    assert token == "sk-oat-a"


def _prime_pool(pool):
    for slot in pool._slots:
        try:
            slot.provider.get_access_token()
        except Exception:
            pass


def test_multi_account_failover_when_exhausted(tmp_path: Path):
    p1 = _write_creds(tmp_path, "acct1.json", int((time.time() + 3600) * 1000), "sk-oat-a")
    p2 = _write_creds(tmp_path, "acct2.json", int((time.time() + 3600) * 1000), "sk-oat-b")
    pool = load_account_pool(f"{p1}:{p2}")
    assert pool is not None
    _prime_pool(pool)
    pool.mark_account_exhausted("sk-oat-a", time.time() + 3600)
    token = pool.get_access_token()
    assert token == "sk-oat-b"


def test_multi_account_next_reset_at_when_all_exhausted(tmp_path: Path):
    p1 = _write_creds(tmp_path, "acct1.json", int((time.time() + 3600) * 1000), "sk-oat-a")
    p2 = _write_creds(tmp_path, "acct2.json", int((time.time() + 3600) * 1000), "sk-oat-b")
    pool = load_account_pool(f"{p1}:{p2}")
    _prime_pool(pool)
    reset_a = time.time() + 100
    reset_b = time.time() + 200
    pool.mark_account_exhausted("sk-oat-a", reset_a)
    pool.mark_account_exhausted("sk-oat-b", reset_b)
    next_reset = pool.next_reset_at()
    assert next_reset is not None
    assert abs(next_reset - reset_a) < 1


def test_multi_account_mark_exhausted_is_monotone_forward(tmp_path: Path):
    p1 = _write_creds(tmp_path, "acct1.json", int((time.time() + 3600) * 1000), "sk-oat-a")
    pool = load_account_pool(str(p1))
    _prime_pool(pool)
    pool.mark_account_exhausted("sk-oat-a", time.time() + 3600)
    later_reset = pool.next_reset_at()
    pool.mark_account_exhausted("sk-oat-a", time.time() + 5)
    still_later = pool.next_reset_at()
    assert still_later >= later_reset - 1


def test_load_account_pool_empty_returns_none():
    assert load_account_pool("") is None
    assert load_account_pool(":::") is None


def test_load_account_pool_ignores_nonexistent_files(tmp_path: Path):
    p1 = _write_creds(tmp_path, "acct1.json", int((time.time() + 3600) * 1000), "sk-oat-a")
    bad = tmp_path / "nonexistent.json"
    pool = load_account_pool(f"{bad}:{p1}")
    assert pool is not None
    token = pool.get_access_token()
    assert token == "sk-oat-a"
