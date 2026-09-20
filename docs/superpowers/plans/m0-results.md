# M0 results — 2026-09-13

Single-task smoke of the DSH harness: `01_Productivity_Flow_task_1_arxiv_digest`,
model `qwen3.8-flash-next` @ **xhigh**, via `bash script/run.sh dsh …`.

## Gate verdict: PASS (mechanics) — score is data, not plumbing

| Check | Result |
|---|---|
| `score.json` written, **no `error` key** | ✅ 28 metrics graded |
| `usage.json` | ✅ `request_count=39`, input 853,656 / output 19,756 / total 873,412, `self_hosted: true` |
| Compat transcript | ✅ 81 entries at `chat.jsonl` (converted from DSH zstd session events) |
| In-container grading | ✅ ran with the gpt-5.4 judge path unchanged |
| Container lifecycle | ✅ started → warmup → xhigh patch → graded → cleaned up |

**Score: 0.00 overall** — the agent was still mid-reasoning about arXiv
submitted-date range semantics when the task's own 1200 s budget expired
(`agent.log` tail shows live deliberation, not a stall). No deliverable files
existed in `results/` at kill time, so all automated checks graded 0.

## M1 audit questions (recorded, not yet answered)

1. **xhigh slow-tail on long-horizon browse tasks.** 39 requests / 853k input
   tokens in 20 min = deepening single-threaded context, still on the fetch
   stage. OpenClaw completes this task within the same budget. Candidate
   mitigations to A/B in M1: `--thinking medium` for category 01 (design pins
   xhigh everywhere — change requires re-approval), or accept as an honest
   harness characteristic for the leaderboard footnote.
2. **Judge transcript fidelity** (risk R2): zero-score path exercised the
   automated checks; judge-based metrics on non-empty transcripts still
   unexercised — covered by category 04 in M1.
3. Timeout kill is clean (no orphan container; sweep verified).

## Infra fixes discovered by M0 (all committed)

- Profile materialization (`--from-default-profile headless`) + model pin via
  profile `cordis.patch.yml` — settings.yaml `agent-default-model` is ignored
  when the template pins a default.
- Base image bakes a dead proxy ENV → cleared in `Dockerfile.dsh` build layer.
- LB probe must be authenticated (gateway 401s unauthenticated requests).
- `verify_image.sh`: capture-then-grep (pipefail + `grep -q` SIGPIPE artifact).

## Status

Tasks 1–7 complete. Next: asset pre-provisioning (`script/prepare.sh`), then
nightly timer install for M3 (05:00 America/Chicago, window 05:00–07:30,
parallel 4, resumable ledger).
