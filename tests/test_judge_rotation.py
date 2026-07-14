"""Monthly ARN-rotation guard for the judge council.

Company policy rotates the three Bedrock judge inference-profile ARNs every
month, which changes the opaque profile-id suffix (the part the OLD code keyed
pricing/budget/cache on). This test proves the family-decoupled path is
rotation-proof end to end: a brand-new (never-seen) Sonnet profile-id tail,
fed only through the JUDGE_COUNCIL_SONNET_ARN env var, still prices correctly
because register_judges_for_batch() registers the CURRENT tail against the
stable family rate, and litellm.completion_cost() then resolves that tail.

Offline only — register_model() and completion_cost() are pure local catalog
operations (no network, no live LLM).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

litellm = pytest.importorskip("litellm")

from src.utils import grading, judge_litellm  # noqa: E402

ROTATED_SONNET_ARN = (
    "bedrock/arn:aws:bedrock:ap-south-1:426628337772:"
    "application-inference-profile/rotatedaug2026sonnet"
)
ROTATED_TAIL = "rotatedaug2026sonnet"


@pytest.fixture(autouse=True)
def _isolate(monkeypatch):
    for var in (
        "JUDGE_COUNCIL_MEMBERS",
        "JUDGE_COUNCIL_GLM_ARN",
        "JUDGE_COUNCIL_KIMI_ARN",
    ):
        monkeypatch.delenv(var, raising=False)
    judge_litellm._registered_tails.clear()
    yield


def test_rotated_sonnet_arn_prices_at_family_rate(monkeypatch):
    monkeypatch.setenv("JUDGE_COUNCIL_SONNET_ARN", ROTATED_SONNET_ARN)

    members = grading.council_members()
    assert [m.family for m in members] == ["sonnet"]
    assert judge_litellm._arn_tail(members[0].model) == ROTATED_TAIL

    judge_litellm.register_judges_for_batch(members)
    grading.validate_judge_pricing(members)

    resp = litellm.types.utils.ModelResponse(
        usage=litellm.types.utils.Usage(
            prompt_tokens=10_000, completion_tokens=2_000, total_tokens=12_000
        )
    )
    resp.model = ROTATED_SONNET_ARN

    cost = litellm.completion_cost(completion_response=resp, custom_llm_provider="bedrock")

    r_in, r_out, _r_cr, _r_cw = grading._FAMILY_RATES["sonnet"]
    expected = 10_000 * r_in + 2_000 * r_out
    assert cost == pytest.approx(expected, rel=1e-9)
