"""Strip LLM-emitted duplicates of imports/helpers/env constants.

The wrapper prefix already supplies the `_request`, `api_get`, `api_post`, etc.
helpers and the `<SERVICE>_URL` constants. Strip any duplicates the LLM emits
in its own output so the assembled file isn't full of redefinitions.

Ported from kensei2/models/kensei2_sandbox.py (lines 911-930).
"""

from __future__ import annotations

import re

_STRIP_IMPORT_RE = re.compile(
    r"^(?:import\s+\w+|from\s+\w[\w.]*\s+import\s+.*)$",
    re.MULTILINE,
)
_STRIP_HELPER_RE = re.compile(
    r"^def\s+(?:_get|_post|_request|api_get|api_post|read_file|file_exists)\s*\(.*?(?=\nclass\s|\ndef\s[^_]|\Z)",
    re.MULTILINE | re.DOTALL,
)
_STRIP_ENVIRON_RE = re.compile(
    r"^[A-Z_]+_URL\s*=\s*os\.environ.*$",
    re.MULTILINE,
)


def sanitize_llm_test_code(code: str) -> str:
    code = _STRIP_IMPORT_RE.sub("", code)
    code = _STRIP_ENVIRON_RE.sub("", code)
    code = _STRIP_HELPER_RE.sub("", code)
    code = re.sub(r"\n{4,}", "\n\n\n", code)
    return code.strip()
