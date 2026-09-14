from __future__ import annotations

ALLOWED_RUNGS = frozenset({"off", "low", "medium", "xhigh"})
DEFAULT_RUNG = "xhigh"
PROVIDER_ID = "wcb-lb"


def resolve_rung(thinking: str | None) -> str:
    rung = (thinking or DEFAULT_RUNG).strip().lower()
    if rung not in ALLOWED_RUNGS:
        raise ValueError(
            f"reasoning rung '{rung}' not in {sorted(ALLOWED_RUNGS)} "
            "(qwen3.8-flash-next contract: unsupported rungs hard-400)")
    return rung


def patch_entry_yaml(provider: str, model: str, rung: str) -> str:
    return ("- id: agent-default-model\n"
            "  config:\n"
            f"    provider: {provider}\n"
            f"    model: {model}\n"
            f"    reasoningEffort: {rung}\n")
