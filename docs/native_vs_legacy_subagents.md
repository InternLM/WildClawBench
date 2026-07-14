# Native OpenClaw Sub-agents vs. the Legacy Spawn Process

How multi-agent (sub-agent) spawning works in WildClawBench, and how the
**native OpenClaw** path differs from the **legacy connector-skill** path it
replaced.

---

## TL;DR

| | **Legacy** (`spawn-subagent-connector`) | **Native** (current default) |
|---|---|---|
| Who actually spawns | A **harness Python script** (`subagent_director.py`) | The **OpenClaw binary** (`sessions_spawn`) |
| What the parent invokes | `Bash → python3 .../spawn_subagent.py` (a skill) | The native `sessions_spawn` tool |
| What a "child" is | A bounded LLM call the script makes to LiteLLM | A **real OpenClaw session** in the session store |
| Child tools | Fixed custom allowlist (`Read/Write/Edit/Grep/Glob/Bash`) | Full OpenClaw tool set + the task's connector skills |
| Child transcript | `{spawn_id}.jsonl` written by the script | `…/agents/main/sessions/<uuid>.jsonl` written by the binary |
| Spawn ledger | `spawn_tree.jsonl` written by the script | `sessions.json` index written by the binary |
| Nesting | Hard-blocked in code | Blocked by `subagentControlScope: none` (leaf children) |
| Harness role | **Implements** spawning | **Only enables + steers + harvests** |
| Runner branch | `inject_subagent_tool(...)` | `configure_native_subagents(...)` |

The migration moved spawning **out of the harness and into the OpenClaw binary**,
so the benchmark measures real OpenClaw multi-agent behaviour (the way reference
goldens like `Larry_Bates` / `amanda-tran` were produced) instead of a
harness-simulated sub-agent.

---

## How they're selected

`src/agents/openclaw/runner.py`:

```python
if spec.multi_agent_enabled:
    _ma_cfg = spec.multi_agent_config or {}
    if _ma_cfg.get("native", True):       # native is the DEFAULT
        configure_native_subagents(spec.task_id, _ma_cfg)
    else:
        inject_subagent_tool(spec.task_id, _ma_cfg)   # legacy
```

- `multi_agent_enabled` is set by the task parser when a task opts in via
  `task.yaml: multi_agent_complex_turns: [...]`, a `multi_agent:` config block,
  or a `Multi-Agent` label in `prompts.txt` — **or** globally by
  `WCB_MULTI_AGENT_DEFAULT` (default `1`; set to `0` to disable).
- `_default_multi_agent_config()` returns `{"native": True, ...}`, so the native
  path is taken unless a task explicitly sets `native: false`.

---

## Legacy path — `spawn-subagent-connector` (harness-implemented)

**Enabled by:** `inject_subagent_tool()` in `src/utils/docker_utils.py`.

**What it installs** into `/usr/lib/node_modules/openclaw/skills/spawn-subagent-connector/`:
- `SKILL.md` — instructions + a "when to fan out" trigger checklist (the steering).
- `scripts/spawn_subagent.py` — the runtime (`src/utils/subagent_director.py`).
- `scripts/subagent_tools.py` — the child's tool implementations.

**How a spawn happens:**
1. The parent model decides to fan out (steered by the SKILL.md description).
2. It runs `Bash → python3 .../spawn_subagent.py` with a JSON spec
   (`role`, `instructions`, `allowed_tools`, `max_tool_calls`, …).
3. **`subagent_director.py` (harness code) runs the child** as a short, bounded
   LLM session against the same LiteLLM sidecar, using its own re-implemented
   tools (`Read/Write/Edit/Grep/Glob/Bash`).
4. It writes one NDJSON row to `spawn_tree.jsonl`, the full child transcript to
   `subagents/{spawn_id}.jsonl`, and a `{spawn_id}.delivery.json`, then prints
   the child's final text back to the parent.

**Properties:**
- The "sub-agent" is **not** an OpenClaw session — it's a Python-driven LLM call.
- Bounded by harness ceilings (`max_tool_calls ≤ 50`, `timeout ≤ 600s`).
- **No nested spawning** — `subagent_director.py` rejects `spawn_subagent` in
  `allowed_tools`.
- Because it's a skill, it bypassed the `coding` tool-profile filter entirely.

---

## Native path — `sessions_spawn` (binary-implemented)

**Enabled by:** `configure_native_subagents()` in `src/utils/docker_utils.py`.
The harness does **not** implement spawning here; it only makes it usable:

1. **`tools.alsoAllow`** — adds the session tools to the active `coding` tool
   profile so they're callable. (The `coding` profile — from
   `@mariozechner/pi-coding-agent` — otherwise filters out
   `sessions_spawn`/`sessions_list`/… , which is why native spawning silently
   did nothing before this fix.) Tools allowed:
   `sessions_spawn, subagents, agents_list, sessions_list, sessions_history, sessions_send`.
   (`sessions_yield` is **not** registered in this build.)
