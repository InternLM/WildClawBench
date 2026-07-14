#!/usr/bin/env python3
"""Bootstrap a shared LiteLLM sidecar + docker network that survives across
multiple rep python processes within a single `bash script/run.sh` invocation.

WHY THIS FILE EXISTS
====================
Default behavior of `eval/run_batch.py::_setup_litellm_and_mocks` was to
build a fresh network + sidecar per rep (per python invocation). For K reps
this meant K `docker pull`, K `docker network create`, K `docker run`, K
`wait_for_litellm_healthy` polls, K `verify_litellm_upstream_reachable`
synthetic POSTs — every one of which is a Docker-side raise point that, when
flaky, exits the rep with a raw traceback OUTSIDE the b7 wrap and surfaces
to the user as "rep 2 failed for no reason". See
`docs/reps-failure-diagnosis.md` §B (THIRTEEN unwrapped raise sites in
pre-`_run_dispatch` setup) and §A1/§A3/§A4 (cross-rep coupling: Bedrock TPM,
Docker bridge IP pool, work/ disk fill).

This script does that Docker-heavy setup ONCE at the bash level. The python
side then SHORT-CIRCUITS `_setup_litellm_and_mocks` when it sees the
WCB_SHARED_SIDECAR + WCB_SHARED_NETWORK env vars, reusing the same sidecar
+ network across all reps + all tasks + all models in the batch.

INTERFACE CONTRACT (bash <-> python)
====================================
- This script writes one line per output field to STDOUT in `key=value`
  form, e.g.:
      name=wcb-shared-ll-12345-20260628_123012
      network=wcb-shared-net-12345-20260628_123012
      usage_log=/abs/path/to/work/litellm-usage-shared-12345-20260628_123012/usage.jsonl
      yaml_path=/abs/path/to/work/litellm-config-shared-12345-20260628_123012.yaml
      master_key=sk-litellm-…
  Caller (`script/run.sh::bootstrap_shared_sidecar`) parses these and
  `export`s WCB_SHARED_NETWORK / WCB_SHARED_SIDECAR / WCB_SHARED_SIDECAR_USAGE_LOG
  / WCB_SHARED_SIDECAR_YAML / WCB_SHARED_LITELLM_MASTER_KEY for child python
  processes to read.
- Logging / progress lines go to STDERR so bash can `tee` STDOUT into a
  parser without pollution.
- Exit code 0 = ready; non-zero = bash should abort the batch (no reps can
  run without a sidecar).

INVARIANTS
==========
- Container name MUST NOT contain the substring `ll-` so the
  `cleanup_orphans` global sweep at `script/run.sh:352` (filter `name=ll-`,
  which is a Docker substring match) cannot tear down the shared sidecar
  mid-batch. Current chosen prefix: `wcbsh-sidecar-`.
- Network name MUST NOT contain `k3net-` so the same sweep (filter
  `name=k3net-` at run.sh:363) leaves it alone. Current chosen prefix:
  `wcbsh-net-`.
- All names suffixed with `$$-$(date +%Y%m%d_%H%M%S)` so concurrent
  `run.sh` invocations don't collide.
- This file is the python counterpart of the Bash `bootstrap_shared_sidecar`
  function in `script/run.sh`. The bash side OWNS teardown via EXIT/INT/TERM
  trap; this script must NOT register atexit / signal handlers itself.

CALLER-SIDE OPT-OUT
===================
`_setup_litellm_and_mocks` falls back to per-rep behavior when the env vars
are absent (e.g. when the user runs `python3 eval/run_batch.py` directly
without going through `script/run.sh`). The convergence invariant in
`script/AGENTS.md` ("run.sh and direct python should converge on identical
artifacts") still holds: same sidecar image, same config yaml, same master
key — just different lifecycle owner.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make src/utils importable regardless of cwd, matching eval/run_batch.py's
# sys.path tweak. Caller must invoke us via `python3 eval/bootstrap_sidecar.py`
# from the repo root (run.sh enforces this with `cd "$(dirname "$0")/.."`).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from src.utils.config import Config  # noqa: E402
from src.utils.litellm_sidecar import (  # noqa: E402
    CC_BRIDGE_INTERNAL_PORT,
    build_litellm_config_yaml,
    create_network,
    ensure_litellm_headroom_image,
    pull_litellm_image,
    start_bridge,
    start_litellm,
    stop_bridge,
    stop_litellm,
    verify_litellm_upstream_reachable,
    wait_for_bridge_healthy,
    wait_for_bridge_host_port,
    wait_for_litellm_healthy,
)


def _emit(key: str, value: str) -> None:
    """Write a single key=value line to STDOUT for bash to parse."""
    sys.stdout.write(f"{key}={value}\n")
    sys.stdout.flush()


def _log(msg: str) -> None:
    """Progress goes to STDERR so STDOUT stays parseable."""
    sys.stderr.write(f"[bootstrap_sidecar] {msg}\n")
    sys.stderr.flush()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bootstrap shared LiteLLM sidecar + network for the batch.",
    )
    parser.add_argument(
        "--name-suffix",
        required=True,
        help="Suffix appended to resource names (e.g. '12345-20260628_123012'). "
             "Bash provides $$-$(date +%%Y%%m%%d_%%H%%M%%S).",
    )
    parser.add_argument(
        "--skip-upstream-verify",
        action="store_true",
        help="Skip the synthetic Bedrock/OpenAI ping (faster cold start, no "
             "guarantee that upstream is reachable).",
    )
    args = parser.parse_args()

    # Match the eval/run_batch.py naming scheme but with explicit `wcb-shared-`
    # prefixes that DO NOT collide with run.sh's cleanup_orphans filters
    # (`name=ll-`, `name=mocks-`, `name=t_`, `name=k3net-`).
    suffix = args.name_suffix
    network = f"wcbsh-net-{suffix}"
    sidecar = f"wcbsh-sidecar-{suffix}"
    cc_bridge = f"wcbsh-cc-bridge-{suffix}"
    cc_bridge_url = ""

    config = Config.from_env()
    use_litellm = config.litellm_enabled()
    if not use_litellm:
        _log("Config disables LiteLLM (no creds); reps will run in OpenRouter fallback mode")
        _emit("name", "")
        _emit("network", "")
        _emit("usage_log", "")
        _emit("yaml_path", "")
        _emit("master_key", "")
        _emit("cc_bridge", "")
        _emit("cc_bridge_url", "")
        _emit("cc_bridge_host_port", "")
        _emit("cc_bridge_host_url", "")
        return 0

    _agent_headroom = (
        os.environ.get("KENSEI_AGENT_HEADROOM_ENABLED", "").strip().lower()
        in ("1", "true", "yes", "on")
    )
    # Live-token stream tap (docs/STREAMING_PLAN.md). Batch-scoped gate (R6):
    # evaluated once here; run.sh sets WCB_STREAM=1 only for single-run
    # foreground batches (--stream flag + K==1 gate).
    _stream_enabled = (
        os.environ.get("WCB_STREAM", "").strip().lower()
        in ("1", "true", "yes", "on")
    )

    use_oauth = config.use_claude_oauth and bool(config.cc_account_pool)
    bridge_secret = config.cc_bridge_secret
    if use_oauth and not bridge_secret:
        import secrets
        bridge_secret = secrets.token_hex(32)
        _log("generated ephemeral WCB_CC_BRIDGE_SECRET for this batch")
    cc_bridge_host_port = ""
    if use_oauth:
        cc_bridge_url = f"http://{cc_bridge}:{CC_BRIDGE_INTERNAL_PORT}"
        os.environ["WCB_CC_BRIDGE_SECRET"] = bridge_secret
        # Publish the bridge on a loopback host port so the HOST-side judge
        # (grading.py -> judge_litellm) can reach it for the Sonnet-via-OAuth
        # route. If WCB_CC_BRIDGE_HOST_PORT is preset we honor it; otherwise pick
        # a free ephemeral port. start_bridge reads WCB_CC_BRIDGE_HOST_PORT and
        # binds 127.0.0.1:<port>:8765 (secret still gates every request).
        import socket
        cc_bridge_host_port = os.environ.get("WCB_CC_BRIDGE_HOST_PORT", "").strip()
        if not cc_bridge_host_port:
            _s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _s.bind(("127.0.0.1", 0))
            cc_bridge_host_port = str(_s.getsockname()[1])
            _s.close()
            os.environ["WCB_CC_BRIDGE_HOST_PORT"] = cc_bridge_host_port

    litellm_yaml = build_litellm_config_yaml(
        bedrock_sonnet_arn=config.bedrock_sonnet_arn if config.aws_bearer_token else "",
        bedrock_arn=config.bedrock_inference_arn if config.aws_bearer_token else "",
        aws_region=config.bedrock_region,
        openai_api_key=config.openai_api_key,
        openai_whisper_api_key=config.openai_whisper_api_key,
        enable_usage_callback=True,
        enable_headroom_callback=_agent_headroom,
        anthropic_api_key=config.anthropic_api_key,
        use_claude_oauth=use_oauth,
        bridge_url=cc_bridge_url,
        enable_oauth_usage_callback=use_oauth,
        # §1.5 (docs/STREAMING_PLAN.md): on the OAuth agent path the sidecar
        # sits IN FRONT of the buffering cc-bridge, so its hook would only see
        # an end-of-turn burst — the real-time tap there is the bridge tee.
        # Register the sidecar callback only on the non-OAuth (Bedrock) path.
        enable_stream_callback=_stream_enabled and not use_oauth,
    )
    if not litellm_yaml:
        _log(
            "LiteLLM requested but no Bedrock/OpenAI creds resolved. "
            "Refusing to silently downgrade to OpenRouter (strict mode)."
        )
        return 2

    _log(f"pulling LiteLLM image (one-time per host)…")
    pull_litellm_image()
    if _agent_headroom:
        _log("ensuring headroom image…")
        ensure_litellm_headroom_image()

    _log(f"creating network {network}…")
    create_network(network)

    # Live-stream feed (docs/STREAMING_PLAN.md §2.2) — resolved BEFORE the
    # cc-bridge start: on this branch the bridge tee is the real-time token
    # tap and needs the feed dir mounted at container start. Separate sink
    # from usage.jsonl / usage_oauth.jsonl (m0130).
    stream_callback_src = ""
    stream_log_dir_str = ""
    stream_log_path = None
    if _stream_enabled:
        stream_callback_src = str(
            Path(__file__).resolve().parent.parent / "src" / "utils" / "litellm_stream_callback.py"
        )
        stream_log_dir = config.work_dir / f"litellm-stream-shared-{suffix}"
        stream_log_dir.mkdir(parents=True, exist_ok=True)
        stream_log_path = stream_log_dir / "stream.jsonl"
        stream_log_path.touch(exist_ok=True)
        try:
            os.chmod(stream_log_path, 0o600)
            os.chmod(stream_log_dir, 0o700)
        except OSError as exc:
            _log(f"warning: chmod failed on stream log dir/file ({exc})")
        stream_log_dir_str = str(stream_log_dir)

    if use_oauth:
        pool_paths = [p.strip() for p in config.cc_account_pool.split(":") if p.strip()]
        pool_dirs = {os.path.dirname(os.path.abspath(p)) for p in pool_paths if os.path.isfile(p)}
        if not pool_dirs:
            _log(
                f"OAuth pool spec {config.cc_account_pool!r} resolved to zero readable files. "
                f"Point WCB_CC_ACCOUNT_POOL at host-side OAuth credential JSON file(s)."
            )
            return 6
        if len(pool_dirs) > 1:
            _log(
                f"OAuth pool files span multiple host directories {pool_dirs}. "
                f"Consolidate under one directory (e.g. ~/.wcb/oauth_pool/) so a single "
                f"docker -v mount can expose them all."
            )
            return 6
        pool_host_dir = next(iter(pool_dirs))
        bridge_ok = False
        for _attempt in range(1, 4):
            _log(
                f"starting cc-bridge {cc_bridge} on network {network} "
                f"(pool={pool_host_dir}) attempt {_attempt}/3, host_port={cc_bridge_host_port}…"
            )
            try:
                start_bridge(
                    container_name=cc_bridge,
                    network=network,
                    pool_host_dir=pool_host_dir,
                    bridge_secret=bridge_secret,
                    # Real-time tee sink (docs/STREAMING_PLAN.md §3.2); empty
                    # when streaming off → tee inert, bridge unchanged.
                    stream_log_host_dir=stream_log_dir_str,
                )
            except Exception as exc:
                _log(f"start_bridge failed: {exc}")
                try:
                    stop_bridge(cc_bridge)
                except Exception:  # noqa: BLE001
                    pass
                return 6
            if not wait_for_bridge_healthy(cc_bridge):
                _log(
                    f"cc-bridge {cc_bridge} did not become healthy in time. "
                    f"Override WCB_CC_BRIDGE_HEALTH_TIMEOUT (seconds) for slow hosts."
                )
                try:
                    stop_bridge(cc_bridge)
                except Exception:  # noqa: BLE001
                    pass
                return 7

            if wait_for_bridge_host_port(cc_bridge_host_port):
                bridge_ok = True
                break

            _log(
                f"cc-bridge host port 127.0.0.1:{cc_bridge_host_port} unreachable "
                f"(Docker Desktop dropped the loopback publish); recreating on a fresh port"
            )
            try:
                stop_bridge(cc_bridge)
            except Exception:  # noqa: BLE001
                pass
            _s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            _s2.bind(("127.0.0.1", 0))
            cc_bridge_host_port = str(_s2.getsockname()[1])
            _s2.close()
            os.environ["WCB_CC_BRIDGE_HOST_PORT"] = cc_bridge_host_port

        if not bridge_ok:
            _log(
                "cc-bridge host port never became reachable after 3 attempts; the "
                "host-side Sonnet judge would fail with Connection refused. Aborting."
            )
            try:
                stop_bridge(cc_bridge)
            except Exception:  # noqa: BLE001
                pass
            return 7

    config.work_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = config.work_dir / f"litellm-config-shared-{suffix}.yaml"
    cfg_path.write_text(litellm_yaml, encoding="utf-8")

    callback_src = (
        Path(__file__).resolve().parent.parent / "src" / "utils" / "litellm_usage_callback.py"
    )
    usage_dir = config.work_dir / f"litellm-usage-shared-{suffix}"
    usage_dir.mkdir(parents=True, exist_ok=True)
    usage_log_path = usage_dir / "usage.jsonl"
    usage_log_path.touch(exist_ok=True)
    # S-003 hardening: same owner-only modes as eval/run_batch.py:1631-1639.
    # Sidecar container must run as the same UID/GID as the host bash for
    # the bind mount to be writable.
    try:
        os.chmod(usage_log_path, 0o600)
        os.chmod(usage_dir, 0o700)
    except OSError as exc:
        _log(f"warning: chmod failed on usage dir/file ({exc}); sidecar may fail to write")

    headroom_callback_src = ""
    headroom_log_dir_str = ""
    if _agent_headroom:
        headroom_callback_src = str(
            Path(__file__).resolve().parent.parent / "src" / "utils" / "litellm_headroom_callback.py"
        )
        headroom_log_dir = config.work_dir / f"litellm-headroom-shared-{suffix}"
        headroom_log_dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(headroom_log_dir, 0o700)
        except OSError as exc:
            _log(f"warning: chmod failed on headroom log dir ({exc})")
        headroom_log_dir_str = str(headroom_log_dir)

    # (Live-stream feed dir was resolved ABOVE the cc-bridge start.)

    _log(f"starting sidecar {sidecar} on network {network}…")
    oauth_cb_src = ""
    if use_oauth:
        oauth_cb_src = str(
            Path(__file__).resolve().parent.parent / "src" / "utils" / "litellm_usage_oauth_callback.py"
        )
    try:
        start_litellm(
            container_name=sidecar,
            network=network,
            host_config_path=str(cfg_path),
            master_key=config.litellm_master_key,
            aws_bearer_token=config.aws_bearer_token,
            aws_region=config.bedrock_region,
            openai_api_key=config.openai_api_key,
            openai_whisper_api_key=config.openai_whisper_api_key,
            usage_callback_host_path=str(callback_src),
            usage_log_host_dir=str(usage_dir),
            headroom_callback_host_path=headroom_callback_src,
            headroom_log_host_dir=headroom_log_dir_str,
            enable_headroom=_agent_headroom,
            anthropic_api_key=config.anthropic_api_key,
            oauth_usage_callback_host_path=oauth_cb_src,
            stream_callback_host_path=stream_callback_src,
            stream_log_host_dir=stream_log_dir_str,
        )
    except Exception as exc:
        _log(f"start_litellm failed: {exc}")
        try:
            stop_litellm(sidecar)
        except Exception:  # noqa: BLE001
            pass
        return 3

    if not wait_for_litellm_healthy(sidecar):
        _log(
            f"LiteLLM sidecar {sidecar} did not become healthy in time. "
            f"Override KENSEI_LITELLM_HEALTH_TIMEOUT (seconds) for slow hosts."
        )
        return 4

    if not args.skip_upstream_verify:
        probe_model = (
            "claude-opus-4.7"
            if use_oauth
            or (config.aws_bearer_token and config.bedrock_inference_arn)
            or config.anthropic_api_key
            else "gpt-5.5" if config.openai_api_key
            else ""
        )
        if probe_model:
            ok, detail = verify_litellm_upstream_reachable(
                sidecar, master_key=config.litellm_master_key, model_name=probe_model,
            )
            if not ok:
                _log(
                    f"LiteLLM sidecar {sidecar} up but upstream unreachable "
                    f"via model={probe_model!r}: {detail}. Fix Bedrock IAM / "
                    f"region / network before retrying."
                )
                return 5

    _log(f"sidecar {sidecar} ready on network {network}")

    _emit("name", sidecar)
    _emit("network", network)
    _emit("usage_log", str(usage_log_path))
    _emit("yaml_path", str(cfg_path))
    _emit("master_key", config.litellm_master_key)
    _emit("cc_bridge", cc_bridge if use_oauth else "")
    _emit("cc_bridge_url", cc_bridge_url)
    _emit("cc_bridge_host_port", cc_bridge_host_port)
    _emit(
        "cc_bridge_host_url",
        f"http://127.0.0.1:{cc_bridge_host_port}" if cc_bridge_host_port else "",
    )
    _emit("stream_log", str(stream_log_path) if stream_log_path else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
