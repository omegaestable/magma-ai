"""Permanent regression gate for mistakes caught by the spot-check harness.

`stage2/experiments/spotcheck.py` runs randomized cross-source batches and
appends any *mistake* — a wrong verdict, an unsound certificate, or a crash — to
`stage2/fixtures/spotcheck_failures.jsonl`. This test replays every pinned row
so a mistake found once can never silently return: it runs inside
`pytest stage2/tests`, which `package_solver.ps1` requires to pass.

The contract enforced per row is exactly the accuracy contract — the solver must
never *submit* a verdict that contradicts the ground-truth label, and any
certificate it does emit must pass the offline oracles. Skipping a pinned row is
allowed: a skip costs coverage, not correctness, and the point of the gate is to
prevent the solver ever again emitting the *wrong* answer for that row.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import oracles

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1] / "fixtures" / "spotcheck_failures.jsonl"
)


def _load_rows() -> list[dict]:
    if not FIXTURE_PATH.exists():
        return []
    rows = []
    for line in FIXTURE_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


ROWS = _load_rows()


def _row_id(row: dict) -> str:
    return str(row.get("id") or f"{row.get('eq1_id')}_{row.get('eq2_id')}")


@pytest.mark.skipif(not ROWS, reason="no spot-check failures pinned yet")
@pytest.mark.parametrize("row", ROWS, ids=[_row_id(r) for r in ROWS])
def test_spotcheck_regression(solver, row):
    problem = {
        "id": row.get("id"),
        "eq1_id": row.get("eq1_id"),
        "eq2_id": row.get("eq2_id"),
        "equation1": row["equation1"],
        "equation2": row["equation2"],
        "answer": row.get("answer"),
    }
    record = solver.solve_problem(problem, false_time_budget=5.0)

    # A skip is safe: the solver declines to answer, which is never a wrong
    # submission. The regression we guard against is emitting the WRONG verdict.
    if record is None:
        pytest.skip("solver skips this row (safe: no verdict submitted)")

    answer = record["answer"]
    verdict = answer["verdict"]
    label = row.get("answer")
    if isinstance(label, bool):
        expected = "true" if label else "false"
        assert verdict == expected, (
            f"WRONG VERDICT on {_row_id(row)}: label={expected}, "
            f"solver submitted {verdict} via {record.get('route')}")

    # And any certificate it emits must still be sound.
    eq1 = solver.parse_equation(str(problem["equation1"]))
    eq2 = solver.parse_equation(str(problem["equation2"]))
    code = answer["code"]

    if verdict == "false":
        oracles.check_false_certificate(code, eq1, eq2)
    else:
        shape = oracles.classify_true_certificate(code)
        if shape == "exact_expr":
            oracles.check_true_exact_certificate(code, eq1, eq2)
        elif shape == "singleton":
            oracles.check_true_singleton_certificate(code, eq1)
        elif shape == "lemma":
            oracles.check_true_lemma_certificate(code, eq1, eq2)
        extras = [t for _n, t in solver.WITNESS_TABLES]
        extras.extend(t for _r, t in solver.structured_family_tables())
        oracles.model_check_true(
            eq2, oracles.model_battery(eq1, extras, fin3_samples=200, seed=17))
