# WildClawBench — How the Harness Works (Plain-English Flow)

This README explains, in user-flow terms (not code), how a task runs end to end:
what files a task ships, how the **OpenClaw** agent runs against them, **where the
injection comes from and which file is used when**, and how the run is graded.

---

## 1. The one-paragraph picture

A **task** is a folder of input files describing a realistic multi-day scenario
for one persona (e.g. *Gloria Wiggins*, a grant writer). The harness **stages a
workspace**, **starts mock versions of real apps** (Gmail, Calendar, Sheets…),
**seeds the starting world**, then runs the **OpenClaw agent** through ~50 timed
user messages. Between certain turns it **injects changes** ("mutations") into
that world to test whether the agent notices. When the run ends, two graders
score it. The whole thing is recorded as `output.json`.

```
TASK INPUT  ──►  STAGE WORKSPACE + START MOCK APIS  ──►  SEED WORLD (stage0)
                                                              │
                          ┌───────────────────────────────────┘
                          ▼
                 RUN OPENCLAW over 50 turns
                 (inject mid-session changes between turns)
                          │
                          ▼
                 GRADE (tests + rubric)  ──►  output.json + score
```

---

## 2. What a task ships (the input bundle)

Every task lives under `input/<task name>/` and contains:

```
input/<task name>/
├── persona/             ← WHO the agent is (its identity + memory + tools)
│   ├── IDENTITY.md      · the persona's name, role, situation
│   ├── USER.md          · facts about the user it works for
│   ├── MEMORY.md        · long-term memory it starts with
│   ├── AGENTS.md        · operating rules / house style
│   ├── SOUL.md          · voice / values
│   ├── TOOLS.md         · which tools/apps it may use
│   └── HEARTBEAT.md     · the anchor schedule / recurring beats
│
├── data/                ← WORKSPACE FILES the agent starts with (docs, sheets, PDFs)
│                          (these are copied into the agent's /root/workspace)
│
├── mock_data/           ← THE APPS. One folder per fake service, each becomes a
│   ├── gmail-api/         live mock server with seeded data the agent can call.
│   ├── google-calendar-api/
│   ├── google-sheets-api/  … (16 services for Gloria)
│   └── …
│
├── inject/              ← THE CHANGES injected over time (see §5). NOT read by
│   ├── stage0/            the agent — read by the harness, applied to the world.
│   ├── stage1/
│   ├── stage2/
│   └── stage3/
│
├── prompts.txt          ← THE SCRIPT: the 50 timed user "wake-up" messages
├── task.yaml            ← the agent's system prompt + task_type
├── task.py              ← the deterministic CHECKERS (pass/fail tests)
├── test_outputs.py      ← the pytest form of those checkers
├── test_weights.json    ← which checkers count, and how much
├── rubric.json          ← the LLM-judged quality criteria
└── golden_steer_flow.md ← the "ideal solve path" (used only for golden building)
```

**Rule of thumb for who reads what:**
- The **agent** reads `persona/` (its context) and `data/` (its workspace files), and calls `mock_data/` services over the network.
- The **harness** reads `inject/`, `prompts.txt`, `task.yaml`, `task.py`, `rubric.json`. The agent never sees these directly.

---

## 3. What the OpenClaw agent can actually access

When the agent is running, its world is just two things:

```
   ┌─────────────────────────────────────────────┐
   │  OpenClaw agent (the model being tested)     │
   │                                              │
   │  (1) A filesystem:  /root/workspace/         │
   │      ├── persona files (IDENTITY.md, …)      │  ← from persona/
   │      └── documents (budgets, PDFs, sheets)   │  ← from data/
   │                                              │
   │  (2) Network access to mock app URLs:        │
   │      GMAIL_API_URL = http://…:8017           │  ← from mock_data/gmail-api
   │      CALENDAR_API_URL = http://…:8016        │  ← from mock_data/google-calendar-api
   │      … (one URL per service, as env vars)    │
   └─────────────────────────────────────────────┘
```

It works by running shell commands (`ls`, `cat`, read a file, `curl` an API URL),
writing files, setting reminders, etc. It does **not** know it's a test, does not
see the rubric, the checkers, or the injection folder. It only experiences the
**effects**: an email appears in its inbox, a calendar value is different than it
remembered, a sheet got updated.

