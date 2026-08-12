"""Ground-truth dead-code probe for solver routes.

Name matching is unreliable (a route's dispatch label rarely equals its
function name). This wraps every module-level `*_route` / `*_source` /
`*_block` function, runs the public corpus, and records which ones were
actually CALLED and which ever returned a usable result.

A function that is called but never succeeds contributes nothing on this
corpus and is a de-bloat candidate; one that is never even called is
unreachable from the current dispatch order.

**Instrumentation happens after import, so anything the module already called
while executing is invisible to it.** Since 2026-08-11 that is the normal case
for the `*_block` certificate-text builders: the route families are built by
factories at import time, so `singleton_from_1111_block("h1111")` runs once
during module execution and never again. Those names are recovered statically
by `_called_at_import` and reported separately — without that, this tool says
18 live builders are unreachable, and rail 1 exists because acting on that
would cost real coverage.

Usage:
    python stage2/experiments/probe_dead_routes.py --limit 0
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOLVER_PATH = REPO_ROOT / "stage2" / "solver" / "solver.py"
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "experiments"))

TARGET_RE = re.compile(r"_(route|source|block)$")


def _called_at_import(path: Path = SOLVER_PATH) -> set[str]:
    """Target names invoked by module-level code, which runs before wrapping."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for statement in tree.body:
        if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        for node in ast.walk(statement):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if TARGET_RE.search(node.func.id):
                    names.add(node.func.id)
    return names


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

    at_import = _called_at_import()
    never_called = [n for n in all_targets
                    if not called.get(n) and n not in at_import]
    never_succeeded = [n for n in all_targets
                       if called.get(n) and not succeeded.get(n)]
    live = [n for n in all_targets if succeeded.get(n)]
    import_live = sorted(n for n in all_targets
                         if n in at_import and not called.get(n))

    print(f"\nsolved {solved}/{len(problems)}")
    print(f"live (ever succeeded):   {len(live)}")
    print(f"live at import time:     {len(import_live)}")
    print(f"called but never useful: {len(never_succeeded)}")
    print(f"never called at all:     {len(never_called)}")

    print("\n=== CALLED BUT NEVER SUCCEEDED (dead on this corpus) ===")
    for n in never_succeeded:
        print(f"  {n:56s} calls={called[n]}")
    print("\n=== LIVE AT IMPORT (evaluated once while the module loads) ===")
    for n in import_live:
        print(f"  {n}")
    print("\n=== NEVER CALLED (unreachable in current dispatch) ===")
    for n in never_called:
        print(f"  {n}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({
        "problems": len(problems), "solved": solved,
        "live": {n: succeeded[n] for n in live},
        "live_at_import": import_live,
        "called_never_succeeded": {n: called[n] for n in never_succeeded},
        "never_called": never_called,
    }, indent=2), encoding="utf-8")
    print(f"\nWrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
