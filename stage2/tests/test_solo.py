"""`run_solo` driven end to end against a scripted proxy.

Solo is one of the two graded entry points and nothing in the gate executed it
before this file (TEST-1): the only prior mention of `run_solo` was a static AST
scan. `audit_corpus.py` does not run it either, so the whole class of bug that
scored 287/1000 in Marathon - a control-flow defect in the entry point, not in
an engine - had no local detector on the Solo side.

The harness replaces `solver.send_proxy_call` with a scripted stand-in and
feeds the start message through `sys.stdin`, which is exactly the surface the
official `pipeline/proxy.py` presents.
"""

from __future__ import annotations

import io
import json
import sys
import time

import pytest

DIAMOND = "◇"

# A row the deterministic pass refutes instantly with a named 2-element witness.
EASY_FALSE_ROW = {
    "id": "solo_easy", "eq1_id": 8, "eq2_id": 23,
    "equation1": "x = y " + DIAMOND + " x",
    "equation2": "x " + DIAMOND + " (y " + DIAMOND + " z) = x",
}


class ScriptedProxy:
    """Records the solver's calls and replies from a script."""

    def __init__(self, judge_statuses, llm_texts):
        self.judge_statuses = list(judge_statuses)
        self.llm_texts = list(llm_texts)
        self.calls: list[dict] = []
        self.contexts: list[dict] = []

    def __call__(self, message):
        self.calls.append(message)
        if message.get("call") == "judge":
            status = self.judge_statuses.pop(0) if self.judge_statuses else "incorrect"
            return {"status": status, "stderr": "scripted"}
        if message.get("call") == "llm":
            self.contexts.append(dict(message.get("context") or {}))
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

    @property
    def kinds(self):
        return [str(c.get("call")) for c in self.calls]


@pytest.fixture
def solo(solver, monkeypatch):
    """Run `run_solo` with a scripted proxy, and put the module back afterwards."""
    saved_effort = solver.effort_tier()

    def run(problem, *, budget=3600.0, judge_statuses=(), llm_texts=(),
            rounds=None, env=None):
        proxy = ScriptedProxy(judge_statuses, llm_texts)
        monkeypatch.setattr(solver, "send_proxy_call", proxy)
        start = {"type": "start", "problem": problem,
                 "budget": {"timeout_seconds": budget}} if budget is not None else {
                     "type": "start", "problem": problem}
        monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(start) + "\n"))
        if rounds is not None:
            monkeypatch.setenv("MAGMA_SOLO_LLM_ROUNDS", str(rounds))
        for key, value in (env or {}).items():
            monkeypatch.setenv(key, value)
        monkeypatch.setattr(solver, "_PROCESS_START", time.monotonic())
        assert solver.run_solo() == 0
        return proxy

    yield run
    solver.set_effort(saved_effort)
    solver.set_hard_deadline(None)
    solver.arm_memory_guard(False)


# ---------------------------------------------------------------------------
# TEST-1: the protocol itself
# ---------------------------------------------------------------------------

def test_accepted_deterministic_certificate_stops_after_one_judge_call(solo):
    proxy = solo(EASY_FALSE_ROW, judge_statuses=["accepted"])
    assert len(proxy.judge_calls) == 1, proxy.kinds
    assert len(proxy.llm_calls) == 0, proxy.kinds


def test_judge_payload_is_exactly_call_verdict_code(solo):
    """Rail 8: route labels go to stderr, never into the payload."""
    proxy = solo(EASY_FALSE_ROW, judge_statuses=["accepted"])
    body = proxy.judge_calls[0]
    assert set(body) == {"call", "verdict", "code"}, sorted(body)
    assert body["verdict"] in ("true", "false")
    assert isinstance(body["code"], str) and body["code"].strip()


def test_the_start_message_budget_beats_the_environment_variable(solver, solo):
    """The proxy's `budget.timeout_seconds` is the real clock; the env var is
    the local-testing fallback, so a small env value must not shrink the tier."""
    solo(EASY_FALSE_ROW, budget=3600.0, judge_statuses=["accepted"],
         env={"JUDGE_SOLO_BUDGET_SECONDS": "60"})
    assert solver.effort_tier() == solver.effort_for_seconds(3600.0)
    assert solver.effort_tier() == "deep"


def test_the_environment_variable_is_used_when_the_message_carries_no_budget(solver, solo):
    solo(EASY_FALSE_ROW, budget=None, judge_statuses=["accepted"],
         env={"JUDGE_SOLO_BUDGET_SECONDS": "60"})
    assert solver.effort_tier() == solver.effort_for_seconds(60.0)


