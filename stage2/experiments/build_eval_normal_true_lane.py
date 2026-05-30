#!/usr/bin/env python3
"""Build the evaluation_normal TRUE-lane discovery fixture.

This is a development helper only. The generated manifest lives under
tmp_stage2_smoke/ and keeps the Hugging Face evaluation_normal subset clearly
separate from official public promotion evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOURCE = REPO_ROOT / "data" / "hf_cache" / "evaluation_normal.jsonl"
DEFAULT_SOLVER = REPO_ROOT / "stage2" / "solver" / "solver.py"
DEFAULT_TMP = REPO_ROOT / "tmp_stage2_smoke"


def load_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] == "[":
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [row for row in payload if isinstance(row, dict)]
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        if line.strip():
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def load_solver(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("eval_normal_true_lane_solver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import solver from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def deterministic_record(
    solver: Any,
    row: dict[str, Any],
    *,
    false_time_budget: float | None,
    source: Path,
    source_index: int,
) -> dict[str, Any]:
    route = "skip:none"
    verdict = None
    priority: tuple[Any, ...] | None = None
    llm_priority: tuple[Any, ...] | None = None
    try:
        solved = solver.solve_problem(row, false_time_budget=false_time_budget)
        if isinstance(solved, dict):
            route = str(solved.get("route", route))
            answer = solved.get("answer")
            if isinstance(answer, dict):
                verdict = answer.get("verdict")
            raw_priority = solved.get("priority")
            if isinstance(raw_priority, tuple):
                priority = raw_priority
        eq1 = solver.parse_equation(str(row["equation1"]))
        eq2 = solver.parse_equation(str(row["equation2"]))
        if priority is None:
            priority = solver.problem_priority(row, eq1, eq2)
        llm_priority = solver.llm_problem_priority(priority, row)
    except Exception as exc:  # noqa: BLE001
        route = f"skip:error:{type(exc).__name__}"

    return {
        "source": "evaluation_normal",
        "source_path": rel(source),
        "source_row_index": source_index,
        "analysis_only": True,
        "id": row.get("id"),
        "eq1_id": row.get("eq1_id"),
        "eq2_id": row.get("eq2_id"),
        "equation1": row.get("equation1"),
        "equation2": row.get("equation2"),
        "expected": row.get("answer"),
        "deterministic_route": route,
        "deterministic_verdict": verdict,
        "deterministic_priority": list(priority) if priority is not None else None,
        "llm_priority": list(llm_priority) if llm_priority is not None else None,
    }


def sort_key(record: dict[str, Any]) -> tuple[int, list[Any], int, str]:
    route = str(record.get("deterministic_route") or "skip:none")
    unresolved_rank = 0 if route == "skip:none" or route.startswith("skip:error:") else 1
    priority = record.get("llm_priority")
    if not isinstance(priority, list):
        priority = [9, 9, 9999, str(record.get("id", ""))]
    return (unresolved_rank, priority, int(record.get("source_row_index") or 0), str(record.get("id", "")))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--solver", type=Path, default=DEFAULT_SOLVER)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--false-time-budget", type=float, default=4.0)
    parser.add_argument("--date-label", default=f"{datetime.now():%Y-%m-%d}")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--ledger-output", type=Path, default=None)
    parser.add_argument("--meta-output", type=Path, default=None)
    args = parser.parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")
    source = args.source.resolve()
    solver_path = args.solver.resolve()
    output = (
        args.output
        or DEFAULT_TMP / f"{args.date_label}-eval-normal-true100.jsonl"
    ).resolve()
    ledger_output = (
        args.ledger_output
        or output.with_name(output.stem + "-ledger.jsonl")
    ).resolve()
    meta_output = (
        args.meta_output
        or output.with_name(output.stem + "-meta.json")
    ).resolve()

    rows = load_rows(source)
    true_rows = [(idx, row) for idx, row in enumerate(rows, 1) if row.get("answer") is True]
    solver = load_solver(solver_path)
    ledger = [
        deterministic_record(
            solver,
            row,
            false_time_budget=args.false_time_budget,
            source=source,
            source_index=idx,
        )
        for idx, row in true_rows
    ]
    ledger.sort(key=sort_key)
    selected_ids = {str(row.get("id")) for row in ledger[: args.limit]}
    selected_rows = [row for _idx, row in true_rows if str(row.get("id")) in selected_ids]
    selected_rows_by_id = {str(row.get("id")): row for row in selected_rows}
    ordered_rows = [selected_rows_by_id[str(record["id"])] for record in ledger[: args.limit]]

    write_jsonl(output, ordered_rows)
    write_jsonl(ledger_output, ledger[: args.limit])
    meta = {
        "label": "evaluation_normal_true_lane",
        "analysis_only": True,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": rel(source),
        "solver": rel(solver_path),
        "manifest": rel(output),
        "ledger": rel(ledger_output),
        "limit": args.limit,
        "true_rows_available": len(true_rows),
        "selected_rows": len(ordered_rows),
        "false_time_budget": args.false_time_budget,
        "deterministic_skips_selected": sum(
            1 for record in ledger[: args.limit] if record.get("deterministic_route") == "skip:none"
        ),
    }
    meta_output.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"selected_rows={len(ordered_rows)} true_rows_available={len(true_rows)}")
    print(f"deterministic_skips_selected={meta['deterministic_skips_selected']}")
    print(f"manifest={output}")
    print(f"ledger={ledger_output}")
    print(f"meta={meta_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
