#!/usr/bin/env python3
"""Run a handful of problems one at a time, printing every stage.

For each row: the equations, the deterministic route (if any), the raw model
response, what the solver's parser extracted from it, and the oracle verdict.
No threading, no buffering tricks - meant to be watched live.
"""
from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "experiments"))
sys.path.insert(0, str(REPO / "stage2" / "solver"))
sys.path.insert(0, str(REPO / "stage2" / "tests"))

from llm_balanced_eval import (API_KEY, call_llm, fill_prompt,  # noqa: E402
                               load_rows, verify_candidate)
import solver as S  # noqa: E402


class Args:
    model = "openai/gpt-oss-120b"
    reasoning = "medium"
    temperature = 0.0
    max_tokens = 6144
    http_timeout = 180.0
    retries = 1
    allow_fallbacks = False
    seed = 0


def main() -> int:
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    effort = sys.argv[2] if len(sys.argv) > 2 else "standard"
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 7
    if len(sys.argv) > 4:
        Args.reasoning = sys.argv[4]

    if not API_KEY:
        print("No OpenRouter key found.", file=sys.stderr)
        return 2

    S.set_effort(effort)
    print(f"effort={effort} reasoning={Args.reasoning} model={Args.model}\n")

    rows = load_rows()
    rng = random.Random(seed)
    true_rows = [r for r in rows if r.get("answer") is True]
    false_rows = [r for r in rows if r.get("answer") is False]
    rng.shuffle(true_rows)
    rng.shuffle(false_rows)

    # Prefer rows the deterministic solver does NOT already solve, so we are
    # actually watching the LLM lane do something.
    def unresolved(pool):
        for row in pool:
            if S.solve_problem(row, false_time_budget=1.0) is None:
                yield row

    picks = []
    t_it, f_it = unresolved(true_rows), unresolved(false_rows)
    for i in range(n):
        picks.append(next(t_it) if i % 2 == 0 else next(f_it))

    for i, problem in enumerate(picks, 1):
        print("=" * 78)
        print(f"[{i}/{n}] {problem['id']}  label={problem['answer']}")
        print(f"  eq1: {problem['equation1']}")
        print(f"  eq2: {problem['equation2']}")

        analysis = S.solver_analysis(problem)
        prompt = fill_prompt(S.PROMPT, problem, analysis, "")
        print(f"\n  -> calling {Args.model} ...", flush=True)
        t0 = time.monotonic()
        result = call_llm(prompt, Args)
        dt = time.monotonic() - t0
        if "error" in result:
            print(f"  LLM ERROR after {dt:.0f}s: {result['error']}")
            continue

        text = result["text"]
        print(f"  <- got response in {dt:.0f}s "
              f"({result['completion_tokens']} tokens, "
              f"truncated={result['truncated']})")
        print("\n  --- raw response ---")
        print("  " + text.strip().replace("\n", "\n  ")[:1500])
        print("  --- end response ---\n")

        candidate, reason = S.candidate_from_llm_text_with_reason(
            problem, text, allow_raw_true=False)
        if candidate is None:
            print(f"  PARSE RESULT: rejected ({reason})")
            continue

        print(f"  PARSE RESULT: verdict={candidate['answer']['verdict']} "
              f"route={candidate['route']}")
        status, detail = verify_candidate(problem, candidate)
        tag = {"correct": "CORRECT", "WRONG_VERDICT_SUBMITTED": "!!! WRONG VERDICT !!!",
              "UNSOUND_CERT": "!!! UNSOUND CERT !!!"}[status]
        print(f"  ORACLE: {tag} ({detail})")
        if status != "correct":
            print(f"  code:\n    " + candidate["answer"]["code"].replace("\n", "\n    "))
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
