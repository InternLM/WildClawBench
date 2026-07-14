---
name: audit-gate
description: Use when auditing this project's deliverables against the CRUCIBLE gate — run instruments, review evidence, and verify findings fail-closed.
---

This skill defers entirely to the contract in `CRUCIBLE.md` and the run playbook in
`audit/README.md`. It never restates the axes, severity scale, or disposition vocabulary.

The two reviewer artifacts are `findings.yaml` and `REPORT.md` (project root). The only
admissible evidence source is `audit/evidence.yaml`. The gate is
`uv run --project audit python audit/audit.py verify --findings findings.yaml --context audit/evidence.yaml`,
which exits 0 only when the report is internally honest and every required instrument ran clean.
