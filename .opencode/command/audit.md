---
description: Run the CRUCIBLE audit gate (run instruments → review → verify)
agent: build
---

The contract is `@CRUCIBLE.md`. The run playbook is `@audit/README.md`. Do not restate the contract.

Phase 1 — generate evidence:
!`uv run --project audit python audit/audit.py run`

Phase 2 — review: read `@REVIEW.md` as your instructions and `@audit/evidence.yaml` as the
ONLY source of instrumented evidence. Write `findings.yaml` and `REPORT.md` at the project
root (strip any `_template`/`_example` keys; `REPORT.md` is the single human report and its
**Bug Tickets** section holds the JIRA-style tickets).

Phase 3 — gate:
!`uv run --project audit python audit/audit.py verify --findings findings.yaml --context audit/evidence.yaml`

Findings are UNGATED until `verify` exits 0.
