"""Pacing: the Marathon second deterministic pass, the Solo overtime slot,
the Solo rejected-certificate retry and the speculative Marathon fallback.

Why this file exists at all: neither graded entry point (`run_marathon`,
`run_solo`) had a test that *executed* it, and every pacing bug this repo has
paid for -- the memory-guard reset that scored 287/1000, the per-row deadline
that turned a slow row into `not_attempted` for the whole tail, the tier
inversion -- is a control-flow defect that `audit_corpus.py` structurally
cannot see, because it never runs either entry point.

Everything here drives the real functions with monkeypatched *engines*, so the
pacing arithmetic and the loop structure are what is under test, not the
mathematics.
"""

from __future__ import annotations

import io
import json
import sys
import time

import pytest


# --------------------------------------------------------------------------
# unit pins on the pacing arithmetic
# --------------------------------------------------------------------------

def test_marathon_row_budget_reserves_a_floor_for_every_queued_row(solver):
    """Rail 13: borrowing alone starves the tail, just later."""
    # 1000 s, 100 rows left: the fair share is 10 s, the borrow is 3x that,
    # and the reservation for the 99 rows behind keeps it well inside 1000.
    budget = solver.marathon_row_budget(1000.0, 100)
    assert 0.0 < budget <= 30.0
    assert budget <= 1000.0 - solver.MARATHON_ROW_MIN_SECONDS * 99
    # Last row: it may have everything that is left.
    assert solver.marathon_row_budget(1000.0, 1) == pytest.approx(1000.0)
    # Nothing left still yields the floor rather than a negative budget.
    assert solver.marathon_row_budget(0.0, 10) == pytest.approx(0.0)


def test_marathon_llm_time_reserve_is_zero_when_the_lane_cannot_run(solver):
    assert solver.marathon_llm_time_reserve(300_000.0, False) == 0.0
    assert solver.marathon_llm_time_reserve(0.0, True) == 0.0


def test_marathon_llm_time_reserve_shape(solver):
    """A share of what is left, floored for a few calls, capped at half."""
    big = solver.marathon_llm_time_reserve(300_000.0, True)
    assert big == pytest.approx(solver.MARATHON_LLM_TIME_RESERVE_SHARE * 300_000.0)
    # Small remaining clock: the floor would take everything, so the cap binds
    # and a second pass still gets half.
    small = solver.marathon_llm_time_reserve(600.0, True)
    assert small == pytest.approx(300.0)


def test_marathon_second_pass_row_budget_respects_the_llm_reserve(solver):
    """The reserve comes off the top; only the rest is divided."""
    remaining, reserve = 10_000.0, 2_000.0
    per_row = solver.marathon_second_pass_row_budget(remaining, 20, reserve)
    usable = remaining - reserve
    assert per_row == pytest.approx(
        solver.MARATHON_SECOND_PASS_SHARE * usable / 20)
    # Committing every row's slice must not reach the reserve.
    assert per_row * 20 <= usable
    # The cap binds on a big clock and a small unresolved set.
    assert solver.marathon_second_pass_row_budget(300_000.0, 1, 60_000.0) == \
        pytest.approx(solver.MARATHON_SECOND_PASS_ROW_MAX)
    # A reserve that swallows the clock leaves no second pass at all.
    assert solver.marathon_second_pass_row_budget(100.0, 4, 100.0) == 0.0
    assert solver.marathon_second_pass_row_budget(1000.0, 0, 0.0) == 0.0


def test_marathon_second_pass_tier_is_one_step_up_or_deep(solver):
    assert solver.marathon_second_pass_tier("fast", 10.0) == "standard"
    assert solver.marathon_second_pass_tier("standard", 10.0) == "deep"
    assert solver.marathon_second_pass_tier("deep", 10.0) == "deep"
    # A slice `effort_for_seconds` would already call deep goes straight there.
    assert solver.marathon_second_pass_tier("fast", 240.0) == "deep"


