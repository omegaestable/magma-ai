"""
Batch evaluation runner.

Usage:
    python -m pipeline.runner --submission examples/solo/demos/baseline --problems examples/problems/sample_20.json
    python -m pipeline.runner --submission examples/solo/demos/baseline --problems examples/problems/hard1.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from pipeline.proxy import load_config, load_problems, run_solver


def main():
    parser = argparse.ArgumentParser(description="Run evaluation pipeline")
    parser.add_argument("--submission", required=True, help="Path to submission directory")
    parser.add_argument("--problems", required=True,
                        help="Path to problems file (JSON array or JSONL, auto-detected)")
    parser.add_argument("--config", default=None, help="Path to config.json (default: pipeline/config.json)")
    parser.add_argument("--output", default=None, help="Output results file")
    args = parser.parse_args()

    config = load_config(args.config)
    problems = load_problems(args.problems)
    submission_name = Path(args.submission).name

    output_path = args.output or str(REPO_ROOT / "pipeline" / "results" / f"{submission_name}.json")
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Load existing results — keep solved entries, drop failed ones so a retry
    # replaces the old entry in place instead of appending a duplicate for the
    # same id (the previous behaviour silently bloated results.json on rerun).
    existing_solved = set()
    existing_results: list[dict] = []
    if Path(output_path).exists():
        for entry in json.loads(Path(output_path).read_text()):
            if entry.get("solved"):
                existing_solved.add(entry["id"])
                existing_results.append(entry)

    solver_cfg = config["solver"]
    llm_cfg = config["llm"]

    print(f"Pipeline Runner")
    print(f"  Submission:  {args.submission}")
    print(f"  Problems:    {len(problems)}")
    print(f"  Config:      timeout={solver_cfg['timeout_seconds']}s, "
          f"max_output_tokens={llm_cfg['max_output_tokens']}")
    print(f"  LLM:         {llm_cfg['model']} (provider: {llm_cfg.get('provider', 'default')})")
    print(f"  Output:      {output_path}")
    print()

    results = existing_results

    solved_count = len(existing_solved)
    failed_count = 0
    total_time = 0.0

    for i, problem in enumerate(problems, 1):
        pid = problem["id"]
        eq1 = f"Equation{problem['eq1_id']}"
        eq2 = f"Equation{problem['eq2_id']}"

        if pid in existing_solved:
            print(f"[{i}/{len(problems)}] {pid}: SKIP (already solved)")
            continue

        print(f"[{i}/{len(problems)}] {pid}: {eq1} -> {eq2}", end="", flush=True)

        t0 = time.time()
        result = run_solver(args.submission, problem, config)
        elapsed = time.time() - t0
        total_time += elapsed

        entry = {
            "id": pid,
            "eq1_id": problem["eq1_id"],
            "eq2_id": problem["eq2_id"],
            "elapsed_seconds": round(elapsed, 2),
            **result,
        }
        results.append(entry)

        # Save after each problem
        Path(output_path).write_text(json.dumps(results, indent=2, ensure_ascii=False))

        if result["solved"]:
            solved_count += 1
            print(f" -> SOLVED ({result['verdict']}) in {elapsed:.1f}s "
                  f"[llm:{result['llm_calls']}, judge:{result['judge_calls']}]", flush=True)
        else:
            failed_count += 1
            print(f" -> FAILED in {elapsed:.1f}s "
                  f"[llm:{result['llm_calls']}, judge:{result['judge_calls']}]", flush=True)

    total = len(problems)
    print(f"\n{'='*60}")
    print(f"Results: {solved_count}/{total} solved, {failed_count} failed")
    print(f"Total time: {total_time:.1f}s")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
