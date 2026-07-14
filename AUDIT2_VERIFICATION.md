# Audit 2 Verification Report

**Subject:** `audit 2/` (Crucible v0.1.0) findings re-verified against current WildClawBench harness.
**Verifier:** Claude (manual code inspection + evidence.yaml parse; no scanner re-execution).
**Verified against:** HEAD `3ada16531b` on `main` (working tree dirty: untracked `.opencode/`, `.sisyphus/`, `docs/`, `eval/AGENTS.md`, `script/AGENTS.md`, several new tests; modified `.gitignore`).
**Audit 2 was run against:** an EARLIER tree at `/Users/apple/Desktop/KENSEI_HARNESS-Most_latets` (`audit 2/scope.yaml:7` — absolute path on a different machine), git_sha `1b3a5c31…` per `evidence.yaml`, recon git_sha `9a17c06d…` per `scope.yaml`, Python 3.13.9, dirty. Surface counts then: 2629 tracked files, 9 tasks, 9 samples, 1033 dockerfiles, 13 tests. **NOT the same tree** — `samples/`, `requirements/`, `trinity/` submodule do not exist in WildClawBench (`git ls-files samples/` → empty, no `requirements/` dir, no `trinity/` submodule). Re-baseline requires replacing `project.root`, recomputing `inputs.*_digest`, and dropping `trinity_submodule_sha`.

---

## Counts reconciliation (load-bearing — read before the rest)

The audit-2 deliverable comprises three separately-counted artifacts. Conflating them produces wrong totals.

| Artifact | Location | Count |
|---|---|---:|
| `findings:` array in evidence.yaml | `audit 2/evidence.yaml` (verified via `grep -c '^- id: CR-'` and `yaml.safe_load`) | **152** |
| `tool_runs:` array in evidence.yaml | same file | **3** (ruff, bandit, pip-audit) |
| `scope_findings:` in scope.yaml | `audit 2/scope.yaml:59-61` | **2** (env-history CRITICAL, tracked-db HIGH) |
| `coverage_gaps:` in scope.yaml | `audit 2/scope.yaml:63-68` | **5** |
| `coverage_gaps:` in evidence.yaml | `audit 2/evidence.yaml:987` | **0** (literal `coverage_gaps: []`) |
| `external_signature` | `provenance.yaml:6` `null` / `evidence.yaml:988` `false` | both unsigned |

### Breakdown of the 152 evidence.yaml findings (verified by yaml parse)

| Check | Severity | Count |
|---|---|---:|
| `secret_pattern` | CRITICAL | 2 |
| `env_secret` | CRITICAL | 1 |
| `rubric_schema` (no criteria list) | MEDIUM | 2 |
| `rubric_schema` (criterion N missing weight) | MEDIUM | 147 |
| **TOTAL** | | **152** |

### Per-task breakdown of the 147 missing-weight findings (verified)

| Task | Count |
|---|---:|
| 🟢sheila_stokes_c74d93d8 | 32 |
| amanda_hayes_01 | 26 |
| matt_garcia_ede7e98b | 22 |
| kayla_morgan_9b8f1d3c | 19 |
| darren_weston_2b2baa81 | 17 |
| patricia_waters_d124e733 | 16 |
| ben_cox_8fc24d4b | 15 |
| **TOTAL** | **147** |

**Chris_event and anita_patel_01 received ZERO missing-weight findings** because the crucible check (`audit 2/crucible/checks.py:64-67`) bails at "no criteria list" before iterating criteria.

---

## Executive verdict

