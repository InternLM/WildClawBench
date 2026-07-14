#!/usr/bin/env python3
"""Rewrite Golden_Trajectory.json so its tool usage looks real (diverse
read/write/edit/cron/exec) instead of all-exec. Preserves every graded
deliverable's dates/labels/content. Regenerates the linear envelope chain."""
import json, copy

SRC = "Golden_Trajectory.json"
d = json.load(open(SRC))
msgs = d["messages"]

# ---------------------------------------------------------------- helpers
def block_types(m):
    c = m["message"].get("content")
    return [b.get("type") for b in c] if isinstance(c, list) else []

def first_toolcall(m):
    c = m["message"].get("content")
    if isinstance(c, list):
        for b in c:
            if isinstance(b, dict) and b.get("type") == "toolCall":
                return b
    return None

def mk_assistant(blocks):
    return {"type": "message", "message": {"role": "assistant", "content": blocks}}

def mk_toolresult(call_id, tool_name, text, is_error=False):
    return {"type": "message", "message": {
        "role": "toolResult", "toolCallId": call_id, "toolName": tool_name,
        "isError": is_error, "content": [{"type": "text", "text": text}]}}

def think(t):
    return {"type": "thinking", "thinking": t, "thinkingSignature": ""}

def textb(t):
    return {"type": "text", "text": t}

def toolcall(cid, name, args):
    return {"type": "toolCall", "id": cid, "name": name, "arguments": args}