---

## 4. The run, step by step (what happens when a task executes)

```
┌── 1. STAGE THE WORKSPACE ────────────────────────────────────────────────┐
│   Copy persona/ + data/ into the agent's /root/workspace.                 │
│   The agent now has its identity files and its starting documents.        │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
┌── 2. START THE MOCK APPS ────────────────────────────────────────────────┐
│   For each folder in mock_data/, start a mock server seeded with that      │
│   app's data, and hand the agent its URL (as an env var).                  │
│   Now "Gmail", "Calendar", "Sheets" etc. exist and respond.                │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
┌── 3. SEED THE WORLD  (inject/stage0) ────────────────────────────────────┐
│   The harness applies stage0 — the BASELINE. It loads the pre-existing     │
│   emails, calendar events, contacts, and sheet values so the world looks   │
│   "lived in" at turn 0. stage0 is NOT a trick; it's the starting state.    │
│   (Snapshot "before_injection" is taken here.)                             │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
┌── 4. RUN THE AGENT OVER 50 TURNS ────────────────────────────────────────┐
│   for each turn k = 0 … 49:                                                │
│      • (between turns) the harness fires the matching inject stage —        │
│        applying that stage's mutations to the apps (see §5).                │
│      • deliver prompts.txt turn k (the user's wake-up message).             │
│      • the agent reads files / calls apps / writes deliverables / replies.  │
│   Context is kept across turns (same session), so memory carries forward.   │
│   (Snapshot "after_injection" is taken at the end.)                        │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
┌── 5. GRADE ──────────────────────────────────────────────────────────────┐
│   (a) Deterministic CHECKERS (task.py / test_outputs.py) — exact pass/fail │
│       on the final state (was the file written? the event created?).       │
│   (b) RUBRIC (rubric.json) — an LLM judge council scores quality / handling.│
└───────────────────────────────────────────────────────────────────────────┘
                                   │
┌── 6. RECORD ─────────────────────────────────────────────────────────────┐
│   Write output.json (the full trajectory), agent_state.json (final world), │
│   score.json, usage, and inject_timeline.jsonl (what got injected when).    │
└───────────────────────────────────────────────────────────────────────────┘
```