2. **AGENTS.md steering** — a fan-out directive is appended to the persona
   bootstrap (`/root/AGENTS.md`), which *does* surface in the system prompt.
   (OpenClaw does **not** surface SKILL.md descriptions in the system prompt, so
   a steering skill would never reach the model — the steering must live in the
   persona.)
3. **`agents.defaults.subagents.maxConcurrent`** — fan-out width cap.

**How a spawn happens:**
1. Parent calls **`agents_list`** → discovers the allowed agent (`main`).
2. Parent calls **`sessions_spawn`** once per workstream. This build's args:
   `label`, `task`, `runtime: "subagent"`, `mode: "run"`, `cwd`.
   It returns:
   ```json
   { "status": "accepted",
     "childSessionKey": "agent:main:subagent:<uuid>",
     "runId": "<uuid>", "mode": "run" }
   ```
3. **The OpenClaw binary** creates a **real session** for each child at
   `/root/.openclaw/agents/main/sessions/<uuid>.jsonl`, with full tools + the
   task's connector skills, running **asynchronously** in the still-alive
   gateway (`mode: "run"` = fire-and-return).
4. Children are tracked in **`sessions.json`**:
   `{ "<canonical key>": { sessionId, label, spawnedBy, subagentRole: "leaf",
     subagentControlScope: "none", spawnDepth: 1 } }`.
5. The parent collects results via `sessions_list` / `sessions_history`
   (there is no `sessions_yield` in this build).

**Nesting:** children are **leaves** (`subagentRole: leaf`,
`subagentControlScope: none`, `spawnDepth: 1`) — they cannot spawn further.
Only the parent (`agent:main:chat`, `spawnDepth: 0`) spawns. One delegation
level, no grandchildren (unless `subagentControlScope` were opened to
`"children"`, which the harness does not do).

---

## Tool sets

**Parent (agent)** — full catalog:
`read, write, edit, apply_patch, grep, find, ls, exec, process, web_search,
web_fetch, browser, canvas, nodes, cron, message, gateway, agents_list,
sessions_list, sessions_history, sessions_send, sessions_spawn, subagents,
session_status, image, image_generate` + the task's API connector skills.

**Sub-agent (leaf child)** — same coding tools + the task's connector skills,
but **without** the fan-out/collect tools (`sessions_spawn`, `agents_list`, …),
because it is a leaf with `subagentControlScope: none`.

---

## Harvest & output format (native)

Because native children are separate sessions, the harness adds capture +
assembly the script used to do inline:

1. **Wait** — `OpenClawAgent._wait_for_subagents()` holds the container open
   after the parent turn ends until the child sessions quiesce (or `max_wait`),
   so async children finish instead of being killed at teardown.
2. **Collect** — `collect_output_from_container()` copies
   `/root/.openclaw/agents/main/sessions/` into `run_N/task_output/sessions/`.
3. **Transform** — `attach_native_subagents()` (in
   `src/utils/trajectory/builder.py`) reads `sessions.json` + each child
   `<sessionId>.jsonl` and emits the **Larry_Bates layout**:
   - `output.json` gains `meta_info.agents = { root, spawned: [...] }`
   - `subagents/NN_<label>.json` — one **JSON** file per child (not `.jsonl`),
     with `meta_info = { task_name, task_description, task_completion_status,
     parent_session, session_key, platform, message_count }` + `messages`
   - `spawn_tree/parent_spawn_tree.txt`

The raw `.jsonl` exists only as the intermediate session store; the published
sub-agent trajectories are clean `.json`.

---

## Why the switch

- **Fidelity** — measures real OpenClaw `sessions_spawn` behaviour, not a
  harness-simulated LLM call.
- **Real sessions** — children are first-class OpenClaw sessions with the full
  tool surface and the binary's own lifecycle (`spawnMode`,
  `subagentControlScope`, `maxConcurrent`).
- **Reference parity** — output matches the native-spawn reference goldens
  (`Larry_Bates`, `amanda-tran`).

### Trade-off the migration introduced (and fixed)

The legacy skill bypassed the `coding` tool-profile filter; the native tools do
**not**. So switching silently disabled spawning until the harness:
(a) `alsoAllow`'d the session tools, (b) moved steering from a SKILL.md into
AGENTS.md, and (c) added the wait + collect + transform so async children are
captured. The parent currently spawns in async `mode: "run"` and may
fire-and-forget; a stronger wait-and-collect steering (poll
`sessions_list`/`sessions_history`, synthesize before ending) is the remaining
lever for a fully-collected parent run.
