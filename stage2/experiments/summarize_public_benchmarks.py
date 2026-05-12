#!/usr/bin/env python3
"""Summarize Stage 2 public benchmark runner outputs.

This script joins official problem manifests with pipeline.runner JSON outputs,
then writes a markdown summary and an unsolved-problem ledger with route labels.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
PROBLEMS_DIR = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
RESULTS_DIR = REPO_ROOT / "stage2" / "results"
DEFAULT_SETS = ("normal", "hard1", "hard2", "hard3")

WITNESS_TABLES = {
    "LP": [[0, 0], [1, 1]],
    "RP": [[0, 1], [0, 1]],
    "C0": [[0, 0], [0, 0]],
    "XOR": [[0, 1], [1, 0]],
    "AND": [[0, 0], [0, 1]],
    "OR": [[0, 1], [1, 1]],
    "XNOR": [[1, 0], [0, 1]],
    "A2": [[0, 0], [1, 0]],
    "Z3A": [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
    "T3L": [[0, 0, 0], [0, 0, 0], [0, 1, 0]],
    "T3R": [[0, 0, 0], [0, 0, 0], [0, 0, 1]],
}
AFFINE_SIZES = (2, 3, 5)


def load_manifest(name: str) -> list[dict[str, Any]]:
    path = PROBLEMS_DIR / f"{name}.jsonl"
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_results(date: str, name: str) -> dict[str, dict[str, Any]]:
    path = RESULTS_DIR / f"{date}-{name}-finite-countermodels.json"
    if not path.exists():
        return {}
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["id"]: row for row in rows}


def code_table(code: str) -> tuple[int | None, list[list[int]] | None]:
    size_match = re.search(r"Magma \(Fin (\d+)\)", code)
    table_match = re.search(r'finOpTable "([^"]+)"', code)
    if not table_match:
        return None, None
    try:
        table = json.loads(table_match.group(1))
    except json.JSONDecodeError:
        return None, None
    size = int(size_match.group(1)) if size_match else len(table)
    return size, table


def stderr_route(result: dict[str, Any]) -> str | None:
    for item in reversed(result.get("log", [])):
        if item.get("type") != "solver_stderr":
            continue
        tail = item.get("tail")
        if not isinstance(tail, str):
            continue
        try:
            payload = json.loads(tail.strip())
        except json.JSONDecodeError:
            continue
        route = payload.get("route")
        if isinstance(route, str) and route:
            return route
    return None


def affine_route(table: list[list[int]]) -> str | None:
    n = len(table)
    if n not in AFFINE_SIZES:
        return None
    for a in range(n):
        for b in range(n):
            for c in range(n):
                candidate = [[(a * x + b * y + c) % n for y in range(n)] for x in range(n)]
                if candidate == table:
                    if c == 0:
                        return f"false:linear:z{n}:{a},{b}"
                    return f"false:affine:z{n}:{a},{b},{c}"
    return None


def route_label(problem: dict[str, Any], result: dict[str, Any]) -> str:
    routed = stderr_route(result)
    if routed:
        return routed

    verdict = result.get("verdict")
    if verdict == "true" and problem.get("eq1_id") == problem.get("eq2_id"):
        return "true:reflexive"
    if verdict == "true":
        code = str(result.get("code", ""))
        if "have hall : ∀ a b : G, a = b" in code:
            return "true:singleton"
        if ".trans" in code:
            return "true:bridge_or_rewrite"
        return "true:rewrite_or_template"
    if verdict != "false":
        return f"{verdict or 'unknown'}:unlabeled"

    size, table = code_table(str(result.get("code", "")))
    if table is None:
        return "false:unknown_countermodel"
    for name, witness in WITNESS_TABLES.items():
        if table == witness:
            return f"false:witness:{name}"
    affine = affine_route(table)
    if affine:
        return affine
    return f"false:enum_fin{size or len(table)}"


def next_family(problem: dict[str, Any]) -> str:
    expected = problem.get("answer")
    if expected is False:
        return "finite_countermodel_gap"
    if expected is True and problem.get("eq1_id") == problem.get("eq2_id"):
        return "reflexive_true_regression"
    if expected is True:
        return "true_template_gap"
    return "unknown_public_label"


def summarize(date: str, sets: tuple[str, ...], summary_path: Path, ledger_path: Path) -> None:
    set_rows = []
    route_counts: Counter[str] = Counter()
    next_family_counts: Counter[str] = Counter()
    total = Counter()
    ledger_rows = []

    for name in sets:
        problems = load_manifest(name)
        results = load_results(date, name)
        row = Counter({"problems": len(problems), "result_rows": len(results)})

        for problem in problems:
            expected = problem.get("answer")
            row[f"expected_{str(expected).lower()}"] += 1
            result = results.get(problem["id"])
            if not result:
                row["missing_result"] += 1
                ledger_rows.append(ledger_entry(name, problem, None, "missing_result"))
                continue

            if result.get("solved"):
                route = route_label(problem, result)
                row["solved"] += 1
                row[f"solved_{result.get('verdict', 'unknown')}"] += 1
                row["llm_calls"] += int(result.get("llm_calls", 0) or 0)
                row["judge_calls"] += int(result.get("judge_calls", 0) or 0)
                row["elapsed_seconds"] += float(result.get("elapsed_seconds", 0) or 0)
                route_counts[route] += 1
            else:
                row["failed"] += 1
                row["llm_calls"] += int(result.get("llm_calls", 0) or 0)
                row["judge_calls"] += int(result.get("judge_calls", 0) or 0)
                row["elapsed_seconds"] += float(result.get("elapsed_seconds", 0) or 0)
                ledger = ledger_entry(name, problem, result, "failed")
                next_family_counts[ledger["next_suspected_family"]] += 1
                ledger_rows.append(ledger)

        set_rows.append((name, row))
        total.update(row)

    write_summary(summary_path, date, set_rows, total, route_counts, next_family_counts)
    with ledger_path.open("w", encoding="utf-8") as handle:
        for row in ledger_rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def ledger_entry(
    source_set: str,
    problem: dict[str, Any],
    result: dict[str, Any] | None,
    status: str,
) -> dict[str, Any]:
    judge_status = None
    if result:
        judge_status = result.get("judge_status") or result.get("status")
    attempted = "deterministic_skip"
    if result and result.get("judge_calls"):
        attempted = route_label(problem, result)
    return {
        "id": problem["id"],
        "source_set": source_set,
        "eq1_id": problem.get("eq1_id"),
        "eq2_id": problem.get("eq2_id"),
        "expected_public_answer": problem.get("answer"),
        "attempted_route": attempted,
        "runner_status": status,
        "judge_status": judge_status,
        "judge_calls": int(result.get("judge_calls", 0) or 0) if result else 0,
        "llm_calls": int(result.get("llm_calls", 0) or 0) if result else 0,
        "elapsed_seconds": result.get("elapsed_seconds") if result else None,
        "next_suspected_family": next_family(problem),
    }


def write_summary(
    path: Path,
    date: str,
    set_rows: list[tuple[str, Counter[str]]],
    total: Counter[str],
    route_counts: Counter[str],
    next_family_counts: Counter[str],
) -> None:
    lines = [
        "# Public Finite Countermodels Summary",
        "",
        f"Date: {date}",
        "",
        "Solver artifact: `stage2/submissions/solver.py`",
        "",
        "| Set | Problems | Solved | TRUE | FALSE | Failed/missing | Expected TRUE | Expected FALSE | Judge calls | LLM calls | Runner time (s) |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, row in set_rows:
        failed = row["failed"] + row["missing_result"]
        lines.append(
            f"| `{name}` | {row['problems']} | {row['solved']} | "
            f"{row['solved_true']} | {row['solved_false']} | {failed} | "
            f"{row['expected_true']} | {row['expected_false']} | "
            f"{row['judge_calls']} | {row['llm_calls']} | {row['elapsed_seconds']:.1f} |"
        )

    failed_total = total["failed"] + total["missing_result"]
    lines.extend(
        [
            f"| **Total** | {total['problems']} | {total['solved']} | "
            f"{total['solved_true']} | {total['solved_false']} | {failed_total} | "
            f"{total['expected_true']} | {total['expected_false']} | "
            f"{total['judge_calls']} | {total['llm_calls']} | {total['elapsed_seconds']:.1f} |",
            "",
            "## Accepted Route Labels",
            "",
        ]
    )
    if route_counts:
        for route, count in route_counts.most_common():
            lines.append(f"- `{route}`: {count}")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Public `answer` fields are used only for triage labels, not solver policy.",
            "- Failed rows with zero judge calls are deterministic skips, not rejected Lean certificates.",
            "- The paired failure ledger is `stage2/results/2026-05-12-public-failure-ledger.jsonl`.",
            "",
            "## Next Families",
            "",
        ]
    )
    if next_family_counts:
        for family, count in next_family_counts.most_common():
            lines.append(f"- `{family}`: {count}")
    else:
        lines.append("- None")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="2026-05-12")
    parser.add_argument("--sets", nargs="*", default=list(DEFAULT_SETS))
    parser.add_argument(
        "--summary",
        type=Path,
        default=RESULTS_DIR / "2026-05-12-public-finite-countermodels-summary.md",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=RESULTS_DIR / "2026-05-12-public-failure-ledger.jsonl",
    )
    args = parser.parse_args()

    summarize(args.date, tuple(args.sets), args.summary, args.ledger)
    print(f"Wrote {args.summary}")
    print(f"Wrote {args.ledger}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
