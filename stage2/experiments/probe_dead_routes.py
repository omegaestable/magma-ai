"""Ground-truth dead-code probe for solver routes.

Name matching is unreliable (a route's dispatch label rarely equals its
function name). This wraps every module-level `*_route` / `*_source` /
`*_block` function, runs the public corpus, and records which ones were
actually CALLED and which ever returned a usable result.

A function that is called but never succeeds contributes nothing on this
corpus and is a de-bloat candidate; one that is never even called is
unreachable from the current dispatch order.

Usage:
    python stage2/experiments/probe_dead_routes.py --limit 0
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

TARGET_RE = re.compile(r"_(route|source|block)$")


def _instrument(mod):
    called: Counter = Counter()
    succeeded: Counter = Counter()

    def wrap(name, fn):
        def wrapped(*a, **kw):
            called[name] += 1
            out = fn(*a, **kw)
            if out is not None and out is not False:
                succeeded[name] += 1
            return out
        wrapped.__name__ = name
        wrapped.__wrapped_original__ = fn
        return wrapped

    for name in dir(mod):
        if not TARGET_RE.search(name):
            continue
        fn = getattr(mod, name)
        if not callable(fn):
            continue
        # A worker handles several chunks. Always re-wrap the ORIGINAL with the
        # fresh counters: wrapping a wrapper would leave earlier counters live
        # and silently drop rare successes into a discarded Counter.
        original = getattr(fn, "__wrapped_original__", None)
        if original is not None:
            setattr(mod, name, wrap(name, original))
        elif getattr(fn, "__module__", None) == mod.__name__:
            setattr(mod, name, wrap(name, fn))
    return called, succeeded


def _run_chunk(problems: list[dict]) -> tuple[dict, dict, int]:
    import solver as S

    called, succeeded = _instrument(S)
    solved = 0
    for problem in problems:
        try:
            if S.solve_problem(problem, false_time_budget=2.0) is not None:
                solved += 1
        except Exception:  # noqa: BLE001
            pass
    return dict(called), dict(succeeded), solved


def main() -> int:
    from audit_corpus import SETS, load_problems

    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="per-set cap; 0 = all")
    ap.add_argument("--include-hf", action="store_true",
                    help="also probe the HF mirror evaluation sets")
    ap.add_argument("--workers", type=int,
                    default=max(1, min(16, (os.cpu_count() or 2) - 2)))
    ap.add_argument("--out", type=Path,
                    default=REPO_ROOT / "stage2" / "results" / "dead-routes.json")
    args = ap.parse_args()

    sources = dict(SETS)
    if args.include_hf:
        # HF mirror evaluation sets are kept out of headline public evidence,
        # but they are legitimate extra coverage for a dead-code verdict.
        hf = REPO_ROOT / "data" / "hf_cache"
        for name in ("evaluation_normal", "evaluation_hard",
                     "evaluation_extra_hard", "evaluation_order5"):
            path = hf / f"{name}.jsonl"
            if path.exists():
                sources[f"hf:{name}"] = path

    problems: list[dict] = []
    for name, path in sorted(sources.items()):
        if not path.exists():
            continue
        rows = load_problems(path)
        problems.extend(rows[: args.limit] if args.limit else rows)
    print(f"probing {len(problems)} problems from {len(sources)} sets "
          f"on {args.workers} workers...")

    size = max(1, len(problems) // (args.workers * 4))
    chunks = [problems[i:i + size] for i in range(0, len(problems), size)]
    called: Counter = Counter()
    succeeded: Counter = Counter()
    solved = 0
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for c, s, n in pool.map(_run_chunk, chunks):
            called.update(c)
            succeeded.update(s)
            solved += n

    import solver as S
    all_targets = sorted(
        n for n in dir(S)
        if TARGET_RE.search(n) and callable(getattr(S, n))
        and getattr(getattr(S, n), "__module__", None) in (S.__name__, None)
    )

    never_called = [n for n in all_targets if not called.get(n)]
    never_succeeded = [n for n in all_targets
                       if called.get(n) and not succeeded.get(n)]
    live = [n for n in all_targets if succeeded.get(n)]

    print(f"\nsolved {solved}/{len(problems)}")
    print(f"live (ever succeeded):   {len(live)}")
    print(f"called but never useful: {len(never_succeeded)}")
    print(f"never called at all:     {len(never_called)}")

    print("\n=== CALLED BUT NEVER SUCCEEDED (dead on this corpus) ===")
    for n in never_succeeded:
        print(f"  {n:56s} calls={called[n]}")
    print("\n=== NEVER CALLED (unreachable in current dispatch) ===")
    for n in never_called:
        print(f"  {n}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "problems": len(problems), "solved": solved,
        "live": {n: succeeded[n] for n in live},
        "called_never_succeeded": {n: called[n] for n in never_succeeded},
        "never_called": never_called,
    }, indent=2), encoding="utf-8")
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
