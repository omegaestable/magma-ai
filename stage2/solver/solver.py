"""Stage 2 solver scaffold for SAIR Equational Theories.

This file is intentionally conservative: it only submits a certificate for the
trivial reflexive implication case where eq1_id == eq2_id. All other problems are
skipped until deterministic proof and counterexample engines are added.
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any


PROMPT = """You are helping produce Lean 4 certificates for magma equation implications.
Problem: {problem.equation1} implies {problem.equation2}?
Return only JSON with a verdict and Lean code candidate.
"""

MAX_SUBMISSION_BYTES = 500_000


def reflexive_true_certificate() -> str:
    return """import JudgeProblem

def submission : Goal := by
  intro G _ h
  exact h
"""


def is_reflexive_problem(problem: dict[str, Any]) -> bool:
    return problem.get("eq1_id") == problem.get("eq2_id")


def make_true_answer(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem.get("id"),
        "verdict": "true",
        "code": reflexive_true_certificate(),
    }


def load_json_line(stream: Any) -> dict[str, Any] | None:
    line = stream.readline()
    if not line:
        return None
    return json.loads(line)


def run_solo() -> int:
    payload = load_json_line(sys.stdin)
    if not payload:
        return 0

    problem = payload.get("problem", payload)
    if not isinstance(problem, dict):
        return 0

    if not is_reflexive_problem(problem):
        print("No deterministic certificate available for this problem.", file=sys.stderr)
        return 0

    request = make_true_answer(problem)
    request.pop("id", None)
    request["call"] = "judge"
    print(json.dumps(request, separators=(",", ":")), flush=True)

    response = load_json_line(sys.stdin)
    if response:
        print(json.dumps({"judge_status": response.get("status")}), file=sys.stderr)
    return 0


def iter_manifest(path: str) -> list[dict[str, Any]]:
    problems: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as manifest_file:
        for line in manifest_file:
            stripped = line.strip()
            if stripped:
                problems.append(json.loads(stripped))
    return problems


def append_answer(path: str, answer: dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as output_file:
        output_file.write(json.dumps(answer, separators=(",", ":")))
        output_file.write("\n")
        output_file.flush()


def run_marathon() -> int:
    manifest_path = os.environ.get("JUDGE_MARATHON_MANIFEST")
    output_path = os.environ.get("JUDGE_MARATHON_OUTPUT")
    if not manifest_path or not output_path:
        print("Missing Marathon manifest/output environment variables.", file=sys.stderr)
        return 2

    solved = 0
    for problem in iter_manifest(manifest_path):
        if is_reflexive_problem(problem):
            append_answer(output_path, make_true_answer(problem))
            solved += 1

    print(f"submitted_reflexive={solved}", file=sys.stderr)
    return 0


def is_marathon_mode() -> bool:
    return bool(os.environ.get("JUDGE_MARATHON_MANIFEST") and os.environ.get("JUDGE_MARATHON_OUTPUT"))


def main() -> int:
    if is_marathon_mode():
        return run_marathon()
    return run_solo()


if __name__ == "__main__":
    raise SystemExit(main())
