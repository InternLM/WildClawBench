"""Deterministic lints on generated test code.

L1, L3, L4, L5, L7, L8, L12, L14, L15, L16, L21, L22, L24, L25, L26 — see
PORTING_PLAN docstrings on the original. Empty failure list = draft passes.

Ported verbatim (with naming hygiene) from kensei2/models/kensei2_sandbox.py
(lines 444-804). Callers feed the failure list back into the next attempt's
prompt as "fix these".
"""

from __future__ import annotations

import ast
import re
from typing import Iterable, List, Optional

from .constants import (
    ALLOWED_IMPORTS,
    ALLOWED_WEIGHTS,
    FORBIDDEN_POLARITY_PATTERNS,
    LAZY_STOPWORDS,
    TRIVIALITY_PATTERNS,
)


def collect_test_functions(tree: ast.AST) -> List[ast.FunctionDef]:
    """All `test_*` FunctionDef nodes in an AST tree."""
    return [n for n in ast.walk(tree)
            if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]


def function_has_assert(func: ast.FunctionDef) -> bool:
    return any(isinstance(n, ast.Assert) for n in ast.walk(func))


def function_passes_empty_files(func: ast.FunctionDef) -> bool:
    """L16: True if every assert in the function is just file_exists(...)."""
    asserts = [n for n in ast.walk(func) if isinstance(n, ast.Assert)]
    if not asserts:
        return False
    for node in asserts:
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Is)
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value is True
        ):
            test = test.left
        if not (
            isinstance(test, ast.Call)
            and isinstance(test.func, ast.Name)
            and test.func.id == "file_exists"
        ):
            return False
    return True


_HTTP_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}
_METHOD_KEY_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(/\S*)$", re.IGNORECASE)
# Paths served by the shared middleware/admin plane, not by per-service routers.
_SHARED_PLANE_PREFIXES = ("/audit", "/admin", "/health")


def _route_prefix_match(path: str, route: str) -> bool:
    """True if `path` segment-wise prefix-matches `route` ({params} wildcard)."""
    p_segs = [s for s in path.split("/") if s]
    r_segs = [s for s in route.split("/") if s]
    if len(p_segs) > len(r_segs):
        return False
    for p, r in zip(p_segs, r_segs):
        if r.startswith("{") and r.endswith("}"):
            continue
        if p.startswith("{") and p.endswith("}"):
            continue
        if p.lower() != r.lower():
            return False
    return True


