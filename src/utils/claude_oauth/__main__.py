"""CLI entry: ``python -m src.utils.claude_oauth [--port 8765] [--check]``."""

from __future__ import annotations

import argparse
import logging
import sys

import uvicorn

from .bridge import _resolve_provider, build_app
from .credentials import CredentialsError


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="python -m src.utils.claude_oauth")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--log-level", default="info")
    p.add_argument(
        "--check",
        action="store_true",
        help="Verify credentials load successfully, then exit.",
    )
    args = p.parse_args(argv)

    logging.basicConfig(
        level=args.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Honor WCB_CC_ACCOUNT_POOL if present (multi-account failover);
    # otherwise falls through to single default CredentialProvider.
    provider = _resolve_provider()
    try:
        token = provider.get_access_token()
    except CredentialsError as e:
        print(f"[bridge] credentials error: {e}", file=sys.stderr)
        return 2

    print(f"[bridge] credentials OK (token prefix: {token[:15]}...)")
    if args.check:
        return 0

    print(f"[bridge] listening on http://{args.host}:{args.port}")
    print("[bridge] point clients at:")
    print(f"           export ANTHROPIC_API_BASE=http://{args.host}:{args.port}")
    print("           export ANTHROPIC_API_KEY=kaiju-cc-stub")
    uvicorn.run(
        build_app(provider),
        host=args.host,
        port=args.port,
        log_level=args.log_level,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
