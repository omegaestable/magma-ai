"""Rail 10 as a test: the memory guard's reclaim budget is per row, not per run.

`_mem_reclaims_left` only ever decrements. It used to be set once at import and
never reset inside `run_marathon`'s loop, so three memory-guard trips anywhere
in a manifest failed `_engine_gate()` closed for every remaining problem: a real
Marathon on `normal.jsonl` scored **287/1000** against an offline ceiling of
989/1000, with 0 rejected - pure coverage loss. It is invisible to
`audit_corpus.py` (which never arms the guard) and to Solo (a fresh subprocess
per problem resets everything for free), so only a long single-process Marathon
run exposed it. This is the cheap detector that was missing.

The test deliberately assumes only two things about the deterministic pass, so
it survives a second pass being added to it: every row is attempted at least
once, and the counter is at its armed value before each `solve_problem` call.
"""

from __future__ import annotations

import json

import pytest

DIAMOND = "◇"

ROWS = [
    {"id": f"guard_{index:02d}", "eq1_id": 8, "eq2_id": 23,
     "equation1": "x = y " + DIAMOND + " x",
     "equation2": "x " + DIAMOND + " (y " + DIAMOND + " z) = x"}
    for index in range(10)
]


@pytest.fixture
def marathon(solver, monkeypatch, tmp_path):
    saved_effort = solver.effort_tier()

    def run(on_row, *, budget_seconds="300"):
        manifest = tmp_path / "manifest.jsonl"
        manifest.write_text(
            "\n".join(json.dumps(row) for row in ROWS) + "\n", encoding="utf-8")
        output = tmp_path / "answers.jsonl"
        monkeypatch.setenv("JUDGE_MARATHON_MANIFEST", str(manifest))
        monkeypatch.setenv("JUDGE_MARATHON_OUTPUT", str(output))
        monkeypatch.setenv("JUDGE_MARATHON_BUDGET_SECONDS", budget_seconds)
        monkeypatch.setenv("JUDGE_MARATHON_BUDGET_TOKENS", "0")
        monkeypatch.setattr(solver, "solve_problem", on_row)
        assert solver.run_marathon() == 0
        return output

    yield run
    solver.set_effort(saved_effort)
    solver.set_hard_deadline(None)
    solver.arm_memory_guard(False)
    solver.reset_memory_reclaims()


def _armed_value(solver) -> int:
    solver.reset_memory_reclaims()
    return solver._mem_reclaims_left


def test_the_reclaim_budget_is_reset_before_every_row(solver, marathon):
    armed = _armed_value(solver)
    assert armed > 0, "reset_memory_reclaims() no longer arms a positive budget"
    seen: list[tuple[str, int]] = []

    def on_row(problem, **_kwargs):
        # Record what the row inherited, then spend the whole budget the way a
        # memory-guard trip would. Without a per-row reset the next row starts
        # at 0 and `_engine_gate()` fails closed for the rest of the manifest.
        seen.append((str(problem.get("id")), solver._mem_reclaims_left))
        solver._mem_reclaims_left = 0
        return None

    marathon(on_row)

    attempted = {row_id for row_id, _left in seen}
    assert attempted == {row["id"] for row in ROWS}, (
        f"not every row was attempted: missing {sorted({r['id'] for r in ROWS} - attempted)}")
    starved = [(row_id, left) for row_id, left in seen if left != armed]
    assert not starved, (
        f"rows started with a spent reclaim budget: {starved[:5]} - this is "
        "rail 10, the defect that scored 287/1000 on a real Marathon")


def test_every_solved_row_is_written_exactly_once_with_the_marathon_payload(
        solver, marathon):
    """Rail 8, Marathon shape: `{id, verdict, code}` and nothing else."""

    def on_row(problem, **_kwargs):
        code = solver.false_certificate(2, [[0, 1], [0, 1]])
        return {"answer": {"id": str(problem.get("id")), "verdict": "false",
                           "code": code},
                "route": "test:scripted"}

    output = marathon(on_row)
    lines = [json.loads(line) for line in
             output.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert {line["id"] for line in lines} == {row["id"] for row in ROWS}
    for line in lines:
        assert set(line) == {"id", "verdict", "code"}, sorted(line)


def test_a_crashing_row_does_not_kill_the_manifest(solver, marathon):
    """Rail 11: the per-row try/except wraps the whole iteration."""
    calls: list[str] = []

    def on_row(problem, **_kwargs):
        row_id = str(problem.get("id"))
        calls.append(row_id)
        if row_id.endswith("3"):
            raise RuntimeError("scripted row failure")
        return None

    marathon(on_row)
    assert set(calls) == {row["id"] for row in ROWS}, (
        "one raising row stopped the manifest: " + str(sorted(set(calls))))