# ---------------------------------------------------------------- cron data
# reminder CREATE calls (by tooluse id): exec gog-calendar-create -> cron add
CRON_CREATE = {
 "tooluse_wKy8WbT7pvaXROQ6W2L1Np": dict(  # R2 Call Adobe cancel/downgrade
   job="job_a17f93c0", name="Call Adobe: cancel or downgrade before renewal",
   sched={"kind":"at","at":"2026-09-01T15:00:00Z"},
   text=("Reminder: call Adobe today to cancel, downgrade, or keep your plan "
         "before the annual renewal hits Sept 3. An early-termination fee applies "
         "if you cancel before then — but act now to avoid the auto-renew. "
         "Decide: cancel, downgrade, or keep."),
   human="Tue Sep 1, 2026, 9:00 AM MT", think=
   ("She wants a reminder to make the cancel/downgrade decision call before the "
    "Sept 3 renewal. This is a 'remind me to act' nudge, not a meeting — the right "
    "tool is a cron wake event that pings her with the context, not a calendar block. "
    "I'll set it for Sept 1, 9 AM and carry the ETF detail into the reminder text.")),
 "tooluse_P2ocjaP7Ro9ecMnaR52JiK": dict(  # R1 Check Adobe charge
   job="job_b2c4d6e8", name="Check Adobe charge amount before billing cycle renews tomorrow",
   sched={"kind":"at","at":"2026-09-02T15:00:00Z"},
   text=("Reminder: check your Adobe charge amount before the billing cycle renews "
         "tomorrow. Confirm the correct amount is queued (and any credit from the "
         "May dispute landed) before auto-renew hits Sept 3."),
   human="Wed Sep 2, 2026, 9:00 AM MT", think=
   ("Going with option (a) — a single Sept 2 pre-renewal check, since the Oct 2 label "
    "wouldn't fit once the plan is resolved. This is a self-nudge to verify the charge, "
    "so a cron wake reminder fits better than a calendar entry. One reminder, Sept 2, 9 AM.")),
 "tooluse_Aht0S4Jr4XfbUnnjm8pCmI": dict(  # R3 Prep Dr Lena
   job="job_c3e5f7a9", name="Prep for Dr. Lena appointment tomorrow",
   sched={"kind":"at","at":"2026-09-21T02:00:00Z"},
   text=("Reminder: prep your symptom notes (period dates, skin, energy, anything new "
         "since the February visit) and grab your blood-work order to bring to "
         "tomorrow's PCOS check-in with Dr. Lena Marsh."),
   human="Sun Sep 20, 2026, 8:00 PM MT", think=
   ("She wants a night-before nudge to prep for the appointment. That's a reminder the "
    "assistant should fire at her, so a cron wake event on Sun Sep 20 evening is the "
    "right mechanism — I'll fold the prep checklist into the reminder text.")),
 "tooluse_wGLI38StTwTxyaLUmZoKtR": dict(  # R4 Email Javi
   job="job_d4f6a8b0", name="Email Javi: confirm absence from July 7 + July 9 shifts",
   sched={"kind":"at","at":"2026-06-29T15:00:00Z"},
   text=("Reminder: email Javi (javi@roadrunnerpress.org) to confirm you'll be out the "
         "Tue Jul 7 and Thu Jul 9 print-shop shifts for workshop prep before teaching "
         "Sat Jul 11. Gives the co-op ~10 days notice for coverage."),
   human="Mon Jun 29, 2026, 9:00 AM MT", think=
   ("This is a 'remind me to send the email' nudge — she still drafts/sends it herself, "
    "so a cron wake reminder ~10 days ahead is the right call (not a calendar block). "
    "I'll name the shifts and Javi's address in the reminder so it's actionable when it fires.")),
 "tooluse_4jJbjXWXZVBnZkdHklP4Cf": dict(  # R5 Finalize Coyote files
   job="job_e5a7b9c1", name="Finalize Coyote Ridge label files for delivery tomorrow",
   sched={"kind":"at","at":"2026-07-19T15:00:00Z"},
   text=("Reminder: finalize the Coyote Ridge summer label files today — delivery is "
         "tomorrow (Mon Jul 20). Export print-ready PDFs and confirm Diego's printer "
         "specs before the 1–3 PM delivery block."),
   human="Sun Jul 19, 2026, 9:00 AM MT", think=
   ("Booking this as written per her go-ahead. It's a day-before deadline nudge, so a "
    "cron wake reminder fits — the actual export/deliver work already has its own "
    "calendar block on Jul 20.")),
 "tooluse_mnYNLSUjx648EzaXmnijvk": dict(  # R6 Order supplies
   job="job_f6b8c0d2", name="Order screen printing supplies online",
   sched={"kind":"at","at":"2026-06-29T15:00:00Z"},
   text=("Reminder: order screen-printing supplies online (Southwestern Ink Supply or "
         "alt vendor) so they arrive before the Jul 11 workshop. Use the supply list "
         "from the prep session; 2–5 business-day shipping in-region."),
   human="Mon Jun 29, 2026, 9:00 AM MT", think=
   ("She wants a reminder to order supplies so they arrive before the workshop. A cron "
    "wake event is right — it should ping her to place the order. I'll note the vendor "
    "and lead time in the reminder text.")),
 "tooluse_cjudw90f8wVkU8RNryQxEV": dict(  # R7 Coyote invoice
   job="job_a7c9d1e3", name="Send Coyote Ridge invoice",
   sched={"kind":"at","at":"2026-08-23T19:00:00Z"},
   text=("Reminder: send the Coyote Ridge invoice for the summer label project (final "
         "files delivered Jul 20, review meeting Aug 7). Use your business email "
         "crystal@mesillacreativestudio.com."),
   human="Sun Aug 23, 2026, 1:00 PM MT", think=
   ("Confirming the Coyote Ridge invoice reminder. She'll send the invoice herself, so "
    "this is a cron nudge, not a calendar event — I'll carry the project context and the "
    "business-email note into the reminder.")),
 "tooluse_Slq1e70RR4uQRjiDDp7s8A": dict(  # R8 Desert Bloom invoice
   job="job_b8d0e2f4", name="Send Desert Bloom deposit invoice",
   sched={"kind":"at","at":"2026-09-09T19:00:00Z"},
   text=("Reminder: send the Desert Bloom deposit invoice ahead of the Sept 16 "
         "consultation / logo-project kickoff."),
   human="Wed Sep 9, 2026, 1:00 PM MT", think=
   ("Per her instruction, the Desert Bloom invoice nudge moves to Wed Sept 9 — a week "
    "before kickoff, which is sensible deposit timing. Cron wake reminder, since she "
    "sends the invoice herself.")),
 "tooluse_XnjAyDGXIfU3GLDTxCnIyx": dict(  # R9 Verify Adobe post-renewal
   job="job_c9e1f3a5", name="Verify Adobe post-renewal charge",
   sched={"kind":"at","at":"2026-09-04T19:00:00Z"},
   text=("Reminder: verify the Sept 3 Adobe renewal charge matches your Sept 2 decision "
         "(cancel = no charge / downgrade = new amount / keep = standard amount). Check "
         "Rio Grande CU for the charge and the Adobe account for active-plan status."),
   human="Fri Sep 4, 2026, 1:00 PM MT", think=
   ("Adding the Sept 4 post-renewal verification — it's the cheap insurance step that "
    "closes the obvious gap in the plan. A cron wake reminder fires it at her with the "
    "three branches spelled out.")),
 "tooluse_lsg0Z5IImlna6bzDgRicHt": dict(  # R11 Confirm cancellation
   job="job_d0f2a4b6", name="Confirm Adobe cancellation processed",
   sched={"kind":"at","at":"2026-09-07T17:00:00Z"},
   text=("Reminder: 5 business days after the Sept 2 cancel call — log into Adobe and "
         "confirm the plan shows 'cancelled' / no active subscription. Save a screenshot "
         "for records. If it still shows active, call Adobe again to escalate."),
   human="Mon Sep 7, 2026, 11:00 AM MT", think=
   ("Booking the Sept 7 follow-up she asked for. Adobe often bills the dispute right but "
    "leaves the account technically active, so this checks the account *status* a few "
    "days out — a cron nudge with the escalation step baked in.")),
}
# recurring audit -> cron add with cron-expr schedule
CRON_CREATE_RECUR = {
 "tooluse_spb0V2Jew7CA4u08gQ9JVa": dict(  # R10 Monthly audit
   job="job_e1a3b5c7", name="Monthly subscription audit",
   sched={"kind":"cron","expr":"0 10 15 * *","tz":"America/Denver"},
   text=("Reminder: monthly subscription audit. Review all active subscriptions and "
         "recent charges, cross-check Rio Grande CU + Capital One statements against "
         "expected amounts, cancel anything unused, and flag price changes."),
   human="15th of each month, 10:00 AM MT", think=
   ("Setting up the proactive monthly audit so a hidden charge can't slip past 2+ months "
    "again. A recurring cron wake event on the 15th is exactly the mechanism — it pings "
    "her every month with the checklist.")),
}

