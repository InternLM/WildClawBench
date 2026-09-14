# M4 — matched OpenClaw run (harness-delta control)

Purpose: score OpenClaw on the **identical** endpoint, model, and reasoning
setting as the DSH arm, so the headline claim — *harness delta on a fixed
model* — is a matched comparison, not a model-vs-model comparison.

## Why no extra code beyond `my_api.lb.json`

The bench already supports custom endpoints for OpenClaw via
`--models-config` (`${MY_PROXY_API_KEY}` is expanded host-side, never
committed). `my_api.lb.json` points it at the same LiteLLM LB as the DSH arm;
`nightly_lib.py` builds the matched command automatically when
`WCB_BACKEND=openclaw` (provider-qualified model `wcb-lb/qwen3.8-flash-next`,
per README convention), reusing the same window/ledger/sweep machinery with
its own ledger (`output/openclaw/ledger_openclaw_qwen3.8-flash-next.json`).

## Preflight (before the first matched night) — M3 must be complete first

1. **Single-task smoke** (daytime is fine — one request stream):
   ```bash
   set -a && . .env && set +a
   export MY_PROXY_API_KEY="$WCB_LB_API_KEY" \
          DOCKER_IMAGE=wildclawbench-ubuntu:v1.3 \
          WCB_LB_API_KEY  # openclaw smoke uses MY_PROXY_API_KEY
   python3 eval/run_batch.py --agent-backend openclaw \
     --task tasks/01_Productivity_Flow/01_Productivity_Flow_task_1_arxiv_digest.md \
     --models-config my_api.lb.json --model wcb-lb/qwen3.8-flash-next \
     --thinking xhigh
   ```
   **Open question to settle here:** whether `openclaw config set
   agents.defaults.thinkingDefault xhigh` accepts `xhigh` (the value is passed
   verbatim; upstream docs describe low/medium/high). If it rejects, record
   the accepted top rung in this file and re-check the DSH arm's mapping so the
   comparison stays honest — a rung mismatch invalidates the headline claim.
2. Verify smoke `score.json` has no `error` key and the transcript is
   non-empty (also feeds the R2 judge-fidelity audit for both arms).

## Nightly matched sweep (after smoke passes)

```bash
set -a && . .env && set +a
export WCB_BACKEND=openclaw WCB_LB_API_KEY="$WCB_LB_API_KEY"
systemctl --user start wcb-nightly.service   # or wait for the 05:00 timer
```
The timer runs the default (dsh) backend; run the openclaw arm on nights when
the dsh ledger has no pending tasks (the sweep is exclusive either way — one
arm per night keeps LB load and wall-clock budgets matched).

## Deliverable when both ledgers are terminal

`docs/superpowers/results/leaderboard-packet.md`: per-category DSH vs OpenClaw
deltas, token rows (self-hosted ⇒ cost N/A footnote), judge-audit appendix,
safety manual-review section (06_7 / 06_10), and the submission form fields.
