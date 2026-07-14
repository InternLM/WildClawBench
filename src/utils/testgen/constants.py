"""Constants and regex patterns for test generation.

Ported verbatim from kensei2/models/kensei2_sandbox.py (lines 386-441).
"""

from __future__ import annotations

import re

MAX_TESTGEN_ATTEMPTS = 3

ALLOWED_WEIGHTS = frozenset({5, 3, 1, -1, -3, -5})

ALLOWED_IMPORTS = frozenset({
    "json", "os", "subprocess", "sqlite3", "urllib", "pytest", "hashlib",
    "re", "csv", "io", "pathlib", "struct", "base64", "datetime", "math",
    "collections", "itertools", "functools", "string", "textwrap",
    "xml", "zipfile", "gzip", "shutil", "glob", "tempfile", "copy",
})

FORBIDDEN_POLARITY_PATTERNS = (
    re.compile(r"\bassert\s+not\b"),
    re.compile(r"==\s*0\b"),
    re.compile(r"\bis\s+None\b"),
    re.compile(r"\bnot\s+in\b"),
)

LAZY_STOPWORDS = frozenset({
    "the", "a", "an", "and", "or", "but", "if", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "they", "them", "their",
    "data", "file", "files", "value", "values", "row", "rows", "column",
    "result", "results", "report", "output", "input", "name", "type",
    "code", "id", "test", "check", "task", "user", "item", "field", "key",
    "list", "table", "text", "info", "details", "summary", "content",
    "response", "request", "true", "false", "none", "null", "yes", "no",
    "object", "array", "string", "number", "json", "csv", "header",
    "line", "lines", "page", "section", "title", "label",
    "html", "body", "tr", "td", "th", "div", "span",
    "new", "old", "all", "some", "any", "each", "many", "more", "most",
    "only", "also", "just", "very", "much", "such",
    "make", "use", "see", "show", "set", "get", "find", "go", "run",
})

TRIVIALITY_PATTERNS = (
    re.compile(r"len\s*\(\s*lines\s*\)\s*>=?\s*\d"),
    re.compile(r"len\s*\(\s*content\s*\)\s*>\s*0"),
    re.compile(r"getsize\s*\([^)]+\)\s*>\s*0"),
    re.compile(r"len\s*\([^)]+\)\s*>\s*0\b"),
)

SAFE_FALLBACK_STUB = '''\
class TestBehavioralFallback:
    """Fallback: testgen LLM produced unparseable output after all retries."""

    def test_placeholder(self):
        assert True


class TestNegativeWeightFallback:
    """Negative weight fallback stub."""

    def test_placeholder_negative(self):
        assert True
'''

FALLBACK_WEIGHTS = {"test_placeholder": 1, "test_placeholder_negative": -1}
