"""Run the official Solo runner over a full problem-set file, real proxy, real key.

Does not rewrite the input file (unlike run_playground_parity_llm.py's
fixture modes, which round-trip rows back through the fixture path). Reads
env with local_runner_env precedence (process env, already stripped of the
stale key by clean_run.py, then repo .env, then legacy Windows User env).

Usage:
  python.exe stage2/experiments/run_solo_batch.py --problems <path> --output <path> [--limit N]
"""
from __future__ import annotations

import argparse
import json
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
    parser.add_argument("--problems", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    problems_path = args.problems.resolve()
    output_path = args.output.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.limit is not None:
        # Materialize a sliced copy under the output dir; never touch the source file.
        text = problems_path.read_text(encoding="utf-8")
        stripped = text.lstrip()
        sliced_path = output_path.parent / f"{problems_path.stem}.sliced{args.limit}.jsonl"
        if stripped.startswith("["):
            rows = json.loads(text)[: args.limit]
            sliced_path.write_text(json.dumps(rows), encoding="utf-8")
        else:
            lines = [line for line in text.splitlines() if line.strip()][: args.limit]
            sliced_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        problems_path = sliced_path

    env = runner_env()
    cmd = [
        sys.executable,
        "-m",
        "pipeline.runner",
        "--submission",
        str(SUBMISSION_DIR),
        "--problems",
        str(problems_path),
        "--output",
        str(output_path),
    ]
    print("running:", " ".join(cmd), file=sys.stderr)
    start = time.time()
    completed = subprocess.run(cmd, cwd=OFFICIAL_DIR, env=env, check=False)
    elapsed = time.time() - start
    print(f"solo_batch_done problems={problems_path} returncode={completed.returncode} wall_s={elapsed:.1f}", file=sys.stderr)
    return int(completed.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
