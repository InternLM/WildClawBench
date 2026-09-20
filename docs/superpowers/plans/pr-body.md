# PR body (used with `gh pr create --body-file` after fork push is authorized)

Title: `feat: DSH (DeepSeek Harness) backend + nightly window scheduler`

---

Adds a fifth agent harness — **[DSH / DeepSeek Harness](https://www.npmjs.com/package/@deepseek-ai/dsh)** — alongside OpenClaw, Claude Code, Codex, and Hermes. Unlike the OpenRouter-backed harnesses, the DSH backend runs its solver against a **self-hosted LiteLLM gateway**, and ships with an opt-in **nightly-window scheduler** for running the full 60-task suite in a fixed low-traffic window with a resumable ledger.

## What's in it

- `src/agents/dsh/` — `DshAgent` implementing `BaseAgent`: starts the standard task container, writes a per-task DSH config patch (`--patch`, pinning provider/model/reasoning rung), runs `dsh --profile bench` headless one-shot per task, collects usage from the session transcript. No gateway process (`expects_gateway=False`), same background-exec/timeout pattern as the other backends.
- `src/agents/dsh/compat_transcript.py` — converts DSH's compressed session events into the OpenClaw transcript format the existing grading pipeline already consumes (same precedent as the Hermes adapter). Grading and judge code are untouched.
- `docker/Dockerfile.dsh` + `docker/dsh-settings.yaml` + `docker/verify_image.sh` — solver image on top of `wildclawbench-ubuntu:v1.3` (pins the dsh CLI, materializes a headless `bench` profile, bakes the gateway provider definition) plus an acceptance gate that builds, checks profile/rung/model, probes the gateway, and does one live round-trip.
- `script/nightly_lib.py` — window-bounded (host-local start/stop), resumable per-task ledger (atomic writes, failed rows retried next night), bounded parallelism, container sweep at exit. `WCB_BACKEND=openclaw` reuses the same machinery for matched-control runs against the same endpoint via `my_api.lb.json`.
- Dispatch wiring: `dsh` in `run.sh` / `run_batch.py` / cli choices; README section; `.env.example` keys.
- `tests/` — 25 unit tests (transcript conversion against a captured fixture, rung validation, patch generation, dispatch wiring, nightly ledger/window/commands). All green; upstream tests untouched.

## Evidence

- Image gate passes end-to-end including a live gateway round-trip (`docker/verify_image.sh`).
- Single-task M0 run (`01_Productivity_Flow_task_1_arxiv_digest`): score.json graded in-container with the stock pipeline, `usage.json` collected real token counts (`request_count=39`, 873k tokens), compat transcript consumed by the judge path. Write-up: `docs/superpowers/plans/m0-results.md`.

## Design notes

- **Self-hosted cost reporting**: rows for this backend report tokens; `usage.json` carries `self_hosted: true` and `cost_usd: 0.0` (matching the existing self-hosted precedent rows — no dollar figure is derivable from a private gateway).
- **Reasoning rungs**: `--thinking` accepts `off|low|medium|xhigh` (default `xhigh`) and is validated **before** any container side effects; unsupported values fail fast.
- **Gateway probe is authenticated** and falls back to `host.docker.internal` automatically; both addresses are configurable via `.env`.
- **Nightly scheduler is opt-in** — nothing here changes default execution behavior; the systemd user units in `systemd/` are examples and are not installed by anything in this PR.

## Not included

- No leaderboard row is claimed here; this PR adds the capability, the scheduler, and the verification gates.
- No changes to grading, judge models, task content, or the other four harnesses.