REMINDER_IDS = {  # google event-id prefixes that are now cron (strip from calendar results)
 "rpfjk6ejbhepd4us8qu16vk4fs", "i3q5pj95e29r51r9u1iuob26po",
 "tj5e9jifl815asi658k0cq9m34", "ggu7743uj2o3td1vpb7gkr6288",
 "rbl7mjoqh488ogo43njiap9gp0", "r3qlcvbe48a5nkufoq2fb6r8o4",
 "fnmeguufmgrrobrrgenqv9tuqc", "g1tag792reqmnq0sd2uvmlvh2c",
 "hn64mamuoppvcfretrosf6vk4s", "sov3mi0o5l6vsknmpo992afbfk",
 "c0cr8o4pb9em35be1nr0c48iu4",
}

def cron_add_result(rec, recurring=False):
    if recurring:
        when = "fires monthly on the 15th at 10:00 America/Denver"
    else:
        when = f"fires once at {rec['human']} ({rec['sched']['at']})"
    return (f"Scheduled wake job {rec['job']} — \"{rec['name']}\"\n"
            f"  schedule: {json.dumps(rec['sched'])}\n"
            f"  {when}\n"
            f"  delivery: systemEvent -> main session\n"
            f"  status: active")

# ---------------------------------------------------------------- generic thinking rewrites
# assistant messages whose thinking is the templated "Running exec for this step"
# and that stay as exec (queries / date checks) get genuine reasoning.
THINK_BY_CALLID = {
 "tooluse_yPJzWUyj6lYIHBMXVPXaBU":  # [75] Desert Bloom concept review (event, keep)
   ("Third of the batch: the Desert Bloom concept review she asked for, Wed Sept 30, "
    "1–2:30 PM. It's a client meeting, so it belongs on the calendar. Booking it after "
    "the workshop block and the Javi reminder."),
 "tooluse_uHp5DJm2JLcDWwDUMA1T9t":  # [117] date checks
   ("Before I book anything I should verify the weekdays she gave me — Aug 20, Oct 14, "
    "Oct 21 — because the Desert Bloom dates have been drifting and I don't want to "
    "stack another wrong-day booking. Quick date check on all three."),
 "tooluse_y6z5mcYFebT74JQFnulqyM":  # [125] Desert Bloom final review (event)
   ("Booking the Desert Bloom final review on the corrected date — Wed Oct 14, after "
    "the Sept 30 concept review, which keeps the consult -> concept -> final arc in the "
    "right order. Client meeting, so calendar event."),
 "tooluse_Obbb2ufFrgRTqQFgONDP82":  # [127] Desert Bloom delivery (event)
   ("And the matching file-delivery block, Wed Oct 21, 1–3 PM — mirrors the Coyote Ridge "
    "export-and-deliver setup. Freelance day, print-ready PDF handoff."),
 "tooluse_6F0lvMNOmtStQjLH3iArtz":  # [129] workshop material prep (event)
   ("Last of the four: the workshop material-prep block. It needs to sit before Jul 11, "
    "so Fri Jul 3, 1–3 PM — a freelance afternoon with a weekend buffer before the "
    "workshop. This is a work block, so it stays a calendar event."),
 "tooluse_0vG6lY46kJEIMWekTRAEYL":  # [163] Oct weekend query
   ("She's scoping a girls-trip weekend with Rosa. I'll pull both Oct 2–4 and Oct 9–11 "
    "so I can check them against her standing rhythm and the Desert Bloom tail before "
    "recommending one."),
 "tooluse_Wx45wx6CRfrv83Wt0Uh4oB":  # [183] full pull pg2
   ("First page only covered May–mid-July. Continuing the full-calendar pull from Jul 14 "
    "so the end-of-year summary is complete — I also want to fold in the cron reminders "
    "separately once the events are all gathered."),
 "tooluse_asacpMDmaURoh94DC16ZQ2":  # [185]
   ("Next window of the full pull — mid-August onward. Gathering every calendar event "
    "before I merge them with the cron reminder list for the master view."),
 "tooluse_8jOV2p45ZjIF6fS2ww6jNY":  # [187]
   ("Continuing through September — the densest stretch. Once I have October too I'll "
    "pull the cron reminders and lay the whole thing out."),
 "tooluse_gtftUVJ0i4D1Jpvb8YzWjU":  # [189]
   ("Final calendar window, October to year-end. After this I'll list the cron wake "
    "reminders so the master schedule shows both the events and the nudges."),
}

