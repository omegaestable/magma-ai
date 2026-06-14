"""Mine finite magma countermodels with Z3 for Stage 2 FALSE gaps."""

from __future__ import annotations

import argparse
import importlib.util
import json
from itertools import product
from pathlib import Path
from typing import Any

import z3


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE = ROOT / "stage2" / "fixtures" / "focused_failure_rows_2026-06-14.jsonl"
SOLVER_PATH = ROOT / "stage2" / "solver" / "solver.py"


def load_solver():
    spec = importlib.util.spec_from_file_location("stage2_solver", SOLVER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load solver from {SOLVER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def table_lookup(table: list[list[z3.ArithRef]], left: z3.ArithRef, right: z3.ArithRef, n: int) -> z3.ArithRef:
    expr: z3.ArithRef = table[0][0]
    for a in range(n):
        for b in range(n):
            expr = z3.If(z3.And(left == a, right == b), table[a][b], expr)
    return expr


def eval_z3(term: tuple[Any, ...], env: dict[str, z3.ArithRef], table: list[list[z3.ArithRef]], n: int) -> z3.ArithRef:
    if term[0] == "var":
        return env[str(term[1])]
    return table_lookup(
        table,
        eval_z3(term[1], env, table, n),
        eval_z3(term[2], env, table, n),
        n,
    )


def equation_constraint(
    equation: dict[str, Any],
    values: tuple[int, ...],
    table: list[list[z3.ArithRef]],
    n: int,
) -> z3.BoolRef:
    env = {var: z3.IntVal(value) for var, value in zip(equation["variables"], values)}
    return eval_z3(equation["lhs"], env, table, n) == eval_z3(equation["rhs"], env, table, n)


def mine_countermodel(
    solver_module: Any,
    problem: dict[str, Any],
    *,
    n: int,
    timeout_ms: int,
) -> list[list[int]] | None:
    eq1 = solver_module.parse_equation(str(problem["equation1"]))
    eq2 = solver_module.parse_equation(str(problem["equation2"]))
    table = [[z3.Int(f"t_{row}_{col}") for col in range(n)] for row in range(n)]
    z3_solver = z3.Solver()
    z3_solver.set(timeout=timeout_ms)

    for row in table:
        for cell in row:
            z3_solver.add(cell >= 0, cell < n)

    for values in product(range(n), repeat=len(eq1["variables"])):
        z3_solver.add(equation_constraint(eq1, values, table, n))

    refutations = []
    for values in product(range(n), repeat=len(eq2["variables"])):
        refutations.append(z3.Not(equation_constraint(eq2, values, table, n)))
    z3_solver.add(z3.Or(refutations))

    if z3_solver.check() != z3.sat:
        return None
    model = z3_solver.model()
    concrete = [[int(str(model.evaluate(table[row][col], model_completion=True))) for col in range(n)] for row in range(n)]
    if not solver_module.table_is_counterexample(eq1, eq2, concrete):
        raise RuntimeError("Z3 model failed semantic counterexample validation")
    return concrete


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--id", required=True, help="Problem id to mine from the fixture.")
    parser.add_argument("--min-n", type=int, default=2)
    parser.add_argument("--max-n", type=int, default=6)
    parser.add_argument("--timeout-ms", type=int, default=30000)
    args = parser.parse_args()

    solver_module = load_solver()
    rows = load_rows(args.fixture)
    selected = [row for row in rows if str(row.get("id")) == args.id]
    if not selected:
        raise SystemExit(f"problem id not found in fixture: {args.id}")
    problem = selected[0]

    for n in range(args.min_n, args.max_n + 1):
        table = mine_countermodel(solver_module, problem, n=n, timeout_ms=args.timeout_ms)
        if table is None:
            print(json.dumps({"id": args.id, "n": n, "status": "unsat_or_timeout"}, separators=(",", ":")))
            continue
        print(
            json.dumps(
                {
                    "id": args.id,
                    "n": n,
                    "status": "sat",
                    "table": table,
                },
                separators=(",", ":"),
            )
        )
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