def test_solo_overtime_budget_leaves_a_round_only_when_one_fits(solver):
    # Plenty left: one LLM round's minimum is held back.
    assert solver.solo_overtime_budget(1000.0, 0.0) == pytest.approx(
        1000.0 - solver.SOLO_LLM_ROUND_MIN_SECONDS)
    # A sliver that cannot start a round goes to completion whole.
    assert solver.solo_overtime_budget(230.0, 0.0) == pytest.approx(230.0)
    # The cap binds on a long budget.
    assert solver.solo_overtime_budget(100_000.0, 0.0) == pytest.approx(
        solver.SOLO_OVERTIME_MAX_SECONDS)
    # Past the deadline is zero, never negative.
    assert solver.solo_overtime_budget(0.0, 10.0) == 0.0


def test_solo_deterministic_share_and_llm_timeout_are_the_2026_08_27_values(solver):
    """Pins the two constants this session moved, with their reasons.

    0.55 -> 0.85: the deep deterministic pass is clock-bound (7 of 8 frontier
    rows burn 100% of a 900 s deadline), so the withheld 1,310 s was a real cap
    on deterministic effort handed to a lane measured at 0 accepted / 433 calls.
    300 -> 600 s: the marathon proxy's own `request_timeout_seconds` is 600 and
    it bills the full reservation on the exception path, so a client-side abort
    at 300 s spends the tokens and returns nothing.
    """
    assert solver.SOLO_DETERMINISTIC_SHARE == 0.85
    assert solver.LLM_HTTP_TIMEOUT_SECONDS == 600.0
    assert solver.LLM_CONFIG["http_timeout_seconds"] == 600.0


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

ROWS = [
    {"id": f"row_{i:02d}", "eq1_id": 8 + i, "eq2_id": 100 + i,
     "equation1": "x ◇ y = x", "equation2": "x ◇ (y ◇ z) = x"}
    for i in range(12)
]

SOLO_ROW = {"id": "solo_0001", "eq1_id": 8, "eq2_id": 23,
            "equation1": "x ◇ y = x", "equation2": "x ◇ (y ◇ z) = x"}


class ScriptedProxy:
    """Stands in for the Solo proxy (see the diagnosis prototype)."""

    def __init__(self, judge_statuses, llm_texts=()):
        self.judge_statuses = list(judge_statuses)
        self.llm_texts = list(llm_texts)
        self.calls: list[dict] = []

    def send(self, message):
        self.calls.append(message)
        if message.get("call") == "judge":
            status = self.judge_statuses.pop(0) if self.judge_statuses else "incorrect"
            return {"status": status, "stderr": "scripted"}
        if message.get("call") == "llm":
            if not self.llm_texts:
                return {"error": "no more scripted llm responses"}
            return {"response": self.llm_texts.pop(0)}
        return None

    @property
    def judge_calls(self):
        return [c for c in self.calls if c.get("call") == "judge"]

    @property
    def llm_calls(self):
        return [c for c in self.calls if c.get("call") == "llm"]


@pytest.fixture
def clean_solver_state(solver):
    """Restore every module-level global these entry points move."""
    saved = (solver._EFFORT, solver._HARD_DEADLINE, solver._PROCESS_START,
             dict(solver._MARATHON_ROW_EVIDENCE))
    solver.reset_solo_retry_state()
    solver._MARATHON_ROW_EVIDENCE.clear()
    try:
        yield solver
    finally:
        solver.set_effort(saved[0])
        solver.set_hard_deadline(saved[1])
        solver._PROCESS_START = saved[2]
        solver._MARATHON_ROW_EVIDENCE.clear()
        solver._MARATHON_ROW_EVIDENCE.update(saved[3])
        solver.reset_solo_retry_state()
        solver.reset_hypothesis_model_count()


def _stderr_records(captured: str) -> list[dict]:
    records = []
    for line in captured.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


# --------------------------------------------------------------------------
# Marathon: second pass + speculative fallback
# --------------------------------------------------------------------------