# ---------------------------------------------------------------- doc deliverables (write/edit)
DRAFT_PATH = "/root/workspace/Adobe_billing_dispute_DRAFT.md"
PLAN_PATH  = "/root/workspace/adobe_overcharge_dispute_plan.md"
TIMELINE_PATH = "/root/workspace/adobe_dispute_timeline.md"
DEADLINES_PATH = "/root/workspace/client_deadlines_may-sep_2026.md"
IMPACT_PATH = "/root/workspace/adobe_overcharge_impact.md"

DRAFT_BODY = """# Adobe overcharge dispute — call prep + draft email (DRAFT — not sent)

Status: DRAFT for Crystal's review. Nothing has been sent to Adobe.

## Call prep (Fri May 15, 1:00-2:00 PM MT)
Have ready before dialing Adobe Support:
- Adobe account number
- Last 5 billing statements: Jan, Feb, Mar, Apr, May 2026
- Overcharge: ~$20/mo extra since February (~$60-80 total to date)

Goal: full refund of the overcharge + correct the forward billing rate.
Also ask, while on the call: downgrade/plan-tier options and the exact early-
termination-fee amount, so the September renewal decision needs only one call.

## Draft dispute email (fallback if the call doesn't resolve it)
To: Adobe Customer Care
Subject: Billing dispute - overcharged ~$20/month since February 2026

Hello,

My Creative Cloud subscription has been billed approximately $20/month above my
agreed rate since February 2026 (account number: [ACCOUNT #]). I've attached the
last five statements (January-May 2026) showing the discrepancy.

I'm requesting a refund of the overcharged amount and a correction of my billing
rate going forward. Please confirm the corrected monthly rate and the refund
amount in writing.

Thank you,
Crystal Lee
"""

# ---------------------------------------------------------------- build new message stream
OUT = []
def emit(m): OUT.append(m)

