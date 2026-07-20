#!/usr/bin/env python3
"""Profile deterministic Stage 2 solver routes without judge or LLM calls."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import importlib.util
import json
from pathlib import Path
import re
import statistics
import subprocess
import sys
import time
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems" / "marathon" / "normal_100.jsonl"
DEFAULT_SOLVER = REPO_ROOT / "stage2" / "solver" / "solver.py"
DEFAULT_OUTPUT = REPO_ROOT / "tmp_stage2_smoke" / "solver_route_profile.json"


def load_rows(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if not stripped:
        return []
    if stripped[0] == "[":
        payload = json.loads(text)
        if not isinstance(payload, list):
            raise ValueError(f"Expected JSON array in {path}")
        return [entry for entry in payload if isinstance(entry, dict)]
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            if isinstance(entry, dict):
                rows.append(entry)
    return rows


def load_solver(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("stage2_profiled_solver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import solver from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve_git_commit(revision: str) -> str:
    if not revision or revision.startswith("-") or ":" in revision:
        raise ValueError("--solver-git-ref must be a non-option Git revision without ':'")
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"{revision}^{{commit}}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    commit = completed.stdout.strip()
    if completed.returncode != 0 or not re.fullmatch(r"[0-9a-fA-F]{40}", commit):
        message = completed.stderr.strip() or "git rev-parse failed"
        raise RuntimeError(f"Cannot resolve Git revision {revision!r} to a commit: {message}")
    return commit.lower()


def load_solver_git_revision(revision: str, path: Path) -> tuple[Any, str]:
    try:
        repo_path = path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise ValueError("--solver must be inside the repository when --solver-git-ref is used") from exc
    commit = resolve_git_commit(revision)
    completed = subprocess.run(
        ["git", "show", f"{commit}:{repo_path}"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if completed.returncode != 0:
        message = completed.stderr.strip() or "git show failed"
        raise RuntimeError(f"Cannot load {commit}:{repo_path}: {message}")
    module_name = "stage2_profiled_solver_git"
    module = type(sys)(module_name)
    module.__file__ = f"{commit}:{repo_path}"
    exec(compile(completed.stdout, module.__file__, "exec"), module.__dict__)
    return module, commit


def cold_import_run(path: Path) -> float:
    code = (
        "import importlib.util,json,time;"
        "path=r'''" + str(path) + "''';"
        "start=time.perf_counter();"
        "spec=importlib.util.spec_from_file_location('stage2_cold_solver',path);"
        "module=importlib.util.module_from_spec(spec);"
        "spec.loader.exec_module(module);"
        "print(json.dumps({'seconds':time.perf_counter()-start}))"
    )
    completed = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout.strip().splitlines()[-1])
    return float(payload["seconds"])


def cold_import_stats(path: Path, repeats: int) -> dict[str, Any]:
    if repeats <= 0:
        return {"runs": []}
    runs = [cold_import_run(path) for _repeat_index in range(repeats)]
    return {
        "runs": runs,
        "min": min(runs),
        "median": statistics.median(runs),
        "max": max(runs),
    }


def priority_for(module: Any, problem: dict[str, Any]) -> tuple[int, int, str]:
    try:
        equation_one = module.parse_equation(str(problem["equation1"]))
        equation_two = module.parse_equation(str(problem["equation2"]))
        return module.problem_priority(problem, equation_one, equation_two)
    except Exception:  # noqa: BLE001
        return (9, 0, "skip:parse_error")


def maybe_sort_rows(module: Any, rows: list[dict[str, Any]], sort_by_priority: bool) -> list[dict[str, Any]]:
    selected = [dict(row) for row in rows]
    if sort_by_priority:
        selected.sort(key=lambda problem: priority_for(module, problem))
    return selected


def resolve_false_time_budget(module: Any, args: argparse.Namespace, row_count: int) -> float | None:
    if args.false_time_budget is not None:
        return args.false_time_budget
    if args.marathon_budget_seconds is None:
        return None
    return float(
        module.marathon_per_problem_budget(
            float(args.marathon_budget_seconds),
            row_count,
            float(args.reference_seconds_per_problem),
        )
    )


def profile_rows(
    module: Any,
    rows: list[dict[str, Any]],
    *,
    false_time_budget: float | None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    details: list[dict[str, Any]] = []
    elapsed_by_route: dict[str, list[float]] = defaultdict(list)
    expected_by_route: dict[str, Counter[str]] = defaultdict(Counter)
    verdict_by_route: dict[str, Counter[str]] = defaultdict(Counter)
    route_counts: Counter[str] = Counter()
    started = time.perf_counter()

    for index, problem in enumerate(rows, 1):
        row_started = time.perf_counter()
        record = module.solve_problem(problem, false_time_budget=false_time_budget)
        elapsed = time.perf_counter() - row_started
        answer = record.get("answer") if isinstance(record, dict) else None
        route = str(record.get("route")) if isinstance(record, dict) else "skip:none"
        verdict = answer.get("verdict") if isinstance(answer, dict) else None
        code = str(answer.get("code", "")) if isinstance(answer, dict) else ""
        expected_value = problem.get("answer")
        if expected_value is True:
            expected = "true"
        elif expected_value is False:
            expected = "false"
        else:
            expected = "unknown"

        route_counts[route] += 1
        elapsed_by_route[route].append(elapsed)
        expected_by_route[route][expected] += 1
        verdict_by_route[route][str(verdict)] += 1
        details.append(
            {
                "order": index,
                "id": problem.get("id"),
                "eq1_id": problem.get("eq1_id"),
                "eq2_id": problem.get("eq2_id"),
                "expected": expected,
                "route": route,
                "verdict": verdict,
                "elapsed_seconds": elapsed,
                "code_bytes": len(code.encode("utf-8")) if code else 0,
            }
        )

    total_elapsed = time.perf_counter() - started
    routes: dict[str, Any] = {}
    for route, values in sorted(elapsed_by_route.items()):
        routes[route] = {
            "count": route_counts[route],
            "elapsed_total": sum(values),
            "elapsed_mean": statistics.mean(values),
            "elapsed_median": statistics.median(values),
            "elapsed_max": max(values),
            "expected": dict(expected_by_route[route]),
            "verdicts": dict(verdict_by_route[route]),
        }

    summary = {
        "rows": len(rows),
        "false_time_budget": false_time_budget,
        "elapsed_total": total_elapsed,
        "throughput_rows_per_second": (len(rows) / total_elapsed) if total_elapsed > 0 else None,
        "candidate_count": sum(1 for detail in details if detail["route"] != "skip:none"),
        "skip_count": sum(1 for detail in details if detail["route"] == "skip:none"),
        "route_counts": dict(route_counts),
        "routes": routes,
        "slowest": sorted(details, key=lambda detail: detail["elapsed_seconds"], reverse=True)[:20],
    }
    return details, summary


def family_benchmarks(module: Any, max_n: int) -> dict[str, Any]:
    benchmarks: dict[str, Any] = {}
    for name in ("structured_family_tables", "affine_family_tables", "quadratic_family_tables"):
        function = getattr(module, name)
        started = time.perf_counter()
        count = sum(1 for _route, _table in function(max_n=max_n))
        benchmarks[name] = {
            "count": count,
            "elapsed_seconds": time.perf_counter() - started,
            "max_n": max_n,
        }
    return benchmarks


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--solver", type=Path, default=DEFAULT_SOLVER)
    parser.add_argument("--solver-git-ref", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--details-output", type=Path, default=None)
    parser.add_argument("--false-time-budget", type=float, default=None)
    parser.add_argument("--marathon-budget-seconds", type=float, default=600.0)
    parser.add_argument("--reference-seconds-per-problem", type=float, default=600.0)
    parser.add_argument("--no-sort-by-priority", dest="sort_by_priority", action="store_false")
    parser.add_argument("--cold-import-repeats", type=int, default=3)
    parser.add_argument("--family-max-n", type=int, default=5)
    parser.add_argument("--skip-family-benchmarks", action="store_true")
    args = parser.parse_args()

    args.manifest = args.manifest.resolve()
    args.solver = args.solver.resolve()
    args.output = args.output.resolve()
    if args.details_output is None:
        args.details_output = args.output.with_suffix(".jsonl")
    else:
        args.details_output = args.details_output.resolve()

    rows = load_rows(args.manifest)
    if args.limit is not None:
        rows = rows[: args.limit]
    solver_git_commit: str | None = None
    if args.solver_git_ref:
        solver, solver_git_commit = load_solver_git_revision(args.solver_git_ref, args.solver)
    else:
        solver = load_solver(args.solver)
    rows = maybe_sort_rows(solver, rows, args.sort_by_priority)
    false_time_budget = resolve_false_time_budget(solver, args, len(rows))
    details, summary = profile_rows(solver, rows, false_time_budget=false_time_budget)
    summary.update(
        {
            "manifest": str(args.manifest.relative_to(REPO_ROOT)) if args.manifest.is_relative_to(REPO_ROOT) else str(args.manifest),
            "solver": (
                f"{args.solver_git_ref}:"
                + (str(args.solver.relative_to(REPO_ROOT)).replace("\\", "/") if args.solver.is_relative_to(REPO_ROOT) else str(args.solver))
                if args.solver_git_ref
                else (str(args.solver.relative_to(REPO_ROOT)) if args.solver.is_relative_to(REPO_ROOT) else str(args.solver))
            ),
            "solver_git_ref": args.solver_git_ref,
            "solver_git_commit": solver_git_commit,
            "sort_by_priority": args.sort_by_priority,
            "marathon_budget_seconds": args.marathon_budget_seconds,
            "reference_seconds_per_problem": args.reference_seconds_per_problem,
            "cold_import": (
                {"runs": [], "skipped": "solver loaded from git revision"}
                if args.solver_git_ref
                else cold_import_stats(args.solver, args.cold_import_repeats)
            ),
        }
    )
    if not args.skip_family_benchmarks:
        summary["family_benchmarks"] = family_benchmarks(solver, args.family_max_n)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    write_jsonl(args.details_output, details)

    print(f"profile_rows={summary['rows']} candidates={summary['candidate_count']} skips={summary['skip_count']}")
    print(f"elapsed_total={summary['elapsed_total']:.3f}s false_time_budget={false_time_budget}")
    print(f"output={args.output}")
    print(f"details={args.details_output}")
    for route, count in sorted(summary["route_counts"].items(), key=lambda item: (-item[1], item[0]))[:12]:
        route_elapsed = summary["routes"][route]["elapsed_total"]
        print(f"route={route} count={count} elapsed_total={route_elapsed:.3f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
