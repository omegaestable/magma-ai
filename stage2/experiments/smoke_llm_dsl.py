"""Smoke checks for solver-owned LLM DSL parsing.

This script uses fake LLM payloads only. It does not call a model, read
secrets, or invoke the official proxy.
"""

from __future__ import annotations

import importlib.util
import json
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

    assert solver.candidate_from_llm_text(false_problem, "not json") is None

    banned_payload = json.dumps(
        {
            "verdict": "true",
            "code": "import JudgeProblem\n\ndef submission : Goal := by\n  sorry",
        }
    )
    assert solver.candidate_from_llm_text(true_problem, banned_payload) is None

    duplicate = solver.candidate_from_llm_text(true_problem, true_payload)
    assert duplicate is not None
    first_key = (true_candidate["answer"]["verdict"], true_candidate["answer"]["code"])
    duplicate_key = (duplicate["answer"]["verdict"], duplicate["answer"]["code"])
    assert first_key == duplicate_key

    print("fake_llm_dsl_smoke_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
