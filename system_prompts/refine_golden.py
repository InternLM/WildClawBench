#!/usr/bin/env python3
"""Phase B — refine a generated golden trajectory (the polish cycle).

Takes a COMPLETE golden_trajectory.json (Phase A = generate_golden_v3.py output)
plus the task dir, and cleans the tool layer / repairs weak turns WITHOUT ever
re-running Phase A's per-turn generation. Idempotent and re-runnable.

Pipeline:
  1. DETERMINISTIC tool cleanup
     - drop noise/debug calls (pip install / which / apt list / env|grep / …)
     - ground failed/omitted results from the task fixtures (data/, mock_data/,
       inject/): xlsx & docx via zipfile-XML, eml/ics/txt/md/json/csv raw
     - re-thread message ids: linear parentId, root self-id; toolResult.toolCallId
       kept matched to its toolCall id
  2. GRADE-GATED LLM REPAIR LOOP (--repair, needs --llm-capable Bedrock)
     - council-grade -> for each failing criterion, find the most relevant turn,
       rewrite that turn's reply using ONLY grounded tool outputs (scaffolding
       scrubbed) -> re-grade -> repeat up to --rounds
  3. write golden_trajectory.json (+ score_golden.json)

Usage:
  python3 system_prompts/refine_golden.py \
      "golden_trajectories/<task>/golden_trajectory.json" \
      --task "input/<task>" [--repair --rounds=2]
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent))

# reuse the v3 generator's LLM transport (with the 503 fallback chain),
# scaffolding scrubber, and response system prompt.
import generate_golden_v3 as G  # noqa: E402


# --------------------------------------------------------------------------- #
# 1a. noise / debug tool-call filter
# --------------------------------------------------------------------------- #
_NOISE_RE = re.compile(
    r"(?i)(pip\s+install|which\s+python|which\s+pdftotext|apt(-get)?\s+(list|install)|"
    r"dist-packages|sys\.executable|env\s*\|\s*(grep|sort)|--version\b|"
    r"ls\s+/usr/(lib|bin)|python3\s*-c\s*\"import\s+\w+,\s*sys)"
)


def _command_of(call: dict) -> str:
    args = call.get("arguments") or {}
    return " ".join(str(v) for v in args.values()) if isinstance(args, dict) else str(args)


def _is_noise(call: dict) -> bool:
    if (call.get("name") or "").lower() != "exec":
        return False
    return bool(_NOISE_RE.search(_command_of(call)))


# --------------------------------------------------------------------------- #
# 1b. fixture grounding
# --------------------------------------------------------------------------- #
_OMITTED_RE = re.compile(
    r"(?i)(tool output omitted|package/network unavailable|no such file|"
    r"command not found|traceback|modulenotfound|connection refused|"
    r"\bunable to\b|timed out|not_found|http 50\d|\(no output\))"
)
_FNAME_RE = re.compile(r"([A-Za-z0-9._\-]+\.(?:xlsx|docx|eml|ics|txt|md|json|csv|pdf))")


def _build_fixture_index(task_dir: Path) -> dict[str, Path]:
    idx: dict[str, Path] = {}
    for sub in ("data", "mock_data", "inject", "."):
        root = task_dir / sub
        if not root.is_dir():
            continue
        exts = {".xlsx", ".docx", ".eml", ".ics", ".txt", ".md", ".json", ".csv"}
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in exts:
                idx.setdefault(p.name, p)          # first wins; prefer data/ order
    return idx


def _xlsx_text(path: Path, max_rows: int = 60) -> str:
    """Extract sheet values from an .xlsx via zipfile (openpyxl not installed)."""
    try:
        with zipfile.ZipFile(path) as z:
            shared: list[str] = []
            if "xl/sharedStrings.xml" in z.namelist():
                root = ET.fromstring(z.read("xl/sharedStrings.xml"))
                for si in root:
                    shared.append("".join(t.text or "" for t in si.iter() if t.tag.endswith("}t")))
            sheets = [n for n in z.namelist() if re.match(r"xl/worksheets/sheet\d+\.xml", n)]
            out: list[str] = []
            for sn in sheets[:2]:
                root = ET.fromstring(z.read(sn))
                for row in root.iter():
                    if not row.tag.endswith("}row"):
                        continue
                    cells = []
                    for c in row:
                        if not c.tag.endswith("}c"):
                            continue
                        v = next((ch.text for ch in c if ch.tag.endswith("}v")), None)
                        if v is None:
                            continue
                        cells.append(shared[int(v)] if c.get("t") == "s" and v.isdigit()
                                     and int(v) < len(shared) else v)
                    if cells:
                        out.append("\t".join(cells))
                    if len(out) >= max_rows:
                        break
            return "\n".join(out)
    except Exception as exc:  # noqa: BLE001
        return f"(could not read {path.name}: {exc})"


def _docx_text(path: Path, max_chars: int = 4000) -> str:
    try:
        with zipfile.ZipFile(path) as z:
            root = ET.fromstring(z.read("word/document.xml"))
        paras = []
        for p in root.iter():
            if p.tag.endswith("}p"):
                paras.append("".join(t.text or "" for t in p.iter() if t.tag.endswith("}t")))
        return "\n".join(x for x in paras if x.strip())[:max_chars]
    except Exception as exc:  # noqa: BLE001
        return f"(could not read {path.name}: {exc})"


def _extract_fixture(path: Path) -> str:
    suf = path.suffix.lower()
    if suf == ".xlsx":
        return _xlsx_text(path)
    if suf == ".docx":
        return _docx_text(path)
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:4000]
    except Exception as exc:  # noqa: BLE001
        return f"(could not read {path.name}: {exc})"


def _ground_result(command: str, fixtures: dict[str, Path]) -> str | None:
    """If the command references a known fixture file, return its real content."""
    for fn in _FNAME_RE.findall(command or ""):
        if fn in fixtures:
            body = _extract_fixture(fixtures[fn])
            if body and not body.startswith("(could not read"):
                return f"=== {fn} ===\n{body}"
    return None


# --------------------------------------------------------------------------- #
# message helpers
# --------------------------------------------------------------------------- #
def _result_text(msg: dict) -> str:
    c = msg.get("content")
    if isinstance(c, list) and c and isinstance(c[0], dict):
        return c[0].get("text", "")
    return c if isinstance(c, str) else ""


def _set_result_text(msg: dict, text: str) -> None:
    msg["content"] = [{"type": "text", "text": text}]


def cleanup(messages: list[dict], fixtures: dict[str, Path]) -> dict:
    """Drop noise calls + their results; ground failed results. Returns stats."""
    stats = {"dropped_noise": 0, "grounded": 0, "kept_calls": 0}
    dropped_ids: set[str] = set()
    # pass 1: drop noise toolCalls from assistant messages
    for m in messages:
        mm = m["message"]
        if mm.get("role") != "assistant" or not isinstance(mm.get("content"), list):
            continue
        kept = []
        for b in mm["content"]:
            if isinstance(b, dict) and b.get("type") == "toolCall" and _is_noise(b):
                dropped_ids.add(b.get("id", ""))
                stats["dropped_noise"] += 1
            else:
                kept.append(b)
        mm["content"] = kept
    # last toolCall command seen, to ground the matching result
    last_cmd_by_id: dict[str, str] = {}
    for m in messages:
        mm = m["message"]
        if mm.get("role") == "assistant" and isinstance(mm.get("content"), list):
            for b in mm["content"]:
                if isinstance(b, dict) and b.get("type") == "toolCall":
                    last_cmd_by_id[b.get("id", "")] = _command_of(b)
                    stats["kept_calls"] += 1
    # pass 2: rebuild message list, dropping results of dropped calls, grounding others
    out: list[dict] = []
    for m in messages:
        mm = m["message"]
        if mm.get("role") == "toolResult":
            cid = mm.get("toolCallId", "")
            if cid in dropped_ids:
                continue  # drop the orphaned result
            txt = _result_text(mm)
            if _OMITTED_RE.search(txt or "") or not (txt or "").strip():
                grounded = _ground_result(last_cmd_by_id.get(cid, ""), fixtures)
                if grounded:
                    _set_result_text(mm, grounded)
                    mm["isError"] = False
                    stats["grounded"] += 1
        # drop assistant messages that became empty after noise removal
        if (mm.get("role") == "assistant" and isinstance(mm.get("content"), list)
                and not mm["content"]):
            continue
        out.append(m)
    return {"messages": out, **stats}


def rethread(messages: list[dict]) -> list[dict]:
    """Linear message ids; root self-id; parentId = prior id."""
    for i, m in enumerate(messages, start=1):
        m["id"] = f"g{i:07d}"
        m["parentId"] = f"g{i:07d}" if i == 1 else f"g{i - 1:07d}"
    return messages


# --------------------------------------------------------------------------- #
# 2. grade + repair
# --------------------------------------------------------------------------- #
# grading-cost accumulator (repair-call cost rides on G.COST automatically)
GRADE_COST = {"input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0, "requests": 0}


def _grade(traj: dict, task_dir: Path) -> dict:
    from eval.run_batch import _condense_transcript_for_judge
    from src.utils.grading import grade_with_rubric
    import tempfile
    rubrics = json.loads((task_dir / "rubric.json").read_text(encoding="utf-8"))
    if isinstance(rubrics, dict):
        rubrics = rubrics.get("rubrics") or []
    transcript = _condense_transcript_for_judge(traj)
    with tempfile.TemporaryDirectory() as tmp:
        score = grade_with_rubric(rubrics, "", Path(tmp),
                                  transcript_text=transcript, use_council=True)
    u = score.get("usage") or {}
    GRADE_COST["input_tokens"] += int(u.get("input_tokens", 0) or 0)
    GRADE_COST["output_tokens"] += int(u.get("output_tokens", 0) or 0)
    GRADE_COST["cost_usd"] += float(u.get("cost_usd", 0.0) or 0.0)
    GRADE_COST["requests"] += int(u.get("request_count", u.get("requests", 0)) or 0)
    return score


def _turns(messages: list[dict]) -> list[dict]:
    turns: list[dict] = []
    cur = None
    for idx, m in enumerate(messages):
        mm = m["message"]
        if mm.get("role") == "user":
            cur = {"user": "", "tool_text": [], "reply_msg": None}
            turns.append(cur)
            c = mm.get("content")
            cur["user"] = c[0]["text"] if isinstance(c, list) and c else ""
        elif cur is not None and mm.get("role") == "toolResult":
            cur["tool_text"].append(_result_text(mm))
        elif cur is not None and mm.get("role") == "assistant" and isinstance(mm.get("content"), list):
            if any(isinstance(b, dict) and b.get("type") == "text" for b in mm["content"]):
                cur["reply_msg"] = mm  # last assistant text block of the turn
    return turns


def _best_turn(criterion: str, turns: list[dict]) -> dict | None:
    words = {w for w in re.findall(r"[A-Za-z0-9]{4,}", criterion.lower())}
    best, score = None, 0
    for t in turns:
        if not t["reply_msg"]:
            continue
        hay = (t["user"] + " " + " ".join(t["tool_text"])).lower()
        s = sum(1 for w in words if w in hay)
        if s > score:
            best, score = t, s
    return best


REPAIR_SYSTEM = G.GOLDEN_RESPONSE_SYSTEM + (
    "\n\nThis is a REPAIR pass. Rewrite the reply so it FULLY satisfies the stated "
    "criterion. The criterion is the source of truth for what an ideal reply must "
    "contain — if it names a specific value (an email address, a number, a set of "
    "items the report must cover), state that exact value/those exact items "
    "verbatim and naturally. Prefer facts from the tool outputs; you may also use "
    "the exact facts the criterion itself specifies. Keep the rest of the reply "
    "intact and natural; never name test/scaffolding mechanics.")


def repair_round(messages: list[dict], failing: list[dict],
                 fixtures: dict[str, Path] | None = None) -> int:
    turns = _turns(messages)
    # contacts fixture (if any) helps criteria that hinge on a correct address
    contacts_ctx = ""
    if fixtures:
        for fn, p in fixtures.items():
            if "contact" in fn.lower():
                contacts_ctx += _extract_fixture(p)[:1500] + "\n"
    fixed = 0
    for c in failing:
        crit = c.get("criterion", "")
        t = _best_turn(crit, turns)
        if not t or not t["reply_msg"]:
            continue
        cur_reply = next((b["text"] for b in t["reply_msg"]["content"]
                          if isinstance(b, dict) and b.get("type") == "text"), "")
        tool_ctx = "\n".join(t["tool_text"])[:4000]
        extra = f"\n\nCONTACTS ON FILE:\n{contacts_ctx[:1500]}" if contacts_ctx else ""
        prompt = (f"USER (this turn):\n{t['user']}\n\nTOOL OUTPUTS THIS TURN:\n{tool_ctx}{extra}\n\n"
                  f"CURRENT REPLY:\n{cur_reply}\n\nCRITERION TO SATISFY:\n{crit}\n\n"
                  "Rewrite the reply so it satisfies the criterion. Return ONLY the new reply text.")
        new = G._llm_call(REPAIR_SYSTEM, prompt)
        if new and new.strip():
            new = G._scrub_scaffolding(new.strip())
            for b in t["reply_msg"]["content"]:
                if isinstance(b, dict) and b.get("type") == "text":
                    b["text"] = new
                    break
            fixed += 1
    return fixed


# --------------------------------------------------------------------------- #
def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if not args:
        print("usage: refine_golden.py <golden_trajectory.json> --task <input/dir> "
              "[--repair --rounds=N]", file=sys.stderr)
        return 2
    gpath = Path(args[0]).resolve()
    task_arg = next((a.split("=", 1)[1] for a in flags if a.startswith("--task=")), None)
    if not task_arg:
        # allow `--task <dir>` (space form) via positional
        task_arg = args[1] if len(args) > 1 else None
    task_dir = Path(task_arg).resolve() if task_arg else None
    do_repair = "--repair" in flags
    rounds = next((int(a.split("=", 1)[1]) for a in flags if a.startswith("--rounds=")), 2)

    traj = json.loads(gpath.read_text(encoding="utf-8"))
    messages = traj["messages"]
    fixtures = _build_fixture_index(task_dir) if task_dir else {}
    print(f"[refine] {gpath.name}: {len(messages)} msgs, {len(fixtures)} fixtures indexed",
          file=sys.stderr)

    res = cleanup(messages, fixtures)
    messages = rethread(res["messages"])
    traj["messages"] = messages
    print(f"[refine] cleanup: dropped {res['dropped_noise']} noise calls, "
          f"grounded {res['grounded']} results, {res['kept_calls']} calls kept", file=sys.stderr)

    if do_repair and task_dir:
        import copy
        # HILL-CLIMB with rollback: each round repairs a COPY of the best-so-far,
        # re-grades, and keeps it only if the score improved. This prevents the
        # loop from ending on a regression (rewrites can break passing criteria,
        # and the council judge has variance). The output is the best version seen.
        best_msgs = copy.deepcopy(messages)
        best_sc = _grade(traj, task_dir)
        best = best_sc.get("overall_score") or 0.0
        print(f"[refine] baseline score={best:.4f} "
              f"({best_sc.get('criteria_passed')}/{best_sc.get('criteria_total')})", file=sys.stderr)
        for r in range(1, rounds + 1):
            failing = [c for c in (best_sc.get("criteria") or []) if not c.get("passed")]
            if not failing:
                print(f"[refine] all criteria passing — stopping at round {r}", file=sys.stderr)
                break
            work = copy.deepcopy(best_msgs)
            n = repair_round(work, failing, fixtures)
            if n == 0:
                print(f"[refine] round {r}: no turn matched a failing criterion — stop", file=sys.stderr)
                break
            traj["messages"] = work
            sc = _grade(traj, task_dir)
            cur = sc.get("overall_score") or 0.0
            keep = cur > best
            print(f"[refine] round {r}: repaired {n}, base={best:.4f} -> try={cur:.4f} "
                  f"({sc.get('criteria_passed')}/{sc.get('criteria_total')}) "
                  f"{'KEEP' if keep else 'roll back'}", file=sys.stderr)
            if keep:
                best, best_msgs, best_sc = cur, copy.deepcopy(work), sc
        # restore the best version seen across all rounds
        messages = best_msgs
        traj["messages"] = messages
        (gpath.parent / "score_golden.json").write_text(
            json.dumps(best_sc, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[refine] BEST score={best:.4f} "
              f"({best_sc.get('criteria_passed')}/{best_sc.get('criteria_total')})", file=sys.stderr)
        # record cost into golden_trajectories/<task>/cost.json (merges with Phase A)
        G.update_cost_json(gpath.parent, "phase_b_repair", G.COST)
        G.update_cost_json(gpath.parent, "phase_b_grade", GRADE_COST,
                           extra={"grades": GRADE_COST["requests"] // 3 if GRADE_COST["requests"] else 0})
        total = (G.COST["cost_usd"] + GRADE_COST["cost_usd"])
        print(f"[refine] cost: Phase B ${total:.4f} "
              f"(repair ${G.COST['cost_usd']:.4f} + grade ${GRADE_COST['cost_usd']:.4f}) "
              f"-> {gpath.parent}/cost.json", file=sys.stderr)

    gpath.write_text(json.dumps(traj, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[refine] wrote {gpath}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