**Where the user messages come from:** `prompts.txt` (mirrored from
`task.py`'s `TURNS[*].wake_up_message`). Turn *k*'s text is delivered to the
agent at turn *k*.

---

## 5. The injection system (the heart of the test)

### What "injection" means
The world doesn't stand still. Overnight, prices change, a calendar slot moves, a
new email arrives, a document gets re-issued. The harness simulates this by
**injecting changes between turns**. The point is to test whether the agent
**notices and adapts** — especially **silent** changes it is never told about.

### The folder structure
```
inject/
├── stage0/                ← SEED (applied before turn 0): the baseline world
│   ├── mutations.json     · what to load (emails, calendar, contacts, sheets)
│   └── verify.sh          · sanity check that the seed landed
│
├── stage1/                ← fires between Day 1 and Day 2
│   ├── mutations.json     · the changes (e.g. "page limit 15 → 12", "9:00 → 10:00")
│   ├── emails/  sheets/…  · the new/changed content used by those changes
│   └── verify.sh
│
├── stage2/                ← fires between Day 2 and Day 3
└── stage3/                ← fires between Day 3 and Day 4
```

### What each stage's `mutations.json` says (plain English)
Each entry describes **one change**: which app, what changes, **when it fires**,
and whether it's **silent** (agent not told) or **loud** (visible event). Example:

> *SM2 — google-calendar — move the Henderson visit from 9:00 to 10:00, silently,
> at the Day-1→Day-2 boundary. The agent should notice when it next reads the
> calendar.*

### Three kinds of injection
| Kind | What it does | Agent's experience |
|---|---|---|
| **Seed** (stage0) | Loads the starting world | The world simply exists |
| **Loud** | A visible new event/email | A new item appears in the inbox |
| **Silent** | A hidden change to existing data | A value is quietly different than before |

### Which file is "taken" by whom — the key point
- **OpenClaw (the agent) never reads the `inject/` folder.** It only ever sees
  the **result**: the mock app now returns the new value, or a new email is in
  the inbox.
- **The harness** reads `inject/stageN/mutations.json`, figures out *when* the
  stage should fire (from its turn boundary), and **applies the change to the
  mock apps** (and drops any new files into the workspace inbox). Then the agent,
  on its next read of that app, encounters the new reality.

### When each stage fires
```
        stage0           stage1            stage2            stage3
         seed       ┌── between ──┐   ┌── between ──┐   ┌── between ──┐
   ──────●──────────┤ Day1 → Day2 ├───┤ Day2 → Day3 ├───┤ Day3 → Day4 ├──►
        before      └─────────────┘   └─────────────┘   └─────────────┘
         T0          (e.g. T15/16)     (e.g. T29/30)     (e.g. T42/43)
```
A stage fires at the **turn boundary** named in its `applies_between_turns`. If
that field is missing/empty, **the stage never fires** — the most common way an
injection silently does nothing.

### Important design facts
- Injection is **independent of the agent** — it fires on a fixed turn schedule,
  not in response to what the agent did. The agent's job is to *catch* it.
- A **silent** mutation must be **invisible** — it should change the *original*
  data in place, with no tell-tale filename. If a "mutated" file is dropped into
  the workspace with a name like `..._Mutated.xlsx`, the agent spots the label
  instead of detecting the change, and the test is defeated.

---

## 6. Grading (how a run is scored)

Two independent channels:

```
   agent's run ─┬─► DETERMINISTIC CHECKERS (task.py / test_outputs.py)
                │      exact pass/fail on final state + required phrases
                │      → "did it create the event / write the file / use $X?"
                │
                └─► RUBRIC JUDGE (rubric.json)
                       a council of LLM judges scores quality & handling
                       → "did it catch the silent change / decline the bad action?"
```

- **Checkers** = objective, machine-checkable (state changes, exact values).
- **Rubric** = judgment (did it behave like an ideal assistant?), scored by 3 judges.

The injected mutations connect to grading via the checkers' `detection_turns` /
`checker_ids`: each mutation says *which checker* verifies the agent handled it.

---

## 7. The golden-trajectory pipeline (separate tooling)

A **golden trajectory** is the *ideal* version of a run — what the best possible
agent would have produced. It's built by a separate two-phase pipeline (not part
of a normal eval run):

```
scripts/make_golden.sh "<task>" <run_number>
   │
   ├─ Phase A  generate_golden_v3.py   author ideal replies + reuse real tool calls
   └─ Phase B  refine_golden.py        clean tools, ground results, repair to max score
   → golden_trajectories/<task>/golden_trajectory.json + score + cost
```
It reuses a real run (`run_number`) as the source of authentic tool calls, and
writes everything (including `cost.json`) into the task's golden folder.

---

## 8. Where outputs land

```
output/openclaw/<task name>/trajectories/claude/run_<N>/
├── output.json           ← the full trajectory (the deliverable)
├── chat.jsonl            ← raw turn-by-turn conversation log
├── agent_state.json      ← final world state (used by checkers)
├── inject_timeline.jsonl ← WHAT was injected and WHEN (your injection receipt)
├── snapshot/
│   ├── workspace_before/mock_data   ← world state right after seed
│   └── workspace_after/mock_data    ← world state at end of run
├── mock_health.jsonl / gateway.log  ← infrastructure logs
└── score.json            ← grading result
```

**Two files to check whether injection actually happened:**
1. `inject_timeline.jsonl` — should show `stage1/2/3` events with non-zero counts.
2. `diff -rq snapshot/workspace_before/mock_data snapshot/workspace_after/mock_data`
   — should show **data files changed** (not just `_manifest.json`).
If the timeline only has `stage0` and the snapshot diff is empty, **no mutation
fired** — the run tested nothing mid-session.

---

## 9. The mental model in one line

> **persona/** = who the agent is · **data/** = what's on its desk ·
> **mock_data/** = the apps it can use · **inject/** = how the world changes on it
> over time · **prompts.txt** = what the user asks each turn · **rubric/checkers**
> = how we grade it. The agent only ever touches the first three; the harness
> drives the rest around it.