def _run_marathon(solver, tmp_path, monkeypatch, fake_solve, *,
                  budget_seconds=3600.0, budget_tokens=0, lib_dir=None):
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in ROWS) + "\n",
        encoding="utf-8")
    output = tmp_path / "answers.jsonl"
    monkeypatch.setenv("JUDGE_MARATHON_MANIFEST", str(manifest))
    monkeypatch.setenv("JUDGE_MARATHON_OUTPUT", str(output))
    monkeypatch.setenv("JUDGE_MARATHON_BUDGET_SECONDS", str(budget_seconds))
    monkeypatch.setenv("JUDGE_MARATHON_BUDGET_TOKENS", str(budget_tokens))
    if lib_dir is None:
        monkeypatch.delenv("JUDGE_MARATHON_LIB_DIR", raising=False)
    else:
        monkeypatch.setenv("JUDGE_MARATHON_LIB_DIR", str(lib_dir))
    monkeypatch.setattr(solver, "solve_problem", fake_solve)
    assert solver.run_marathon() == 0
    if not output.exists():
        return []
    lines = [json.loads(line) for line in
             output.read_text(encoding="utf-8").splitlines() if line.strip()]
    return lines


def test_marathon_second_pass_closes_rows_the_first_pass_missed(
        solver, tmp_path, monkeypatch, capsys, clean_solver_state):
    """12 rows: 6 close on pass 1, 4 only on pass 2, 2 never.

    Of the two that never close, exactly one leaves FALSE-search evidence
    (`models_seen > 0`), so exactly one speculative fallback line is written.
    """
    easy = {row["id"] for row in ROWS[:6]}
    hard = {row["id"] for row in ROWS[6:10]}
    with_evidence = ROWS[10]["id"]
    calls: list[tuple[str, str, float | None]] = []
    seen: dict[str, int] = {}

    def fake_solve(problem, *, false_time_budget=None):
        pid = str(problem.get("id"))
        calls.append((pid, solver.effort_tier(), solver._HARD_DEADLINE))
        seen[pid] = seen.get(pid, 0) + 1
        solver.reset_hypothesis_model_count()
        if pid in easy:
            return {"answer": solver.make_true_answer(
                problem, solver.fallback_true_certificate()),
                "route": "true:fake_first", "priority": (0, 0, "t")}
        if pid in hard and seen[pid] >= 2:
            return {"answer": solver.make_true_answer(
                problem, solver.fallback_true_certificate()),
                "route": "true:fake_second", "priority": (0, 0, "t")}
        if pid == with_evidence:
            solver.note_hypothesis_model()
        return None

    lines = _run_marathon(solver, tmp_path, monkeypatch, fake_solve)
    records = _stderr_records(capsys.readouterr().err)

    ids = [line["id"] for line in lines]
    assert len(ids) == len(set(ids)), f"duplicate answer ids: {ids}"
    # 6 easy + 4 second-pass + 1 speculative.
    assert set(ids) == easy | hard | {with_evidence}
    assert len(ids) == 11

    second = [r for r in records
              if str(r.get("route", "")).startswith("second_pass:")
              and "solved_route" in r]
    assert {r["id"] for r in second} == hard
    assert all(r["solved_route"] == "true:fake_second" for r in second)

    # Pass 2 ran one tier above pass 1 and every row of it was deadline-bound.
    first_tier = solver.effort_for_seconds(0.5 * 3600.0 / len(ROWS))
    assert first_tier in ("fast", "standard")
    # Every call in either pass ran under a real per-row deadline (rail 13).
    assert all(deadline is not None for _pid, _tier, deadline in calls)
    # `solve_problem` walks `effort_ladder_to`, so a pass-2 call reports the
    # tier the pass SET, and that tier is above pass 1's.
    pass1_tiers = [tier for pid, tier, _ in calls[:len(ROWS)]]
    pass2_tiers = [tier for pid, tier, _ in calls[len(ROWS):]]
    assert set(pass1_tiers) == {first_tier}
    assert pass2_tiers and set(pass2_tiers) == {"deep"}
    second_tier_labels = {str(r["route"]).split(":", 1)[1] for r in second}
    assert second_tier_labels == {"deep"}

    # Speculative fallback: only the row with model evidence.
    grind = [r for r in records if r.get("route") == "fallback:marathon_grind"
             and "id" in r]
    assert [r["id"] for r in grind] == [with_evidence]
    done = [r for r in records if r.get("route") == "fallback:marathon_grind"
            and r.get("event") == "done"]
    assert done and done[0]["submitted"] == 1
    assert done[0]["skipped_no_model_evidence"] == 1

    # The evidence dict is keyed by id and holds the tuple the LLM lane reads.
    assert solver._MARATHON_ROW_EVIDENCE.get(with_evidence, (0, False))[0] > 0
    assert solver._MARATHON_ROW_EVIDENCE.get(ROWS[11]["id"], (0, False))[0] == 0

    # The tier is handed back, so nothing downstream inherits pass 2's.
    assert solver.effort_tier() == first_tier


