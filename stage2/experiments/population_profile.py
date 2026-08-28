#!/usr/bin/env python3
"""Profile the shape distribution of benchmark sets against the ETP matrix.

Written 2026-08-27 for the population-calibration measurement: every unseen
sweep so far was a *uniform* catalog draw, while the private evaluation set has
four fixed categories.  This script answers "is the official hard/extra-hard
population shaped like a uniform draw?" by tabulating, for each set:

  * eq1 / eq2 operation count (number of magma operators in the term)
  * eq1 / eq2 distinct-variable count
  * fraction of rows whose eq1 has a bare variable on one side
  * TRUE / FALSE balance

Measurement only: nothing here is imported by the solver.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

import solver as S  # noqa: E402

OFFICIAL = REPO_ROOT / "data" / "stage2_official_problems"
HF = REPO_ROOT / "data" / "hf_cache"

SETS = {
    "official_normal": OFFICIAL / "normal.jsonl",
    "official_hard1": OFFICIAL / "hard1.jsonl",
    "official_hard2": OFFICIAL / "hard2.jsonl",
    "official_hard3": OFFICIAL / "hard3.jsonl",
    "hf_evaluation_normal": HF / "evaluation_normal.jsonl",
    "hf_evaluation_hard": HF / "evaluation_hard.jsonl",
    "hf_evaluation_extra_hard": HF / "evaluation_extra_hard.jsonl",
    "hf_evaluation_order5": HF / "evaluation_order5.jsonl",
}


def load(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(ln) for ln in text.splitlines() if ln.strip()]
    return json.loads(text)


def ops(term) -> int:
    if term[0] == "var":
        return 0
    return 1 + ops(term[1]) + ops(term[2])


def eq_shape(text: str) -> tuple[int, int, bool]:
    """(operation count, distinct variable count, bare-variable-side?)"""
    eq = S.parse_equation(text)
    n_ops = ops(eq["lhs"]) + ops(eq["rhs"])
    n_vars = len(eq["variables"])
    bare = eq["lhs"][0] == "var" or eq["rhs"][0] == "var"
    return n_ops, n_vars, bare


def row_shape(row: dict) -> dict:
    o1, v1, b1 = eq_shape(row["equation1"])
    o2, v2, _ = eq_shape(row["equation2"])
    return {
        "id": row.get("id"),
        "eq1_id": row.get("eq1_id"),
        "eq2_id": row.get("eq2_id"),
        "eq1_ops": o1, "eq1_vars": v1, "eq1_bare": b1,
        "eq2_ops": o2, "eq2_vars": v2,
        "answer": row.get("answer"),
    }


def dist(counter: Counter, total: int) -> dict:
    return {str(k): round(100.0 * counter[k] / total, 2) for k in sorted(counter)}


def profile(rows: list[dict]) -> dict:
    shapes = [row_shape(r) for r in rows]
    n = len(shapes)
    out = {
        "n": n,
        "eq1_ops_pct": dist(Counter(s["eq1_ops"] for s in shapes), n),
        "eq1_vars_pct": dist(Counter(s["eq1_vars"] for s in shapes), n),
        "eq2_ops_pct": dist(Counter(s["eq2_ops"] for s in shapes), n),
        "eq2_vars_pct": dist(Counter(s["eq2_vars"] for s in shapes), n),
        "eq1_bare_pct": round(100.0 * sum(1 for s in shapes if s["eq1_bare"]) / n, 2),
        "true_pct": round(100.0 * sum(1 for s in shapes if s["answer"] is True) / n, 2),
        "joint_ops_vars_pct": dist(
            Counter((s["eq1_ops"], s["eq1_vars"]) for s in shapes), n),
        "max_eq_id": max([s["eq1_id"] or 0 for s in shapes]
                         + [s["eq2_id"] or 0 for s in shapes]),
    }
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--extra", type=Path, nargs="*", default=[],
                    help="additional jsonl batches to profile")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    report: dict[str, dict] = {}
    for name, path in SETS.items():
        report[name] = profile(load(path))
    for path in args.extra:
        report[path.stem] = profile(load(path))

    for name, prof in report.items():
        print(f"\n=== {name}  (n={prof['n']}, TRUE {prof['true_pct']}%, "
              f"eq1 bare-var side {prof['eq1_bare_pct']}%, "
              f"max eq id {prof['max_eq_id']}) ===")
        print(f"  eq1 ops  : {prof['eq1_ops_pct']}")
        print(f"  eq1 vars : {prof['eq1_vars_pct']}")
        print(f"  eq2 ops  : {prof['eq2_ops_pct']}")
        print(f"  eq2 vars : {prof['eq2_vars_pct']}")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
