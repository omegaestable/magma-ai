"""Run the official Marathon runner over an arbitrary manifest, real proxy, real key.

For manifests not covered by run_positive_token_sweeps.py's fixed SweepSpec
list (e.g. a custom ETP random sample). Mirrors command_for() in that script.

Usage:
  python.exe stage2/experiments/run_marathon_batch.py --manifest <path> --output-dir <dir> \
      [--budget-tokens N] [--budget-seconds N]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# Tracked copy of the runner wrapper that used to live only under
# `tmp_stage2_smoke/real-run-tools/` (gitignored by `tmp*/`). Paths are derived
# from __file__ so it works from any checkout; the original is left in place.
# Note a git worktree has no `vendor/stage2-official/.lake`, so run this from
# the main tree.
EXPERIMENTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENTS_DIR.parent.parent
OFFICIAL_DIR = REPO_ROOT / "vendor" / "stage2-official"
SUBMISSION_DIR = REPO_ROOT / "stage2" / "submissions"

sys.path.insert(0, str(EXPERIMENTS_DIR))
import local_runner_env  # noqa: E402


def runner_env() -> dict[str, str]:
    env, sources = local_runner_env.load_local_runner_env()
    env["PYTHONUTF8"] = "1"
    home = Path.home()
    elan_bin = str(home / ".elan" / "bin")
    path = env.get("PATH", "")
    if elan_bin not in path.split(os.pathsep):
        env["PATH"] = elan_bin + os.pathsep + path
    # The deployed judge caps now arrive with the env, from
    # `local_runner_env.judge_cap_env()`, which reads them out of
    # `vendor/stage2-official/pipeline/config.json`. Without them
    # `judge/verify.py` falls back to 50,000 / 10,000 / 120 and the scoring pass
    # measures a stricter judge than production -- that is rail 3b-iv, and it
    # cost a real 200-row Marathon a phantom `malformed`. The assert is here
    # because this file is under `tmp*/`, which `.gitignore` excludes: if this
    # copy is ever restored from somewhere without the tracked fix, fail loudly
    # rather than quietly re-inventing the failure.
    assert env.get("MAX_CODE_LENGTH"), (
        "judge caps missing from the runner env -- local_runner_env.judge_cap_env() "
        "did not fire; scoring would use judge/verify.py's 50,000-byte fallback")
    print(f"key_source={sources.get('OPENROUTER_API_KEY') or sources.get('OPENAI_API_KEY')}", file=sys.stderr)
    return env


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--budget-tokens", type=int, default=None)
    parser.add_argument("--budget-seconds", type=float, default=None)
    parser.add_argument("--score-only", action="store_true")
    parser.add_argument("--no-score", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    env = runner_env()
    cmd = [
        sys.executable,
        str(OFFICIAL_DIR / "scripts" / "run_marathon.py"),
        "--solver",
        str(SUBMISSION_DIR),
        "--manifest",
        str(args.manifest.resolve()),
        # upstream 4db175c4 removed --compression-ratio; the flat default
        # (N x 300 s / N x 32768 tokens) equals the old 0.5-ratio numbers.
        "--output-dir",
        str(output_dir),
    ]
    if args.budget_tokens is not None:
        cmd.extend(["--budget-tokens", str(args.budget_tokens)])
    if args.budget_seconds is not None:
        cmd.extend(["--budget-seconds", str(args.budget_seconds)])
    if args.score_only:
        cmd.append("--score-only")
    if args.no_score:
        cmd.append("--no-score")

    print("running:", " ".join(cmd), file=sys.stderr)
    start = time.time()
    completed = subprocess.run(cmd, cwd=REPO_ROOT, env=env, check=False)
    elapsed = time.time() - start
    print(f"marathon_batch_done manifest={args.manifest} returncode={completed.returncode} wall_s={elapsed:.1f}", file=sys.stderr)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
