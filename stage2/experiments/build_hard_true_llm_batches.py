#!/usr/bin/env python3
"""Build hard unresolved-TRUE fixtures for LLM-assisted proof mining.

The output fixture can be fed to the official Solo or Marathon runners. The
ledger keeps public hard evidence separate from Hugging Face/evaluation rows,
which are discovery-only unless promoted elsewhere.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SOLVER = REPO_ROOT / "stage2" / "solver" / "solver.py"
DEFAULT_FIXTURE = REPO_ROOT / "tmp_stage2_smoke" / "hard_true_llm_discovery_fixture.jsonl"
DEFAULT_LEDGER = REPO_ROOT / "tmp_stage2_smoke" / "hard_true_llm_discovery_ledger.jsonl"
PUBLIC_PROBLEMS = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
HF_CACHE = REPO_ROOT / "data" / "hf_cache"

SOURCES: tuple[tuple[str, bool, Path], ...] = (
    ("public_hard1", True, PUBLIC_PROBLEMS / "hard1.jsonl"),
    ("public_hard2", True, PUBLIC_PROBLEMS / "hard2.jsonl"),
    ("public_hard3", True, PUBLIC_PROBLEMS / "hard3.jsonl"),
    ("hf_hard", False, HF_CACHE / "hard.jsonl"),
    ("hf_hard1", False, HF_CACHE / "hard1.jsonl"),
    ("hf_hard2", False, HF_CACHE / "hard2.jsonl"),
    ("hf_hard3", False, HF_CACHE / "hard3.jsonl"),
    ("evaluation_hard", False, HF_CACHE / "evaluation_hard.jsonl"),
    ("evaluation_extra_hard", False, HF_CACHE / "evaluation_extra_hard.jsonl"),
)


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
    spec = importlib.util.spec_from_file_location("hard_true_llm_solver", path)
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


def motif_hint(solver: Any, eq1: dict[str, Any], eq2: dict[str, Any]) -> str:
    if solver.absorption_hypothesis(eq1):
        return "absorption_or_collapse_guided_chain"
    if solver.projection_law_route(eq1):
        return "projection_normalization_chain"
    if solver.projection_cue(eq1, eq2):
        return "boundary_change_guided_chain_or_false_check"
    if eq1["lhs"][0] == "var" or eq1["rhs"][0] == "var":
        return "variable_side_theorem_chain"
    return "product_product_congruence_chain"


def problem_key(row: dict[str, Any]) -> tuple[Any, Any, str, str]:
    return (
        row.get("eq1_id"),
        row.get("eq2_id"),
        str(row.get("equation1", "")),
        str(row.get("equation2", "")),
    )


def unresolved_true_records(
    solver: Any,
    *,
    false_time_budget: float | None,
    scan_limit_per_source: int | None,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[Any, Any, str, str]] = set()
    for source_name, is_public, path in SOURCES:
        if not path.exists():
            continue
        for row_index, row in enumerate(load_rows(path), 1):
            if scan_limit_per_source is not None and row_index > scan_limit_per_source:
                break
            if row.get("answer") is not True:
                continue
            key = problem_key(row)
            if key in seen:
                continue
            seen.add(key)
            solved = solver.solve_problem(row, false_time_budget=false_time_budget)
            if solved is not None:
                continue
            try:
                eq1 = solver.parse_equation(str(row["equation1"]))
                eq2 = solver.parse_equation(str(row["equation2"]))
                priority = solver.problem_priority(row, eq1, eq2)
                llm_priority = solver.llm_problem_priority(priority, row)
                motif = motif_hint(solver, eq1, eq2)
            except Exception as exc:  # noqa: BLE001
                priority = (9, 0, "parse_error")
                llm_priority = (9, 9, 0, str(row.get("id", "")))
                motif = f"parse_error:{type(exc).__name__}"
            records.append(
                {
                    "source": source_name,
                    "source_path": rel(path),
                    "source_row_index": row_index,
                    "public_official": is_public,
                    "id": row.get("id"),
                    "eq1_id": row.get("eq1_id"),
                    "eq2_id": row.get("eq2_id"),
                    "equation1": row.get("equation1"),
                    "equation2": row.get("equation2"),
                    "expected": row.get("answer"),
                    "deterministic_skip_route": "skip:none",
                    "deterministic_priority": list(priority),
                    "llm_priority": list(llm_priority),
                    "llm_response_kind": "not_run",
                    "rejection_reason": "not_run",
                    "judge_status": "not_run",
                    "next_motif_hypothesis": motif,
                    "problem": row,
                }
            )
    records.sort(key=lambda record: (record["llm_priority"], not record["public_official"], str(record["id"])))
    return records


def select_batch(records: list[dict[str, Any]], limit: int, *, require_public: bool) -> list[dict[str, Any]]:
    if limit <= 0:
        return []
    selected: list[dict[str, Any]] = []
    public = [record for record in records if record["public_official"]]
    other = [record for record in records if not record["public_official"]]
    if require_public:
        if not public:
            raise SystemExit("no unresolved public hard TRUE rows found")
        selected.append(public.pop(0))
    pools = [public, other]
    while len(selected) < limit and any(pools):
        progressed = False
        for pool in pools:
            if pool and len(selected) < limit:
                selected.append(pool.pop(0))
                progressed = True
        if not progressed:
            break
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--solver", type=Path, default=DEFAULT_SOLVER)
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--false-time-budget", type=float, default=0.02)
    parser.add_argument("--scan-limit-per-source", type=int, default=None)
    parser.add_argument("--fixture-output", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--ledger-output", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--allow-no-public", action="store_true")
    parser.add_argument("--list-sources", action="store_true")
    args = parser.parse_args()

    if args.list_sources:
        for source_name, is_public, path in SOURCES:
            print(f"{source_name} public={str(is_public).lower()} path={rel(path)} exists={path.exists()}")
        return 0
    if args.limit <= 0:
        raise SystemExit("--limit must be positive")
    if args.scan_limit_per_source is not None and args.scan_limit_per_source <= 0:
        raise SystemExit("--scan-limit-per-source must be positive when supplied")

    solver = load_solver(args.solver.resolve())
    records = unresolved_true_records(
        solver,
        false_time_budget=args.false_time_budget,
        scan_limit_per_source=args.scan_limit_per_source,
    )
    batch = select_batch(records, args.limit, require_public=not args.allow_no_public)
    fixture_rows = [record["problem"] for record in batch]
    ledger_rows = [{key: value for key, value in record.items() if key != "problem"} for record in batch]

    write_jsonl(args.fixture_output.resolve(), fixture_rows)
    write_jsonl(args.ledger_output.resolve(), ledger_rows)
    print(f"candidate_records={len(records)} selected={len(batch)} public_selected={sum(1 for row in ledger_rows if row['public_official'])}")
    print(f"fixture_output={args.fixture_output.resolve()}")
    print(f"ledger_output={args.ledger_output.resolve()}")
    print("ids=" + ",".join(str(row.get("id")) for row in fixture_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
