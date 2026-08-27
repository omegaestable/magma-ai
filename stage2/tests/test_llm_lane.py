"""The LLM lane: derivation replay, budget-derived call allowance, rounds.

Every test here is offline. The lane's two halves — a prompt that asks for a
justified derivation and a parser that replays it rung by rung — were measured
together on 37 hard rows with real calls (2026-08-27): 2/37 settled, and 0/37
with either half alone. What these tests pin is the machinery, so the measured
behaviour cannot silently regress:

* `llm_ladder_candidate` turns a proposed derivation into a `lemma_chain`
  certificate the offline kernel accepts, and refuses laws it cannot prove.
* `marathon_llm_call_allowance` scales with N (the old flat 64-call cap spent
  1.3% of an N=1000 token budget).
* `PROMPT` survives the official proxy's AST extraction and carries every
  placeholder, `{solver.protocol}` included.
* The Marathon lane sends a row a *different* prompt body on a second round —
  temperature 0 + seed 0 make an identical re-prompt a guaranteed repeat — and
  a transient "would be exhausted by this call" no longer kills the lane.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

import oracles

REPO_ROOT = Path(__file__).resolve().parents[2]
VENDOR = REPO_ROOT / "vendor" / "stage2-official"

# hard3_0266: idempotence is derivable from eq1 in ~0.2 s and, with it in
# scope, the goal follows — the row `egg_ladder` was built for, and the
# positive control the protocol study used before spending a token.
LADDER_ROW = {
    "id": "hard3_0266",
    "eq1_id": 2521,
    "eq2_id": 1879,
    "equation1": "x = (y ◇ ((x ◇ z) ◇ z)) ◇ x",
    "equation2": "x = (x ◇ (y ◇ z)) ◇ (w ◇ x)",
}


def _fresh(solver):
    solver.set_effort("fast")
    solver.set_hard_deadline(None)
    solver.clear_term_caches()


# ---------------------------------------------------------------------------
# llm_ladder_candidate


def test_ladder_replays_a_derivation_into_a_verified_certificate(solver):
    _fresh(solver)
    started = time.monotonic()
    candidate, reason = solver.candidate_from_llm_text_with_reason(
        LADDER_ROW,
        json.dumps({"verdict": "true", "derivation": ["a ◇ a = a"]}),
        allow_raw_true=False,
    )
    elapsed = time.monotonic() - started
    assert candidate is not None, reason
    assert candidate["route"].startswith("llm:true:ladder")
    code = candidate["answer"]["code"]
    eq1 = solver.parse_equation(LADDER_ROW["equation1"])
    eq2 = solver.parse_equation(LADDER_ROW["equation2"])
    assert oracles.classify_true_certificate(code) == "lemma_chain"
    oracles.check_true_lemma_chain_certificate(code, eq1, eq2)
    oracles.check_no_banned_tactics(code, "llm")
    # Measured 0.2 s; the bound is loose enough for a loaded box but tight
    # enough to catch a rung budget that stopped being polled.
    assert elapsed < 20.0


def test_ladder_accepts_the_justified_A2_shape(solver):
    _fresh(solver)
    obj = {"verdict": "true", "derivation": [
        {"law": "a ◇ a = a", "from": ["hypothesis"], "subst": "y := x, z := x"},
    ]}
    laws = solver.llm_derivation_law_texts(obj)
    assert laws == ["a ◇ a = a"]
    candidate, _reason = solver.candidate_from_llm_text_with_reason(
        LADDER_ROW, json.dumps(obj), allow_raw_true=False)
    assert candidate is not None
    assert candidate["route"].startswith("llm:true:ladder")


def test_ladder_rejects_laws_it_cannot_prove(solver):
    """Negative control (rail 5c): unprovable laws must cost nothing but time."""
    _fresh(solver)
    candidate, reason = solver.candidate_from_llm_text_with_reason(
        LADDER_ROW,
        json.dumps({"verdict": "true", "derivation": [
            "a ◇ b = b ◇ a",
            "(a ◇ b) ◇ c = a ◇ (b ◇ c)",
        ]}),
        allow_raw_true=False,
    )
    assert candidate is None
    assert "ladder" in reason


def test_ladder_ignores_an_empty_derivation(solver):
    _fresh(solver)
    candidate, _reason = solver.candidate_from_llm_text_with_reason(
        LADDER_ROW, json.dumps({"verdict": "true", "derivation": []}),
        allow_raw_true=False)
    assert candidate is None


def test_false_branch_checks_every_proposed_table(solver):
    """The FALSE round body asks for up to 5 tables; all of them get checked."""
    _fresh(solver)
    problem = {"id": "t", "eq1_id": 1, "eq2_id": 2,
               "equation1": "x ◇ y = x ◇ y", "equation2": "x = y"}
    payload = {"verdict": "false", "tables": [
        [[0, 0], [0, 0]],          # degenerate: satisfies eq1 but not a witness
        [[0, 1], [1, 0]],          # the real one: breaks x = y
    ]}
    candidate, reason = solver.candidate_from_llm_text_with_reason(
        problem, json.dumps(payload), allow_raw_true=False)
    assert candidate is not None, reason
    assert candidate["route"] == "llm:false:table"


# ---------------------------------------------------------------------------
# budget-derived call allowance


@pytest.mark.parametrize("rows", [25, 100, 1000])
def test_call_allowance_scales_with_n(solver, rows):
    budget = rows * 32768
    allowance = solver.marathon_llm_call_allowance(budget, 0)
    expected = (budget - solver.MARATHON_LLM_TOKEN_RESERVE) // solver.MARATHON_LLM_CALL_TOKEN_ESTIMATE
    assert allowance == expected
    # ~4 calls per row at the measured 8k tokens/call — the point of the change:
    # the old flat cap was 64 regardless of N.
    assert allowance >= 3 * rows
    assert allowance > solver.MARATHON_LLM_BATCH_SIZE


def test_call_allowance_edges(solver):
    assert solver.marathon_llm_call_allowance(-1, 10 ** 9) == 10 ** 9
    assert solver.marathon_llm_call_allowance(32768, 0) == 0
    assert solver.marathon_llm_call_allowance(100000, 99000) == 0
    # spending is subtracted, not ignored
    high = solver.marathon_llm_call_allowance(1000000, 0)
    low = solver.marathon_llm_call_allowance(1000000, 500000)
    assert 0 < low < high


# ---------------------------------------------------------------------------
# the prompt shell


def test_prompt_survives_the_official_ast_extractor(solver):
    if str(VENDOR) not in sys.path:
        sys.path.insert(0, str(VENDOR))
    from pipeline.proxy import _extract_prompt_from_solver

    extracted = _extract_prompt_from_solver(REPO_ROOT / "stage2" / "solver" / "solver.py")
    assert extracted, "PROMPT must stay one top-level string literal"
    assert extracted == solver.PROMPT
    for placeholder in ("{problem.id}", "{problem.equation1}", "{problem.equation2}",
                        "{solver.analysis}", "{history.attempts}",
                        "{solver.feedback}", "{solver.protocol}"):
        assert placeholder in extracted, placeholder


def test_protocol_bodies_are_distinct(solver):
    """Round r must not repeat round r-1: temperature 0 + seed 0 are pinned."""
    assert len(solver.PROTOCOL_BODIES) >= 3
    assert len(set(solver.PROTOCOL_BODIES)) == len(solver.PROTOCOL_BODIES)
    # the bare A2 shell is one of the rounds, and the FALSE body is not a
    # TRUE-round body
    assert "" in solver.PROTOCOL_BODIES
    assert solver.PROTOCOL_FALSE_FIRST not in solver.PROTOCOL_BODIES


def test_render_marathon_prompt_fills_the_protocol_and_leaves_no_placeholder(solver):
    problem = {"id": "row", "eq1_id": 11, "eq2_id": 22,
               "equation1": "x = y ◇ x", "equation2": "x ◇ y = x"}
    analysis = solver.solver_analysis(problem)
    body = next(b for b in solver.PROTOCOL_BODIES if b.strip())
    prompt = solver.render_marathon_prompt(problem, analysis, body)
    assert body.strip()[:40] in prompt
    assert "Equation11" in prompt and "Equation22" in prompt
    import re
    assert not re.search(r"\{(?:problem|solver|history)\.[a-zA-Z_0-9]+\}", prompt)
    plain = solver.render_marathon_prompt(problem, analysis)
    assert plain != prompt


def test_solo_llm_round_sends_a_protocol_key(solver):
    """The Solo loop must vary the body; the proxy fills it as {solver.protocol}."""
    source = (REPO_ROOT / "stage2" / "solver" / "solver.py").read_text(encoding="utf-8")
    marker = '"protocol": PROTOCOL_BODIES[round_idx % len(PROTOCOL_BODIES)],'
    assert marker in source


# ---------------------------------------------------------------------------
# direction from evidence


def test_direction_follows_the_false_search_evidence(solver):
    problem = {"id": "ev", "equation1": "x = (y ◇ x) ◇ z", "equation2": "x = y"}
    solver._MARATHON_ROW_EVIDENCE.clear()
    try:
        assert solver.llm_row_direction(problem) == "true"        # unknown
        solver._MARATHON_ROW_EVIDENCE["ev"] = (0, False)
        assert solver.llm_row_direction(problem) == "true"        # no models
        solver._MARATHON_ROW_EVIDENCE["ev"] = (1200, False)
        assert solver.llm_row_direction(problem) == "false"       # cut off
        assert solver.llm_round_body(problem, 0)[0] == solver.PROTOCOL_FALSE_FIRST
        assert solver.llm_round_body(problem, 0)[1] is True
        assert solver.llm_round_body(problem, 1)[0] == solver.PROTOCOL_BODIES[0]
        assert solver.llm_round_body(problem, 2)[0] == solver.PROTOCOL_BODIES[1]
        solver._MARATHON_ROW_EVIDENCE["ev"] = (1200, True)
        assert solver.llm_row_direction(problem) == "true"        # exhausted
        assert solver.llm_round_body(problem, 0)[0] == solver.PROTOCOL_BODIES[0]
    finally:
        solver._MARATHON_ROW_EVIDENCE.clear()


def test_order5_shaped_rows_with_no_models_go_last(solver):
    """Measured 0/120 under every protocol — lowest priority, not excluded."""
    order5 = {"id": "o5", "equation1": "x = (y ◇ (x ◇ x)) ◇ ((y ◇ z) ◇ y)",
              "equation2": "x ◇ y = (((y ◇ z) ◇ z) ◇ z) ◇ z"}
    ordinary = {"id": "o4", "equation1": "x = (y ◇ x) ◇ (x ◇ z)",
                "equation2": "x = y ◇ x"}
    solver._MARATHON_ROW_EVIDENCE.clear()
    try:
        assert solver.llm_row_is_order5_shaped(order5)
        assert not solver.llm_row_is_order5_shaped(ordinary)
        solver._MARATHON_ROW_EVIDENCE["o5"] = (0, True)
        solver._MARATHON_ROW_EVIDENCE["o4"] = (0, True)
        base = (0, 0, "x")
        assert solver.llm_problem_priority(base, order5)[0] == 2
        assert solver.llm_problem_priority(base, ordinary)[0] == 1
        # the FALSE-search-cut-off band outranks both
        solver._MARATHON_ROW_EVIDENCE["o4"] = (500, False)
        assert solver.llm_problem_priority(base, ordinary)[0] == 0
    finally:
        solver._MARATHON_ROW_EVIDENCE.clear()


# ---------------------------------------------------------------------------
# the Marathon lane itself, with a fake model


UNSOLVABLE = [
    {"id": "row_a", "eq1_id": 1, "eq2_id": 2,
     "equation1": "x = (y ◇ (x ◇ x)) ◇ ((y ◇ z) ◇ y)",
     "equation2": "x ◇ y = (((y ◇ z) ◇ z) ◇ z) ◇ z"},
    {"id": "row_b", "eq1_id": 3, "eq2_id": 4,
     "equation1": "x = (y ◇ ((y ◇ x) ◇ x)) ◇ (z ◇ z)",
     "equation2": "x = (y ◇ (((z ◇ y) ◇ z) ◇ y)) ◇ x"},
]


def test_marathon_lane_reprompts_with_a_different_body_and_survives_a_transient(
        solver, tmp_path, monkeypatch):
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text("\n".join(json.dumps(row, ensure_ascii=False)
                                  for row in UNSOLVABLE) + "\n", encoding="utf-8")
    output = tmp_path / "answers.jsonl"

    calls: list[tuple[str, str]] = []

    def fake_call_llm(prompt, config=None, max_seconds=None):
        pid = ""
        for row in UNSOLVABLE:
            if f"Problem {row['id']}:" in prompt:
                pid = row["id"]
        calls.append((pid, prompt))
        if len(calls) == 1:
            # the proxy's per-call reservation refusing ONE request; it used to
            # set stop_llm and kill the lane for the rest of the run
            return {"error": "token budget would be exhausted by this call"}
        return {"response": json.dumps({"verdict": "true", "derivation": ["a = b"]}),
                "tokens_used_call": 5000}

    monkeypatch.setattr(solver, "load_marathon_llm",
                        lambda: (fake_call_llm, lambda: 0, lambda: 10 ** 7))
    monkeypatch.setattr(solver, "MARATHON_DETERMINISTIC_SHARE", 0.03)
    monkeypatch.setenv("JUDGE_MARATHON_MANIFEST", str(manifest))
    monkeypatch.setenv("JUDGE_MARATHON_OUTPUT", str(output))
    monkeypatch.setenv("JUDGE_MARATHON_BUDGET_SECONDS", "120")
    monkeypatch.setenv("JUDGE_MARATHON_BUDGET_TOKENS", str(3 * 32768))
    try:
        assert solver.run_marathon() == 0
    finally:
        solver.set_hard_deadline(None)
        solver.set_effort("fast")

    assert len(calls) > len(UNSOLVABLE), "each row must get more than one call"
    by_row: dict[str, list[str]] = {}
    for pid, prompt in calls:
        by_row.setdefault(pid, []).append(prompt)
    for pid, prompts in by_row.items():
        assert len(prompts) >= 2, pid
        # temperature 0 + seed 0: a repeated prompt is a guaranteed repeat, so
        # the ROUNDS must differ in text. (A row can legitimately see the same
        # text twice: the "would be exhausted" retry re-sends the round it
        # never got an answer to, at a lower output cap.)
        assert len(set(prompts)) >= 3, pid
    # the transient did not stop the lane
    assert len(calls) >= 2 * len(UNSOLVABLE)


# A REAL response, recorded verbatim from gpt-oss-120b (DeepInfra bf16,
# reasoning low, temperature 0, seed 0) on 2026-08-27 for `etp_4453_4652` — a
# row the full deterministic solver misses at 420 s. Replaying it produces a
# `lemma_chain` certificate; the certificate this route emitted for this row,
# and two more from the same run, were **accepted by the real Lean judge**
# (v4.33.1, deployed caps): 3/3, 5.7–7.9 s, 4,257 / 14,597 / 26,168 bytes.
RECORDED_RESPONSE = json.dumps({"verdict": "true", "derivation": [
    {"law": "a ◇ (a ◇ a) = (a ◇ a) ◇ a", "from": ["hypothesis"], "subst": "x->a, y->a, z->a"},
    {"law": "a ◇ (b ◇ a) = (a ◇ a) ◇ b", "from": ["hypothesis"], "subst": "x->a, y->b, z->a"},
    {"law": "(b ◇ a) ◇ a = (a ◇ a) ◇ a", "from": ["hypothesis", "law 1"], "subst": "x->a, y->a, z->b"},
    {"law": "(a ◇ a) ◇ a = (b ◇ a) ◇ a", "from": ["law 3"], "subst": ""},
    {"law": "b ◇ (a ◇ b) = (b ◇ b) ◇ a", "from": ["hypothesis"], "subst": "x->b, y->a, z->b"},
    {"law": "(a ◇ b) ◇ a = (b ◇ b) ◇ a", "from": ["law 5", "law 4"], "subst": ""},
    {"law": "(b ◇ b) ◇ a = (a ◇ a) ◇ a", "from": ["law 3", "law 5"], "subst": ""},
    {"law": "(a ◇ b) ◇ a = (a ◇ a) ◇ a", "from": ["law 6", "law 7"], "subst": ""},
    {"law": "(x ◇ y) ◇ x = (z ◇ w) ◇ w", "from": ["law 8"], "subst": ""},
]}, ensure_ascii=False)

RECORDED_ROW = {
    "id": "etp_4453_4652",
    "eq1_id": 4453,
    "eq2_id": 4652,
    "equation1": "x ◇ (y ◇ x) = (z ◇ x) ◇ y",
    "equation2": "(x ◇ y) ◇ x = (z ◇ w) ◇ w",
}


def test_recorded_real_response_replays_to_a_verified_certificate(solver):
    _fresh(solver)
    candidate, reason = solver.candidate_from_llm_text_with_reason(
        RECORDED_ROW, RECORDED_RESPONSE, allow_raw_true=False)
    assert candidate is not None, reason
    assert candidate["route"].startswith("llm:true:ladder")
    code = candidate["answer"]["code"]
    assert oracles.classify_true_certificate(code) == "lemma_chain"
    oracles.check_true_lemma_chain_certificate(
        code,
        solver.parse_equation(RECORDED_ROW["equation1"]),
        solver.parse_equation(RECORDED_ROW["equation2"]),
    )
    assert len(code.encode("utf-8")) < solver.MAX_LEAN_CODE_BYTES
