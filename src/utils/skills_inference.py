"""Required-API + distractor inference.

The catalog of available APIs is discovered DYNAMICALLY from the `environment/`
folder (every `<name>-api/` dir with a `service.toml`) — not hardcoded. Keyword
matching is derived from each API's slug, with an optional curated keyword/tag
map (`_CURATED_*`) layered on top for the flagship APIs to improve recall.
"""

from __future__ import annotations

import random
import re
from functools import lru_cache
from pathlib import Path

# src/utils/skills_inference.py -> parents[2] == repo root
DEFAULT_ENVIRONMENT_DIR = Path(__file__).resolve().parents[2] / "environment"

# Optional curated enrichment (NOT the source of truth for which APIs exist).
# These add domain-specific terms that don't appear in the slug (e.g. quickbooks
# -> "invoice", "ledger") and coarse domain tags used for distractor selection.
_CURATED_KEYWORDS = {
    "amazon-seller-api":    ("amazon", "seller", "asin", "sku", "fba", "seller central"),
    "etsy-api":             ("etsy", "listing", "shop", "handmade", "craft", "woodwork", "woodcraft"),
    "pinterest-api":        ("pinterest", "pin", "board"),
    "instagram-api":        ("instagram", "insta", "ig ", "ig,", "post", "reel", "story", "stories", "media"),
    "youtube-api":          ("youtube", "video", "channel", "subscriber", "playlist", "upload"),
    "linear-api":           ("linear", "issue", "project management", "sprint", "backlog", "ticket"),
    "quickbooks-api":       ("quickbooks", "invoice", "accounting", "expense", "bill", "payment", "ledger"),
    "google-classroom-api": ("classroom", "course", "assignment", "student", "teacher", "grading"),
    "myfitnesspal-api":     ("myfitnesspal", "fitness", "calorie", "exercise", "workout", "nutrition", "diet", "meal", "run ", "running"),
    "ring-api":             ("ring", "doorbell", "camera", "security", "motion"),
}

_CURATED_TAGS = {
    "amazon-seller-api":    ("commerce", "retail"),
    "etsy-api":             ("commerce", "retail", "creative"),
    "pinterest-api":        ("social", "media", "creative"),
    "instagram-api":        ("social", "media", "creative"),
    "youtube-api":          ("social", "media"),
    "linear-api":           ("productivity", "saas"),
    "quickbooks-api":       ("finance", "saas"),
    "google-classroom-api": ("productivity", "education"),
    "myfitnesspal-api":     ("health", "lifestyle"),
    "ring-api":             ("iot", "lifestyle"),
}

# Back-compat alias (nothing external relies on this, but keep it stable).
DOMAIN_TAGS = _CURATED_TAGS

DISTRACTOR_COUNT = 4
_MIN_TOKEN_LEN = 3
# Slug tokens that are too generic to be reliable match keys on their own.
_TOKEN_STOPWORDS = {"api", "the", "and", "for", "app", "web", "dev", "data"}


def _env_dir(environment_dir=None) -> Path:
    return Path(environment_dir) if environment_dir else DEFAULT_ENVIRONMENT_DIR


def _slug_keywords(api: str) -> tuple[set[str], set[str]]:
    """Derive (token_keywords, phrase_keywords) from an api slug.

    e.g. 'amazon-seller-api' -> tokens {'amazon','seller'},
                                phrases {'amazon seller','amazonseller'}
    """
    base = api[:-4] if api.endswith("-api") else api  # strip trailing '-api'
    parts = [p for p in base.split("-") if p]
    tokens = {p for p in parts if len(p) >= _MIN_TOKEN_LEN and p not in _TOKEN_STOPWORDS}
    phrases: set[str] = set()
    spaced = base.replace("-", " ")
    solid = base.replace("-", "")
    if " " in spaced:
        phrases.add(spaced)        # multi-word, specific -> safe as substring
        if solid and solid != spaced:
            phrases.add(solid)
    return tokens, phrases


def _compile_keywords(api: str) -> "re.Pattern | None":
    """Build one word-boundary regex from an API's slug-derived + curated
    keywords. Word boundaries avoid substring false positives (e.g. 'ring'
    must not match 'bring'/'during')."""
    tokens, phrases = _slug_keywords(api)
    keys: set[str] = set()
    for k in tokens | phrases:
        if k.strip():
            keys.add(k.strip())
    for k in _CURATED_KEYWORDS.get(api, ()):
        if k.strip():                      # tolerate legacy trailing-space hacks
            keys.add(k.strip())
    if not keys:
        return None
    alts = "|".join(re.escape(k) for k in sorted(keys))
    return re.compile(rf"\b(?:{alts})\b")


@lru_cache(maxsize=8)
def _build_catalog(env_str: str) -> dict[str, "re.Pattern"]:
    """Discover every API in the environment folder and compile its keyword
    matcher. Falls back to the curated set if the environment folder is missing."""
    env = Path(env_str)
    catalog: dict[str, re.Pattern] = {}
    if env.is_dir():
        for d in sorted(env.iterdir()):
            if not (d.is_dir() and d.name.endswith("-api") and (d / "service.toml").is_file()):
                continue
            pat = _compile_keywords(d.name)
            if pat is not None:
                catalog[d.name] = pat
    if not catalog:
        for api in _CURATED_KEYWORDS:
            pat = _compile_keywords(api)
            if pat is not None:
                catalog[api] = pat
    return catalog


def available_apis(environment_dir=None) -> list[str]:
    """All API names discovered in the environment folder (sorted)."""
    return sorted(_build_catalog(str(_env_dir(environment_dir))).keys())


def infer_required_apis(prompt: str, environment_dir=None) -> list[str]:
    """Return the APIs (discovered from environment/) whose keywords appear in
    the prompt, matched on word boundaries to avoid substring false positives."""
    if not prompt:
        return []
    pl = prompt.lower()
    catalog = _build_catalog(str(_env_dir(environment_dir)))
    return sorted(api for api, pat in catalog.items() if pat.search(pl))


def compute_distractor_skills(required_apis: list[str], task_id: str,
                              count: int = DISTRACTOR_COUNT,
                              environment_dir=None) -> list[str]:
    """Pick `count` plausible-but-unneeded APIs from the discovered catalog,
    preferring ones that share a curated domain tag with the required APIs."""
    all_apis = available_apis(environment_dir)
    required_set = set(required_apis)
    required_tags: set[str] = set()
    for api in required_apis:
        required_tags.update(_CURATED_TAGS.get(api, ()))

    domain_pool = sorted(
        api for api in all_apis
        if api not in required_set
        and set(_CURATED_TAGS.get(api, ())) & required_tags
    )
    if len(domain_pool) < count:
        leftover = sorted(
            api for api in all_apis
            if api not in required_set and api not in domain_pool
        )
        domain_pool = domain_pool + leftover

    rng = random.Random(task_id or "wildclaw-default")
    rng.shuffle(domain_pool)
    return domain_pool[:count]