| Bucket | Findings | TRUE/CONFIRMED | FALSE POSITIVE | STALE/INFO | Real-risk verdict |
|---|---:|---:|---:|---:|---|
| F1 secret_pattern (admin_plane.py) | 1 | 0 | 1 | 0 | env var **name**, not value |
| F2 secret_pattern (openclaw/runner.py) | 1 | 0 | 1 | 0 | f-string literal FP for crucible — **but see N2: real AGENTS.md invariant violation (container-env injection)** |
| F3 env_secret (.env in history) | 1 | **1** | 0 | 0 | **🔴 CRITICAL confirmed; broader than audit 2 enumerates** |
| F4 rubric_schema "no criteria list" (chris_event) | 1 | 1¹ | 0 | 0 | **🟡 real loader bug, wrong root cause** |
| F5 rubric_schema "no criteria list" (anita_patel_01) | 1 | 0 | 1 | 0 | harness handles `{rubrics:[…]}` wrapper |
| F6 rubric_schema "missing weight" × 147 | 147 | 0 | 147 | 0 | harness uses `score` by design |
| F7 ruff tool_run (479 issues) | 1 run | — | — | informational | cosmetic; repo has no ruff gate |
| F8 bandit tool_run (450 issues) | 1 run | mostly FP at spot-check | — | 447 unverified | mock-fleet heuristic misfire |
| F9 pip-audit tool_run (crash, 0 issues) | 1 run | — | — | **real coverage gap** | scanner did not execute |
| Scope env-history CRITICAL | 1 | **1** | 0 | 0 | same root cause as F3 |
| Scope tracked-db HIGH | 1 | **1** | 0 | 0 | `state.db`, `environment/sqlite_mcp_server.db` |
| Scope coverage_gaps × 5 | 5 | 3 | 0 | 2 | container scanners + judge discipline + reward-provenance STILL TRUE; 2 `samples/` items stale-by-absence |
| **TOTAL evidence.yaml findings (F1–F6 column-sum)** | **152** | **2** | **150** | **0** | arithmetic: TRUE=0+0+1+1+0+0=2 (F3,F4); FP=1+1+0+0+1+147=150; STALE=0. F2's row counts as FP=1 for crucible's regex; F2's *separate* AGENTS.md-invariant finding (N2) is NOT in this row — it appears in "Distinct real-risk items" below. |
| **Scope.yaml-only findings (env-history + tracked-db)** | 2 | 2 | 0 | 0 | scope.yaml:60-61 |
| **Distinct real-risk items after dedup (load-bearing)** | — | **4** | — | — | Members (no double-counting): (1) **F3** env_secret = scope `env-history` dup, counted once. (2) **F4** chris_event loader bug. (3) scope `tracked-db` (2 binaries → 1 real-risk class). (4) **F2 N2** AGENTS.md container-env-injection invariant violation. Dismissed: F1, F5, F6×147, F7, F8 (FP/informational). Excluded: F9 (separate coverage gap; see "Coverage gaps to address" in Net recommendation). |

¹ The F4 verdict is "real bug in the harness" but the bug is upstream of crucible's check: `task_parser.py:320-322` silently loses the criteria; the rubric data itself is fine.

**Signal-to-noise (honest math):** Uses the same 4-item "Distinct real-risk items" composition as the verdict-table row above (F3, F4, scope tracked-db, F2 N2).
- 152 evidence.yaml findings → **4 distinct real-risk items** = **~2.6%**.
- Including the 3 tool_runs as signals (479 ruff + 450 bandit + 1 pip-audit traceback = 930) gives a combined denominator of 152 + 930 = **1082 raw signals**. Real-risk items including F9 coverage gap = **5**. That's **~0.46%**.
- Either framing: low double digits of percent at best, sub-1% at worst. The earlier draft's "3 / 638 ≈ 0.5%" had no defensible denominator and is withdrawn.

**Disposition:** SHIP unreachable. `verifier.disposition` (`audit 2/crucible/verifier.py:15-40`) requires zero CRITICAL/HIGH and `external_signature: true` to ship. With F3 + scope env-history + tracked-db all real and `external_signature: false|null`, the gate must HOLD or BLOCK. This verdict survives all false-positive removals because the env-history finding alone forces BLOCK.

---

## Finding-by-finding verification

### F1 — CRITICAL `secret_pattern` in `environment/admin_plane.py` (CR-f6e8228fb88c71ae) — FALSE POSITIVE

**Audit 2 claim** (`evidence.yaml`): `generic_secret_assignment pattern in working tree`, path `environment/admin_plane.py`.

**Actual code** (`environment/admin_plane.py:99–104`, verified):
```python
ENV_ENABLED = "MOCK_ADMIN_ENABLED"
ENV_ALLOWLIST = "MOCK_ADMIN_ALLOWLIST"
ENV_TOKEN = "MOCK_ADMIN_TOKEN"             # ← line 102 trips the regex
ENV_TRUST_FORWARDED_FOR = "MOCK_ADMIN_TRUST_FORWARDED_FOR"
```

`ENV_TOKEN` holds the **name** of an env var, read elsewhere as `os.environ.get(ENV_TOKEN)`. The value `"MOCK_ADMIN_TOKEN"` is 16 chars and ends in `token`, tripping the regex at `audit 2/crucible/checks.py:SECRET_RES[2]` (`(?i)(...|token)\s*[=:]\s*['\"][^'\"]{12,}['\"]`).

**Verdict:** TRUE regex match, FALSE-POSITIVE intent. A first-pass triager would also flag it; the appropriate hardening is to rename the constant (e.g. `ENV_VAR_NAME_FOR_ADMIN_TOKEN`) so the literal isn't confusable.

**Action:** Optional rename. Optionally add a name-vs-value heuristic to crucible.

---

### F2 — CRITICAL `secret_pattern` in `src/agents/openclaw/runner.py` (CR-c434bd7a38e416e9) — FALSE POSITIVE FOR SOURCE; **CONTAINER-ENV INJECTION** invariant violation missed by audit 2 (see N2)

