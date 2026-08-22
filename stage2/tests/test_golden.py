"""Golden-route regression gate.

Every entry is a real public problem that the solver currently solves, pinned
to the route that solved it. This catches three regression classes at once:

- coverage loss    (a route stops firing / the row stops being solved)
- route drift      (dispatch order changed, a different route now wins)
- soundness loss   (the emitted certificate stops passing the offline oracles)

Regenerate deliberately with stage2/experiments/make_golden.py after an
intentional change; never hand-edit the fixture.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import oracles

GOLDEN_PATH = Path(__file__).resolve().parent / "golden_routes.json"


def _load_entries() -> list[dict]:
    if not GOLDEN_PATH.exists():
        return []
    return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))["entries"]


ENTRIES = _load_entries()


# The general search engines are interchangeable: each is sound, each is
# wall-clock budgeted, and which one reaches a row first flips under CPU load.
# Observed repeatedly on `evaluation_extra_hard_0139`
# (`absorption_closure` <-> `derived_cp_closure`), which made the pre-package
# gate itself flaky. Collapsing them into one family keeps the gate meaningful
# — coverage loss and soundness loss are still caught by the assertions below —
# without failing on a race. Bespoke routes stay distinct so real drift shows.
#
# This is every engine in `solve_problem`'s general-engine block except
# `narrow_grind`, which is deliberately excluded: it is the demoted route whose
# certificates the offline kernel cannot check, so drifting onto it must fail.
# The egg engines belong here for the same reason the closures do and were
# simply missed when they were added — `evaluation_hard_0028` pins
# `alternating_front_self_collapse`, whose route carries an 0.08 s budget and
# needs 22 ms on an idle machine, so under a loaded 16-way gate it loses the
# race to `egg_collapse` and the row is still solved, still TRUE, still
# oracle-checked. The real fix is step-count rather than wall-clock budgets.
GENERAL_CLOSURE_FAMILIES = {
    "true:absorption_closure",
    "true:absorption_context_bridge",
    "true:equational_closure",
    "true:derived_cp_closure",
    "true:projection_bootstrap",
    "true:lemma_bootstrap",
    "true:lemma_chain",
    "true:egg_closure",
    "true:egg_collapse",
    "true:egg_probe",
    "true:egg_bootstrap",
    "true:egg_priority_bootstrap",
    "true:egg_ladder",
    "true:completion",
}


def route_family(route: str) -> str:
    """Engine identity, ignoring timing-dependent variant suffixes.

    Several routes carry a wall-clock budget, so which variant wins can flip
    under CPU load (`true:absorption_closure` vs `...:deep`, or which witness
    table matches first). That is not a regression: the first two segments
    identify the engine, and correctness is enforced by the oracles below.
    """
    family = ":".join(route.split(":")[:2])
    if family in GENERAL_CLOSURE_FAMILIES:
        return "true:general_closure"
    return family


@pytest.mark.skipif(not ENTRIES, reason="golden fixture not generated yet")
@pytest.mark.parametrize(
    "entry", ENTRIES, ids=[f"{e['route']}:{e['id']}" for e in ENTRIES])
def test_golden_route(solver, entry):
    record = solver.solve_problem(entry["problem"], false_time_budget=5.0)
    assert record is not None, (
        f"coverage regression: {entry['id']} was solved by "
        f"{entry['route']}, now skipped")

    answer = record["answer"]
    assert answer["verdict"] == entry["verdict"], (
        f"verdict flip on {entry['id']}: "
        f"{entry['verdict']} -> {answer['verdict']}")
    got_family = route_family(str(record["route"]))
    want_family = route_family(entry["route"])
    # A bespoke fast path that loses its wall-clock race leaves the row to a
    # general closure engine. The row is still solved and still oracle-checked
    # below, so this is the documented timing nondeterminism, not a regression
    # — and failing the pre-package gate on a coin flip is worse than tolerating
    # it, because it invites `-SkipTests`. Drift in any other direction (onto a
    # different bespoke route, or off a general engine) still fails. The real
    # fix is step-count rather than wall-clock budgets; that is still open.
    lost_race = got_family == "true:general_closure" and want_family != got_family
    assert got_family == want_family or lost_race, (
        f"engine drift on {entry['id']}: "
        f"{entry['route']} -> {record['route']}")

    eq1 = solver.parse_equation(str(entry["problem"]["equation1"]))
    eq2 = solver.parse_equation(str(entry["problem"]["equation2"]))
    code = answer["code"]

    oracles.check_no_banned_tactics(code, str(record["route"]))

    if answer["verdict"] == "false":
        oracles.check_false_certificate(code, eq1, eq2)
    else:
        shape = oracles.classify_true_certificate(code)
        if shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        elif shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
        elif shape == "lemma":
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        elif shape == "lemma_chain":
            oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
        extras = [t for _n, t in solver.WITNESS_TABLES]
        extras.extend(t for _r, t in solver.structured_family_tables())
        oracles.model_check_true(
            eq2, oracles.model_battery(eq1, extras, fin3_samples=200, seed=17))


@pytest.mark.skipif(not ENTRIES, reason="golden fixture not generated yet")
def test_golden_covers_many_routes():
    """Guard against the fixture silently collapsing to a few routes."""
    routes = {e["route"] for e in ENTRIES}
    assert len(routes) >= 20, f"golden fixture only covers {len(routes)} routes"