def _leading_literal_path(node: ast.expr) -> Optional[str]:
    """Literal path (or its leading literal part for f-strings) from an AST arg.

    For f-strings like f"/3.0/lists/{lid}/members" only the text before the
    first interpolation is comparable; a trailing partial segment is dropped.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    if isinstance(node, ast.JoinedStr) and node.values:
        first = node.values[0]
        if isinstance(first, ast.Constant) and isinstance(first.value, str):
            lit = first.value
            if len(node.values) > 1 and not lit.endswith("/"):
                lit = lit.rsplit("/", 1)[0] + "/"
            return lit
    return None


def _helper_match_semantics(tree: ast.AST) -> dict:
    """{helper_name: "prefix" | "substring"} for module-level test helpers.

    A helper that compares via .startswith() has prefix semantics (a dropped
    version segment makes it dead code); one that compares via `in` has
    substring semantics (a bare tail like "/send" still matches the full
    served path). startswith wins when both appear.
    """
    semantics: dict = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("test_"):
            continue
        has_startswith = any(
            isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr == "startswith"
            for n in ast.walk(node)
        )
        has_in = any(
            isinstance(n, ast.Compare) and any(isinstance(op, ast.In) for op in n.ops)
            for n in ast.walk(node)
        )
        if has_startswith:
            semantics[node.name] = "prefix"
        elif has_in:
            semantics[node.name] = "substring"
    return semantics


def _extract_endpoint_refs(tree: ast.AST) -> List[tuple]:
    """(service_url_const_or_None, path, mode) triples referenced by the code.

    Sources: api_get/api_post(BASE_URL, "/path"), _get/_post(f"{BASE_URL}/path"),
    "METHOD /path" audit-key literals, and helper calls pairing an HTTP-method
    literal with a path literal (e.g. _endpoint_count(summary, "POST", "/x")).
    mode is "prefix" (strict segment match) or "substring" (tail like "/send"
    is fine), inferred from how the literal is actually consumed.
    """
    helper_modes = _helper_match_semantics(tree)
    # Constants used as `"POST /x" in key` have substring semantics.
    substring_consts = {
        id(operand)
        for node in ast.walk(tree)
        if isinstance(node, ast.Compare) and any(isinstance(op, ast.In) for op in node.ops)
        for operand in [node.left] + list(node.comparators)
        if isinstance(operand, ast.Constant)
    }

    refs: List[tuple] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            fname = node.func.id
            if fname in ("api_get", "api_post") and len(node.args) >= 2:
                const = node.args[0].id if isinstance(node.args[0], ast.Name) else None
                path = _leading_literal_path(node.args[1])
                if path and path.startswith("/"):
                    refs.append((const, path, "prefix"))
                continue
            if fname in ("_get", "_post") and node.args:
                arg = node.args[0]
                if (
                    isinstance(arg, ast.JoinedStr)
                    and len(arg.values) >= 2
                    and isinstance(arg.values[0], ast.FormattedValue)
                    and isinstance(arg.values[0].value, ast.Name)
                    and isinstance(arg.values[1], ast.Constant)
                    and isinstance(arg.values[1].value, str)
                ):
                    lit = arg.values[1].value
                    if len(arg.values) > 2 and not lit.endswith("/"):
                        lit = lit.rsplit("/", 1)[0] + "/"
                    if lit.startswith("/"):
                        refs.append((arg.values[0].value.id, lit, "prefix"))
                continue
            # helper style: any call mixing an HTTP-method literal + path literal
            literals = [
                a.value for a in node.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
            if any(l.upper() in _HTTP_METHODS for l in literals):
                mode = helper_modes.get(fname, "prefix")
                for l in literals:
                    if l.startswith("/"):
                        refs.append((None, l, mode))
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            m = _METHOD_KEY_RE.match(node.value.strip())
            if m:
                mode = "substring" if id(node) in substring_consts else "prefix"
                refs.append((None, m.group(2), mode))
    return refs


def self_validate_tests(
    code: str,
    weights: dict,
    *,
    has_api_services: bool = False,
    distractor_apis: Optional[Iterable[str]] = None,
    service_routes: Optional[dict] = None,
) -> List[str]:
    """Run deterministic lints on generated test code.

    Returns a list of failure strings. Empty list means the draft passes.
    """
    failures: List[str] = []

    # L15: must parse — if not, none of the other lints can run
    try:
        tree = ast.parse(code)
    except SyntaxError as exc:
        return ["L15: emitted code is not valid Python: %s" % exc]

    # L1: forbidden polarity (Convention B)
    seen_polarity: set = set()
    for pat in FORBIDDEN_POLARITY_PATTERNS:
        for m in pat.finditer(code):
            tok = m.group(0)
            if tok not in seen_polarity:
                seen_polarity.add(tok)
                failures.append(
                    "L1: forbidden assertion polarity '%s' — rephrase positively, "
                    "encode bad behavior with a negative weight" % tok
                )

    # L3: lazy substrings
    lazy_pattern = re.compile(r'"([a-z]{2,})"\s+in\s+[A-Za-z_][\w.\[\]]*(?:\.lower\(\))?')
    lazy_hits = []
    for m in lazy_pattern.finditer(code):
        word = m.group(1).lower()
        if word in LAZY_STOPWORDS:
            lazy_hits.append(word)
    if lazy_hits:
        failures.append(
            "L3: lazy single-word substring assertion(s) on common stopwords: %s. "
            "Assert on specific deterministic values instead." % sorted(set(lazy_hits))[:5]
        )

    # L4: weights integrity
    if weights:
        bad = {n: w for n, w in weights.items() if w not in ALLOWED_WEIGHTS}
        if bad:
            failures.append("L4: weight values outside the allowed set {5,3,1,-1,-3,-5}: %s" % bad)

    # L5: class prefix invariants
    class_names = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    bad_classes = [c for c in class_names if not (
        c.startswith("TestBehavioral") or c.startswith("TestOutcome") or c.startswith("TestNegativeWeight")
    )]
    if bad_classes:
        failures.append(
            "L5: class names not matching required prefixes "
            "(TestBehavioral*, TestOutcome*, TestNegativeWeight*): %s" % bad_classes
        )

    # L7: TestNegativeWeight required always
    if not any(c.startswith("TestNegativeWeight") for c in class_names):
        failures.append("L7: no TestNegativeWeight* class emitted — mandatory for every task")

    # L8: at least one SERVICE_URL ref when APIs listed
    if has_api_services and not re.search(r"\b[A-Z][A-Z0-9_]*_URL\b", code):
        failures.append(
            "L8: API services are listed but no <SERVICE>_URL constant is referenced"
        )

    # L12: triviality patterns
    for pat in TRIVIALITY_PATTERNS:
        m = pat.search(code)
        if m:
            failures.append(
                "L12: triviality pattern '%s' — assert on a specific value, not on existence/non-emptiness"
                % m.group(0)
            )
            break

    # L14: every test function must have at least one assert
    test_funcs = collect_test_functions(tree)
    no_assert = [f.name for f in test_funcs if not function_has_assert(f)]
    if no_assert:
        failures.append("L14: test function(s) with NO assert statement: %s" % no_assert)

    # L16: no-op exploit — file_exists-only tests should not exceed 25% of positive weight
    if weights:
        passes_empty = []
        for func in test_funcs:
            if function_passes_empty_files(func):
                passes_empty.append(func.name)
        total_positive = sum(w for w in weights.values() if w > 0)
        passes_empty_positive = sum(
            weights.get(name, 0) for name in passes_empty if weights.get(name, 0) > 0
        )
        if total_positive > 0:
            ratio = passes_empty_positive / total_positive
            if ratio >= 0.25:
                failures.append(
                    "L16: no-op exploit risk — tests that pass on empty files sum to "
                    "%d/%d positive weight (%.0f%%); replace file_exists-only tests with "
                    "content/value assertions: %s" % (
                        passes_empty_positive, total_positive, ratio * 100, passes_empty[:5]
                    )
                )

    # L21: forbidden imports
    forbidden_imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = alias.name.split(".")[0]
                if mod not in ALLOWED_IMPORTS:
                    forbidden_imports.append(mod)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                mod = node.module.split(".")[0]
                if mod not in ALLOWED_IMPORTS:
                    forbidden_imports.append(mod)
    if forbidden_imports:
        failures.append(
            "L21: forbidden import(s) not available in verifier environment: %s. "
            "Only stdlib modules are available." % sorted(set(forbidden_imports))
        )

    # L22: API response shape misuse — iterating api_get/api_post directly
    audit_iter_pattern = re.compile(r"for\s+\w+\s+in\s+(api_get|api_post)\s*\([^)]*\)\s*")
    if audit_iter_pattern.search(code):
        failures.append(
            "L22: potential dict-as-list iteration — code directly iterates the return of "
            "api_get/api_post. Assign to a variable first, unwrap with .get('results', data) "
            "for business endpoints."
        )

    # L24: paginated API response envelope misuse
    if has_api_services:
        api_call_pat = re.compile(r'(\w+)\s*=\s*api_get\s*\([^)]*"/v1/[^"]*"[^)]*\)')
        unwrap_pat = re.compile(r'\.get\s*\(\s*["\']results["\']\s*[,)]')
        paginated_misuse = []
        for match in api_call_pat.finditer(code):
            var_name = match.group(1)
            after = code[match.end():match.end() + 500]
            isinstance_check = re.search(
                r"assert\s+isinstance\s*\(\s*%s\s*,\s*list\s*\)" % re.escape(var_name),
                after,
            )
            if isinstance_check:
                has_unwrap = unwrap_pat.search(code[match.start():match.end() + 500])
                if not has_unwrap:
                    paginated_misuse.append(var_name)
        if paginated_misuse:
            failures.append(
                "L24: paginated API response not unwrapped — %s use "
                "isinstance(var, list) directly on api_get result without handling "
                "the paginated envelope. Use: data.get('results', data) if isinstance(data, dict) "
                "else data" % paginated_misuse[:5]
            )

    # L25: specific-value literal assertions on API response fields
    _STABLE_FIELD_NAMES = {"status", "type", "kind", "method", "media_type", "status_code"}
    literal_assertions = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assert):
            continue
        test = node.test
        if not isinstance(test, ast.Compare):
            continue
        if len(test.ops) != 1 or not isinstance(test.ops[0], (ast.Eq, ast.NotEq)):
            continue
        comparator = test.comparators[0]
        if not isinstance(comparator, ast.Constant):
            continue
        val = comparator.value
        if isinstance(val, bool) or val is None:
            continue
        if isinstance(val, int) and -1 <= val <= 5:
            continue
        left = test.left
        field_name = ""
        if isinstance(left, ast.Subscript) and isinstance(left.slice, ast.Constant):
            field_name = str(left.slice.value).lower()
        if field_name in _STABLE_FIELD_NAMES:
            continue
        if isinstance(val, str) and len(val) > 3:
            literal_assertions.append('"%s"' % (val[:30] + "..." if len(val) > 30 else val))
        elif isinstance(val, float):
            literal_assertions.append(str(val))
        elif isinstance(val, int):
            literal_assertions.append(str(val))

    if len(literal_assertions) > 3:
        failures.append(
            "L25: %d assertions compare API response fields to specific literal values: "
            "%s — these WILL FAIL if mock data differs. Use type/range/presence checks "
            "instead: isinstance(val, str), val > 0, 'key' in obj. Only assert exact "
            "literals for values stated in the task instruction."
            % (len(literal_assertions), ", ".join(literal_assertions[:5]))
        )

    # L26: distractor coverage in TestNegativeWeight*
    if distractor_apis:
        code_lower = code.lower()
        neg_class_methods: set = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name.startswith("TestNegativeWeight"):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                        neg_class_methods.add(item.name.lower())
        neg_code = " ".join(neg_class_methods)
        uncovered = []
        for api in distractor_apis:
            short = api.replace("-api", "").replace("-", "_")
            const = api.upper().replace("-", "_") + "_URL"
            if short not in neg_code and const.lower() not in code_lower:
                uncovered.append(api)
        if uncovered:
            failures.append(
                "L26: missing TestNegativeWeight* coverage for %d distractor API(s): %s "
                "— add at least one negative test per distractor that checks /audit/summary."
                % (len(uncovered), ", ".join(uncovered))
            )

    # L27: endpoint paths must match a served route INCLUDING its full prefix.
    # The audit summary keys requests by the full path (e.g. Mailchimp serves
    # /3.0/lists, so "GET /lists" matches nothing and the test silently no-ops).
    if service_routes:
        all_routes = sorted({r for routes in service_routes.values() for r in routes})
        bad_paths: List[str] = []
        seen_bad: set = set()
        for const, path, mode in _extract_endpoint_refs(tree):
            norm = "/" + "/".join(s for s in path.split("/") if s)
            if norm == "/" or norm.startswith(_SHARED_PLANE_PREFIXES):
                continue
            candidates = service_routes.get(const) if const else None
            if candidates is None:
                if const is not None:
                    continue  # URL constant outside the scoped services — not ours to judge
                candidates = all_routes
            if any(_route_prefix_match(norm, r) for r in candidates):
                continue
            if mode == "substring" and any(norm.lower() in r.lower() for r in candidates):
                continue
            key = (const, norm)
            if key in seen_bad:
                continue
            seen_bad.add(key)
            first_seg = norm.split("/")[1].lower()
            hints = [r for r in candidates if "/%s" % first_seg in r.lower()][:2]
            hint = " (did you mean: %s)" % ", ".join(hints) if hints else ""
            where = " via %s" % const if const else ""
            bad_paths.append("'%s'%s%s" % (norm, where, hint))
        if bad_paths:
            failures.append(
                "L27: endpoint path(s) matching NO served route: %s. Audit summary keys "
                "use the FULL served path — include the API's version/base prefix "
                "(e.g. Mailchimp '/3.0/lists' not '/lists', Salesforce "
                "'/services/data/v59.0/query' not '/query')." % "; ".join(bad_paths[:5])
            )

    return failures