i = 0
N = len(msgs)
while i < N:
    m = msgs[i]
    role = m["message"].get("role")

    if role == "user":
        emit(copy.deepcopy(m)); i += 1; continue

    if role == "toolResult":
        # standalone (shouldn't normally happen unpaired) — copy
        emit(copy.deepcopy(m)); i += 1; continue

    # assistant
    tc = first_toolcall(m)
    if tc is None:
        # pure thinking/text summary turn — possibly inject a write-doc before it
        msg = copy.deepcopy(m)
        c = msg["message"]["content"]
        txt = next((b["text"] for b in c if b.get("type") == "text"), "")
        # which summary?
        if "Adobe Dispute & Resolution Timeline" in txt:
            wid = "tooluse_gwrite01"
            emit(mk_assistant([
                think("She wants the whole Adobe plan laid out as a timeline she can "
                      "scan. I'll save it as a markdown file in her workspace so she has "
                      "a durable copy, then show it in chat."),
                toolcall(wid, "write", {"file_path": TIMELINE_PATH, "content":
                    "# Adobe dispute & resolution timeline\n\n" + txt.split("##",1)[-1]})]))
            emit(mk_toolresult(wid, "write", f"Wrote {len(txt)} bytes to {TIMELINE_PATH}"))
            # prepend a saved-note to the chat text
            for b in c:
                if b.get("type") == "text":
                    b["text"] = f"Saved to `{TIMELINE_PATH}`. Here's the timeline:\n\n" + b["text"]
        elif "Client Deadlines & Deliveries" in txt:
            wid = "tooluse_gwrite02"
            emit(mk_assistant([
                think("A full client-deadline summary is worth keeping as a file, not "
                      "just a chat message — I'll write it to her workspace and then "
                      "render it here."),
                toolcall(wid, "write", {"file_path": DEADLINES_PATH, "content":
                    "# Client deadlines & deliveries — May 6 -> Sept 30, 2026\n\n" + txt.split("##",1)[-1]})]))
            emit(mk_toolresult(wid, "write", f"Wrote {len(txt)} bytes to {DEADLINES_PATH}"))
            for b in c:
                if b.get("type") == "text":
                    b["text"] = f"Saved to `{DEADLINES_PATH}`. Here's the summary:\n\n" + b["text"]
        elif "Adobe Overcharge Dispute — Full Resolution Plan" in txt:
            wid = "tooluse_gwrite03"
            emit(mk_assistant([
                think("This is the master plan she'll come back to from first detection "
                      "through cancellation. I'll save it as a standalone file so it "
                      "outlives the chat, then present it."),
                toolcall(wid, "write", {"file_path": PLAN_PATH, "content":
                    "# Adobe overcharge dispute — full resolution plan\n\n" + txt.split("##",1)[-1]})]))
            emit(mk_toolresult(wid, "write", f"Wrote {len(txt)} bytes to {PLAN_PATH}"))
            for b in c:
                if b.get("type") == "text":
                    b["text"] = f"Saved to `{PLAN_PATH}`. Here's the full plan:\n\n" + b["text"]
        elif "Adobe Overcharge Impact" in txt:
            wid = "tooluse_gwrite04"
            emit(mk_assistant([
                think("The financial breakdown is the kind of thing she'll want to "
                      "reference and maybe paste into the dispute. Saving it to a file, "
                      "then showing it."),
                toolcall(wid, "write", {"file_path": IMPACT_PATH, "content":
                    "# Adobe overcharge impact — Feb 2026 -> today\n\n" + txt.split("##",1)[-1]})]))
            emit(mk_toolresult(wid, "write", f"Wrote {len(txt)} bytes to {IMPACT_PATH}"))
            for b in c:
                if b.get("type") == "text":
                    b["text"] = f"Saved to `{IMPACT_PATH}`. Here's the breakdown:\n\n" + b["text"]
        emit(msg); i += 1; continue

    # assistant message WITH a tool call; its result is msgs[i+1]
    cid = tc["id"]
    result = msgs[i+1] if i+1 < N and msgs[i+1]["message"].get("role") == "toolResult" else None
    base = copy.deepcopy(m)
    bc = base["message"]["content"]

    # --- reminder CREATE -> cron add
    if cid in CRON_CREATE or cid in CRON_CREATE_RECUR:
        recurring = cid in CRON_CREATE_RECUR
        rec = (CRON_CREATE_RECUR if recurring else CRON_CREATE)[cid]
        new_blocks = []
        for b in bc:
            if b.get("type") == "thinking":
                new_blocks.append(think(rec["think"]))
            elif b.get("type") == "text":
                new_blocks.append(b)
            elif b.get("type") == "toolCall":
                new_blocks.append(toolcall(cid, "cron", {
                    "action": "add",
                    "job": {"name": rec["name"], "schedule": rec["sched"],
                            "sessionTarget": "main",
                            "payload": {"kind": "systemEvent", "text": rec["text"]}}}))
        # ensure a thinking block exists
        if not any(b.get("type") == "thinking" for b in new_blocks):
            new_blocks.insert(0, think(rec["think"]))
        emit(mk_assistant(new_blocks))
        emit(mk_toolresult(cid, "cron", cron_add_result(rec, recurring)))
        # after adding the Sept 4 verify reminder -> edit the saved plan file to match
        if cid == "tooluse_XnjAyDGXIfU3GLDTxCnIyx":
            eid = "tooluse_gedit01"
            emit(mk_assistant([
                think("Now that the post-renewal verification step exists, the saved plan "
                      "should reflect it — I'll add the Sept 4 verify line to the dispute "
                      "plan file so the document and the schedule stay in sync."),
                toolcall(eid, "edit", {"file_path": PLAN_PATH,
                    "oldText": "### Phase 3 — Transition (only if Phase 2 = cancel)",
                    "newText": ("- Sept 4, 1:00 PM MT — Verify the post-renewal charge "
                        "(cancel = no charge / downgrade = new amount / keep = standard).\n\n"
                        "### Phase 3 — Transition (only if Phase 2 = cancel)")})]))
            emit(mk_toolresult(eid, "edit", f"Applied 1 edit to {PLAN_PATH}"))
        i += 2; continue

    # --- combined update [143]: material-prep event (keep exec) + R6 order-supplies (cron update)
    if cid == "tooluse_xyRjIbmzDVAeihw6gJBKFO":
        # split into: gog calendar update (event) + cron update (R6)
        ev_id = "tooluse_xyRjIbmzDVAeihw6gJBKFO"
        cr_id = "tooluse_xyRj_cron6"
        emit(mk_assistant([
            think("Applying Option A — swap the two. The material-prep work block (a "
                  "calendar event) moves to Mon Jun 29, 1–3 PM; the supply-order reminder "
                  "(a cron nudge) moves to Mon Jul 6 so there's a 5-day shipping runway "
                  "before the workshop."),
            textb("Applying Option A (swap prep and order dates):"),
            toolcall(ev_id, "exec", {"command":
                "gog calendar update primary 8aspkeas2r6b26o0irh4l77luo "
                "--from 2026-06-29T13:00:00-06:00 --to 2026-06-29T15:00:00-06:00 "
                "--account crystal.lee@Greenridertech.co.in"})]))
        emit(mk_toolresult(ev_id, "exec",
            "id\t8aspkeas2r6b26o0irh4l77luo\nsummary\tWorkshop material prep and supply list\n"
            "timezone\tAmerica/Denver\nstart\t2026-06-29T13:00:00-06:00\nstart-day-of-week\tMonday\n"
            "end\t2026-06-29T15:00:00-06:00\nend-day-of-week\tMonday\n"
            "description\tPrep materials + supply list for July 11 Roadrunner screen printing workshop.\n"
            "reminders\t(calendar default)"))
        emit(mk_assistant([
            toolcall(cr_id, "cron", {"action":"update","jobId":"job_f6b8c0d2",
                "patch":{"schedule":{"kind":"at","at":"2026-07-06T15:00:00Z"},
                         "payload":{"kind":"systemEvent","text":
                    "Reminder: order screen-printing supplies online (Southwestern Ink "
                    "Supply or alt vendor) based on the Jul 11 workshop supply list. Must "
                    "arrive before the workshop."}}})]))
        emit(mk_toolresult(cr_id, "cron",
            "Updated wake job job_f6b8c0d2 — \"Order screen printing supplies online\"\n"
            "  schedule: {\"kind\": \"at\", \"at\": \"2026-07-06T15:00:00Z\"} (Mon Jul 6, 9:00 AM MT)\n"
            "  status: active"))
        i += 2; continue

    # --- combined update [159]: R2 call (cron update) + R1 check (cron update)
    if cid == "tooluse_cV3eFqQ85E23tlV1jfdNGo":
        c1 = "tooluse_cV3e_cronR2"; c2 = "tooluse_cV3e_cronR1"
        emit(mk_assistant([
            think("Interpretation C: move the decision call to a cleaner slot and shift "
                  "the charge-check one day earlier so the order is check -> decide -> "
                  "renew. Both are cron reminders, so I'll patch their schedules (and fix "
                  "the charge-check wording now that it fires two days before renewal)."),
            toolcall(c1, "cron", {"action":"update","jobId":"job_a17f93c0",
                "patch":{"schedule":{"kind":"at","at":"2026-09-02T18:15:00Z"}}})]))
        emit(mk_toolresult(c1, "cron",
            "Updated wake job job_a17f93c0 — \"Call Adobe: cancel or downgrade before renewal\"\n"
            "  schedule: {\"kind\": \"at\", \"at\": \"2026-09-02T18:15:00Z\"} (Wed Sep 2, 12:15 PM MT)\n"
            "  status: active"))
        emit(mk_assistant([
            toolcall(c2, "cron", {"action":"update","jobId":"job_b2c4d6e8",
                "patch":{"schedule":{"kind":"at","at":"2026-09-01T23:15:00Z"},
                         "name":"Check Adobe charge amount before billing cycle renews in 2 days",
                         "payload":{"kind":"systemEvent","text":
                    "Reminder: check your Adobe charge amount — the billing cycle renews "
                    "in 2 days (Sept 3). Confirm pricing, plan tier, and any credit from "
                    "the May dispute before the decision call tomorrow."}}})]))
        emit(mk_toolresult(c2, "cron",
            "Updated wake job job_b2c4d6e8 — \"Check Adobe charge amount before billing cycle renews in 2 days\"\n"
            "  schedule: {\"kind\": \"at\", \"at\": \"2026-09-01T23:15:00Z\"} (Tue Sep 1, 5:15 PM MT)\n"
            "  status: active"))
        i += 2; continue

    # --- generic: keep exec, but maybe rewrite thinking + strip reminder rows from result
    new_blocks = []
    for b in bc:
        if b.get("type") == "thinking" and cid in THINK_BY_CALLID:
            new_blocks.append(think(THINK_BY_CALLID[cid]))
        else:
            new_blocks.append(b)
    if cid in THINK_BY_CALLID and not any(b.get("type")=="thinking" for b in new_blocks):
        new_blocks.insert(0, think(THINK_BY_CALLID[cid]))
    emit(mk_assistant(new_blocks))

    # result: strip reminder rows if this was a calendar events query
    if result is not None:
        r = copy.deepcopy(result)
        rc = r["message"]["content"]
        rtext = rc[0]["text"] if rc and isinstance(rc, list) else ""
        if "gog calendar events" in json.dumps(tc.get("arguments", {})):
            kept = []
            for line in rtext.split("\n"):
                if line.startswith("# Next page:"):
                    continue
                stripped = line.strip()
                if any(stripped.startswith(rid) for rid in REMINDER_IDS):
                    continue
                kept.append(line)
            newtext = "\n".join(kept).rstrip()
            # if only a header remains, say no events
            body = [l for l in kept if l.strip() and not l.strip().startswith("ID ")]
            if not body:
                newtext = "No events"
            rc[0]["text"] = newtext if newtext.strip() else "No events"
        emit(r)
        i += 2
    else:
        i += 1

    # --- post-call doc injections ------------------------------------
    # after creating the dispute CALL event ([11]) -> write the draft email/prep doc
    if cid == "tooluse_3urIYrKpqA4Jm4Fvalvs9I":
        wid = "tooluse_gdraft01"
        emit(mk_assistant([
            think("The task here isn't just to book the call — she needs the dispute "
                  "itself prepared. I'll draft the call talking-points and a fallback "
                  "dispute email to a file in her workspace. Draft only — I never send "
                  "mail on her behalf."),
            toolcall(wid, "write", {"file_path": DRAFT_PATH, "content": DRAFT_BODY})]))
        emit(mk_toolresult(wid, "write", f"Wrote {len(DRAFT_BODY)} bytes to {DRAFT_PATH}"))

    # after adding the Sept 4 verify reminder ([169]) -> edit the plan file
    if cid == "tooluse_XnjAyDGXIfU3GLDTxCnIyx":
        eid = "tooluse_gedit01"
        emit(mk_assistant([
            think("Now that the post-renewal verification step exists, the saved plan "
                  "should reflect it — I'll add the Sept 4 verify line to the dispute "
                  "plan file so the document and the schedule stay in sync."),
            toolcall(eid, "edit", {"file_path": PLAN_PATH,
                "oldText": "### Phase 3 — Transition (only if Phase 2 = cancel)",
                "newText": ("- Sept 4, 1:00 PM MT — Verify the post-renewal charge "
                    "(cancel = no charge / downgrade = new amount / keep = standard).\n\n"
                    "### Phase 3 — Transition (only if Phase 2 = cancel)")})]))
        emit(mk_toolresult(eid, "edit", f"Applied 1 edit to {PLAN_PATH}"))

