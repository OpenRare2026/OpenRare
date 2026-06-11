#!/usr/bin/env python3
"""
Narrative anti-hallucination guard.

The deterministic blocks (rendered by build_context.py) are the ground truth.
A narrative paragraph written by the model is only allowed to *reference* numbers
and IDs that already appear in that slot's ``ground_text``. This module scans a
narrative for "hard" tokens and reports any that are not grounded, so the service
can reject / regenerate / strip before showing the text to the user.

What counts as a *hard* token (must be grounded):
  - IDs:         OMIM:123456, MONDO:0009926, ORPHA:2990, HP:0001324
  - HGVS:        c.1799T>A, p.Val600Glu, p.Ser290=
  - decimals / scientific:  0.634, 1.7e-05, 32.0  (scores, frequencies)
  - long integers (>= 4 digits):  233309256  (coordinates / numeric IDs)
Small bare integers (ranks, counts, ordinals like "3 个变异", "第 2 位") are NOT
flagged, to avoid false positives on ordinary prose.

Grounding test:
  - IDs / HGVS / long ints: case-insensitive substring of ground_text.
  - decimals: equal to some number in ground_text within relative tolerance,
    OR exact substring (handles rounded restatements like 0.634138 -> 0.634).

This is a guardrail, not a proof. It reliably catches an invented frequency,
OMIM id, or score; it is deliberately lenient on small counts.
"""
from __future__ import annotations
import re
from typing import List

ID_RE   = re.compile(r"\b(?:OMIM|MONDO|ORPHA|HP|HGNC)\s*:\s*\d+\b", re.I)
HGVS_RE = re.compile(r"\b[cpgmn]\.[A-Za-z0-9_>+\-*=()]+", re.I)
NUM_RE  = re.compile(r"(?<![\w.])[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?(?![\w])")

NUM_IN_GROUND = re.compile(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?")


def _floats(text: str) -> List[float]:
    out = []
    for m in NUM_IN_GROUND.finditer(text):
        try:
            out.append(float(m.group()))
        except ValueError:
            pass
    return out


def _num_grounded(token: str, ground_text: str, ground_floats: List[float],
                  rel_tol: float = 1e-2) -> bool:
    if token in ground_text:                      # exact substring, fast path
        return True
    try:
        v = float(token)
    except ValueError:
        return False
    for g in ground_floats:
        if g == v:
            return True
        denom = max(abs(g), abs(v), 1e-12)
        if abs(g - v) / denom <= rel_tol:
            return True
    return False


def find_violations(narrative: str, ground_text: str) -> List[str]:
    """Return the list of hard tokens in `narrative` not supported by `ground_text`."""
    gl = ground_text or ""
    gl_low = gl.lower()
    gfloats = _floats(gl)
    violations: List[str] = []

    # mask out ID / HGVS spans first so their digits aren't re-scanned as numbers
    masked = narrative
    for rex in (ID_RE, HGVS_RE):
        for m in rex.finditer(narrative):
            tok = m.group().strip()
            if tok.lower().replace(" ", "") not in gl_low.replace(" ", ""):
                violations.append(tok)
        masked = rex.sub(" ", masked)

    for m in NUM_RE.finditer(masked):
        tok = m.group()
        is_decimal = ("." in tok) or ("e" in tok.lower())
        digits = re.sub(r"\D", "", tok)
        if not (is_decimal or len(digits) >= 4):
            continue                                  # benign small integer
        if not _num_grounded(tok, gl, gfloats):
            violations.append(tok)

    # de-dup, preserve order
    seen, uniq = set(), []
    for v in violations:
        if v not in seen:
            seen.add(v); uniq.append(v)
    return uniq


def is_grounded(narrative: str, ground_text: str) -> bool:
    return not find_violations(narrative, ground_text)


if __name__ == "__main__":
    # tiny self-test
    ground = ("| 1 | p.Val600Glu | missense_variant | HIGH | 0.9 | 32 | 1.93e-04 | "
              "Likely pathogenic |\nOMIM:265000 / MONDO:0009926  gene_score 0.634138")
    good = "该基因顶层变异 p.Val600Glu 为 missense，CADD 32，gnomAD popmax 1.93e-04，较罕见；表型分 0.634 中等。"
    bad  = "该变异 gnomAD 频率约 0.012，对应 OMIM:999999，REVEL 0.88。"
    print("good ->", find_violations(good, ground))   # expect []
    print("bad  ->", find_violations(bad, ground))     # expect 0.012, OMIM:999999, 0.88
