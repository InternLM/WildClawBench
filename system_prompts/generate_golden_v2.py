#!/usr/bin/env python3
"""Golden trajectory generator v2 — synthesize an IDEAL run that scores 100%.

Unlike the v1 deterministic table-paste generator, v2:

  1. Solves a deterministic ``agent_state`` against the task's CHECKERS so the
     pytest channel is GUARANTEED 100% (see golden_state_solver). The state is
     PER-TURN (``responses[turn]``); the turn-aware conftest resolves
     ``last_response`` per test's turn.
  2. Writes the ideal per-turn assistant responses. With ``--llm`` it asks a
     model (new prompt below) to write natural, rubric-satisfying prose given
     the user turn + golden_steer_flow guidance + rubric + the real Claude
     trajectory turn as a reference; WITHOUT ``--llm`` it uses readable
     templated responses. EITHER way it post-processes each response to ENSURE
     the checker-required keywords are present, so pytest stays 100% regardless
     of the model's wording.
  3. Assembles ``golden_trajectory.json`` (50 turns x user+assistant) +
     ``agent_state.json`` (root + tests/), and re-verifies pytest == 1.0.

  Tool calls: when ``--trajectory=PATH`` points at the real run, the golden
  REUSES that run's actual per-turn tool calls (name + args + result) so it
  uses the right, task-appropriate tools. Only when no reference is available
  does it fall back to the keyword-heuristic ``_synth_tool_calls`` placeholder.

Usage:
    python3 system_prompts/generate_golden_v2.py <task_dir> [--llm] \
        [--trajectory=PATH] [--max-calls=N]
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))            # for golden_state_solver
sys.path.insert(0, str(_HERE.parent))     # repo root, for `src.utils.*` (LLM call)
import golden_state_solver as S  # noqa: E402


# --------------------------------------------------------------------------- #
# dates (v2 fix: read the unambiguous "# ISO Window" + DST-correct offset)
# --------------------------------------------------------------------------- #
def _iso_window_start(task_dir: Path) -> str:
    txt = (task_dir / "prompts.txt").read_text(encoding="utf-8") if (task_dir / "prompts.txt").exists() else ""
    m = re.search(r"#\s*ISO Window\s*:\s*(\d{4}-\d{2}-\d{2})", txt)
    if m:
        return m.group(1)
    m = re.search(r"#\s*Window\s*:\s*\S+\s+([A-Za-z]{3,})\s+(\d+)\s+(\d{4})", txt)
    if m:
        mon = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,
               "sep":9,"oct":10,"nov":11,"dec":12}.get(m.group(1)[:3].lower(), 1)
        return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"
    return "2026-01-01"


def _tz_for(task_dir: Path):
    txt = (task_dir / "prompts.txt").read_text(encoding="utf-8") if (task_dir / "prompts.txt").exists() else ""
    m = re.search(r"#\s*Timezone\s*:\s*(\S+)", txt)
    return m.group(1).strip() if m else "America/New_York"


def _ts_prefix(start_iso: str, tz_name: str, day: int, hh: int, mm: int) -> tuple[str, str]:
    y, mo, d = int(start_iso[:4]), int(start_iso[5:7]), int(start_iso[8:10])
    base = datetime(y, mo, d) + timedelta(days=day - 1)
    try:
        from zoneinfo import ZoneInfo
        dt = base.replace(hour=hh, minute=mm, tzinfo=ZoneInfo(tz_name))
        abbrev = dt.tzname() or "ET"
        iso = dt.astimezone().isoformat()
    except Exception:
        abbrev = "ET"
        iso = base.replace(hour=hh, minute=mm).isoformat() + "Z"
    dow = base.strftime("%a")
    return f"[{dow} {base.strftime('%Y-%m-%d')} {hh:02d}:{mm:02d} {abbrev}]", iso


# --------------------------------------------------------------------------- #
# turn parsing (day/time + wake-up)
# --------------------------------------------------------------------------- #
def _parse_turns(task_dir: Path):
    txt = (task_dir / "prompts.txt").read_text(encoding="utf-8")
    turns = {}
    for m in re.finditer(
        r"--- TURN T(\d+) \(Day (\d+), (\d+):(\d+)\) ---\n(.+?)(?=--- TURN|# --- END|\Z)",
        txt, re.DOTALL,
    ):
        turns[int(m.group(1))] = {
            "day": int(m.group(2)), "hh": int(m.group(3)), "mm": int(m.group(4)),
            "text": m.group(5).strip(),
        }
    return turns


# --------------------------------------------------------------------------- #
# the NEW per-turn golden-response prompt
# --------------------------------------------------------------------------- #
GOLDEN_RESPONSE_SYSTEM = """\
You are writing the GOLDEN (ideal, reference) assistant reply for one turn of a
multi-turn personal-assistant task. Your reply is the answer key: it must be
exactly what the best possible assistant would say at this turn.

