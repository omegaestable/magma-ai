#!/usr/bin/env python3
"""Run reproducible positive-token Marathon sweeps across local Stage 2 corpora.

This is a development helper, not submitted solver code. It keeps official
public evidence and Hugging Face discovery evidence separated while using the
same vendored Marathon runner and packaged single-file solver for every lane.

As of 2026-05-30 this helper refuses nonpositive token budgets. Active Marathon
validation must exercise the official LLM/proxy budget path even when the
expected improvement is deterministic.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import local_runner_env


REPO_ROOT = Path(__file__).resolve().parents[2]
SOLVER_DIR = REPO_ROOT / "stage2" / "submissions"
VENDOR_PROBLEMS = REPO_ROOT / "vendor" / "stage2-official" / "examples" / "problems"
HF_CACHE = REPO_ROOT / "data" / "hf_cache"
DEFAULT_RUN_ROOT = REPO_ROOT / "tmp_stage2_smoke"


@dataclass(frozen=True)
class SweepSpec:
    name: str
    lane: str
    role: str
    manifest: Path


def official_specs() -> list[SweepSpec]:
    return [
        SweepSpec("sample_20", "official_smoke", "smoke", VENDOR_PROBLEMS / "sample_20.json"),
        SweepSpec("sample_200", "official_smoke", "smoke", VENDOR_PROBLEMS / "sample_200.json"),
        SweepSpec(
            "normal_100",
            "official_smoke",
            "marathon_smoke",
            VENDOR_PROBLEMS / "marathon" / "normal_100.jsonl",
        ),
        SweepSpec("normal", "official_public", "benchmark", VENDOR_PROBLEMS / "normal.jsonl"),
        SweepSpec("hard1", "official_public", "benchmark", VENDOR_PROBLEMS / "hard1.jsonl"),
        SweepSpec("hard2", "official_public", "benchmark", VENDOR_PROBLEMS / "hard2.jsonl"),
        SweepSpec("hard3", "official_public", "benchmark", VENDOR_PROBLEMS / "hard3.jsonl"),
    ]


def hf_specs(*, include_core_duplicates: bool) -> list[SweepSpec]:
    core = [
        SweepSpec("hf_normal", "hf_core", "benchmark_duplicate", HF_CACHE / "normal.jsonl"),
        SweepSpec("hf_hard", "hf_core", "benchmark", HF_CACHE / "hard.jsonl"),
        SweepSpec("hf_hard1", "hf_core", "benchmark_duplicate", HF_CACHE / "hard1.jsonl"),
        SweepSpec("hf_hard2", "hf_core", "benchmark_duplicate", HF_CACHE / "hard2.jsonl"),
        SweepSpec("hf_hard3", "hf_core", "benchmark_duplicate", HF_CACHE / "hard3.jsonl"),
    ]
    if not include_core_duplicates:
        core = [spec for spec in core if spec.name == "hf_hard"]
    return core + [
        SweepSpec(
            "evaluation_normal",
            "hf_analysis",
            "analysis_only",
            HF_CACHE / "evaluation_normal.jsonl",
        ),
        SweepSpec(
            "evaluation_hard",
            "hf_analysis",
            "analysis_only",
            HF_CACHE / "evaluation_hard.jsonl",
        ),
        SweepSpec(
            "evaluation_extra_hard",
            "hf_analysis",
            "analysis_only",
            HF_CACHE / "evaluation_extra_hard.jsonl",
        ),
        SweepSpec(
            "evaluation_order5",
            "hf_analysis",
            "analysis_only",
            HF_CACHE / "evaluation_order5.jsonl",
        ),
    ]


def select_specs(scope: str, *, include_core_duplicates: bool) -> list[SweepSpec]:
    official = official_specs()
    smoke = [spec for spec in official if spec.lane == "official_smoke"]
    public = [spec for spec in official if spec.lane == "official_public"]
    hf = hf_specs(include_core_duplicates=include_core_duplicates)
    if scope == "smoke":
        return smoke
    if scope == "official":
        return public
    if scope == "hf":
        return hf
    if scope == "all":
        return smoke + public + hf
    raise ValueError(f"Unknown scope: {scope}")


def load_problem_rows(path: Path) -> list[dict[str, Any]]:
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
        line = line.strip()
        if line:
            row = json.loads(line)
            if isinstance(row, dict):
                rows.append(row)
    return rows


def problem_stats(path: Path) -> dict[str, int]:
    rows = load_problem_rows(path)
    return {
        "problems": len(rows),
        "expected_true": sum(1 for row in rows if row.get("answer") is True),
        "expected_false": sum(1 for row in rows if row.get("answer") is False),
    }


def read_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def stderr_json_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    prefix = "[marathon:stderr] "
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if prefix not in line:
            continue
        payload = line.split(prefix, 1)[1].strip()
        try:
            record = json.loads(payload)
        except json.JSONDecodeError:
            continue
        if isinstance(record, dict):
            records.append(record)
    return records


def run_metrics(run_dir: Path) -> dict[str, Any]:
    summary = read_summary(run_dir / "summary.json") or {}
    records = stderr_json_records(run_dir / "run.log")
    solver_summaries = [record for record in records if "submitted_total" in record]
    final_solver_summary = solver_summaries[-1] if solver_summaries else {}
    llm_disabled_reasons = sorted(
        {
            str(record.get("reason") or "unknown")
            for record in records
            if record.get("route") == "llm:disabled"
        }
    )
    missing_upstream_key = "no upstream API key" in (run_dir / "run.log").read_text(
        encoding="utf-8", errors="replace"
    ) if (run_dir / "run.log").exists() else False
    return {
        "score": summary.get("score"),
        "attempted": summary.get("attempted"),
        "not_attempted": summary.get("not_attempted"),
        "by_status": summary.get("by_status") if isinstance(summary.get("by_status"), dict) else {},
        "wall_seconds": summary.get("wall_seconds"),
        "tokens_used": summary.get("tokens_used"),
        "llm_calls": int(final_solver_summary.get("llm_calls", 0) or 0),
        "submitted_total": final_solver_summary.get("submitted_total"),
        "submitted_deterministic": final_solver_summary.get("submitted_deterministic"),
        "missing_upstream_key": missing_upstream_key,
        "llm_disabled_reasons": llm_disabled_reasons,
    }


def summary_row(spec: SweepSpec, run_dir: Path, status: str, returncode: int | None) -> dict[str, Any]:
    stats = problem_stats(spec.manifest)
    metrics = run_metrics(run_dir)
    return {
        "name": spec.name,
        "lane": spec.lane,
        "role": spec.role,
        "manifest": repo_relative(spec.manifest),
        "run_dir": repo_relative(run_dir),
        "status": status,
        "returncode": returncode,
        "problems": stats["problems"],
        "expected_true": stats["expected_true"],
        "expected_false": stats["expected_false"],
        "score": metrics["score"],
        "attempted": metrics["attempted"],
        "not_attempted": metrics["not_attempted"],
        "by_status": metrics["by_status"],
        "wall_seconds": metrics["wall_seconds"],
        "tokens_used": metrics["tokens_used"],
        "llm_calls": metrics["llm_calls"],
        "submitted_total": metrics["submitted_total"],
        "submitted_deterministic": metrics["submitted_deterministic"],
        "missing_upstream_key": metrics["missing_upstream_key"],
        "llm_disabled_reasons": metrics["llm_disabled_reasons"],
    }


def write_combined(run_root: Path, rows: list[dict[str, Any]]) -> None:
    payload = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "solver": str((SOLVER_DIR / "solver.py").relative_to(REPO_ROOT)),
        "rows": rows,
    }
    (run_root / "sweep-summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Positive-Token Sweep Summary",
        "",
        f"Generated: {payload['generated_at']}",
        "",
        "| Lane | Dataset | Role | Problems | Score | Attempted | Not attempted | Accepted | Other status | LLM calls | Tokens | Wall s | Status |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in rows:
        by_status = row.get("by_status") or {}
        accepted = by_status.get("accepted", "")
        other = sum(int(v) for k, v in by_status.items() if k != "accepted") if by_status else ""
        score = "" if row.get("score") is None else row["score"]
        attempted = "" if row.get("attempted") is None else row["attempted"]
        not_attempted = "" if row.get("not_attempted") is None else row["not_attempted"]
        llm_calls = "" if row.get("llm_calls") is None else row["llm_calls"]
        tokens = "" if row.get("tokens_used") is None else row["tokens_used"]
        wall = "" if row.get("wall_seconds") is None else f"{float(row['wall_seconds']):.1f}"
        lines.append(
            f"| `{row['lane']}` | `{row['name']}` | `{row['role']}` | {row['problems']} | "
            f"{score} | {attempted} | {not_attempted} | {accepted} | {other} | "
            f"{llm_calls} | {tokens} | {wall} | `{row['status']}` |"
        )
    lines.append("")
    (run_root / "sweep-summary.md").write_text("\n".join(lines), encoding="utf-8")


def command_for(
    spec: SweepSpec,
    run_dir: Path,
    compression_ratio: float,
    budget_tokens: int,
    budget_seconds: float | None,
) -> list[str]:
    command = [
        sys.executable,
        str(REPO_ROOT / "vendor" / "stage2-official" / "scripts" / "run_marathon.py"),
        "--solver",
        str(SOLVER_DIR),
        "--manifest",
        str(spec.manifest),
        "--output-dir",
        str(run_dir),
    ]
    # upstream 4db175c4 removed --compression-ratio (flat N*300s default,
    # numerically identical to the old 0.5 ratio); a non-default ratio is
    # applied here as an explicit wall-clock budget instead.
    if budget_seconds is None and compression_ratio != 0.5:
        n = sum(1 for line in spec.manifest.open(encoding="utf-8") if line.strip())
        budget_seconds = compression_ratio * n * 600.0
    command.extend(["--budget-tokens", str(budget_tokens)])
    if budget_seconds is not None:
        command.extend(["--budget-seconds", str(budget_seconds)])
    return command


def validate_llm_requirement(row: dict[str, Any], *, require_llm: bool) -> str | None:
    if not require_llm:
        return None
    if row.get("missing_upstream_key"):
        return "missing upstream key or proxy configuration"
    if int(row.get("llm_calls", 0) or 0) <= 0:
        reasons = row.get("llm_disabled_reasons") or []
        if reasons:
            return f"zero llm_calls (disabled reasons: {', '.join(reasons)})"
        return "zero llm_calls"
    if int(row.get("tokens_used", 0) or 0) <= 0:
        return "zero tokens_used"
    return None


def runner_env() -> dict[str, str]:
    env, _sources = local_runner_env.load_local_runner_env()
    env["PYTHONUTF8"] = "1"
    home = Path.home()
    elan_bin = str(home / ".elan" / "bin")
    path = env.get("PATH", "")
    if elan_bin not in path.split(os.pathsep):
        env["PATH"] = elan_bin + os.pathsep + path
    return env


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope", choices=("smoke", "official", "hf", "all"), default="all")
    parser.add_argument("--only", nargs="*", default=None, help="Optional dataset names to run")
    parser.add_argument("--include-hf-core-duplicates", action="store_true")
    parser.add_argument("--compression-ratio", type=float, default=0.5)
    parser.add_argument("--run-root", type=Path, default=None)
    parser.add_argument(
        "--budget-tokens",
        type=int,
        default=131072,
        help="Positive token budget passed to the official Marathon runner. Values <= 0 are rejected.",
    )
    parser.add_argument(
        "--budget-seconds",
        type=float,
        default=None,
        help="Optional wall-clock budget override passed to the official Marathon runner.",
    )
    parser.add_argument(
        "--require-llm",
        action="store_true",
        help="Fail if a completed run records zero llm_calls or zero tokens_used.",
    )
    parser.add_argument("--force", action="store_true", help="Rerun even when summary.json exists")
    parser.add_argument("--list", action="store_true", help="List selected datasets and exit")
    args = parser.parse_args()

    run_root = (args.run_root or (DEFAULT_RUN_ROOT / f"{datetime.now():%Y-%m-%d}-positive-token-sweep")).resolve()
    specs = select_specs(args.scope, include_core_duplicates=args.include_hf_core_duplicates)
    if args.only:
        wanted = set(args.only)
        specs = [spec for spec in specs if spec.name in wanted]
    if not specs:
        print("No datasets selected.", file=sys.stderr)
        return 2

    for spec in specs:
        stats = problem_stats(spec.manifest)
        print(
            f"{spec.lane}/{spec.name}: {stats['problems']} rows "
            f"({stats['expected_true']} true / {stats['expected_false']} false) -> {spec.manifest}"
        )
    if args.list:
        return 0

    solver_entries = sorted(item.name for item in SOLVER_DIR.iterdir()) if SOLVER_DIR.exists() else []
    if solver_entries != ["solver.py"]:
        print(f"Submission dir must contain only solver.py; found {solver_entries!r}", file=sys.stderr)
        return 2

    if args.budget_tokens <= 0:
        print("Marathon validation with --budget-tokens <= 0 is banned in this repo.", file=sys.stderr)
        return 2

    key_state = local_runner_env.upstream_key_state()
    print(
        "llm_budget_mode=enabled budget_tokens={0} key_source={1} key_present={2}".format(
            args.budget_tokens,
            key_state["source"],
            str(bool(key_state["value"])).lower(),
        )
    )
    if args.require_llm and not key_state["value"]:
        print(
            "LLM usage required but no upstream key was found in process env, repo .env, or Windows User environment.",
            file=sys.stderr,
        )
        return 2

    run_root.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    overall_rc = 0
    for spec in specs:
        run_dir = run_root / spec.lane / spec.name
        summary_path = run_dir / "summary.json"
        if summary_path.exists() and not args.force:
            print(f"\n[skip] {spec.name}: existing {summary_path}")
            rows.append(summary_row(spec, run_dir, "skipped_existing", 0))
            write_combined(run_root, rows)
            continue

        run_dir.mkdir(parents=True, exist_ok=True)
        cmd = command_for(spec, run_dir, args.compression_ratio, args.budget_tokens, args.budget_seconds)
        (run_dir / "launcher-command.json").write_text(
            json.dumps({"command": cmd}, indent=2),
            encoding="utf-8",
        )
        print(f"\n[run] {spec.lane}/{spec.name}")
        print(" ".join(cmd))
        env = runner_env()
        proc = subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=False)
        status = "completed" if proc.returncode == 0 else "failed"
        row = summary_row(spec, run_dir, status, proc.returncode)
        llm_failure = validate_llm_requirement(row, require_llm=args.require_llm)
        if llm_failure is not None and status == "completed":
            status = "failed_llm_requirement"
            row["status"] = status
            row["llm_requirement_failure"] = llm_failure
            overall_rc = 1
        rows.append(row)
        write_combined(run_root, rows)
        if proc.returncode != 0 or llm_failure is not None:
            overall_rc = proc.returncode or 1
            break

    print(f"\nCombined summary: {run_root / 'sweep-summary.md'}")
    print(f"Combined JSON:    {run_root / 'sweep-summary.json'}")
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())
