# Output Nomenclature

Two independent scoring channels run per task per run. Historically both used `tests_*` keys; that caused confusion. As of b71 the rubric channel uses canonical `criteria_*` keys with `tests_*` kept only as deprecated aliases for back-compat.

## At-a-glance map

| What you want | Where to find it | Field name |
| --- | --- | --- |
| **Agent-produced artifacts for one run** | `output/<backend>/<task>/trajectories/<model>/run_N/task_output/artifacts/` | files only |
| Full workspace forensic copy | `output/<backend>/<task>/trajectories/<model>/run_N/task_output/workspace_full/` | files only |
| Rubric judge verdict for one run | `output/<backend>/<task>/trajectories/<model>/run_N/score.json` | `overall_score`, `rubric_weights_percentage` |
| Rubric pass counts for one run | same file | `criteria_total`, `criteria_passed`, `criteria_failed` |
| Per-criterion judge breakdown | same file | `criteria[]` |
| Pytest reward for one run | `output/<backend>/<task>/trajectories/<model>/run_N/task_output/logs/verifier/reward.txt` | scalar in `[0,1]` |
| Pytest detailed report | same dir | `ctrf.json`, `test_function_outputs.json`, `test_output.log` |
| Generated test code | `output/<backend>/<task>/data/tests/test_outputs.py` (shared across runs) | — |
| Generated test weights | `output/<backend>/<task>/data/tests/test_weights.json` | — |
| Per-run summary across many runs | `output/<backend>/<task>/pass_summary.json` | `runs[].rubric_weights_percentage` |
| Aggregate average across runs of a model | same file | `average_rubric_weights_percentage` |
| Cross-task model rollup (mean and pass@K) | run `python3 script/aggregate_runs.py` | `output/<backend|all>_aggregate_summary.json` |
| Best-of-K rollout score for one task | aggregator output | `by_task_model[].pass_at_k`, `by_task_model[].k` |
| Eval-wide pass@K (mean of per-task best) | aggregator output | `by_model[].average_pass_at_k` |

## Agent-produced artifacts (canonical location)

`task_output/artifacts/` is the standardized location where every file the agent created or modified during the run is stored, with input data and persona scratch filtered out.

How it's built (`src/utils/docker_utils.py:collect_output_from_container`):

