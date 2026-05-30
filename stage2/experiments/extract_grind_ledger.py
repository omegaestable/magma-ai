#!/usr/bin/env python3
"""Extract exact true:grind ledgers from analyzed Marathon run dirs.

This joins `answers.jsonl` with the official runner `summary.json` status rows.
The output is intended for regression fixtures and route triage, not solver policy.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from analyze_marathon_run import answer_kind, load_answers, load_json, load_problem_rows, manifest_from_launcher


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))

from solver import absorption_hypothesis, parse_equation, term_depth, term_size  # noqa: E402


def lane_name(run_dir: Path) -> str:
    return run_dir.name


def grind_features(problem: dict[str, Any]) -> dict[str, Any]:
    eq1 = parse_equation(str(problem.get("equation1", "")))
    eq2 = parse_equation(str(problem.get("equation2", "")))
    sizes = [term_size(eq1["lhs"]), term_size(eq1["rhs"]), term_size(eq2["lhs"]), term_size(eq2["rhs"])]
    depths = [term_depth(eq1["lhs"]), term_depth(eq1["rhs"]), term_depth(eq2["lhs"]), term_depth(eq2["rhs"])]
    return {
        "eq1_var_count": len(eq1["variables"]),
        "eq2_var_count": len(eq2["variables"]),
        "max_term_size": max(sizes),
        "max_term_depth": max(depths),
        "absorption_hypothesis": absorption_hypothesis(eq1),
        "same_lhs": eq1["lhs"] == eq2["lhs"],
        "rhs_matches_goal_lhs": eq1["rhs"] == eq2["lhs"],
    }


def grind_rows(run_dir: Path) -> list[dict[str, Any]]:
    manifest = manifest_from_launcher(run_dir)
    problems = {str(row.get("id")): row for row in load_problem_rows(manifest)}
    answers = load_answers(run_dir / "answers.jsonl")
    summary = load_json(run_dir / "summary.json")
    statuses = {str(row.get("id")): row for row in summary.get("per_problem", []) if isinstance(row, dict)}
    lane = lane_name(run_dir)
    rows: list[dict[str, Any]] = []
    for problem_id, answer in sorted(answers.items()):
        if answer_kind(answer) != "true:grind":
            continue
        status_row = statuses.get(problem_id, {})
        problem = problems.get(problem_id, {"id": problem_id})
        code = str(answer.get("code", ""))
        rows.append(
            {
                "lane": lane,
                "id": problem_id,
                "status": status_row.get("status"),
                "verdict": status_row.get("verdict"),
                "expected": problem.get("answer"),
                "answer": problem.get("answer"),
                "eq1_id": problem.get("eq1_id"),
                "eq2_id": problem.get("eq2_id"),
                "equation1": problem.get("equation1"),
                "equation2": problem.get("equation2"),
                "code_bytes": len(code.encode("utf-8")),
                **grind_features(problem),
            }
        )
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dirs", nargs="+", type=Path)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args()

    all_rows: list[dict[str, Any]] = []
    for run_dir in args.run_dirs:
        all_rows.extend(grind_rows(run_dir.resolve()))

    accepted = [row for row in all_rows if row.get("status") == "accepted"]
    incorrect = [row for row in all_rows if row.get("status") == "incorrect"]
    other = [row for row in all_rows if row.get("status") not in {"accepted", "incorrect"}]
    write_jsonl(args.out_dir / "true_grind_all.jsonl", all_rows)
    write_jsonl(args.out_dir / "true_grind_accepted.jsonl", accepted)
    write_jsonl(args.out_dir / "true_grind_incorrect.jsonl", incorrect)
    if other:
        write_jsonl(args.out_dir / "true_grind_other.jsonl", other)

    by_lane_status: Counter[tuple[str, str]] = Counter((str(row.get("lane")), str(row.get("status"))) for row in all_rows)
    print(f"wrote {len(all_rows)} true:grind rows to {args.out_dir}")
    for (lane, status), count in sorted(by_lane_status.items()):
        print(f"{lane}\t{status}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
