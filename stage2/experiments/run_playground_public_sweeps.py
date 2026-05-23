#!/usr/bin/env python3
"""Run official public Marathon sweeps with playground-equivalent settings.

This is the canonical local path for wide public-set checks when the goal is to
mirror the published Stage 2 playground/evaluation setup as closely as the
local harness allows:

- packaged single-file solver
- official Marathon proxy path
- published Marathon reference budgets (3600 s / 65536 tokens per problem)
- mandatory nonzero LLM usage
- automatic post-run gap analysis

The local harness still uses local infrastructure and public development sets,
so it cannot reproduce private playground manifests or any organizer-side model
changes that have not yet landed in the official repository.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import analyze_zero_token_run as analyzer
import run_playground_parity_llm as parity
import run_zero_token_sweeps as sweeps


REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "tmp_stage2_smoke"
DEFAULT_OUTPUT_DIR = TMP_DIR / "playground_public_sweeps"
DEFAULT_DATASETS = ("hard1", "hard2", "hard3")
PLAYGROUND_REF_PER_PROBLEM_SECONDS = 3600
PLAYGROUND_REF_PER_PROBLEM_TOKENS = 65536


def selected_specs(names: list[str] | None) -> list[sweeps.SweepSpec]:
    specs = sweeps.select_specs("official", include_core_duplicates=False)
    if not names:
        wanted = set(DEFAULT_DATASETS)
    else:
        wanted = set(names)
    selected = [spec for spec in specs if spec.name in wanted]
    if not selected:
        raise SystemExit("no official public datasets selected")
    missing = sorted(wanted - {spec.name for spec in selected})
    if missing:
        raise SystemExit(f"unknown official dataset names: {', '.join(missing)}")
    return selected


def derive_budgets(spec: sweeps.SweepSpec, compression_ratio: float) -> tuple[float, int]:
    n = sweeps.problem_stats(spec.manifest)["problems"]
    budget_seconds = compression_ratio * n * PLAYGROUND_REF_PER_PROBLEM_SECONDS
    budget_tokens = int(compression_ratio * n * PLAYGROUND_REF_PER_PROBLEM_TOKENS)
    return budget_seconds, budget_tokens


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> int:
    print("running:", " ".join(str(part) for part in command))
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    return int(completed.returncode)


def write_combined(
    output_dir: Path,
    rows: list[dict[str, Any]],
    *,
    submission: dict[str, Any],
    key_status: dict[str, Any],
    compression_ratio: float,
) -> None:
    payload = {
        "label": "playground-equivalent-public-sweep",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "compression_ratio": compression_ratio,
        "reference_seconds_per_problem": PLAYGROUND_REF_PER_PROBLEM_SECONDS,
        "reference_tokens_per_problem": PLAYGROUND_REF_PER_PROBLEM_TOKENS,
        "submission": submission,
        "key_status": key_status,
        "rows": rows,
    }
    (output_dir / "playground_public_sweep_summary.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "# Playground-Equivalent Public Sweep Summary",
        "",
        f"Generated: {payload['generated_at']}",
        f"Compression ratio: {compression_ratio}",
        f"Reference budget: {PLAYGROUND_REF_PER_PROBLEM_SECONDS}s / {PLAYGROUND_REF_PER_PROBLEM_TOKENS} tokens per problem",
        "",
        "| Dataset | Problems | Budget s | Budget tok | Score | Attempted | Not attempted | LLM calls | Tokens used | Gap summary | Status |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in rows:
        gap_counts = row.get("gap_counts") or {}
        if gap_counts:
            gap_summary = ", ".join(f"{key}={value}" for key, value in sorted(gap_counts.items()))
        else:
            gap_summary = ""
        lines.append(
            f"| `{row['name']}` | {row['problems']} | {int(row['budget_seconds'])} | {row['budget_tokens']} | "
            f"{'' if row.get('score') is None else row['score']} | "
            f"{'' if row.get('attempted') is None else row['attempted']} | "
            f"{'' if row.get('not_attempted') is None else row['not_attempted']} | "
            f"{row.get('llm_calls', '')} | {'' if row.get('tokens_used') is None else row['tokens_used']} | "
            f"{gap_summary} | `{row['status']}` |"
        )
    lines.append("")
    (output_dir / "playground_public_sweep_summary.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def prepare_submission(args: argparse.Namespace, env: dict[str, str]) -> tuple[list[str], dict[str, Any], dict[str, Any]]:
    failures: list[str] = []
    if not args.skip_smokes:
        if parity.run_python_smokes(env) != 0:
            failures.append("local Python/DSL smokes failed")
    if not args.skip_package:
        if parity.run_package(env) != 0:
            failures.append("solver packaging failed")
    submission = parity.submission_cleanliness()
    if not submission["only_solver_py"]:
        failures.append(f"submission directory is not single-file: {submission['entries']}")
    if not submission["under_size_limit"]:
        failures.append(f"submission solver.py exceeds size limit or is missing: {submission['size_bytes']}")
    key_status = parity.key_status()
    if not key_status["present"]:
        failures.append("local upstream OpenRouter/OpenAI key is not configured")
    elif key_status["has_whitespace"]:
        failures.append("local upstream key contains whitespace")
    return failures, submission, key_status


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="*", default=None, help="Official public datasets to run; default hard1 hard2 hard3.")
    parser.add_argument("--compression-ratio", type=float, default=0.5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR / f"{datetime.now():%Y-%m-%d}-playground-public-sweep")
    parser.add_argument("--skip-smokes", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    parser.add_argument("--keep-output", action="store_true")
    args = parser.parse_args()

    if args.compression_ratio <= 0:
        raise SystemExit("--compression-ratio must be positive")

    specs = selected_specs(args.only)
    args.output_dir = args.output_dir.resolve()
    parity.reset_output_dir(args.output_dir, keep_output=args.keep_output)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    env = parity.runner_env()
    failures, submission, key_status = prepare_submission(args, env)
    rows: list[dict[str, Any]] = []
    overall_rc = 0

    if failures:
        for failure in failures:
            print(f"preflight_failure={failure}", file=sys.stderr)
        write_combined(
            args.output_dir,
            rows,
            submission=submission,
            key_status=key_status,
            compression_ratio=args.compression_ratio,
        )
        return 1

    for spec in specs:
        budget_seconds, budget_tokens = derive_budgets(spec, args.compression_ratio)
        run_dir = args.output_dir / spec.lane / spec.name
        run_dir.mkdir(parents=True, exist_ok=True)
        command = sweeps.command_for(
            spec,
            run_dir,
            args.compression_ratio,
            budget_tokens,
            budget_seconds,
        )
        (run_dir / "launcher-command.json").write_text(
            json.dumps({"command": command}, indent=2),
            encoding="utf-8",
        )

        print(f"\n[run] {spec.lane}/{spec.name}")
        print(
            f"playground_budget_seconds={int(budget_seconds)} playground_budget_tokens={budget_tokens} "
            f"manifest={spec.manifest}"
        )
        returncode = run_command(command, REPO_ROOT, env)
        status = "completed" if returncode == 0 else "failed"
        row = sweeps.summary_row(spec, run_dir, status, returncode)
        row["budget_seconds"] = budget_seconds
        row["budget_tokens"] = budget_tokens
        row["profile"] = "playground_equivalent"

        if (run_dir / "summary.json").exists():
            analysis = analyzer.analyze(run_dir)
            row["analysis_path"] = sweeps.repo_relative(run_dir / "analysis.json")
            row["gap_counts"] = analysis.get("gap_counts", {})
            row["route_counts"] = analysis.get("route_counts", {})

        llm_failure = sweeps.validate_llm_requirement(row, require_llm=True)
        if llm_failure is not None and status == "completed":
            status = "failed_llm_requirement"
            row["status"] = status
            row["llm_requirement_failure"] = llm_failure
            overall_rc = 1
        rows.append(row)
        write_combined(
            args.output_dir,
            rows,
            submission=submission,
            key_status=key_status,
            compression_ratio=args.compression_ratio,
        )

        if returncode != 0:
            overall_rc = returncode or 1

    print(f"\nCombined summary: {args.output_dir / 'playground_public_sweep_summary.md'}")
    print(f"Combined JSON:    {args.output_dir / 'playground_public_sweep_summary.json'}")
    return overall_rc


if __name__ == "__main__":
    raise SystemExit(main())