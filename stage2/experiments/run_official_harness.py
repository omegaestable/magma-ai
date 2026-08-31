"""Run Stage-2 release checks with the local Lean 4.33.1 toolchain.

Elan's shim needs a machine-wide default toolchain, which is not guaranteed on
managed runners.  The official judge accepts explicit LEAN_BIN and LAKE_BIN
paths, so this wrapper resolves the project-pinned toolchain and forwards the
chosen official harness unchanged.  It makes no network call and edits no
vendored file.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
VENDOR = ROOT / "vendor" / "stage2-official"
TOOLCHAIN = "leanprover--lean4---v4.33.1"
RUNNERS = {
    "solo": ("scripts/run_harness.py",),
    "marathon": ("scripts/run_marathon_harness.py",),
    "gate": (
        "-m", "pytest", "stage2/tests", "-q", "-n", "auto",
        "--basetemp", "stage2/results/pytest_package_gate",
        "-p", "no:cacheprovider",
    ),
    "hf-order5": (
        "stage2/experiments/audit_corpus.py", "--set", "hf_evaluation_order5",
    ),
}


def resolve_toolchain() -> tuple[Path, Path]:
    """Return direct binaries, preferring explicit caller configuration."""
    lean = Path(os.environ.get("LEAN_BIN", ""))
    lake = Path(os.environ.get("LAKE_BIN", ""))
    if lean.is_file() and lake.is_file():
        return lean, lake

    elan_home = Path(os.environ.get("ELAN_HOME", Path.home() / ".elan"))
    bin_dir = elan_home / "toolchains" / TOOLCHAIN / "bin"
    lean = bin_dir / "lean.exe"
    lake = bin_dir / "lake.exe"
    if lean.is_file() and lake.is_file():
        return lean, lake
    raise FileNotFoundError(
        "Lean 4.33.1 toolchain not found. Set LEAN_BIN and LAKE_BIN to direct "
        "binaries, or install the toolchain under ELAN_HOME."
    )


def command(
    which: str,
    *,
    audit_file: Path | None = None,
    audit_out: Path | None = None,
    audit_effort: str = "standard",
    audit_row_budget: int = 540,
    audit_workers: int = 3,
) -> tuple[list[str], dict[str, str], Path]:
    if which in ("solo", "marathon") and not VENDOR.is_dir():
        raise FileNotFoundError(f"Missing official harness: {VENDOR}")
    lean, lake = resolve_toolchain()
    env = os.environ.copy()
    env["LEAN_BIN"] = str(lean)
    env["LAKE_BIN"] = str(lake)
    # `judge.verify` honors LEAN_BIN, while the Marathon harness's optional
    # Lean branch uses PATH discovery.  Keep both mechanisms pointed at the
    # same direct, project-pinned binaries without changing the host PATH.
    env["PATH"] = str(lean.parent) + os.pathsep + env.get("PATH", "")
    if which == "audit":
        if audit_file is None or audit_out is None:
            raise ValueError("audit requires --audit-file and --audit-out")
        argv = [
            sys.executable, "stage2/experiments/audit_corpus.py",
            "--file", str(audit_file), "--effort", audit_effort,
            "--row-budget", str(audit_row_budget), "--workers", str(audit_workers),
            "--out", str(audit_out),
        ]
        return argv, env, ROOT
    cwd = ROOT if which in ("gate", "hf-order5") else VENDOR
    return [sys.executable, *RUNNERS[which]], env, cwd


def run(which: str) -> int:
    argv, env, cwd = command(which)
    print(f"{which}: Lean={env['LEAN_BIN']}")
    result = subprocess.run(argv, cwd=cwd, env=env, check=False)
    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=(*RUNNERS, "audit", "both"))
    parser.add_argument(
        "--background-log", type=Path,
        help="run one harness hidden in the background and write combined output here",
    )
    parser.add_argument("--audit-file", type=Path)
    parser.add_argument("--audit-out", type=Path)
    parser.add_argument("--audit-effort", choices=("fast", "standard", "deep"),
                        default="standard")
    parser.add_argument("--audit-row-budget", type=int, default=540)
    parser.add_argument("--audit-workers", type=int, default=3)
    args = parser.parse_args()
    if args.background_log:
        if args.mode == "both":
            parser.error("--background-log requires one check, not both")
        args.background_log.parent.mkdir(parents=True, exist_ok=True)
        argv, env, cwd = command(
            args.mode,
            audit_file=args.audit_file,
            audit_out=args.audit_out,
            audit_effort=args.audit_effort,
            audit_row_budget=args.audit_row_budget,
            audit_workers=args.audit_workers,
        )
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        with args.background_log.open("w", encoding="utf-8") as log:
            process = subprocess.Popen(
                argv,
                cwd=cwd,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=log,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )
        print(f"{args.mode}: started PID {process.pid}; log={args.background_log}")
        return 0
    modes = tuple(RUNNERS) if args.mode == "both" else (args.mode,)
    for mode in modes:
        status = run(mode)
        if status:
            return status
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