def test_marathon_second_pass_never_re_attempts_a_solved_row(
        solver, tmp_path, monkeypatch, capsys, clean_solver_state):
    """A row answered in pass 1 must not be touched again: the scorer keeps the
    LAST write for an id, so a second line could only destroy an acceptance."""
    solved_once = {row["id"] for row in ROWS[:10]}
    calls: list[str] = []

    def fake_solve(problem, *, false_time_budget=None):
        pid = str(problem.get("id"))
        calls.append(pid)
        solver.reset_hypothesis_model_count()
        if pid in solved_once:
            return {"answer": solver.make_true_answer(
                problem, solver.fallback_true_certificate()),
                "route": "true:fake_first", "priority": (0, 0, "t")}
        return None

    lines = _run_marathon(solver, tmp_path, monkeypatch, fake_solve)
    capsys.readouterr()
    assert len(lines) == 10
    assert len({line["id"] for line in lines}) == 10
    for pid in solved_once:
        assert calls.count(pid) == 1, f"{pid} was re-attempted after solving"
    for pid in {row["id"] for row in ROWS[10:]}:
        assert calls.count(pid) == 2, f"{pid} missed its second pass"


def test_marathon_second_pass_leaves_the_llm_reserve(
        solver, tmp_path, monkeypatch, capsys, clean_solver_state):
    """With the lane possible, the pass reserves clock instead of taking all."""
    def fake_solve(problem, *, false_time_budget=None):
        solver.reset_hypothesis_model_count()
        return None

    lib_dir = tmp_path / "lib"
    lib_dir.mkdir()
    _run_marathon(solver, tmp_path, monkeypatch, fake_solve,
                  budget_tokens=100_000, lib_dir=lib_dir)
    records = _stderr_records(capsys.readouterr().err)
    starts = [r for r in records if r.get("event") == "start"
              and str(r.get("route", "")).startswith("second_pass:")]
    assert starts, "second pass logged no start record"
    start = starts[0]
    assert start["llm_reserve_seconds"] > 0.0
    assert start["unresolved"] == len(ROWS)
    # Every row's slice together must fit inside what is not reserved.
    assert (start["row_budget_seconds"] * start["unresolved"]
            <= start["remaining_seconds"] - start["llm_reserve_seconds"] + 1.0)


def test_marathon_second_pass_is_skipped_when_no_clock_remains(
        solver, tmp_path, monkeypatch, capsys, clean_solver_state):
    """A tiny budget must not produce a pass with a meaningless slice."""
    def fake_solve(problem, *, false_time_budget=None):
        solver.reset_hypothesis_model_count()
        return None

    _run_marathon(solver, tmp_path, monkeypatch, fake_solve, budget_seconds=6.0)
    records = _stderr_records(capsys.readouterr().err)
    solved_rows = [r for r in records if "solved_route" in r]
    assert not solved_rows


# --------------------------------------------------------------------------
# Solo: overtime slot and rejected-certificate retry
# --------------------------------------------------------------------------

def _run_solo(solver, monkeypatch, proxy, problem, *, budget=3600.0, rounds=0):
    monkeypatch.setattr(solver, "send_proxy_call", proxy.send)
    monkeypatch.setenv("MAGMA_SOLO_LLM_ROUNDS", str(rounds))
    monkeypatch.setattr(
        sys, "stdin",
        io.StringIO(json.dumps({"type": "start", "problem": problem,
                                "budget": {"timeout_seconds": budget}},
                               ensure_ascii=False) + "\n"))
    solver._PROCESS_START = time.monotonic()
    assert solver.run_solo() == 0


