"""Auto-repair truncated Python emitted by the LLM.

Bedrock occasionally cuts off mid-string when hitting max_tokens. Close unbalanced
strings/brackets at EOF so the rest still parses, salvaging the partial draft.

Ported verbatim from kensei2/models/kensei2_sandbox.py (lines 478-579).
"""

from __future__ import annotations

import ast
from typing import Optional


def auto_repair_truncated_python(code: str) -> Optional[str]:
    """Close unbalanced strings/brackets at EOF so truncated LLM output parses.

    Returns repaired code on success, or None if unrepairable.
    """
    if not code:
        return None
    try:
        ast.parse(code)
        return code
    except SyntaxError:
        pass

    pairs = {"(": ")", "[": "]", "{": "}"}

    def _scan(src):
        stack = []
        in_s = False
        trp = False
        q = ""
        start = -1
        i = 0
        n = len(src)
        while i < n:
            ch = src[i]
            if in_s:
                if trp:
                    if src[i:i + 3] == q * 3:
                        in_s = False
                        trp = False
                        i += 3
                        continue
                    i += 1
                    continue
                if ch == "\\" and i + 1 < n:
                    i += 2
                    continue
                if ch == q:
                    in_s = False
                elif ch == "\n":
                    in_s = False
                i += 1
                continue
            if ch == "#":
                while i < n and src[i] != "\n":
                    i += 1
                continue
            if ch in ('"', "'"):
                if src[i:i + 3] in ('"""', "'''"):
                    in_s = True
                    trp = True
                    q = ch
                    start = i
                    i += 3
                    continue
                in_s = True
                trp = False
                q = ch
                start = i
                i += 1
                continue
            if ch in "([{":
                stack.append(pairs[ch])
            elif ch in ")]}":
                if stack and stack[-1] == ch:
                    stack.pop()
            i += 1
        return in_s, trp, q, start, stack

    in_string, triple, quote, str_start, bracket_stack = _scan(code)

    suffix = ""
    if in_string:
        suffix = (quote * 3) if triple else quote
    while bracket_stack:
        suffix += bracket_stack.pop()

    if suffix:
        repaired = code + suffix
        try:
            ast.parse(repaired)
            return repaired
        except SyntaxError:
            pass

    if in_string and str_start >= 0:
        trunc = code[:str_start].rstrip()
        while trunc and trunc[-1] in ", \t\n":
            trunc = trunc[:-1]
        in_s2, _, _, _, stack2 = _scan(trunc)
        if not in_s2:
            suffix2 = ""
            while stack2:
                suffix2 += stack2.pop()
            repaired = trunc + suffix2
            try:
                ast.parse(repaired)
                return repaired
            except SyntaxError:
                pass

    return None
