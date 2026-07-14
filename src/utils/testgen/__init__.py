"""Test-generation pipeline ported from kensei2.

LLM-driven pytest + weights generator with deterministic lint feedback loop.
See `generator.generate_task_tests` for the main entry point.

Routing: Bedrock Converse direct (kensei2 parity). Auth via
`Config.aws_bearer_token` + `Config.bedrock_inference_arn` + `Config.bedrock_region`.
"""

from .generator import generate_task_tests, TestGenResult
from .intent import generate_intent_tests
from .constants import MAX_TESTGEN_ATTEMPTS, ALLOWED_WEIGHTS, SAFE_FALLBACK_STUB

__all__ = [
    "generate_task_tests",
    "generate_intent_tests",
    "TestGenResult",
    "MAX_TESTGEN_ATTEMPTS",
    "ALLOWED_WEIGHTS",
    "SAFE_FALLBACK_STUB",
]
