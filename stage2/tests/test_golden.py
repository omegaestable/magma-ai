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


def route_family(route: str) -> str:
    """Engine identity, ignoring timing-dependent variant suffixes.

    Several routes carry a wall-clock budget, so which variant wins can flip
    under CPU load (`true:absorption_closure` vs `...:deep`, or which witness
    table matches first). That is not a regression: the first two segments
    identify the engine, and correctness is enforced by the oracles below.
    """
    return ":".join(route.split(":")[:2])


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
    assert route_family(str(record["route"])) == route_family(entry["route"]), (
        f"engine drift on {entry['id']}: "
        f"{entry['route']} -> {record['route']}")

    eq1 = solver.parse_equation(str(entry["problem"]["equation1"]))
    eq2 = solver.parse_equation(str(entry["problem"]["equation2"]))
    code = answer["code"]

    if answer["verdict"] == "false":
        oracles.check_false_certificate(code, eq1, eq2)
    else:
        shape = oracles.classify_true_certificate(code)
        if shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        elif shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
        extras = [t for _n, t in solver.WITNESS_TABLES]
        extras.extend(t for _r, t in solver.structured_family_tables())
        oracles.model_check_true(
            eq2, oracles.model_battery(eq1, extras, fin3_samples=200, seed=17))


@pytest.mark.skipif(not ENTRIES, reason="golden fixture not generated yet")
def test_golden_covers_many_routes():
    """Guard against the fixture silently collapsing to a few routes."""
    routes = {e["route"] for e in ENTRIES}
    assert len(routes) >= 20, f"golden fixture only covers {len(routes)} routes"