1. Right before the agent runs, the harness takes a baseline snapshot of the workspace (every file's path + size + mtime). This happens after task inputs and persona files are staged. Captured by `snapshot_workspace_state(task_id)` invoked from each agent runner.
2. After the agent finishes, the harness re-walks the workspace and copies into `artifacts/` only the files whose `(size, mtime, is_symlink)` differs from the baseline, OR that didn't exist in the baseline at all.
3. Excluded by default from the diff (matched by relative path): `results/`, `gt/`, `tmp/`, `.git/`, `node_modules/`, `.venv/`, `venv/`, `__pycache__/`, `.cache/`.

Properties:

- **Empty `artifacts/`** means the agent produced no new or modified files — useful signal for diagnosing "did the agent actually do anything" without scanning a 100-file mix.
- **`workspace_full/` is always populated** (forensic copy of the entire workspace including inputs). Use this when `artifacts/` is empty and you need to see what the agent saw.
- Backends that don't take a baseline snapshot get a silently-empty `artifacts/`. As of b99 all three primary backends (openclaw, codex, claudecode) take the snapshot.
- Judges read deliverables from `artifacts/` first (via `_DELIVERABLE_DIR_NAMES` in `grading.py`), falling back to `workspace_full/` for older runs or for legacy harbor `results/` dirs.

The legacy `workspace/results/` sub-collection (from harbor/kensei2.py:2638) was removed in b99 because agents were never instructed to write there and the dir was always empty.

## Channel A — Pytest test executor

**Owner:** `src/utils/test_executor.py:_compute_reward`
**Triggered when:** `--execute-tests` is on and generated/inline tests run against the agent workspace.
**Reward formula (user m1420 line 1):**

```
reward = max(0, (Σ passed_positive_weights − Σ |triggered_negative_weights|) / Σ all_positive_weights)
```

A "triggered" negative-weight test is a guardrail that FIRED (failure mode actually occurred). Its absolute weight is subtracted from the numerator.

**Output files:**
- `task_output/logs/verifier/reward.txt` — scalar reward in `[0,1]`
- `task_output/logs/verifier/ctrf.json` — Common Test Report Format
- `task_output/logs/verifier/test_function_outputs.json` — per-test return values
- `task_output/logs/verifier/test_output.log` — pytest stdout

**Authoritative test count keys** (used by harbor bundle's `test_result`):
- `tests_total`, `tests_passed`, `tests_failed` — these ARE the real pytest counts here.

## Channel B — Rubric judge

**Owner:** `src/utils/grading.py:_grade_council` (and single-judge fallback)
**Triggered when:** rubric.json exists for the task. Runs once per task per run.
**Spec source:** `judge_walkthrough_2026_05_27` — five-section prompt (question / agent_conversation / output_files / numbered rubric) with per-criterion `[[SATISFIED: Yes|No]]` verdicts. See `_judge_system_prompt()`.
**Verdict format:** Each judge emits exactly N verdicts (where N = number of rubric criteria) wrapped in `<judgment>...</judgment>`:

```
N. <verbatim criterion>
[[RATIONALE: <prose>]]
[[SATISFIED: Yes|No]]
[[TRUNCATION_AFFECTED: Yes|No]]
```

Polarity rule per walkthrough §2: `SATISFIED` always reflects the criterion text literally. If the criterion is "agent sent duplicate messages", `SATISFIED: Yes` means the agent ACTUALLY DID send duplicates. The aggregator translates `satisfied × weight_sign` into `passed`.

**Aggregator (council):** **Unanimous, else Sonnet source-of-truth tiebreak** per criterion (b82+b83). For each criterion index `i`: (1) **Unanimous** — if every configured member voted at `i` AND all agree on `SATISFIED`, use that verdict (`resolved_by="unanimous"`). (2) **Else Sonnet** — if the Sonnet member (located by stable family `sonnet`, never the rotating ARN) emitted a verdict at `i`, Sonnet's verdict IS the criterion verdict (`resolved_by="sonnet"`). This deliberately covers BOTH a genuine Yes/No split (all voted, disagree) AND partial coverage (a smaller-context judge — Kimi 256k, GLM 200k — truncated/failed and never reached `i`); Sonnet has full context and is the source of truth. NOT counted as abstained. (3) **Else Human Evaluation** — no unanimity AND Sonnet itself cast no verdict at `i` (Sonnet failed entirely, or rarely truncated): `i` is appended to `abstention_flags`, counted in `criteria_abstained`, contributes 0 to the numerator (`resolved_by="human_eval"`, `human_eval="required"`). If the roster has no sonnet member, `sonnet_idx` is None and all non-unanimous criteria abstain (a warning is logged). If fewer than 2 members parse-OK overall, council returns None and single-judge fallback runs.

Rationale (user m1543 verbatim): _"not every model has the same input context and is not judging on all rubrics except Sonnet, then why enforce this? Just have it done."_ Strict equal-coverage was abandoned because it artificially invented No-votes the model did not cast; rather than break ties or fill gaps by majority, Sonnet — the only member guaranteed full context — is now the source of truth that resolves both genuine disagreements and partial coverage. Pure abstention (Human Evaluation) is reserved for when Sonnet itself produced no verdict.

**Reward formula (walkthrough §4, equivalent to user m1420 line 1):**

```
weighted = Σ weight for each criterion where the resolved satisfied = True
total_positive = Σ weight for each criterion where weight > 0
overall_score = max(0.0, min(1.0, weighted / total_positive))
```

This collapses to the user m1420 formula because `satisfied=True` on a negative-weight criterion contributes `+(-w)` = `-|w|` to `weighted`. **No fractions are possible** — Yes/No verdicts produce integer-weighted attribution by construction (b78 supersedes b51 binary quantization).

**Output file:** `output/<backend>/<task>/trajectories/<model>/run_N/score.json`

**Canonical top-level keys (b71 + b78 + b82/b83):**
- `overall_score` — float in `[0,1]`, always a rational `k / total_positive`
- `rubric_weights_percentage` — `overall_score * 100`, 2 dp (user m1420 line 2)
- `criteria_total`, `criteria_passed`, `criteria_failed`, `criteria_abstained` — counts of rubric criteria. **Invariant:** `criteria_total == criteria_passed + criteria_failed + criteria_abstained`.
- `criteria[]` — per-criterion breakdown (see below)
- `judge_model` — `'council'` if ≥2 council members survived parsing, else ARN/model string
- `judge_council` — present only when council ran. Contains: `members`, `surviving`, `failed`, `aggregation: 'unanimous_or_sonnet_tiebreak'` (b82), `per_member_user_chars`, `per_member_verdict_count` (b82) showing how many criteria each council member actually covered before truncation (Sonnet's coverage is load-bearing — it resolves every non-unanimous criterion it reaches)
- `truncation_flags` — criterion ids where any judge flagged `TRUNCATION_AFFECTED: Yes`. Diagnostic only; does not affect score.
- `abstention_flags` (b82) — criterion ids that fell through to **Human Evaluation**: non-unanimous AND Sonnet emitted no verdict (`resolved_by="human_eval"`, `human_eval="required"`). A criterion where Kimi/GLM abstained but Sonnet voted is NOT abstained (it is resolved by Sonnet). These are counted in `criteria_abstained`; they contribute 0 to `weighted` AND are NOT counted in `criteria_passed` or `criteria_failed`.

**Per-criterion shape (council, b78 + b82/b83):**

```json
{
  "id": 12,
  "weight": 5,
  "criterion": "verbatim criterion text",
  "satisfied": true,                            // resolved verdict (bool): unanimous / Sonnet / human_eval
  "passed": true,                               // post-polarity (bool); false on the human_eval branch
  "resolved_by": "sonnet",                      // 'unanimous' | 'sonnet' | 'human_eval' — how the verdict was decided
  "human_eval": "",                             // 'required' only on the human_eval branch, else ''
  "voters": 2,                                  // b82: judges who voted on this criterion
  "voted_by_judge": [true, true, false],        // b82: raw per-member coverage at this index
  "votes": "Yes/Yes/Abstain",                   // human-readable raw vote string ('Yes'|'No'|'Abstain')
  "satisfied_by_judge": [true, true, false],    // raw per-member verdicts (False for abstainers)
  "rationales_by_judge": ["...", "...", "(abstained — output truncated before this criterion)"],
  "truncation_affected_by_judge": [false, false, false],
  "judges": ["urg0zifsjiga", "q6g7fi6wumk3", "u4czm4f2p"],
  "is_positive": true
}
```

The raw per-member fields (`voters`, `voted_by_judge`, `votes`, `satisfied_by_judge`, `rationales_by_judge`) are unchanged: they still show the underlying per-judge split that the `resolved_by` rule then resolves into the single `satisfied`/`passed` verdict.

**Per-criterion shape (single-judge, b78 + b83):**

```json
{
  "id": 12,
  "weight": 5,
  "criterion": "verbatim criterion text",
  "satisfied": true,
  "passed": true,
  "voted": true,                                // b83: false if judge truncated before this index
  "rationale": "...",
  "truncation_affected": false,
  "is_positive": true
}
```

**Deprecated keys (b71, kept for back-compat with old tooling):**
- `tests_total` = `criteria_total`
- `tests_passed` = `criteria_passed`
- `tests_failed` = `criteria_failed`

**Dropped keys (b78, no longer emitted):**
- `score: float` (per-criterion) — superseded by `satisfied: bool`
- `scores_by_judge: [float]` — superseded by `satisfied_by_judge: [bool]`
- `stddev` (per-criterion) — Yes/No has no stddev
- `reason` / `reasons_by_judge` (per-criterion) — renamed `rationale` / `rationales_by_judge`
- `disagreement_flags` (top-level) — superseded by `truncation_flags`
- `disagreement_threshold` (judge_council block) — no stddev anymore

Do not depend on the deprecated aliases for new code. They will be removed in a future release.

## Channel boundary

The deprecated `tests_*` rubric aliases LOOK like Channel A counts but are NOT. The harbor bundle's `tr_meta` adapter at `eval/run_batch.py:706` is the bridge — when no real pytest ran, it reads the rubric-channel `tests_*` keys (which are aliases of `criteria_*`) to populate the harbor `test_result` block. Channel A keys (when pytest ran) take precedence.

## Per-run summary file

`output/<backend>/<task>/pass_summary.json` written by `eval/run_batch.py:_write_pass_summary`:

```json
{
  "runs": [
    {
      "run_index": 1,
      "reward": 0.983,
      "rubric_weights_percentage": 98.3,
      "criteria_total": 23, "criteria_passed": 23, "criteria_failed": 0,
      "tests_total": 23, "tests_passed": 23, "tests_failed": 0,   // deprecated aliases
      "elapsed_time": 412.5,
      ...
    },
    ...
  ],
  "average_reward": 0.961,
  "average_rubric_weights_percentage": 96.10,   // user m1420 line 3 (per-task, per-model mean)
  "run_count": 3
}
```

## Cross-task / cross-model aggregator

`script/aggregate_runs.py` walks `output/<backend>/*/trajectories/<model>/run_*/score.json` and emits:

- `output/<backend>_aggregate_summary.json` (with `--backend openclaw`)
- `output/all_aggregate_summary.json` (default)

Each summary has two sections:

### `by_task_model[]` — one row per (backend, task, model)

```json
{
  "backend": "openclaw",
  "task_id": "alden-croft",
  "model": "claude-opus-4.7",
  "runs": [{"run": 1, "rubric_weights_percentage": 60.0, ...}, ...],
  "run_count": 4,
  "average_rubric_weights_percentage": 77.5,   // mean of this task's runs
  "stddev_rubric_weights_percentage": 14.79,
  "pass_at_k": 100.0,                          // walkthrough §4: best run for this task
  "k": 4                                        // K = run_count for this task
}
```

### `by_model[]` — one row per (backend, model), rolled up across all tasks

```json
{
  "backend": "openclaw",
  "model": "claude-opus-4.7",
  "run_count": 11,                              // total runs across all tasks
  "task_count": 2,                              // distinct tasks this model attempted
  "average_rubric_weights_percentage": 71.67,   // user m1420 line 3: mean of ALL runs
  "stddev_rubric_weights_percentage": 22.05,
  "average_pass_at_k": 95.0,                    // walkthrough §4 eval-aggregate: mean of per-task best
  "stddev_pass_at_k": 5.0
}
```

### Mean vs pass@K — both reported, neither replaces the other

- `average_rubric_weights_percentage` rewards **consistency** — every run counts equally, including the bad ones.
- `average_pass_at_k` rewards **capability** — each task contributes only its best run; the model is credited for ever having solved it.

A model that scores `60, 60, 60, 60` on a task has mean 60 / pass@4 60. A model that scores `0, 0, 0, 100` on the same task has mean 25 / pass@4 100. Different models tell different stories and both stories matter; pick the one that matches the question you're asking.

## Formula reference (user m1420 + walkthrough §4)

```
final_reward = max(0, (Σ passed_positive_weights − Σ |triggered_negative_weights|) / Σ all_positive_weights)
rubric_weights_percentage = final_reward × 100
average_rubric_weights_percentage = mean(rubric_weights_percentage across all runs for a model)
pass_at_k(task, model) = max(rubric_weights_percentage across K runs of that task by that model)
average_pass_at_k(model) = mean(pass_at_k across all tasks for that model)
```

| Line | Where enforced |
| --- | --- |
| 1 (pytest reward) | `src/utils/test_executor.py:_compute_reward` |
| 1 (rubric overall_score) | `src/utils/grading.py:_grade_council` and single-judge — algebraically equivalent because binary scores × signed weights / positive-only denominator collapses to the user formula |
| 2 (percentage) | `src/utils/grading.py` return dict (`rubric_weights_percentage`), `eval/run_batch.py:_write_pass_summary` (per-run), `script/aggregate_runs.py` (cross-run) |
| 3 (mean over runs of a model) | `eval/run_batch.py:_write_pass_summary` (per-task `average_rubric_weights_percentage`), `script/aggregate_runs.py` (cross-task `by_model.average_rubric_weights_percentage`) |
| 4 (pass@K per task) | `script/aggregate_runs.py` `by_task_model[].pass_at_k` (best of K runs for that task), walkthrough §4 |
| 5 (eval-aggregate pass@K) | `script/aggregate_runs.py` `by_model[].average_pass_at_k` (mean of per-task best across all tasks), walkthrough §4 'eval-aggregate = mean of per-task values' |

## Task input layout — `input/<task_id>/`

Native directory format (dominant). YAML/MD single-file variants also exist; see `src/utils/task_parser.py`.

### Required files
| File | Role |
| --- | --- |
| `prompt.txt` | Agent task description, verbatim |
| `rubric.json` | Bare list **or** `{rubrics: [...]}`; each criterion `{id, criterion, weight ∈ {±5, ±3, ±1}, evaluation_target}` |

### Optional files & subdirs
| Path | Role |
| --- | --- |
| `persona/` | openclaw bootstrap files — see persona table below |
| `data/` | Agent workspace inputs (subdirs preserved per b16 Gap B) |
| `mock_data/<api>-api/*` | Read-only CSV/JSON overlays bind-mounted at `/opt/mocks/<api>/<filename>:ro` (b1–b8) |
| `drift.yaml` | DriftDirector script (b1–b8) |
| `taxonomy.json` | Overrides derived l1/l2 |
| `task_config.yaml` | Feeds testgen cache key (b54 Issue 3) |
| `gt/` | Grader-only artifacts; never staged to workspace |

### `persona/` — the 7 openclaw bootstrap files (b88, b89)

Each file is copied to `/root/<NAME>.md` inside the agent container by `inject_lobster_workspace` (`src/utils/docker_utils.py:762`) and indexed into `/root/memory/` by `_index_memory` (`src/agents/openclaw/runner.py:514`) so `memory_search` can surface their content.

| File | Role | Currently shipped by |
| --- | --- | --- |
| `AGENTS.md` | Operating instructions (precedence-equivalent to `AGENT.md`) | renata-voss, alden-croft |
| `SOUL.md` | Personality & tone | renata-voss, alden-croft |
| `MEMORY.md` | Curated long-term memory; also seeded as today's + yesterday's daily memory (b16 Fix 2) | renata-voss, alden-croft |
| `IDENTITY.md` | Agent name, vibe, emoji | alden-croft only |
| `USER.md` | User profile, preferred name/address, timezone | alden-croft only |
| `TOOLS.md` | User-maintained tool notes | alden-croft only |
| `HEARTBEAT.md` | Scheduled-task checklist | alden-croft only |

**Per-task asymmetry is intentional**: each task author chooses which files to ship. Missing files are silently skipped (`[ -f "$f" ] && cp` pattern). Source-of-truth for the 7-file allowlist: `docs.openclaw.ai/concepts/agent-workspace`.

### Files harness **ignores** at task root
`tests/`, `solution/`, `environment/`, `task.toml`, `instruction.md`, `test_outputs.py` (the hand-authored test file is NOT loaded; only the auto-generated `output/<backend>/<task>/data/tests/test_outputs.py` is reused per the b54 hash-keyed cache).

### Auto-populated by `_augment_task_with_mocks` (run_batch.py)
`env_dir`, `required_apis` (keyword + mock_data subdir union), `distractor_apis` (all 101 − required, per b58), `mock_overlays`, `env_dict` (all 101 `<API>_API_URL` env vars), `drift_script_path`, `attachments`.

## System prompts (b96)

All LLM system prompts and user-prompt templates used by the harness live in `system_prompts/` at repo root. Loader is `src/utils/prompt_loader.py:load_prompt(name, **fmt)`.

### Files (7)

| File | Loaded by | Role |
| --- | --- | --- |
| `judge_system.md` | `grading._judge_system_prompt` | Walkthrough Yes/No verdict format (b78). |
| `judge_user.md` | `grading._judge_user_prompt` | Template; placeholders: `{task_description}`, `{transcript}`, `{output_files}`, `{rubrics_block}`, `{n_criteria}`. |
| `testgen_system.md` | `testgen.generator._load_prompt("testgen_system")` | Test-generation system prompt. |
| `testgen_intent.md` | `testgen.intent._load_intent_system_prompt` | Intent extraction. |
| `testgen_user.md` | reference only (not loaded by code) | Test-generation user prompt template. |
| `testgen_weights_system.md` | reference only | Weight assignment system prompt. |
| `testgen_rubric_overlap.md` | reference only | Rubric/test overlap heuristics. |

### Loader contract

- `load_prompt('judge_system')` — returns the file's text verbatim. LRU-cached after first read.
- `load_prompt('judge_user', task_description='…', transcript='…', output_files='…', rubrics_block='…', n_criteria=12)` — returns the file's text with `.format(**fmt)` applied.
- `.md` suffix optional: both `'judge_system'` and `'judge_system.md'` work.
- Repo-root anchored — works regardless of `cwd` (test_executor subprocesses, CI runners).
- Missing file → `PromptNotFoundError`. Path traversal (e.g. `../etc/passwd`) → `PromptNotFoundError`.
- Hot-edit a prompt: set `WCB_PROMPT_NOCACHE=1` to bypass the cache. Otherwise restart Python.

### Editing footgun

Prompts loaded with `**fmt` are Python format strings — literal `{` or `}` MUST be doubled (`{{`, `}}`). Prompts loaded with no `**fmt` skip `.format()` entirely (braces pass through).

### See also

`system_prompts/README.md` for the loader contract from the prompt author's perspective.