print(f"messages: {N} -> {len(OUT)}")

# ---------------------------------------------------------------- insert cron-list surfacing
# After the Sept 1-11 calendar query result, and after the final full pull,
# surface the cron reminders so the summaries are sourced.
def cron_list_block(window_label, lines):
    cid = "tooluse_gcronls_" + str(abs(hash(window_label)) % 10000)
    body = "JOB ID         NEXT FIRE                     NAME\n" + "\n".join(lines)
    return cid, body

# locate insertion points by scanning OUT for the matching exec query results
def insert_after_result(pred, assistant_blocks, result_msg):
    for idx in range(len(OUT)):
        msg = OUT[idx]
        if msg["message"].get("role") != "toolResult":
            continue
        # find the toolCall that produced it (previous assistant)
        # match on the *call* args via pred over the preceding assistant message
        j = idx - 1
        while j >= 0 and OUT[j]["message"].get("role") != "assistant":
            j -= 1
        if j < 0:
            continue
        atc = first_toolcall(OUT[j])
        if atc and pred(atc):
            OUT.insert(idx+1, result_msg)
            OUT.insert(idx+1, mk_assistant(assistant_blocks))
            return True
    return False

# Sept 1-11 cron list
# As of this turn only these reminders exist (the Sept moves + verify/confirm/audit
# are all created later in the conversation), matching the calendar state then.
cid_a, body_a = cron_list_block("sep1_11", [
 "job_a17f93c0   2026-09-01T09:00 MT           Call Adobe: cancel or downgrade before renewal",
 "job_b2c4d6e8   2026-09-02T09:00 MT           Check Adobe charge amount before billing cycle renews tomorrow",
 "job_b8d0e2f4   2026-09-09T13:00 MT           Send Desert Bloom deposit invoice",
])
insert_after_result(
 lambda atc: atc.get("name")=="exec" and "2026-09-01T00:00:00-06:00" in json.dumps(atc.get("arguments",{})) and "2026-09-11" in json.dumps(atc.get("arguments",{})),
 [think("The reminders for this window live as cron wake jobs, not calendar events, so "
        "I'll pull the cron list too and merge both into the Sept 1–11 view."),
  toolcall(cid_a, "cron", {"action":"list","window":{"from":"2026-09-01","to":"2026-09-11"}})],
 mk_toolresult(cid_a, "cron", body_a))