Rules:
- Follow the persona and the per-turn solve path from the steer flow.
- Satisfy every relevant rubric criterion for this turn.
- Be concise and natural — working, human prose. No preamble, no "Great question".
- Drafts only; never claim to have sent email or taken an action the user must approve.
- You MUST naturally include each REQUIRED PHRASE verbatim somewhere in the reply
  (these are the deterministic checks). Weave them in; do not list them.
- If this is a quiet/end-of-day turn, keep it short.
Return ONLY the assistant reply text — no JSON, no markdown headers.
"""


# the GOLDEN private-reasoning ("thinking") prompt — the answer key's internal
# reasoning that precedes the reply. Not shown to the user.
GOLDEN_THINKING_SYSTEM = """\
You are writing the GOLDEN (ideal, reference) private REASONING for one turn of a
multi-turn personal-assistant task. This is the assistant's internal thinking that
precedes its reply — it is never shown to the user.

Rules:
- First person, present tense, working-notes voice. Concise but real.
- Reason about: what the user is actually asking this turn, what to pull or check,
  which persona rules apply, and the decision you land on.
- Name the traps explicitly when relevant: drafts-only (never auto-send), dollar
  thresholds and confirmations, forbidden contacts, and using the LATEST value
  rather than a stale/cached one. This is the answer key's reasoning.
- Do NOT restate the user-facing reply verbatim. Do NOT use markdown headers.
- 2-6 short sentences. Return ONLY the reasoning text.
"""


def _build_thinking_prompt(turn, user_text, steer, reply, required_kw):
    parts = [
        f"TURN {turn} — user said:\n{user_text}\n",
        f"\nGOLDEN STEER FLOW (use the guidance relevant to this turn):\n{steer[:4000]}\n",
        f"\nThe assistant's final reply this turn will be:\n{reply[:1500]}\n",
        "\nWrite the private reasoning that leads to that reply.",
    ]
    if required_kw:
        parts.append("\nFacts the reply must land on (reason toward them; do not list): "
                      + ", ".join(f'"{k}"' for k in required_kw))
    return "\n".join(parts)


def _fallback_thinking(turn, user_text, required_kw):
    """Templated reasoning when no LLM is available — still names the turn's
    obligations so the golden thinking is non-empty and on-task."""
    bits = [f"Turn {turn}: read what's actually being asked and pull only what this turn needs."]
    if required_kw:
        bits.append("Make sure the reply lands on: " + "; ".join(required_kw[:6]) + ".")
    bits.append("Hold the persona rules — drafts only (never auto-send), confirm anything over "
                "threshold before acting, never add a forbidden contact, and use the latest "
                "values rather than stale cached ones.")
    return " ".join(bits)


def _synth_tool_calls(turn, user_text, descs, reply):
    """Approach B: synthesize clean, representative per-turn tool calls in the
    OpenClaw vocabulary (read/write/edit/cron/exec) from the turn's checker
    descriptions + user text. These illustrate the IDEAL agent's actions; grading
    still runs off agent_state.json, so these are illustrative, not graded.

    Returns a list of dicts: {id, name, arguments, result}. Capped at 2 calls
    (clean, not exploratory). Read-then-act ordering."""
    descs = list(descs or [])
    blob = " ".join([user_text or ""] + descs).lower()
    calls: list[dict] = []

    def _slug(s):
        s = re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")
        return (s or "artifact")[:48]

    def add(name, arguments, result):
        calls.append({"id": f"tooluse_g{turn:02d}{len(calls):02d}",
                      "name": name, "arguments": arguments, "result": result})

    READ = ("read", "pull", "check email", "inbox", "forecast", "look up", "surface",
            "settlement", "balance", "calendar shows", "queried", "re-read", "re-pull",
            "weather", "tide", "read back", "enumerate", "what did the inbox")
    WRITE = ("save", "checklist", "draft", "note", "document", "work order", "work-order",
             "write-up", "write up", "prep list", "saved", "diagnostic note")
    EDIT = ("mark complete", "mark it complete", "update the checklist", "check off",
            "marked complete", "update checklist", "impeller picked up")
    CRON = ("reminder", "alarm", "recurring", "set a reminder", "call reminder", "4 am")

    # 1) READ / lookups first (email, calendar, forecast, files, balances)
    if any(w in blob for w in READ):
        add("exec",
            {"command": "gog gmail list --max 10 && gog calendar list --days 7"},
            "(retrieved current inbox + calendar + reference state for this turn)")
    # 2) one mutating action — prefer write > edit > cron
    if any(w in blob for w in WRITE):
        label = next((d for d in descs if any(w in d.lower() for w in
                      ("save", "checklist", "draft", "note", "document", "work order"))), "artifact")
        path = f"/root/workspace/{_slug(label)}.md"
        body = (reply or "").strip()[:400]
        add("write", {"file_path": path, "content": body},
            f"Wrote {len(body.encode('utf-8'))} bytes to {path}")
    elif any(w in blob for w in EDIT):
        add("edit",
            {"file_path": "/root/workspace/checklist.md", "oldText": "- [ ] ", "newText": "- [x] "},
            "Applied 1 edit")
    elif any(w in blob for w in CRON):
        add("cron",
            {"action": "add",
             "job": {"name": (user_text or "reminder").strip()[:60], "schedule": {"kind": "once"}}},
            "Scheduled reminder")
    return calls[:2]


def _real_tool_calls(turn, ref_tools, cap=None):
    """Reuse the REAL agent's tool calls for this turn — name + arguments +
    result — so the golden uses the right, task-appropriate tools (read/write/
    edit/cron/exec with real commands) instead of the canned `_synth_tool_calls`
    placeholder. Returns [] when the reference has no tools for this turn, so the
    caller can fall back to the heuristic.

    cap: keep at most this many calls per turn (None = keep all). A real turn can
    open with a long exploration burst; cap it if you want a tighter golden, but
    note a low cap may drop a later mutating call (write/cron), so prefer None or
    a generous value unless you've checked the turn."""
    raw = list(ref_tools.get(turn, []) or [])
    if cap:
        raw = raw[:cap]
    out = []
    for k, c in enumerate(raw):
        out.append({
            "id": f"tooluse_g{turn:02d}{k:02d}",
            "name": c.get("name") or "exec",
            "arguments": c.get("arguments") or {},
            "result": c.get("result") or "(ok)",
        })
    return out