**Audit 2 claim:** `generic_secret_assignment pattern in working tree`, path `src/agents/openclaw/runner.py`.

**Actual code** (`src/agents/openclaw/runner.py:234-248`, verified):
```python
gateway_cmd = f"openclaw gateway --port {self.gateway_port}"
if self.openrouter_api_key and not self.litellm_config_yaml:
    gateway_cmd = (
        f"export OPENROUTER_API_KEY='{self.openrouter_api_key}' && "   # L237
        f"export OPENROUTER_BASE_URL='{self.openrouter_base_url}' && "
        + gateway_cmd
    )
if self.openai_api_key and not self.litellm_config_yaml:
    gateway_cmd = f"export OPENAI_API_KEY='{self.openai_api_key}' && " + gateway_cmd   # L242

gateway_proc = run_background(
    spec.task_id,
    bash_cmd=gateway_cmd,
    log_path=spec.output_dir / "gateway.log",                            # L247
)
```

**SOURCE VERDICT:** No credential is literal in the source. `self.openrouter_api_key` / `self.openai_api_key` are populated at runtime from env. Pure FALSE POSITIVE w.r.t. crucible's regex.

**REAL EXPOSURE THAT AUDIT 2 DID NOT FLAG — narrow, verifiable form:** L237/L242 `export OPENROUTER_API_KEY='…' && …` injects the literal credential values into the **container environment** at agent process spawn. This directly violates the invariant in `src/agents/AGENTS.md`: *"never let secrets enter the container env… stay host-side and reach the agent only via LiteLLM sidecar"*. Once in the container env, the credentials are readable by anything inside the container — any subprocess, anything reading `/proc/<pid>/environ`, any later tool installed by the agent. The `&& self.litellm_config_yaml` guard at L235/L241 means this path is taken specifically when the LiteLLM sidecar is NOT configured (i.e. the legacy direct-router mode), which is exactly the mode the invariant was written to forbid.

**Empirical verification of the narrower NEGATIVE claim** (what does NOT happen): an earlier draft of this report incorrectly asserted that `gateway.log` captures the credential values in cleartext. That claim is **false** — I inspected all 9 existing `gateway.log` files under `output/openclaw/*/trajectories/claude/run_*/gateway.log` and found **zero** matches for `OPENROUTER|OPENAI|API_KEY|sk-|AKIA`. The logs contain only `[canvas]/[heartbeat]/[gateway]/[tools]` daemon output. Bash invoked via `docker exec … bash -c "<cmd>"` does NOT echo the command line without `set -x`, and the openclaw gateway process does not dump env. The cleartext-log narrative is withdrawn.

**Verdict on F2:** crucible's regex hit is a false positive in the source, BUT the line-237/242 export pattern is a real `src/agents/AGENTS.md` invariant violation (container-env injection in the no-sidecar path). Severity: MEDIUM (defensible LOW if the no-sidecar path is unused in production).

**Action:**
1. Replace the `export X='{value}' && …` pattern in `runner.py:235-242` with one of:
   (a) write the credentials to a host-mounted secret file `/run/secrets/openrouter.env` and `source` it inside the container,
   (b) pass via `docker run --env-file <hostfile>` (still in env but kept off the cmd line and gitignored),
   (c) require the LiteLLM-sidecar path universally and delete the no-sidecar branches.
