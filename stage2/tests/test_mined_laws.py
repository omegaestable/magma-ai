"""Gate for the LLM-mined rung laws (`MINED_LEMMA_LIBRARY_TEXT`).

Provenance of the laws themselves: proposed by `gpt-oss-120b` in the 2026-08-27
prompt-protocol probe and then **proved from eq1 by the solver**. They ship as
general universally quantified laws, never as row ids (rail 9); the row ids
below are controls, exactly as the rest of the gate uses them.

What this pins:
  * every mined law parses, and none duplicates one of the 601 entries the
    curated + enumerated library already had (a duplicate would be pure cost);
  * three rows the full solver misses at 420 s/row close through
    `true:egg_ladder:*` at `fast` tier, with a certificate the independent
    offline kernel accepts (positive control, rail 5c);
  * a FALSE row is not claimed TRUE by the widened library (negative control).
"""

from __future__ import annotations

import time

import pytest

import oracles
import solver


# `id` is carried only so a failure names the row; solver policy never sees it.
MINED_POSITIVE_CONTROLS = [
    {
        "id": "etp_3983_3800",
        "eq1_id": 3983,
        "eq2_id": 3800,
        "equation1": "x ◇ y = (y ◇ (z ◇ w)) ◇ x",
        "equation2": "x ◇ y = (z ◇ x) ◇ (w ◇ w)",
    },
    {
        "id": "etp_4453_4652",
        "eq1_id": 4453,
        "eq2_id": 4652,
        "equation1": "x ◇ (y ◇ x) = (z ◇ x) ◇ y",
        "equation2": "(x ◇ y) ◇ x = (z ◇ w) ◇ w",
    },
    {
        "id": "etp_4465_4468",
        "eq1_id": 4465,
        "eq2_id": 4468,
        "equation1": "x ◇ (y ◇ x) = (z ◇ w) ◇ y",
        "equation2": "x ◇ (y ◇ x) = (z ◇ w) ◇ u",
    },
]

# A FALSE row from `hard2`: the widened library must not turn a countermodel row
# into a claimed proof. eq1 has a small nontrivial model, so the mined scan is
# *enabled* here — the negative control exercises the new code, it does not
# dodge it.
MINED_NEGATIVE_CONTROL = {
    "id": "hard2_0001",
    "eq1_id": 4538,
    "eq2_id": 4505,
    "equation1": "x ◇ (y ◇ z) = (y ◇ w) ◇ w",
    "equation2": "x ◇ (y ◇ y) = (z ◇ w) ◇ u",
}


def test_mined_laws_parse_and_are_distinct_from_the_existing_library():
    keys = set()
    for name, text in solver.MINED_LEMMA_LIBRARY_TEXT:
        law = solver.parse_equation(text)
        assert law["lhs"] != law["rhs"], f"{name} is a tautology: {text}"
        key = solver.canonical_law_key(law)
        assert key not in keys, f"{name} duplicates an earlier mined law"
        keys.add(key)
    assert len(keys) == len(solver.MINED_LEMMA_LIBRARY_TEXT)

    prior = set()
    for _name, text in solver.LEMMA_LIBRARY_TEXT:
        prior.add(solver.canonical_law_key(solver.parse_equation(text)))
    for _name, text in solver.enumerated_lemma_library():
        prior.add(solver.canonical_law_key(solver.parse_equation(text)))
    assert not (keys & prior), "mined law already in the 601-entry library"


def test_mined_laws_reach_the_rung_scanner_first():
    """They must sit ahead of the 600 enumerated candidates to be scanned."""
    names = [name for name, _text in solver.full_lemma_library()]
    mined = [i for i, name in enumerate(names) if name.startswith("mined")]
    assert len(mined) == len(solver.MINED_LEMMA_LIBRARY_TEXT)
    assert max(mined) < min(i for i, n in enumerate(names)
                            if n.startswith("enum"))


def test_mined_scan_gate_is_off_only_on_the_order5_collapse_shape():
    """The gate that keeps the extra scan free where it measured 0/80.

    It takes BOTH signals. `order5_17591_11190` is order-5 shaped and has no
    small nontrivial model, so the scan is skipped; `etp_4453_4652` also has no
    small nontrivial model but is order-4 shaped, and the mined laws close it —
    so the model signal alone must NOT switch the scan off.
    """
    order5 = solver.parse_equation("x = (y * z) * (y * (z * (x * z)))")
    assert solver.mined_lemma_scan_is_useful(order5) is False
    order4 = solver.parse_equation("x ◇ (y ◇ x) = (z ◇ x) ◇ y")
    assert solver.mined_lemma_scan_is_useful(order4) is True
    ordinary = solver.parse_equation("a ◇ b = b ◇ a")
    assert solver.mined_lemma_scan_is_useful(ordinary) is True


@pytest.mark.parametrize("problem", MINED_POSITIVE_CONTROLS,
                         ids=lambda p: p["id"])
def test_mined_laws_close_residual_order4_rows(problem):
    """Rows the full solver misses at 420 s/row, closed by a mined rung.

    The route is exercised directly rather than through `solve_problem`: the
    ladder sits near the end of the engine order, so end-to-end these rows only
    reach it after a minute of earlier engines (that path is covered by the
    audit, not by the gate). What this pins is the mechanism — the mined law is
    found as a rung and the resulting `lemma_chain` certificate is accepted by
    the independent offline kernel.
    """
    solver.set_effort("fast")
    solver.set_hard_deadline(None)
    solver.clear_term_caches()
    eq1 = solver.parse_equation(problem["equation1"])
    eq2 = solver.parse_equation(problem["equation2"])
    started = time.monotonic()
    result = solver.egg_ladder_route(eq1, eq2)
    elapsed = time.monotonic() - started
    assert result is not None, f"{problem['id']} no longer closes"
    route, code = result
    assert route.startswith("true:egg_ladder"), route
    # Measured 18-19 s each isolated, 52 s for `etp_3983_3800` under the gate's
    # own `-n 3`. The bound is deliberately far above both: this asserts the
    # ladder does not fall off a cliff, and a wall clock measured under
    # unknown load is not evidence of anything finer (rails 5e, 22).
    assert elapsed < 120.0, f"{problem['id']} took {elapsed:.1f}s"
    oracles.check_no_banned_tactics(code, route)
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)


def test_mined_laws_do_not_claim_a_false_row():
    """Negative control (rail 5c): a FALSE row must not become a TRUE claim.

    `hard2_0001` is order-4 shaped, so the mined scan is enabled on it — this
    exercises the new code rather than dodging it.
    """
    solver.set_effort("fast")
    solver.set_hard_deadline(None)
    solver.clear_term_caches()
    eq1 = solver.parse_equation(MINED_NEGATIVE_CONTROL["equation1"])
    assert solver.mined_lemma_scan_is_useful(eq1) is True
    record = solver.solve_problem(dict(MINED_NEGATIVE_CONTROL),
                                  false_time_budget=5.0)
    assert record is None or record["answer"]["verdict"] == "false", record
