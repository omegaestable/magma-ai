#!/usr/bin/env python3
"""Run local OpenRouter-backed LLM checks through the official Stage 2 proxy.

This is the positive-token counterpart to zero-token Marathon sweeps. It is
meant to prove that a candidate exercised the playground-facing LLM paths:
official packaging, Solo proxy calls, Marathon proxy calls, and nonzero token
accounting. It never prints upstream key values.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import homelab_llm_probe as probe


REPO_ROOT = Path(__file__).resolve().parents[2]
TMP_DIR = REPO_ROOT / "tmp_stage2_smoke"
OFFICIAL_DIR = REPO_ROOT / "vendor" / "stage2-official"
SUBMISSION_DIR = REPO_ROOT / "stage2" / "submissions"
SOLVER_PATH = REPO_ROOT / "stage2" / "solver" / "solver.py"
SMOKE_LLM_DSL = REPO_ROOT / "stage2" / "experiments" / "smoke_llm_dsl.py"
PACKAGE_SCRIPT = REPO_ROOT / "stage2" / "solver" / "package_solver.ps1"
OFFICIAL_CONFIG = OFFICIAL_DIR / "pipeline" / "config.json"
DEFAULT_OUTPUT_DIR = TMP_DIR / "playground_parity_llm"
DEFAULT_FIXTURE = TMP_DIR / "playground_parity_llm_fixture.jsonl"
SUMMARY_NAME = "playground_parity_summary.json"
REF_PER_PROBLEM_TOKENS = 65536


def runner_env(*, enable_grind: bool) -> dict[str, str]:
    env = probe.runner_env()
    env["MAGMA_ENABLE_GRIND"] = "1" if enable_grind else "0"
    env.setdefault("MAGMA_SOLO_LLM_ROUNDS", "2")
    return env


def run_command(command: list[str], cwd: Path, env: dict[str, str]) -> int:
    printable = " ".join(str(part) for part in command)
    print(f"running: {printable}")
    completed = subprocess.run(command, cwd=cwd, env=env, check=False)
    return int(completed.returncode)


def run_python_smokes(env: dict[str, str]) -> int:
    exit_code = run_command(
        [sys.executable, "-m", "py_compile", str(SOLVER_PATH), str(SMOKE_LLM_DSL)],
        REPO_ROOT,
        env,
    )
    if exit_code != 0:
        return exit_code
    return run_command([sys.executable, str(SMOKE_LLM_DSL)], REPO_ROOT, env)


def run_package(env: dict[str, str]) -> int:
    shell = shutil.which("pwsh") or shutil.which("powershell")
    if shell is None:
        print("package_shell_missing=true")
        return 1
    return run_command(
        [shell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(PACKAGE_SCRIPT)],
        REPO_ROOT,
        env,
    )


def submission_cleanliness() -> dict[str, Any]:
    entries = sorted(path.name for path in SUBMISSION_DIR.iterdir()) if SUBMISSION_DIR.exists() else []
    solver_path = SUBMISSION_DIR / "solver.py"
    size = solver_path.stat().st_size if solver_path.exists() else None
    return {
        "entries": entries,
        "size_bytes": size,
        "only_solver_py": entries == ["solver.py"],
        "under_size_limit": size is not None and size <= 500_000,
    }


def reset_output_dir(path: Path, *, keep_output: bool) -> None:
    if keep_output or not path.exists():
        return
    resolved = path.resolve()
    try:
        resolved.relative_to(TMP_DIR.resolve())
    except ValueError as exc:
        raise SystemExit(f"refusing to clear output dir outside tmp_stage2_smoke: {path}") from exc
    if resolved.is_file():
        raise SystemExit(f"output dir path is a file: {path}")
    shutil.rmtree(resolved)


def missing_key_in(value: Any) -> bool:
    text = json.dumps(value, ensure_ascii=False)
    return (
        "OPENAI_API_KEY or OPENROUTER_API_KEY not set" in text
        or "OPENAI_API_KEY not set" in text
        or "OPENROUTER_API_KEY not set" in text
    )


def solo_metrics(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"missing": True, "rows": 0, "llm_calls": 0, "missing_key_rows": 0}
    rows = json.loads(path.read_text(encoding="utf-8"))
    statuses: Counter[str] = Counter()
    missing_key_rows = 0
    for row in rows:
        if missing_key_in(row):
            missing_key_rows += 1
        for entry in row.get("log", []):
            if entry.get("type") == "judge":
                status = entry.get("response", {}).get("status")
                if status:
                    statuses[str(status)] += 1
    return {
        "missing": False,
        "rows": len(rows),
        "solved": sum(1 for row in rows if row.get("solved")),
        "llm_calls": sum(int(row.get("llm_calls", 0) or 0) for row in rows),
        "judge_calls": sum(int(row.get("judge_calls", 0) or 0) for row in rows),
        "missing_key_rows": missing_key_rows,
        "judge_statuses": dict(statuses),
        "ids": [row.get("id") for row in rows],
    }


def stderr_json_records(log_path: Path) -> list[dict[str, Any]]:
    if not log_path.exists():
        return []
    records: list[dict[str, Any]] = []
    prefix = "[marathon:stderr] "
    for line in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
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


def marathon_metrics(output_dir: Path) -> dict[str, Any]:
    summary_path = output_dir / "summary.json"
    log_path = output_dir / "run.log"
    if not summary_path.exists():
        return {"missing": True, "llm_calls": 0, "tokens_used": 0, "missing_key_rows": 0}
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    records = stderr_json_records(log_path)
    solver_summaries = [record for record in records if "submitted_total" in record]
    final_solver_summary = solver_summaries[-1] if solver_summaries else {}
    route_counts: Counter[str] = Counter()
    for record in records:
        route = record.get("route")
        if route:
            route_counts[str(route)] += 1
    return {
        "missing": False,
        "score": summary.get("score"),
        "attempted": summary.get("attempted"),
        "not_attempted": summary.get("not_attempted"),
        "by_status": summary.get("by_status", {}),
        "tokens_used": int(summary.get("tokens_used") or 0),
        "tokens_exhausted": bool(summary.get("tokens_exhausted")),
        "llm_calls": int(final_solver_summary.get("llm_calls", 0) or 0),
        "submitted_deterministic": final_solver_summary.get("submitted_deterministic"),
        "submitted_total": final_solver_summary.get("submitted_total"),
        "solver_routes": final_solver_summary.get("routes", {}),
        "stderr_routes": dict(route_counts),
        "missing_key_rows": 1 if missing_key_in(records) else 0,
    }


def write_fixture(args: argparse.Namespace) -> list[dict[str, Any]]:
    rows = probe.select_unresolved_true(args.manifest, args.summary, args.limit)
    if not rows:
        raise SystemExit("no unresolved TRUE rows selected for parity probe")
    probe.write_fixture(rows, args.fixture)
    print(f"fixture={args.fixture} rows={len(rows)} ids={','.join(str(row['id']) for row in rows)}")
    return rows


def official_max_output_tokens() -> int:
    config = json.loads(OFFICIAL_CONFIG.read_text(encoding="utf-8"))
    return int(config.get("llm", {}).get("max_output_tokens", REF_PER_PROBLEM_TOKENS))


def run_solo(fixture_path: Path, output_path: Path, env: dict[str, str]) -> int:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.unlink(missing_ok=True)
    return run_command(
        [
            sys.executable,
            "-m",
            "pipeline.runner",
            "--submission",
            str(SUBMISSION_DIR),
            "--problems",
            str(fixture_path),
            "--output",
            str(output_path),
        ],
        OFFICIAL_DIR,
        env,
    )


def run_marathon(args: argparse.Namespace, env: dict[str, str]) -> int:
    output_dir = args.output_dir / "marathon"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "scripts/run_marathon.py",
        "--solver",
        str(SUBMISSION_DIR),
        "--manifest",
        str(args.fixture),
        "--output-dir",
        str(output_dir),
        "--compression-ratio",
        str(args.compression_ratio),
    ]
    if args.marathon_budget_tokens is not None:
        command.extend(["--budget-tokens", str(args.marathon_budget_tokens)])
    if args.marathon_budget_seconds is not None:
        command.extend(["--budget-seconds", str(args.marathon_budget_seconds)])
    return run_command(command, OFFICIAL_DIR, env)


def add_failures(summary: dict[str, Any], failures: list[str], *, require_llm: bool) -> None:
    clean = summary["submission"]
    if not clean["only_solver_py"]:
        failures.append(f"submission directory is not single-file: {clean['entries']}")
    if not clean["under_size_limit"]:
        failures.append(f"submission solver.py exceeds size limit or is missing: {clean['size_bytes']}")

    solo = summary.get("solo")
    if solo is not None:
        if solo.get("missing"):
            failures.append("Solo output missing")
        if solo.get("missing_key_rows", 0):
            failures.append("Solo reported missing upstream key/proxy")
        if require_llm and int(solo.get("llm_calls", 0) or 0) <= 0:
            failures.append("Solo recorded zero LLM calls")

    marathon = summary.get("marathon")
    if marathon is not None:
        if marathon.get("missing"):
            failures.append("Marathon summary missing")
        if marathon.get("missing_key_rows", 0):
            failures.append("Marathon reported missing upstream key/proxy")
        if require_llm and int(marathon.get("llm_calls", 0) or 0) <= 0:
            failures.append("Marathon solver summary recorded zero LLM calls")
        if require_llm and int(marathon.get("tokens_used", 0) or 0) <= 0:
            failures.append("Marathon summary recorded zero tokens used")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=probe.DEFAULT_MANIFEST)
    parser.add_argument("--summary", type=Path, default=probe.DEFAULT_SUMMARY)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--compression-ratio", type=float, default=0.5)
    parser.add_argument("--marathon-budget-tokens", type=int, default=None)
    parser.add_argument("--marathon-budget-seconds", type=float, default=None)
    parser.add_argument("--skip-package", action="store_true")
    parser.add_argument("--skip-direct-openrouter-smoke", action="store_true")
    parser.add_argument("--skip-solo", action="store_true")
    parser.add_argument("--skip-marathon", action="store_true")
    parser.add_argument("--keep-output", action="store_true")
    parser.add_argument("--enable-grind", action="store_true")
    args = parser.parse_args()

    if args.limit <= 0:
        raise SystemExit("--limit must be positive")
    if args.compression_ratio <= 0:
        raise SystemExit("--compression-ratio must be positive")
    if not args.manifest.exists():
        raise SystemExit(f"manifest not found: {args.manifest}")
    if not args.summary.exists():
        raise SystemExit(f"summary not found: {args.summary}")

    env = runner_env(enable_grind=args.enable_grind)
    reset_output_dir(args.output_dir, keep_output=args.keep_output)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    rows = write_fixture(args)

    if not args.skip_marathon and args.marathon_budget_tokens is None:
        derived_tokens = int(args.compression_ratio * len(rows) * REF_PER_PROBLEM_TOKENS)
        if derived_tokens <= official_max_output_tokens():
            raise SystemExit(
                "default Marathon token budget is too small to force a full-config LLM call; "
                "increase --limit, --compression-ratio, or set --marathon-budget-tokens"
            )

    if not args.skip_package:
        failures.extend([] if run_python_smokes(env) == 0 else ["local Python/DSL smokes failed"])
        failures.extend([] if run_package(env) == 0 else ["solver packaging failed"])

    direct_exit_code: int | None = None
    if not args.skip_direct_openrouter_smoke:
        probe.print_key_status()
        try:
            direct_exit_code = probe.run_direct_openrouter_smoke()
        except SystemExit as exc:
            direct_exit_code = int(exc.code) if isinstance(exc.code, int) else 1
            print(f"direct_openrouter_smoke_error={exc}")
        if direct_exit_code != 0:
            failures.append("direct OpenRouter smoke failed")

    solo: dict[str, Any] | None = None
    if not args.skip_solo:
        solo_output = args.output_dir / "solo_result.json"
        if run_solo(args.fixture, solo_output, env) != 0:
            failures.append("official Solo runner failed")
        solo = solo_metrics(solo_output)

    marathon: dict[str, Any] | None = None
    if not args.skip_marathon:
        if run_marathon(args, env) != 0:
            failures.append("official Marathon runner failed")
        marathon = marathon_metrics(args.output_dir / "marathon")

    summary: dict[str, Any] = {
        "label": "playground-parity-positive-token-llm",
        "fixture": str(args.fixture),
        "row_ids": [row.get("id") for row in rows],
        "grind_enabled": args.enable_grind,
        "direct_openrouter_smoke_exit_code": direct_exit_code,
        "submission": submission_cleanliness(),
    }
    if solo is not None:
        summary["solo"] = solo
    if marathon is not None:
        summary["marathon"] = marathon

    add_failures(summary, failures, require_llm=not (args.skip_solo and args.skip_marathon))
    summary["failures"] = failures
    summary_path = args.output_dir / SUMMARY_NAME
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"parity_summary={summary_path}")
    if failures:
        for failure in failures:
            print(f"parity_failure={failure}")
        return 1
    print("parity_status=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())