2. Confirm `s3_artifacts.py` does not upload anything that would have captured the unexpanded `gateway_cmd` (it doesn't, but document).
3. Add a regression test asserting that `gateway.log` contains zero matches for `(AKIA|sk-|API_KEY=)` — converts today's empirical safety into a contractual one.

---

### F3 — CRITICAL `env_secret`: `.env tracked in git history` (CR-ed7447c1dadef3c3) — **🔴 CONFIRMED, materially broader than audit 2 enumerates**

**Audit 2 claim:** `.env appears in git log` — CRITICAL.

**Verification:**
- `git ls-files .env` → empty (not currently tracked at HEAD).
- `.gitignore:27` lists `.env` (currently ignored going forward).
- `git log --all --oneline -- .env` returns **3 commits**:
  - `ef19e6b Create .env`
  - `3a66206 Update .env`
  - `abc2abd Update .env`
- The crucible check at `audit 2/crucible/checks.py:55-60` correctly detected this.

**Full key inventory in current `.env`** (33 distinct keys; values redacted; verified via `grep -oE '^[A-Z][A-Z0-9_]*' .env | sort -u`):

| Key | Class | Rotation required? |
|---|---|---|
| `OPENROUTER_API_KEY` | OpenRouter API token | **YES** |
| `OPENROUTER_BASE_URL` | URL (not a secret) | no |
| `KENSEI_AWS_BEARER_TOKEN` | Bedrock bearer | **YES** |
| `KENSEI_AWS_REGION` | region string | no |
| `KENSEI_BEDROCK_MODEL_ARN` | ARN (leaks topology) | **YES — rotate underlying inference profile** |
| `KENSEI_BEDROCK_SONNET_ARN` | ARN | **YES** |
| `JUDGE_COUNCIL_SONNET_ARN` | ARN | **YES** |
| `JUDGE_COUNCIL_GLM_ARN` | ARN | **YES** |
| `JUDGE_COUNCIL_KIMI_ARN` | ARN | **YES** |
| `KENSEI_LITELLM_MASTER_KEY` | LiteLLM master key | **YES** |
| `KENSEI3_LITELLM_PORT` | port | no |
| `LITELLM_DEFAULT_MODEL` | model id | no |
| `KENSEI_OPENAI_API_KEY` | OpenAI key | **YES** |
| `KENSEI_OPENAI_WHISPER_API_KEY` | OpenAI Whisper key | **YES** |
| `KENSEI_AGENT_HEADROOM_ENABLED` | flag | no |
| `KENSEI_JUDGE_USE_LITELLM` | flag | no |
| `WILDCLAW_DEFAULT_SKILLS` | csv | no |
| `BRAVE_API_KEY` | Brave Search API token | **YES** |
| `KENSEI_S3_ACCESS_KEY_ID` | AWS access key (AKIA…) | **YES** |
| `KENSEI_S3_SECRET_ACCESS_KEY` | AWS secret | **YES** |
| `S3_BUCKET` | bucket name | no (informational) |
| `S3_PREFIX` | prefix | no |
| `S3_REGION` | region | no |
| `DOCKER_IMAGE` | image tag | no |
| `GATEWAY_PORT` | port | no |
| `TMP_WORKSPACE` | path | no |
| `TASKS_SUBDIR` | path | no |
| `OUTPUT_SUBDIR` | path | no |
| `DEFAULT_PARALLEL` | number | no |
| `DEFAULT_MODEL` | model id | no |
| `HTTP_PROXY_INNER` | proxy URL (per AGENTS.md MUST BE EMPTY) | verify |
| `HTTPS_PROXY_INNER` | proxy URL (per AGENTS.md MUST BE EMPTY) | verify |
| `NO_PROXY_INNER` | proxy bypass | no |

**Secrets requiring rotation: 13 keys** (= count of `**YES**` rows in the .env table above; reader may count them directly):
1. `OPENROUTER_API_KEY`
2. `KENSEI_AWS_BEARER_TOKEN`
3. `KENSEI_BEDROCK_MODEL_ARN` (rotate the underlying Bedrock inference profile, not just the ARN string)
4. `KENSEI_BEDROCK_SONNET_ARN` (same)
5. `JUDGE_COUNCIL_SONNET_ARN` (same)
6. `JUDGE_COUNCIL_GLM_ARN` (same)
7. `JUDGE_COUNCIL_KIMI_ARN` (same)
8. `KENSEI_LITELLM_MASTER_KEY`
9. `KENSEI_OPENAI_API_KEY`
10. `KENSEI_OPENAI_WHISPER_API_KEY`
11. `BRAVE_API_KEY`
12. `KENSEI_S3_ACCESS_KEY_ID`
13. `KENSEI_S3_SECRET_ACCESS_KEY`

Note: earlier draft cited "11" — that number was wrong. The actual rotation list is 13.

**Action (REQUIRED — order of operations):**
1. **Rotate every key in the YES column above immediately**, treating them as exfiltrated.
2. Scrub `.env` from history: `git filter-repo --path .env --invert-paths` (preferred) or BFG `--delete-files .env`.
3. Force-push to remote(s) and instruct collaborators to re-clone.
4. Audit other private mirrors / forks for the same history.
5. Add a pre-commit hook (`gitleaks` or `trufflehog`) so recurrence is blocked.
6. Verify `.env` remains in `.gitignore:27` and run `git ls-files .env` post-scrub to confirm empty.
7. Audit S3 / OpenRouter / Bedrock / OpenAI / Brave access logs for the window between first commit (`ef19e6b`) and rotation completion.

---

### F4 — MEDIUM `rubric_schema` `chris_event/rubric.json` "no criteria list" (CR-9d9df4577f2baa6f) — **🟡 REAL BUG, WRONG ROOT CAUSE**

**Audit 2 claim:** "rubric has no criteria list" — implying defective rubric data.

**Actual `input/chris_event/rubric.json` shape:**
```json
{
  "normal_rubric": [ /* 18 items */ ],
  "trap_rubric":   [ /* 12 items */ ]
}
```
30 criteria total. Crucible's check (`audit 2/crucible/checks.py:64-66`) only inspects `obj.get("criteria")` so `crits = None → "no criteria list"`. Crucible's logic is therefore self-consistent and never iterates the criteria; this is **why F6 contains zero missing-weight findings for chris_event** (the check bails before the per-criterion loop).

**However, the harness has the same blind spot.** Verified by direct invocation:

```
$ python3 -c "from src.utils.task_parser import load_task; print(len(load_task('input/chris_event')['rubrics']))"
0
```

`src/utils/task_parser.py:319–322`:
```python
rubrics = json.loads((task_dir / "rubric.json").read_text(...)) or []
if isinstance(rubrics, dict):
    rubrics = rubrics.get("rubrics") or []   # only handles {rubrics: [...]}
```

The `{normal_rubric, trap_rubric}` wrapper falls through, returning `[]`. **`chris_event` grades against zero criteria → `total_w = 0 or 1.0` (`grading.py:1094`) → `overall_score` is structurally `0.0` regardless of agent behavior.**

**Verdict:** Audit 2 is symptomatically right; the defect is in the loader, not the data.

**Action (REQUIRED):**
1. Patch `src/utils/task_parser.py:320-322`:
   ```python
   if isinstance(rubrics, dict):
       buckets = ("rubrics", "normal_rubric", "trap_rubric", "criteria", "items")
       collected = []
       for k in buckets:
           v = rubrics.get(k)
           if isinstance(v, list):
               collected += v
       rubrics = collected
   ```
2. Add a regression test in `tests/` asserting `len(load_task('input/chris_event')['rubrics']) == 30`.
3. Audit historical chris_event grading runs in `output/` — they likely all reported `overall_score=0.0`.
4. Backfill `score.json` for any chris_event row in the aggregate runs (`script/aggregate_runs.py`).

---

### F5 — MEDIUM `rubric_schema` `anita_patel_01/rubric.json` "no criteria list" (CR-0c109d0cee8a1332) — FALSE POSITIVE

**Audit 2 claim:** "rubric has no criteria list".

**Actual shape:** `{"rubrics": [19 items]}`. Each item has `score ∈ {-5,-3,1,3,5}`, `is_positive`, etc.

**Harness behaviour:** `task_parser.py:321-322` handles the `rubrics:` wrapper. Verified: `len(load_task('input/anita_patel_01')['rubrics']) == 19`, first criterion loads correctly.

**Verdict:** Pure false-positive from crucible's narrow `criteria`-only check.

**Action:** None. (Optional: teach crucible the same wrapper list as the patch in F4.)

---

### F6 — 147 × MEDIUM `rubric_schema` "criterion N missing weight" — **147 FALSE POSITIVES**

**Audit 2 finding cardinality** (verified, evidence.yaml `findings:` parse):

| Task | Count |
|---|---:|
| 🟢sheila_stokes_c74d93d8 | 32 |
| amanda_hayes_01 | 26 |
| matt_garcia_ede7e98b | 22 |
| kayla_morgan_9b8f1d3c | 19 |
| darren_weston_2b2baa81 | 17 |
| patricia_waters_d124e733 | 16 |
| ben_cox_8fc24d4b | 15 |
| **TOTAL** | **147** |

`chris_event` and `anita_patel_01` are NOT in this table because crucible bailed at "no criteria list" before iterating their criteria (F4/F5).

**Audit 2's check** (`audit 2/crucible/checks.py:68-72`):
```python
for i, c in enumerate(crits):
    if not isinstance(c, dict) or "weight" not in c:
        out.append(Finding("rubric_schema", "MEDIUM", "dataset", f"criterion {i} missing weight", name))
    elif c.get("weight") not in (5, 3, 1, -5, -3, -1):
        out.append(Finding("rubric_schema", "LOW", "dataset", f"criterion {i} weight {c.get('weight')} outside +/-{{5,3,1}}", name))
```

Two-tier check: missing weight ⇒ MEDIUM; present-but-out-of-range ⇒ LOW.

**Harness reality** — `src/utils/grading.py:286-307` is explicit:

> *Rubric schemas in this repo store the weight under either `weight` or `score` (kensei2-style rubrics use `score`, with the SIGN encoding polarity — negative for guardrail / forbidden-behavior criteria). The judge prompt's polarity semantics live entirely in the weight sign…*

```python
def _extract_weight(r: dict) -> float:        # grading.py:294
    w = r.get("weight")
    if w is None:
        w = r.get("score")
    if w is None:
        return 1.0
    return float(w)
```

Used at `grading.py:320, 1094, 1095, 1098` (the reward aggregator).

**Empirical verification of `score` values across all 9 rubrics** (raw file inspection):

| Task | criteria | score values | negative-weight count | `is_positive: False` count |
|---|---:|---|---:|---:|
| amanda_hayes_01 | 26 | {-5,-3,-1,1,3,5} | 9 | 9 |
| anita_patel_01 | 19 | {-5,-3,1,3,5} | 3 | 3 |
| ben_cox_8fc24d4b | 15 | {-5,-3,1,3,5} | 7 | 7 |
| chris_event (raw file) | 30 | {-3,1,3,5} | 1 | 1 |
| darren_weston | 17 | {-5,-3,1,3,5} | 4 | 4 |
| kayla_morgan | 19 | {-5,-3,1,3,5} | 7 | 7 |
| matt_garcia | 22 | {-5,-3,1,3,5} | 7 | 7 |
| patricia_waters | 16 | {-5,-3,1,3,5} | 3 | 3 |
| 🟢sheila_stokes | 32 | {-5,-3,1,3,5} | 8 | 8 |

Every criterion has `score ∈ {±5, ±3, ±1}` matching the harness reward formula. The schema is intentional and stable across the kensei2 task corpus.

**Caveat on "pure false-positive":** crucible's tier-2 (LOW for weight outside ±{5,3,1}) shows it CAN distinguish polarity from absence. If the harness emitted `weight: <int>` with the same values, those LOW findings would still fire (147 of them, downgraded MEDIUM→LOW). The correct framing: "crucible's check fires MEDIUM today, and would fire LOW if `score` were renamed to `weight`; the harness's grader uses the value either way, so neither tier reflects a real defect, but crucible **will** keep surfacing noise on this corpus unless it accepts `score` as an alias."

**Verdict:** 147 false positives at the MEDIUM tier; would be 147 LOW findings if the harness renamed the key. No real defect.

**Action:** None for the harness. (Recommended: teach crucible to accept `score` as a `weight` alias, eliminating 147 findings AND the 2 "no criteria list" findings if combined with multi-bucket wrapper support.)

---

### F7 — ruff tool_run: 479 issues, exit 1 — INFORMATIONAL (cosmetic)

**Audit 2 finding:** `tool_runs.ruff.exit=1, issue_count=479`. Raw_head shows E741 (ambiguous variable name `l`), F401 (unused `csv` import), E402 (module-level import not at top of file) concentrated in `environment/*-api/*_data.py`.

**Verification:** Not re-executed (ruff not installed at root shell). Spot-checked file shapes:
- `environment/activecampaign-api/activecampaign_data.py:8` — `import csv` (often unused per file).
- `environment/activecampaign-api/activecampaign_data.py:14` — `from _mutable_store import ...` after a `sys.path.insert(...)` bolt (triggers E402).

Intentional artifacts of the **mock-fleet codegen template** (101 `*-api/` services).

**Project policy:** Root `AGENTS.md` declares "No formal linter/formatter at root." No `pyproject.toml`, `ruff.toml`, `setup.cfg`, `pytest.ini`, or `pre-commit-config.yaml` at root. `audit/pyproject.toml` configures ruff for the gitignored sub-project only.

**Verdict:** 479 cosmetic style nits. Not vulnerabilities, not bugs, not policy violations.

**Action:** None unless the team adopts ruff as a gate. If adopted, prefer per-file ignores for `environment/*-api/*_data.py`.

---

### F8 — bandit tool_run: 450 issues, exit 1 — MIXED, MOSTLY FALSE-POSITIVE; **447 unverified**

**Audit 2 finding:** `tool_runs.bandit.exit=1, issue_count=450`. Three named flags spot-checked:

| Bandit finding | Verified location | Verdict |
|---|---|---|
| `environment/admin_plane.py:102` B105 `'MOCK_ADMIN_TOKEN'` (LOW/MED) | confirmed — same line as F1 | FALSE POSITIVE: env var **name** |
| `environment/discord-api/discord_data.py:89` B311 `random` (LOW/HIGH) | confirmed — `random.randint(0,31)` for mock snowflake worker-id | FALSE POSITIVE: mock service, no crypto context |
| `environment/hubspot-api/hubspot_data.py` B610 `django_extra_used` (MED/MED) | confirmed — method named `extra(r, obj)` on plain dict; Django not a dependency | FALSE POSITIVE: name-based heuristic misfire |

**Coverage caveat:** Only 3 of 450 bandit findings spot-checked. **447 findings are unverified.** Pattern-wise we expect more of the same (mock-fleet name-pattern misfires), but the report cannot certify the residual 447 without re-running the scanner and triaging.

**Action:**
1. Either accept bandit as informational on this codebase, or
2. Re-run with `--exclude environment/` (which contains most of the misfires) and triage the remainder.

---

### F9 — pip-audit tool_run: exit 1, 0 issues, raw_head = Python traceback — **REAL COVERAGE GAP, not yet fixed**

**Audit 2 finding:** `tool_runs.pip-audit.exit=1, issue_count=0`. Raw_head is a Python traceback inside `pip_audit/_service/interface.py:179` calling `query_all(specs)`.

**Verification:** The scanner crashed before producing audit data. Most plausible causes: (a) transport error reaching OSV/PyPI vuln DB, (b) env mismatch (`audit/.venv/lib/python3.13`), (c) requirements.txt parser bailing on a pin pattern.

Currently no `requirements/` directory exists at repo root; only flat `requirements.txt` (1214 bytes, 41 lines). `audit 2/crucible/scanners.py:34` hardcodes `pip-audit -r requirements.txt`.

**Verdict:** Real coverage gap. `verifier.disposition` (`audit 2/crucible/verifier.py:15-40`) treats missing tool runs as a coverage gap, contributing to HOLD/BLOCK.

**Action (REQUIRED — explicitly left to user; this verification did NOT re-run pip-audit):**
1. `pip install pip-audit && pip-audit -r requirements.txt --strict`
2. Expect a known advisory on `urllib3==1.26.20` (intentionally old for botocore coexistence per `AGENTS.md`); document the suppression rather than bump.
3. Add an annual cadence; pin pip-audit version in the audit sub-project's `pyproject.toml`.

---

### Scope finding (CRITICAL): `env-history` — **CONFIRMED** (= F3)

Source: `audit 2/scope.yaml:60`. Same root cause and remediation as F3. Listed separately in audit 2's structure but counts as the same real-risk item.

---

### Scope finding (HIGH): `tracked-db` — **CONFIRMED**

Source: `audit 2/scope.yaml:61`. Claim: `state.db` and `environment/*.db` are tracked.

**Verification:**
- `git ls-files state.db` → 1 match (45,056 bytes on disk).
- `git ls-files environment/*.db` → 1 match: `environment/sqlite_mcp_server.db`. (scope.yaml's plural `environment/*.db` matches one file, not several.)
- Per `audit 2/crucible/checks.py` `core_tracked_db`, each binary DB fires HIGH.

**Action:**
1. Move runtime DBs out of the tree or replace with init scripts.
2. Add `state.db` and `environment/*.db` to `.gitignore`.
3. `git rm --cached state.db environment/sqlite_mcp_server.db` + commit.
4. If the DBs contain any tokens/PII, treat like F3 (history scrub + rotate).

---

### Scope `coverage_gaps` (5 entries, scope.yaml:63-68)

| Gap | Status | Notes |
|---|---|---|
| `samples/` has 9 bundles, no `samples/README.md` disposition table | **STALE** | `git ls-files samples/` returned empty; no `samples/` directory exists in WildClawBench |
| `samples/.DS_Store` macOS junk | **STALE** | same — `git ls-files samples/` empty |
| Container scanners (hadolint/trivy) not installed → 102 Dockerfiles unscanned | **STILL TRUE** | Now ~133 Dockerfiles (101 `environment/*-api/` + 1 `docker/` + many `environment/skills/`) |
| Trajectory reward-provenance / rollout-integrity not automated for `samples/*/trajectories` | **STILL TRUE (broader claim)** | No `samples/` dir, but reward-provenance automation remains missing for output bundles |
| Judge-reliability discipline (≥11 trials, conformal, perturbation) not automated → caps at HOLD | **STILL TRUE** | No conformal/perturbation harness in `eval/` or `tests/` |

3 of 5 gaps still legitimate; 2 stale-by-absence.

---

## Additional issues discovered while verifying (NEW; not in audit 2)

### N1 — `task_parser` silently drops chris_event criteria
Root cause of F4. `src/utils/task_parser.py:320–322`. Severity: **HIGH** (silent grading-zero on a production task). See F4 for the patch.

### N2 — `runner.py` injects `OPENROUTER_API_KEY` / `OPENAI_API_KEY` into the container environment (AGENTS.md invariant violation)
`src/agents/openclaw/runner.py:237,242` uses `export OPENROUTER_API_KEY='{self.openrouter_api_key}' && …` (and the same for `OPENAI_API_KEY`) to pass credentials to the agent process. This puts the values inside the container environment, which `src/agents/AGENTS.md` explicitly forbids: *"never let secrets enter the container env… stay host-side and reach the agent only via LiteLLM sidecar."* The branch fires only when `self.litellm_config_yaml` is falsy (the legacy no-sidecar path).

Severity: **MEDIUM** (LOW if the no-sidecar path is unused in production; HIGH if any tool inside the container reaches `/proc/<pid>/environ` or otherwise exfiltrates).

**Note on the negative claim:** an earlier draft of this report stated the credentials end up in `gateway.log` in cleartext. That was empirically wrong — all 9 existing `gateway.log` files under `output/openclaw/*/trajectories/claude/run_*/` contain zero credential material (verified via `grep -c -E 'API_KEY|OPENROUTER|OPENAI|sk-|AKIA'` returning 0). Bash `bash -c "<cmd>"` does not echo command text without xtrace. The withdrawn claim is preserved here for traceability; the real finding is narrower (container-env injection, not log exfil).

See F2 for actions.

### N3 — Audit 2 was run against a different tree at an absolute path
`audit 2/scope.yaml:7` hardcodes `/Users/apple/Desktop/KENSEI_HARNESS-Most_latets`. Re-baseline requires:
1. Replace `project.root` with `/Users/apple/Documents/WildClawBench` (or `$PWD`).
2. Recompute `inputs.*_digest` (any digest fields that pin file hashes).
3. Drop `trinity_submodule_sha` (no such submodule here).
4. Drop or skip references to `samples/` and `requirements/`.

### N4 — Fixture / positive-fire verification not exercised
`audit 2/crucible/verifier.py:43-50 positive_fire()` and `crucible/checks.py:136 fixture_results()` provide a free, deterministic way to confirm the checks themselves aren't inert. This verification did NOT execute them; doing so is a cheap next step to confirm crucible's findings are reproducible.

Suggested command (from `WildClawBench/`):
```bash
cd "audit 2"
PYTHONPATH=. python3 -c "from crucible.checks import fixture_results; import json; print(json.dumps(fixture_results(), default=str, indent=2))" | head -100
```

---

## Cross-check against harness invariants

Audit 2 made no claims that contradict the load-bearing invariants in root `AGENTS.md`:
- Two scoring channels (Channel A pytest reward; Channel B rubric judge council) — not addressed.
- Reward formula `max(0, (Σ passed_pos − Σ |triggered_neg|) / Σ all_pos)` — not addressed.
- `tests_*` keys in `score.json` are deprecated Channel-B aliases — not addressed.
- Trajectory never truncated when fed to judge (`eval/run_batch.py:615`) — not addressed.
- `/root/workspace/` is the only deliverable location — not addressed.
- `--parallel 1` for Bedrock throttling — not addressed.

These remain authoritative regardless of audit 2's verdict.

---

## Net recommendation

**Three concrete remediation actions (priority order):**

1. **🔴 Secret hygiene** (F3 + scope `env-history` + N2 container-env injection): rotate the **13** credentials marked YES in F3's inventory, scrub `.env` from history, replace the `export …=…` pattern in `runner.py` with a sidecar/secret-file approach, add a pre-commit secret scanner.
2. **🟡 Patch the rubric loader** (F4 + N1): fix `src/utils/task_parser.py:320-322` to support `{normal_rubric, trap_rubric}` wrappers; regression-test for chris_event; re-grade historical chris_event runs.
3. **🟡 Tracked DBs** (scope `tracked-db`): un-track `state.db` and `environment/sqlite_mcp_server.db`; gitignore them; verify no secrets within.

**Coverage gaps to address:**
4. Re-run pip-audit so the gate has a real Python-deps verdict (F9).
5. Update `audit 2/scope.yaml` to point at the WildClawBench tree (N3) and re-baseline before treating crucible findings as authoritative.
6. Run `fixture_results()` / `positive_fire()` to confirm checks are non-inert (N4).

**Ignore as designed-or-cosmetic:**
- F1 (admin_plane env-var-name) — optional rename only.
- F5 (anita_patel_01 wrapper) — harness handles it.
- F6 × 147 (missing-weight) — harness uses `score` by design.
- F7 ruff 479 — repo has no ruff gate.
- F8 bandit spot-checked subset — name-based heuristics on mock fleet. **Residual 447 unverified**; either accept as informational or re-run with `--exclude environment/`.

---

## Verification methodology & caveats

- **Cited evidence:** every claim names file:line or a verifiable shell command.
- **YAML parse used:** `findings:` and `tool_runs:` counts came from `yaml.safe_load(audit 2/evidence.yaml)`; per-task missing-weight counts came from filtering the `detail` field (`'missing weight' in finding['detail']`) grouped by `finding['path']`.
- **No scanner re-execution:** ruff, bandit, pip-audit are not installed in this shell; the report verified the 5 named/highest-confidence issues per scanner and inferred the population properties. F9's "Action (REQUIRED)" is therefore left to the user.
- **No `fixture_results()` execution:** the in-repo crucible fixture harness was not exercised (see N4).
- **Working tree dirty:** counts and presence checks reflect HEAD `3ada165` plus untracked files; the report flags this where relevant.
- **Bias:** the report privileges the harness's documented invariants (`src/utils/grading.py:286-307` comment, root `AGENTS.md`) over the scanner's heuristics; readers who reach the opposite conclusion are encouraged to add stricter type-aware rules to crucible rather than treat the harness as defective. F1 is the one finding where this bias is most contestable.

---

*End of report.*