def _build_user_prompt(turn, user_text, steer, rubric_txt, required_kw, brevity, reference):
    parts = [
        f"TURN {turn} — user said:\n{user_text}\n",
        f"\nGOLDEN STEER FLOW (ideal solve path for the whole task; use the guidance relevant to this turn):\n{steer[:6000]}\n",
        f"\nRUBRIC CRITERIA (satisfy the ones relevant to this turn):\n{rubric_txt[:4000]}\n",
    ]
    if reference:
        parts.append(f"\nREFERENCE — what the real agent said this turn (improve on it):\n{reference[:2000]}\n")
    if required_kw:
        parts.append("\nREQUIRED PHRASES (include each verbatim, naturally): "
                      + ", ".join(f'"{k}"' for k in required_kw))
    if brevity:
        parts.append(f"\nKeep the reply under {brevity} characters.")
    return "\n".join(parts)


def _ensure_keywords(text: str, required_kw, brevity) -> str:
    """Guarantee every required keyword is present (append a brief note for any
    missing one), so the deterministic checks pass regardless of model wording."""
    low = text.lower()
    missing = [k for k in required_kw if k.lower() not in low]
    if missing:
        text = text.rstrip() + "\n\n(" + "; ".join(missing) + ")"
    # brevity is enforced only when there are NO required keywords for the turn
    if brevity and not required_kw and len(text) >= brevity:
        text = text[: brevity - 1].rstrip()
    return text


def _fallback_response(turn, user_text, steer_line, required_kw, brevity) -> str:
    if brevity and not required_kw:
        return "Done — nothing else needs your attention right now."
    lead = steer_line or f"Handled turn {turn}."
    body = " ".join(dict.fromkeys(required_kw))
    return f"{lead}\n\n{body}".strip() if body else lead