# Final full-schedule cron list (everything)
cid_b, body_b = cron_list_block("full", [
 "job_f6b8c0d2   2026-07-06T09:00 MT           Order screen printing supplies online",
 "job_d4f6a8b0   2026-06-29T09:00 MT           Email Javi: confirm absence from July 7 + July 9 shifts",
 "job_e5a7b9c1   2026-07-19T09:00 MT           Finalize Coyote Ridge label files for delivery tomorrow",
 "job_a7c9d1e3   2026-08-23T13:00 MT           Send Coyote Ridge invoice",
 "job_b2c4d6e8   2026-09-01T17:15 MT           Check Adobe charge amount before billing cycle renews in 2 days",
 "job_a17f93c0   2026-09-02T12:15 MT           Call Adobe: cancel or downgrade before renewal",
 "job_c9e1f3a5   2026-09-04T13:00 MT           Verify Adobe post-renewal charge",
 "job_d0f2a4b6   2026-09-07T11:00 MT           Confirm Adobe cancellation processed",
 "job_b8d0e2f4   2026-09-09T13:00 MT           Send Desert Bloom deposit invoice",
 "job_c3e5f7a9   2026-09-20T20:00 MT           Prep for Dr. Lena appointment tomorrow",
 "job_e1a3b5c7   15th @ 10:00 MT (recurring)   Monthly subscription audit",
])
insert_after_result(
 lambda atc: atc.get("name")=="exec" and "2026-10-02T00:00:00-06:00" in json.dumps(atc.get("arguments",{})) and "2026-12-31" in json.dumps(atc.get("arguments",{})),
 [think("Calendar events are all gathered. Now the cron wake reminders — these are the "
        "nudges I set as wake jobs rather than calendar entries, and the master view "
        "should show both."),
  toolcall(cid_b, "cron", {"action":"list"})],
 mk_toolresult(cid_b, "cron", body_b))

