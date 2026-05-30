"""Smoke checks for solver-owned LLM DSL parsing.

This script uses fake LLM payloads only. It does not call a model, read
secrets, or invoke the official proxy.
"""

from __future__ import annotations

import importlib.util
import json
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOLVER_PATH = ROOT / "stage2" / "solver" / "solver.py"


def load_solver():
    spec = importlib.util.spec_from_file_location("stage2_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load solver from {SOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    solver = load_solver()

    false_problem = {
        "id": "fake_false",
        "eq1_id": 1,
        "eq2_id": 2,
        "equation1": "x = x",
        "equation2": "x = y",
    }
    false_payload = json.dumps({"verdict": "false", "counterexample_table": [[0, 0], [1, 1]]})
    false_candidate = solver.candidate_from_llm_text(false_problem, false_payload)
    assert false_candidate is not None
    assert false_candidate["answer"]["verdict"] == "false"

    true_problem = {
        "id": "fake_true",
        "eq1_id": 3,
        "eq2_id": 4,
        "equation1": "x = x ◇ y",
        "equation2": "x = x ◇ x",
    }
    true_payload = json.dumps(
        {
            "verdict": "true",
            "proof_kind": "rewrite_chain",
            "chain": ["x", "x ◇ x"],
        }
    )
    true_candidate = solver.candidate_from_llm_text(true_problem, true_payload)
    assert true_candidate is not None
    assert true_candidate["answer"]["verdict"] == "true"
    assert set(true_candidate["answer"]) == {"id", "verdict", "code"}

    extra_answer = dict(true_candidate["answer"])
    extra_answer["route"] = "internal:metadata"
    extra_answer["debug"] = {"not": "judge-visible"}
    expected_judge_payload = {
        "verdict": true_candidate["answer"]["verdict"],
        "code": true_candidate["answer"]["code"],
    }
    expected_marathon_payload = {
        "id": true_candidate["answer"]["id"],
        **expected_judge_payload,
    }
    assert solver.judge_answer_payload(extra_answer) == expected_judge_payload
    assert solver.marathon_answer_payload(extra_answer) == expected_marathon_payload
    assert solver.judge_answer_payload({"id": "bad", "verdict": "unknown", "code": "x"}) is None
    assert solver.judge_answer_payload(
        {"id": "bad", "verdict": "true", "code": "x" * (solver.MAX_LEAN_CODE_BYTES + 1)}
    ) is None

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "answers.jsonl"
        assert solver.append_answer(str(output_path), extra_answer) is True
        assert json.loads(output_path.read_text(encoding="utf-8").strip()) == expected_marathon_payload
        assert solver.append_answer(str(output_path), {"id": "", "verdict": "true", "code": "x"}) is False
        assert len(output_path.read_text(encoding="utf-8").splitlines()) == 1

    steps_payload = json.dumps(
        {
            "verdict": "true",
            "steps": [
                {"from": "x", "to": "x ◇ x"},
            ],
        }
    )
    steps_candidate, steps_reason = solver.candidate_from_llm_text_with_reason(true_problem, steps_payload)
    assert steps_candidate is not None, steps_reason
    assert steps_candidate["route"] == "llm:true:rewrite_chain"

    guided_problem = {
        "id": "fake_guided_true",
        "eq1_id": 7,
        "eq2_id": 8,
        "equation1": "x = x ◇ y",
        "equation2": "x = (x ◇ x) ◇ x",
    }
    guided_payload = json.dumps(
        {
            "verdict": "true",
            "proof_kind": "guided_chain",
            "chain": ["x", "(x ◇ x) ◇ x"],
        }
    )
    guided_candidate, guided_reason = solver.candidate_from_llm_text_with_reason(guided_problem, guided_payload)
    assert guided_candidate is not None, guided_reason
    assert guided_candidate["route"] == "llm:true:guided_chain"

    bad_endpoint_payload = json.dumps(
        {
            "verdict": "true",
            "proof_kind": "guided_chain",
            "chain": ["x ◇ x", "(x ◇ x) ◇ x"],
        }
    )
    bad_endpoint_candidate, bad_endpoint_reason = solver.candidate_from_llm_text_with_reason(
        guided_problem,
        bad_endpoint_payload,
    )
    assert bad_endpoint_candidate is None
    assert bad_endpoint_reason == "guided_chain_unproved_or_bad_endpoints"

    unproved_payload = json.dumps(
        {
            "verdict": "true",
            "proof_kind": "guided_chain",
            "chain": ["x", "y"],
        }
    )
    unproved_problem = {
        "id": "fake_unproved_true",
        "eq1_id": 9,
        "eq2_id": 10,
        "equation1": "x = x",
        "equation2": "x = y",
    }
    unproved_candidate, unproved_reason = solver.candidate_from_llm_text_with_reason(unproved_problem, unproved_payload)
    assert unproved_candidate is None
    assert unproved_reason == "guided_chain_unproved_or_bad_endpoints"

    extra_var_payload = json.dumps(
        {
            "verdict": "true",
            "proof_kind": "guided_chain",
            "chain": ["x", "z", "y"],
        }
    )
    extra_var_candidate, extra_var_reason = solver.candidate_from_llm_text_with_reason(
        unproved_problem,
        extra_var_payload,
    )
    assert extra_var_candidate is None
    assert extra_var_reason == "rewrite_chain_uses_non_goal_variables"

    no_json_candidate, no_json_reason = solver.candidate_from_llm_text_with_reason(false_problem, "not json")
    assert no_json_candidate is None
    assert no_json_reason == "no_json_object"

    bare_false_candidate, bare_false_reason = solver.candidate_from_llm_text_with_reason(
        false_problem,
        json.dumps({"verdict": "false"}),
    )
    assert bare_false_candidate is None
    assert bare_false_reason == "false_verdict_without_table"

    bad_table_payload = json.dumps({"verdict": "false", "counterexample_table": [[0, 1], [1]]})
    bad_table_candidate, bad_table_reason = solver.candidate_from_llm_text_with_reason(
        false_problem,
        bad_table_payload,
    )
    assert bad_table_candidate is None
    assert bad_table_reason == "false_table_invalid_shape"

    not_counterexample_problem = {
        "id": "fake_not_counterexample",
        "eq1_id": 5,
        "eq2_id": 6,
        "equation1": "x = x",
        "equation2": "x = x",
    }
    not_counterexample_payload = json.dumps({"verdict": "false", "counterexample_table": [[0, 0], [1, 1]]})
    not_counterexample_candidate, not_counterexample_reason = solver.candidate_from_llm_text_with_reason(
        not_counterexample_problem,
        not_counterexample_payload,
    )
    assert not_counterexample_candidate is None
    assert not_counterexample_reason == "false_table_not_counterexample"

    banned_payload = json.dumps(
        {
            "verdict": "true",
            "code": "import JudgeProblem\n\ndef submission : Goal := by\n  sorry",
        }
    )
    assert solver.candidate_from_llm_text(true_problem, banned_payload) is None

    helper_code_payload = json.dumps(
        {
            "verdict": "true",
            "code": (
                "import JudgeProblem\n\n"
                "namespace SubmissionSupport\n\n"
                "def helperMarker : Nat := 0\n\n"
                "theorem helperStep {G : Type} [Magma G] "
                "(h : ∀ x y : G, x = x ◇ y) (x : G) : x = x ◇ x := by\n"
                "  exact h x x\n\n"
                "end SubmissionSupport\n\n"
                "def submission : Goal := by\n"
                "  intro G _ h\n"
                "  intro x\n"
                "  exact SubmissionSupport.helperStep h x\n"
            ),
        }
    )
    helper_code_candidate = solver.candidate_from_llm_text(true_problem, helper_code_payload)
    assert helper_code_candidate is not None
    assert helper_code_candidate["route"] == "llm:true:raw_code"

    disabled_raw_candidate, disabled_raw_reason = solver.candidate_from_llm_text_with_reason(
        true_problem,
        helper_code_payload,
        allow_raw_true=False,
    )
    assert disabled_raw_candidate is None
    assert disabled_raw_reason == "raw_true_disabled"

    proof_payload = json.dumps({"verdict": "true", "proof": "intro x\n  exact h x x"})
    proof_candidate, proof_reason = solver.candidate_from_llm_text_with_reason(true_problem, proof_payload)
    assert proof_candidate is None
    assert proof_reason == "proof_body_unsupported"

    proof_body_payload = json.dumps({"verdict": "true", "proof_body": "intro x\n  exact h x x"})
    proof_body_candidate, proof_body_reason = solver.candidate_from_llm_text_with_reason(
        true_problem,
        proof_body_payload,
    )
    assert proof_body_candidate is None
    assert proof_body_reason == "proof_body_unsupported"

    def fake_marathon_call(prompt, *, config=None, max_seconds=None):
        assert "Return exactly one JSON object" in prompt
        assert config is not None
        assert config["max_output_tokens"] == solver.LLM_MAX_OUTPUT_TOKENS
        assert max_seconds is not None and max_seconds > 0
        return {
            "response": true_payload,
            "tokens_used_call": 111,
            "tokens_used_total": 111,
            "budget_remaining": 4096,
        }

    marathon_result = solver.marathon_llm_attempt(
        fake_marathon_call,
        true_problem,
        solver.LLM_CONFIG,
        time.monotonic() + 30.0,
    )
    assert marathon_result["route"] == "llm:true:rewrite_chain"
    assert marathon_result["tokens_used_call"] == 111

    duplicate = solver.candidate_from_llm_text(true_problem, true_payload)
    assert duplicate is not None
    first_key = (true_candidate["answer"]["verdict"], true_candidate["answer"]["code"])
    duplicate_key = (duplicate["answer"]["verdict"], duplicate["answer"]["code"])
    assert first_key == duplicate_key

    print("fake_llm_dsl_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