def test_solo_overtime_completion_runs_exactly_once_on_an_unsolved_row(
        solver, monkeypatch, capsys, clean_solver_state):
    """SOLO-1/SOLO-2: one escalated completion call between the deterministic
    pass and the LLM lane, with a real budget and `escalate=True`."""
    seen: list[dict] = []

    def fake_solve(problem, *, false_time_budget=None):
        solver.reset_hypothesis_model_count()
        return None

    def fake_completion(eq1, eq2, *, time_budget, bridge=True, escalate=False):
        seen.append({"time_budget": time_budget, "escalate": escalate})
        # Deliberately NOT the reflexive certificate: the insurance call has
        # already banked that exact text, and `attempted` dedupes by (verdict,
        # code), so an identical cert would be silently dropped.
        return ("true:completion:join",
                solver.grind_true_certificate(["x", "y", "z"]))

    monkeypatch.setattr(solver, "solve_problem", fake_solve)
    monkeypatch.setattr(solver, "completion_prove", fake_completion)
    proxy = ScriptedProxy(["incorrect", "accepted"])
    _run_solo(solver, monkeypatch, proxy, SOLO_ROW)
    capsys.readouterr()

    assert len(seen) == 1, f"overtime ran {len(seen)} times"
    assert seen[0]["escalate"] is True
    assert seen[0]["time_budget"] == pytest.approx(
        solver.SOLO_OVERTIME_MAX_SECONDS, abs=5.0)
    # Judge calls: the insurance reflexive cert, then the overtime certificate.
    assert len(proxy.judge_calls) == 2
    for body in proxy.judge_calls:
        assert set(body) == {"call", "verdict", "code"}   # rail 8


def test_solo_overtime_is_not_run_when_the_deterministic_pass_answered(
        solver, monkeypatch, capsys, clean_solver_state):
    """It is additive by construction: it may never displace an engine."""
    seen: list[float] = []

    def fake_solve(problem, *, false_time_budget=None):
        solver.reset_hypothesis_model_count()
        return {"answer": solver.make_true_answer(
            problem, solver.fallback_true_certificate()),
            "route": "true:fake", "priority": (0, 0, "t")}

    def fake_completion(eq1, eq2, *, time_budget, bridge=True, escalate=False):
        seen.append(time_budget)
        return None

    monkeypatch.setattr(solver, "solve_problem", fake_solve)
    monkeypatch.setattr(solver, "completion_prove", fake_completion)
    proxy = ScriptedProxy(["accepted"])
    _run_solo(solver, monkeypatch, proxy, SOLO_ROW)
    capsys.readouterr()
    assert seen == []
    assert len(proxy.judge_calls) == 1


def test_solo_retries_a_rejected_false_witness_with_a_different_table(
        solver, monkeypatch, capsys, clean_solver_state):
    """SOLO-5: the second judge call must carry DIFFERENT code, and the exact
    rejected table must be barred from every witness gate afterwards."""
    first = [[0, 0], [0, 0]]
    second = [[0, 1], [1, 0]]
    calls: list[int] = []

    def fake_solve(problem, *, false_time_budget=None):
        calls.append(1)
        solver.reset_hypothesis_model_count()
        table = first if len(calls) == 1 else second
        return {
            "answer": solver.make_false_answer(problem, 2, table),
            "route": "false:fake", "priority": (0, 0, "f"),
            "order": 2, "table": table,
        }

    monkeypatch.setattr(solver, "solve_problem", fake_solve)
    proxy = ScriptedProxy(["incorrect", "accepted"])
    _run_solo(solver, monkeypatch, proxy, SOLO_ROW)
    capsys.readouterr()

    assert len(calls) == 2, "no retry after a rejected certificate"
    assert len(proxy.judge_calls) == 2
    assert proxy.judge_calls[0]["code"] != proxy.judge_calls[1]["code"]
    assert solver.witness_table_rejected(first)
    assert not solver.witness_table_rejected(second)


