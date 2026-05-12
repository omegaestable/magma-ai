"""Stage 2 solver for SAIR Equational Theories.

The current deterministic core handles:
1. reflexive TRUE implications;
2. finite FALSE witnesses from small canned magmas and bounded Fin n search.

Unsupported cases are skipped rather than answered speculatively.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from itertools import product
from typing import Any


PROMPT = """You are helping produce Lean 4 certificates for magma equation implications.
Problem: {problem.equation1} implies {problem.equation2}?
Return only JSON with a verdict and Lean code candidate.
"""

MAX_SUBMISSION_BYTES = 500_000

WITNESS_TABLES = (
    ("LP", [[0, 0], [1, 1]]),
    ("RP", [[0, 1], [0, 1]]),
    ("C0", [[0, 0], [0, 0]]),
    ("XOR", [[0, 1], [1, 0]]),
    ("AND", [[0, 0], [0, 1]]),
    ("OR", [[0, 1], [1, 1]]),
    ("XNOR", [[1, 0], [0, 1]]),
    ("A2", [[0, 0], [1, 0]]),
    ("Z3A", [[0, 1, 2], [1, 2, 0], [2, 0, 1]]),
    ("T3L", [[0, 0, 0], [0, 0, 0], [0, 1, 0]]),
    ("T3R", [[0, 0, 0], [0, 0, 0], [0, 0, 1]]),
)


def reflexive_true_certificate() -> str:
    return """import JudgeProblem

def submission : Goal := by
  intro G _ h
  exact h
"""


def false_certificate(n: int, table: list[list[int]]) -> str:
    table_str = json.dumps(table, separators=(",", ":"))
    return (
        "import JudgeProblem\n"
        "import JudgeDecide.DecideBang\n"
        "import JudgeFinOp.MemoFinOp\n"
        "open MemoFinOp\n\n"
        "def submission : Goal := by\n"
        f"  let m : Magma (Fin {n}) := {{\n"
        f"    op := finOpTable \"{table_str}\"\n"
        "  }\n"
        f"  refine Exists.intro (Fin {n}) ?_\n"
        "  refine Exists.intro m ?_\n"
        "  decideFin!\n"
    )


def is_reflexive_problem(problem: dict[str, Any]) -> bool:
    return problem.get("eq1_id") == problem.get("eq2_id")


def make_true_answer(problem: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": problem.get("id"),
        "verdict": "true",
        "code": reflexive_true_certificate(),
    }


def make_false_answer(problem: dict[str, Any], n: int, table: list[list[int]]) -> dict[str, Any]:
    return {
        "id": problem.get("id"),
        "verdict": "false",
        "code": false_certificate(n, table),
    }


def strip_outer_parens(text: str) -> str:
    s = text.strip()
    while len(s) >= 2 and s[0] == "(" and s[-1] == ")":
        depth = 0
        wraps = True
        for idx, char in enumerate(s):
            if char == "(":
                depth += 1
            elif char == ")":
                depth -= 1
            if depth == 0 and idx < len(s) - 1:
                wraps = False
                break
        if not wraps:
            break
        s = s[1:-1].strip()
    return s


def parse_term(text: str, variables: set[str]):
    s = strip_outer_parens(text)
    depth = 0
    last_op = -1
    for idx, char in enumerate(s):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif char in {"◇", "*"} and depth == 0:
            last_op = idx
    if last_op >= 0:
        left = parse_term(s[:last_op], variables)
        right = parse_term(s[last_op + 1 :], variables)
        return lambda env, left_fn=left, right_fn=right: env["op"](left_fn(env), right_fn(env))
    if len(s) == 1 and s in variables:
        return lambda env, v=s: env[v]
    raise ValueError(f"cannot parse term: {text!r}")


def parse_equation(text: str):
    if "=" not in text:
        raise ValueError(f"cannot parse equation: {text!r}")
    variables = []
    seen: set[str] = set()
    for var in re.findall(r"\b([a-z])\b", text):
        if var not in seen:
            seen.add(var)
            variables.append(var)
    lhs, rhs = text.split("=", 1)
    return variables, parse_term(lhs, seen), parse_term(rhs, seen)


def equation_holds(variables: list[str], lhs_fn: Any, rhs_fn: Any, table: list[list[int]]) -> bool:
    n = len(table)

    def op(a: int, b: int) -> int:
        return table[a][b]

    for values in product(range(n), repeat=len(variables)):
        env = {"op": op}
        env.update(zip(variables, values))
        if lhs_fn(env) != rhs_fn(env):
            return False
    return True


def table_is_counterexample(
    eq1: tuple[list[str], Any, Any],
    eq2: tuple[list[str], Any, Any],
    table: list[list[int]],
) -> bool:
    eq1_vars, eq1_lhs, eq1_rhs = eq1
    eq2_vars, eq2_lhs, eq2_rhs = eq2
    return equation_holds(eq1_vars, eq1_lhs, eq1_rhs, table) and not equation_holds(
        eq2_vars,
        eq2_lhs,
        eq2_rhs,
        table,
    )


def enumerate_tables(n: int):
    total = n ** (n * n)
    for encoding in range(total):
        yield [[(encoding // (n ** (row * n + col))) % n for col in range(n)] for row in range(n)]


def find_counterexample(
    problem: dict[str, Any],
    *,
    max_n: int = 3,
    time_budget: float | None = None,
) -> tuple[int, list[list[int]]] | None:
    try:
        eq1 = parse_equation(str(problem["equation1"]))
        eq2 = parse_equation(str(problem["equation2"]))
    except (KeyError, ValueError):
        return None

    for _name, table in WITNESS_TABLES:
        if len(table) <= max_n and table_is_counterexample(eq1, eq2, table):
            return len(table), table

    deadline = time.monotonic() + time_budget if time_budget else None
    for n in range(2, max_n + 1):
        for table in enumerate_tables(n):
            if deadline is not None and time.monotonic() >= deadline:
                return None
            if table_is_counterexample(eq1, eq2, table):
                return n, table
    return None


def deterministic_answer(
    problem: dict[str, Any],
    *,
    false_time_budget: float | None = None,
) -> dict[str, Any] | None:
    if is_reflexive_problem(problem):
        return make_true_answer(problem)
    counterexample = find_counterexample(problem, time_budget=false_time_budget)
    if counterexample is None:
        return None
    n, table = counterexample
    return make_false_answer(problem, n, table)


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

    answer = deterministic_answer(problem)
    if answer is None:
        print("No deterministic certificate available for this problem.", file=sys.stderr)
        return 0

    request = dict(answer)
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

    problems = iter_manifest(manifest_path)
    budget_seconds = float(os.environ.get("JUDGE_MARATHON_BUDGET_SECONDS", "3600"))
    per_problem_budget = max(0.25, min(3.0, budget_seconds / max(1, len(problems))))

    solved = 0
    for problem in problems:
        answer = deterministic_answer(problem, false_time_budget=per_problem_budget)
        if answer is not None:
            append_answer(output_path, answer)
            solved += 1

    print(f"submitted_deterministic={solved}", file=sys.stderr)
    return 0


def is_marathon_mode() -> bool:
    return bool(os.environ.get("JUDGE_MARATHON_MANIFEST") and os.environ.get("JUDGE_MARATHON_OUTPUT"))


def main() -> int:
    if is_marathon_mode():
        return run_marathon()
    return run_solo()


if __name__ == "__main__":
    raise SystemExit(main())