# ---------------------------------------------------------------- prose fixes
GRAND_OLD = ("**Grand total this session:** 22 one-off events + 2 recurring series "
             "(13 weekly planning + 8 monthly audits) = **43 calendar entries created/modified**.")
GRAND_NEW = ("**Grand total this session:** 13 calendar events (incl. the 13-occurrence "
             "weekly-planning series) + 11 cron wake reminders (incl. the monthly "
             "subscription-audit series). Calendar entries are the meetings, "
             "appointments, and work blocks; the cron jobs are the 'remind-me-to-act' "
             "nudges that ping you when they fire.")
for m in OUT:
    c = m["message"].get("content")
    if isinstance(c, list):
        for b in c:
            if b.get("type") == "text" and GRAND_OLD in b.get("text", ""):
                b["text"] = b["text"].replace(GRAND_OLD, GRAND_NEW)

# ---------------------------------------------------------------- re-thread envelope chain
prev = "d0000000"
last_ts = msgs[0]["timestamp"]
for n, msg in enumerate(OUT, start=1):
    msg["type"] = "message"
    msg["id"] = f"d{n:07d}"
    msg["parentId"] = prev
    if msg.get("timestamp"):
        last_ts = msg["timestamp"]
    else:
        msg["timestamp"] = last_ts
    prev = msg["id"]

d["messages"] = OUT
json.dump(d, open(SRC, "w"), ensure_ascii=False, indent=1)
print("wrote", SRC, "with", len(OUT), "messages")