def test_solo_retry_of_a_rejected_true_certificate_excludes_its_route(
        solver, monkeypatch, capsys, clean_solver_state):
    """A TRUE rejection has no table to bar, so the ROUTE is excluded and
    `solve_problem_pass` falls through to the next candidate."""
    calls: list[int] = []

    def fake_solve(problem, *, false_time_budget=None):
        calls.append(1)
        solver.reset_hypothesis_model_count()
        if len(calls) == 1:
            return {"answer": solver.make_true_answer(
                problem, solver.fallback_true_certificate()),
                "route": "true:first_route", "priority": (0, 0, "t")}
        return {"answer": solver.make_true_answer(
            problem, solver.grind_true_certificate(["x", "y", "z"])),
            "route": "true:second_route", "priority": (0, 0, "t")}

    monkeypatch.setattr(solver, "solve_problem", fake_solve)
    proxy = ScriptedProxy(["incorrect", "accepted"])
    _run_solo(solver, monkeypatch, proxy, SOLO_ROW)
    capsys.readouterr()

    assert len(calls) == 2
    assert solver.route_excluded("true:first_route")
    assert proxy.judge_calls[0]["code"] != proxy.judge_calls[1]["code"]


def test_excluded_route_makes_solve_problem_pass_fall_through(
        solver, clean_solver_state):
    """The exclusion is consulted where an alternative exists, and it changes
    the answer rather than suppressing it (rail 1: never lose a row)."""
    problem = dict(SOLO_ROW)
    baseline = solver.solve_problem(problem)
    assert baseline is not None
    solver.exclude_route(str(baseline["route"]))
    alternative = solver.solve_problem(problem)
    if alternative is not None:
        assert alternative["route"] != baseline["route"]


def test_rejected_witness_table_is_barred_from_both_witness_gates(
        solver, clean_solver_state):
    """`table_is_counterexample` and `witness_check` are twins; a bar that only
    reached one of them would be invisible on whichever portfolio used the
    other (rail 5f-v)."""
    eq1 = solver.parse_equation("x ◇ y = x")
    eq2 = solver.parse_equation("x ◇ y = y")
    table = [[0, 0], [1, 1]]
    assert solver.table_is_counterexample(eq1, eq2, table)
    assert solver.witness_check(eq1, eq2, table)
    solver.note_rejected_witness_table(table)
    assert not solver.table_is_counterexample(eq1, eq2, table)
    assert not solver.witness_check(eq1, eq2, table)
    # The bar must not cost the hypothesis-model evidence rail 5 depends on.
    solver.reset_hypothesis_model_count()
    solver.witness_check(eq1, eq2, table)
    assert solver.hypothesis_models_seen() == 1
    solver.reset_solo_retry_state()
    assert solver.table_is_counterexample(eq1, eq2, table)


def test_solver_analysis_suppresses_very_likely_true_after_a_false_rejection(
        solver):
    """SOLO-5's second half: the 'very likely TRUE' cue is actively wrong when
    the search DID find a countermodel and only its rendering was rejected."""
    default = solver.solver_analysis(SOLO_ROW)
    assert "very likely TRUE" in default
    after_false = solver.solver_analysis(SOLO_ROW, rejected_verdict="false")
    assert "very likely TRUE" not in after_false
    assert "REJECTED" in after_false
    after_true = solver.solver_analysis(SOLO_ROW, rejected_verdict="true")
    assert "very likely TRUE" not in after_true


def test_marathon_row_evidence_is_the_name_the_llm_lane_reads(solver):
    """Pinned by name: another lane reads this dict defensively with `.get`."""
    assert isinstance(solver._MARATHON_ROW_EVIDENCE, dict)
    assert callable(solver.note_marathon_row_evidence)


def test_pacing_helpers_make_no_proxy_calls(solver):
    """Rail: stdin/stdout proxy traffic stays inside `run_solo`. The new
    helpers are called from it, so they must not carry the traffic themselves
    (`test_no_judge_call_outside_solo` scans for this too; this is the local
    statement of the same contract)."""
    import ast
    import inspect

    for name in ("solo_overtime_completion", "solo_retry_record",
                 "solo_overtime_budget", "note_marathon_row_evidence",
                 "marathon_second_pass_row_budget", "marathon_llm_time_reserve"):
        source = inspect.getsource(getattr(solver, name))
        tree = ast.parse(source)
        called = {node.func.id for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)}
        assert not called & {"judge_via_solo_proxy", "send_proxy_call",
                             "load_json_line"}, name