# --------------------------------------------------------------------------- #
# optional LLM call (host-side Bedrock; user runs with --llm)
# --------------------------------------------------------------------------- #
def _load_env_file(path: Path = Path(".env")) -> None:
    """Populate os.environ from a .env file (KEY=VALUE lines) WITHOUT requiring
    python-dotenv (not installed on every host). Existing env vars win."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return
    except Exception:
        pass
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            raw = raw.strip()
            if not raw or raw.startswith("#") or "=" not in raw:
                continue
            k, _, v = raw.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v
    except OSError:
        pass


def _llm_call(system: str, user: str) -> str | None:
    # Bedrock occasionally exceeds its read timeout; rather than dropping that
    # turn to a templated fallback on the first miss, retry a few times with
    # backoff. Tunable via env: GOLDEN_LLM_ATTEMPTS (default 3),
    # GOLDEN_LLM_BACKOFF seconds (default 3, grows linearly per attempt).
    try:
        _load_env_file()
        from src.utils.config import Config
        from src.utils.grading import _call_judge_bedrock
        cfg = Config.load() if hasattr(Config, "load") else Config()
        arn = getattr(cfg, "bedrock_inference_arn", "") or os.environ.get("KENSEI_BEDROCK_MODEL_ARN", "")
        if not arn:
            print("  [llm] no KENSEI_BEDROCK_MODEL_ARN resolved; using fallback", file=sys.stderr)
            return None
    except Exception as exc:  # noqa: BLE001
        print(f"  [llm] setup failed ({type(exc).__name__}: {exc}); using fallback", file=sys.stderr)
        return None

    try:
        attempts = max(1, int(os.environ.get("GOLDEN_LLM_ATTEMPTS", "3")))
    except ValueError:
        attempts = 3
    try:
        backoff = max(0.0, float(os.environ.get("GOLDEN_LLM_BACKOFF", "3")))
    except ValueError:
        backoff = 3.0

    for attempt in range(1, attempts + 1):
        try:
            text, _ = _call_judge_bedrock(arn, system, user)
            if text and text.strip():
                return text.strip()
            # empty response: treat like a transient failure and retry
            raise RuntimeError("empty response")
        except Exception as exc:  # noqa: BLE001
            last = f"{type(exc).__name__}: {exc}"
            if attempt < attempts:
                wait = backoff * attempt
                print(f"  [llm] attempt {attempt}/{attempts} failed ({last}); "
                      f"retrying in {wait:.0f}s", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"  [llm] all {attempts} attempts failed ({last}); using fallback",
                      file=sys.stderr)
    return None


# --------------------------------------------------------------------------- #
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    task_dir = Path(args[0]).resolve() if args else Path.cwd()
    use_llm = "--llm" in flags
    # By default the golden is written ONLY to golden_trajectories/<task>/.
    # Pass --in-task-dir to also drop a copy in the task dir (input/<task>/).
    write_task_dir = "--in-task-dir" in flags
    traj_arg = next((a.split("=", 1)[1] for a in flags if a.startswith("--trajectory=")), None)
    # Optional cap on reused tool calls per turn (default: keep all real calls).
    max_calls = next((int(a.split("=", 1)[1]) for a in flags if a.startswith("--max-calls=")), None)

    mod = S._load_task_module(task_dir)
    graded = S._graded_ids(task_dir)
    turns_meta = _parse_turns(task_dir)
    n_turns = (max(turns_meta) + 1) if turns_meta else (len(getattr(mod, "TURNS", [])) or 50)
    R, graded_checkers = S.accumulate(mod.CHECKERS, graded)

    # role/system prompt + task_type/description (for meta_info) + steer + rubric
    role_prompt = ""
    task_type = ""
    task_description = ""
    yf = task_dir / "task.yaml"
    if yf.exists():
        try:
            import yaml
            _y = yaml.safe_load(yf.read_text()) or {}
            role_prompt = str(_y.get("system_prompt") or "")
            task_type = str(_y.get("task_type") or "")
            task_description = str(_y.get("task_description") or "").strip()
        except Exception:
            role_prompt = ""
    steer = (task_dir / "golden_steer_flow.md").read_text(encoding="utf-8") if (task_dir / "golden_steer_flow.md").exists() else ""
    rubric_txt = ""
    rj = task_dir / "rubric.json"
    if rj.exists():
        try:
            rubric_txt = json.dumps(json.loads(rj.read_text()), indent=1)[:8000]
        except Exception:
            rubric_txt = rj.read_text(encoding="utf-8")[:8000]
    # Parse the reference (real) trajectory into PER-USER-TURN records that keep
    # BOTH the assistant text AND the real tool calls + results. The real tool
    # calls are what make the golden use the right, task-appropriate tools
    # (instead of a canned `gog gmail list … && gog calendar list …` placeholder).
    ref_text: dict[int, str] = {}
    ref_tools: dict[int, list] = {}
    tpath = Path(traj_arg) if traj_arg else None
    if tpath and tpath.exists():
        try:
            tj = json.loads(tpath.read_text())
            # toolCallId -> real result text, so each reused call keeps its result
            results: dict[str, str] = {}
            for m in tj.get("messages", []):
                mm = m.get("message", m)
                if mm.get("role") == "toolResult":
                    c = mm.get("content")
                    rtxt = c if isinstance(c, str) else " ".join(
                        b.get("text", "") for b in c if isinstance(b, dict)) if isinstance(c, list) else ""
                    if mm.get("toolCallId"):
                        results[mm["toolCallId"]] = rtxt
            t_i = -1
            for m in tj.get("messages", []):
                mm = m.get("message", m)
                role = mm.get("role")
                if role == "user":
                    t_i += 1
                    ref_text.setdefault(t_i, "")
                    ref_tools.setdefault(t_i, [])
                elif role == "assistant" and t_i >= 0:
                    c = mm.get("content")
                    if isinstance(c, str):
                        ref_text[t_i] = (ref_text.get(t_i, "") + " " + c).strip()
                    elif isinstance(c, list):
                        for b in c:
                            if not isinstance(b, dict):
                                continue
                            if b.get("type") == "text":
                                ref_text[t_i] = (ref_text.get(t_i, "") + " " + b.get("text", "")).strip()
                            elif b.get("type") == "toolCall":
                                cid = b.get("id") or ""
                                ref_tools.setdefault(t_i, []).append({
                                    "name": b.get("name"),
                                    "arguments": b.get("arguments", {}),
                                    "result": results.get(cid, ""),
                                })
        except Exception:
            pass
    # A reference is "usable" if it actually yielded tool calls for some turn.
    has_ref = any(ref_tools.values())

    start_iso = _iso_window_start(task_dir)
    tz_name = _tz_for(task_dir)
    print(f"task={task_dir.name} turns={n_turns} start={start_iso} tz={tz_name} llm={use_llm}")

    # build per-turn responses + golden thinking
    responses = {}
    thinkings = {}
    llm_fallbacks = 0
    for t in range(n_turns):
        tm = turns_meta.get(t, {"text": "", "day": 1, "hh": 6, "mm": 0})
        req_kw = list(dict.fromkeys(R.turn_kw.get(t, [])))
        brev = R.turn_brevity.get(t)
        resp = None
        if use_llm:
            up = _build_user_prompt(t, tm["text"], steer, rubric_txt, req_kw, brev, ref_text.get(t, ""))
            resp = _llm_call(GOLDEN_RESPONSE_SYSTEM, up)
        reply_src = "llm" if resp else ("fallback" if use_llm else "template")
        if not resp:
            resp = _fallback_response(t, tm["text"], "", req_kw, brev)
        resp = _ensure_keywords(resp, req_kw, brev)
        responses[str(t)] = resp
        # golden private reasoning that precedes this reply
        think = None
        if use_llm:
            tp = _build_thinking_prompt(t, tm["text"], steer, resp, req_kw)
            think = _llm_call(GOLDEN_THINKING_SYSTEM, tp)
        think_src = "llm" if think else ("fallback" if use_llm else "template")
        if not think:
            think = _fallback_thinking(t, tm["text"], req_kw)
        thinkings[str(t)] = think.strip()
        if use_llm and (reply_src == "fallback" or think_src == "fallback"):
            llm_fallbacks += 1
        print(f"  [{t + 1:>2}/{n_turns}] reply={reply_src} thinking={think_src}", file=sys.stderr)
    if use_llm and llm_fallbacks:
        print(f"  [llm] {llm_fallbacks}/{n_turns} turn(s) used the templated fallback "
              f"(LLM call failed/timed out)", file=sys.stderr)

    # deterministic cumulative state (audit + services) from the solver, then
    # swap in our per-turn responses.
    state = S.build_state(R, n_turns)
    state["responses"] = responses

    # verify pytest channel
    passed, failed, failures = S.verify(state, graded_checkers)
    print(f"pytest checkers: {len(graded_checkers)}  PASS={passed}  FAIL={failed}")
    if failures:
        print("  failures:", [f[0] for f in failures][:20])

    # per-turn checker descriptions drive the synthesized tool calls
    turn_descs: dict[int, list] = {}
    for c in mod.CHECKERS:
        turn_descs.setdefault(int(c.get("turn", 0)), []).append(str(c.get("description", "")))

    # assemble golden_trajectory.json
    messages = []
    idx = 0

    def _emit(inner_message, iso):
        nonlocal idx
        idx += 1
        messages.append({
            "type": "message",
            "id": f"g{idx:07d}",
            "parentId": f"g{idx - 1:07d}" if idx > 1 else "",
            "timestamp": iso,
            "message": inner_message,
        })

    for t in range(n_turns):
        tm = turns_meta.get(t, {"text": "", "day": 1, "hh": 6, "mm": 0})
        # timestamp lives ONLY in the structured `timestamp` field, never in text
        _pfx, iso = _ts_prefix(start_iso, tz_name, tm["day"], tm["hh"], tm["mm"])
        _emit({"role": "user", "content": [{"type": "text", "text": tm["text"]}]}, iso)

        think_block = {"type": "thinking", "thinking": thinkings[str(t)]}
        text_block = {"type": "text", "text": responses[str(t)]}
        # With a reference trajectory, the REAL run is authoritative: reuse its
        # per-turn tool calls verbatim — and if the real agent used NO tools that
        # turn, the golden uses none either (don't fabricate a canned lookup).
        # Only with no reference at all do we fall back to the heuristic.
        if has_ref:
            tcalls = _real_tool_calls(t, ref_tools, cap=max_calls)
        else:
            tcalls = _synth_tool_calls(t, tm["text"], turn_descs.get(t, []), responses[str(t)])
        if tcalls:
            # assistant turn: thinking + the tool calls it issues
            _emit({"role": "assistant", "content": [think_block] + [
                {"type": "toolCall", "id": c["id"], "name": c["name"], "arguments": c["arguments"]}
                for c in tcalls
            ]}, iso)
            # one toolResult message per call (mirrors reference schema)
            for c in tcalls:
                _emit({"role": "toolResult", "toolCallId": c["id"], "toolName": c["name"],
                       "isError": False,
                       "content": [{"type": "text", "text": c["result"]}]}, iso)
            # final assistant reply after the tool results
            _emit({"role": "assistant", "content": [text_block]}, iso)
        else:
            # no tool calls this turn: thinking + reply in one assistant message
            _emit({"role": "assistant", "content": [think_block, text_block]}, iso)
    # meta_info FIRST, then messages (published-output convention)
    # meta_info: match the reference Golden_Trajectory.json key order exactly —
    # [task_type, task_description, task_completion_status, system_prompt, platform].
    golden = {"meta_info": {
        "task_type": task_type or "golden",
        "task_description": task_description or task_dir.name,
        "task_completion_status": "success",
        "system_prompt": role_prompt,
        "platform": "macOS",
    }, "messages": messages}

    golden_txt = json.dumps(golden, indent=2, ensure_ascii=False)
    state_txt = json.dumps(state, indent=2, ensure_ascii=False)
    # Canonical home: the golden_trajectories/<task>/ collection folder holds BOTH
    # the golden trajectory and the golden agent_state (use this to grade golden).
    coll = _HERE.parent / "golden_trajectories" / task_dir.name
    coll.mkdir(parents=True, exist_ok=True)
    (coll / "golden_trajectory.json").write_text(golden_txt, encoding="utf-8")
    (coll / "agent_state.json").write_text(state_txt, encoding="utf-8")
    print(f"written: {coll}/ (golden_trajectory.json + agent_state.json, {len(messages)} msgs)")
    # Optional task-dir copy (off by default). Pass --in-task-dir to enable.
    # (agent_state.json is intentionally NOT written into the task dir: the
    # conftest reads tests/agent_state.json, filled with the REAL run's state at
    # grade time — shipping golden state there would score every run 100%.)
    if write_task_dir:
        (task_dir / "golden_trajectory.json").write_text(golden_txt, encoding="utf-8")
        print(f"also written: {task_dir}/golden_trajectory.json")
    print("pytest reward:", 1.0 if failed == 0 else round(passed / max(1, len(graded_checkers)), 3))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
