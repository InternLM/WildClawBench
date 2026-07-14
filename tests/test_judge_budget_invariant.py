"""Guards `_FAMILY_EVIDENCE` against silent context-window overruns.

Worst-case dispatch must fit:

    budget_chars / EMPIRICAL_CHARS_PER_TOKEN_FLOOR
        + member_max_output_tokens + SAFETY_TOKEN_BUFFER
        <= ctx_window

The chars/token FLOOR (denser-than-typical evidence) is the regression-canary;
silent drifts in maxTokens or budget constants previously caused the
alden-croft run_2/run_3 council to collapse 0/3. This test makes the next
such drift fail loud at CI time instead of at first-judge time.

Keyed by stable judge FAMILY (sonnet/glm/kimi), not by the monthly-rotating
Bedrock inference-profile id — see src/utils/grading.py family-decoupling block.
Context windows + max_output match AWS-published model cards (Sonnet 4.6,
Kimi K2.5, GLM 5). chars/token floors match the numbers stamped in
src/utils/grading.py:_FAMILY_EVIDENCE comment block.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utils import grading  # noqa: E402


SAFETY_TOKEN_BUFFER = 3000
SCAFFOLD_CHARS = 5000


_FAMILY_LIMITS = {
    "sonnet": {"ctx_window": 1_000_000, "chars_per_token_floor": 1.375},
    "kimi":   {"ctx_window":   262_144, "chars_per_token_floor": 1.15},
    "glm":    {"ctx_window":   202_752, "chars_per_token_floor": 1.15},
}


@pytest.mark.parametrize("family", sorted(grading._FAMILY_EVIDENCE))
def test_member_budget_fits_context_window(family):
    budget, max_output = grading._FAMILY_EVIDENCE[family]
    limits = _FAMILY_LIMITS.get(family)
    assert limits is not None, (
        f"_FAMILY_EVIDENCE has family {family!r} but _FAMILY_LIMITS in this test "
        "does not — add the new family's ctx_window and chars_per_token_floor "
        "(run probe_judge_only.py to measure the floor)."
    )
    ctx = limits["ctx_window"]
    cpt_floor = limits["chars_per_token_floor"]
    dispatched_chars = budget + SCAFFOLD_CHARS
    worst_case_input_tokens = dispatched_chars / cpt_floor
    total_tokens = worst_case_input_tokens + max_output + SAFETY_TOKEN_BUFFER
    assert total_tokens <= ctx, (
        f"Budget overrun for {family}: "
        f"({budget:,} budget + {SCAFFOLD_CHARS} scaffold) / {cpt_floor} cpt = "
        f"{worst_case_input_tokens:,.0f} input tokens + "
        f"{max_output} maxTokens + {SAFETY_TOKEN_BUFFER} safety = "
        f"{total_tokens:,.0f} total > {ctx:,} context window. "
        "Either lower the budget, lower this family's max_output, or raise the "
        "chars/token floor (only with new probe evidence)."
    )


def test_every_priced_family_has_evidence_budget():
    for family in grading._FAMILY_RATES:
        assert family in grading._FAMILY_EVIDENCE, (
            f"Family {family!r} has a rate in _FAMILY_RATES but no _FAMILY_EVIDENCE "
            "entry — it would fall through to _DEFAULT_JUDGE_MAX_EVIDENCE (likely "
            "too tight or too loose). Add its budget + max_output."
        )


def test_evidence_budget_families_are_priced_and_known():
    for family in grading._FAMILY_EVIDENCE:
        assert family in grading._FAMILY_RATES, (
            f"Family {family!r} has an evidence budget but no _FAMILY_RATES entry; "
            "every council family must be priced (validate_judge_pricing enforces "
            "this at runtime)."
        )
        assert family in _FAMILY_LIMITS, (
            f"Family {family!r} has an evidence budget but no _FAMILY_LIMITS guard "
            "in this test — add its ctx_window + chars_per_token_floor."
        )