# ---------------------------------------------------------------------------
# SOLO-4: no insurance judge call before the first LLM round
# ---------------------------------------------------------------------------

def _unsolvable(solver, monkeypatch, *, models_seen=0):
    """Make the deterministic pass return nothing, cheaply and deterministically."""
    monkeypatch.setattr(solver, "solve_problem", lambda *a, **k: None)
    monkeypatch.setattr(solver, "solver_analysis", lambda problem, **kwargs: "scripted analysis")
    monkeypatch.setattr(solver, "hypothesis_models_seen", lambda: models_seen)


def test_no_judge_call_precedes_the_first_llm_call_on_an_unsolved_row(
        solver, monkeypatch, solo):
    """SOLO-4. The insurance `exact h` certificate is gone.

    It could never be `accepted` (`pipeline/runner.py` scores only `solved`,
    which `proxy.py` sets on `accepted` alone), it cost 1.0-2.8 s of real Lean,
    and `proxy.py` rendered it into `{history.attempts}` - so round 0, the most
    valuable prompt of the row, opened with a guaranteed-failing attempt and its
    type-mismatch error.
    """
    _unsolvable(solver, monkeypatch)
    proxy = solo(EASY_FALSE_ROW, rounds=1, llm_texts=["not json at all"])
    assert proxy.kinds, "run_solo made no proxy calls at all"
    assert proxy.kinds[0] == "llm", proxy.kinds
    assert not any(c.get("code", "").endswith("exact h\n") for c in proxy.judge_calls)


def test_the_skip_deterministic_log_line_survives(solver, monkeypatch, solo, capsys):
    _unsolvable(solver, monkeypatch)
    solo(EASY_FALSE_ROW, rounds=0)
    assert "skip:deterministic" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# SOLO-3: a duplicate LLM answer must change the next prompt
# ---------------------------------------------------------------------------

def test_a_duplicate_llm_candidate_sets_feedback_for_the_next_round(
        solver, monkeypatch, solo, capsys):
    """Deployed sampling is temperature 0.0 / seed 0.

    A duplicate makes no judge call, so `{history.attempts}` does not grow
    either: without feedback the next prompt is byte-identical and every
    remaining round is a guaranteed repeat (measured before the fix: 5 llm
    calls, feedback empty in all 5).
    """
    _unsolvable(solver, monkeypatch)
    # The table must be a genuine countermodel for this row, or the candidate
    # is rejected at parse time and the *reject* branch sets feedback instead -
    # which is how the first draft of this test passed against the bug.
    answer = json.dumps({"verdict": "false", "table": [[0, 1], [0, 1]]})
    proxy = solo(EASY_FALSE_ROW, rounds=4, judge_statuses=["incorrect"],
                 llm_texts=[answer] * 4)
    log = capsys.readouterr().err
    assert "llm:duplicate" in log, (
        "the scripted run never reached the duplicate branch, so this test "
        "proves nothing: " + log)
    assert "llm:reject" not in log, log
    assert len(proxy.judge_calls) == 1, "a duplicate must not be re-judged"
    # Round 0 sends the candidate; round 1 repeats it and is the round that
    # detects the duplicate (its prompt was already in flight). Every round
    # after that must carry the feedback.
    assert len(proxy.contexts) >= 3, proxy.contexts
    for context in proxy.contexts[2:]:
        assert context.get("feedback"), (
            "a duplicate round left `feedback` empty, so the next prompt is "
            "byte-identical and the round is spent for nothing")


# ---------------------------------------------------------------------------
# The speculative-grind gate
# ---------------------------------------------------------------------------

def test_no_model_evidence_makes_no_extra_judge_call(solver, monkeypatch, solo, capsys):
    """Rail 5: a FALSE search that saw 0 models of the hypothesis proved nothing,
    so the speculative TRUE fallback must not be sent."""
    _unsolvable(solver, monkeypatch, models_seen=0)
    proxy = solo(EASY_FALSE_ROW, rounds=0)
    assert proxy.judge_calls == [], proxy.calls
    assert "fallback:skip_no_model_evidence" in capsys.readouterr().err


def test_with_model_evidence_the_speculative_fallback_is_sent_once(
        solver, monkeypatch, solo):
    _unsolvable(solver, monkeypatch, models_seen=42)
    proxy = solo(EASY_FALSE_ROW, rounds=0, judge_statuses=["incorrect"])
    assert len(proxy.judge_calls) == 1, proxy.calls
    assert set(proxy.judge_calls[0]) == {"call", "verdict", "code"}
