"""Mace4-style finite countermodel finder for magma implications.

Why this exists: the solver's FALSE lane is a portfolio of *canned* tables
(named witnesses, affine/linear/quadratic families) plus `local_model_counterexample`,
a randomized hill-climb over `Fin 4..6`. Both fail on the same class of rows —
laws of the form `x = F(x, ȳ)` with `x` occurring once on the right, which are so
tightly constrained that a random table essentially never satisfies them, and
whose smallest countermodel often lives at order 5-9.

Measured consequence (playground, 2026-07-29): six `hard2` rows with ground-truth
label FALSE were answered `true` by the grind fallback, at 363-847 s each. A TRUE
verdict on a FALSE row can never be accepted, so those were guaranteed misses.

The method here is exhaustive-with-propagation rather than stochastic, which is
what makes higher orders reachable:

- The unknowns are the n^2 Cayley-table cells.
- Every ground instance of eq1 (all n^k assignments of its variables) is a
  constraint. Partial evaluation gives unit propagation: if one side evaluates to
  a value and the other reduces to a single unknown cell, that cell is forced.
- A *target violation* of eq2 is committed to up front (a specific assignment of
  eq2's variables whose two sides must differ), which prunes far harder than
  searching for any model and testing eq2 afterwards.
- Cells are chosen by "most constrained first"; conflicts backtrack.

Everything is verified independently at the end: the returned table is re-checked
exhaustively against eq1 and eq2, so a bug in the search cannot produce an unsound
witness.

    python stage2/experiments/mace_finder.py --ids hard2_0093,hard2_0009 --max-order 8
    python stage2/experiments/mace_finder.py --set hard2 --false-only --max-order 7
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import product
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "stage2" / "solver"))
sys.path.insert(0, str(REPO_ROOT / "stage2" / "tests"))

import oracles  # noqa: E402
import solver as S  # noqa: E402

Term = tuple


# ---------------------------------------------------------------------------
# Partial evaluation over a table with holes
# ---------------------------------------------------------------------------

UNKNOWN = -1


class Conflict(Exception):
    pass


def eval_partial(term: Term, env: dict[str, int], table: list[int], n: int):
    """Partially evaluate `term`. Returns `(value, ready, root)`.

    - `value`  : the term's value, or None if some needed cell is unknown.
    - `ready`  : an unknown cell whose two operands *are* known — a legal place
                 to branch. There is always one when `value` is None.
    - `root`   : set only when the blocking cell is this term's own outermost
                 product, i.e. both children evaluated and only the root lookup
                 is missing.

    The `root` distinction is the whole point. Unit propagation `other_side ->
    this cell` is valid **only** at the root; an earlier version of this file
    returned the innermost blocking cell and assigned the other side's value to
    it, which is simply a different (wrong) equation and made the search declare
    "no countermodel" everywhere.
    """
    if term[0] == "var":
        return env[term[1]], None, None
    lv, lr, _ = eval_partial(term[1], env, table, n)
    rv, rr, _ = eval_partial(term[2], env, table, n)
    if lv is None or rv is None:
        return None, (lr if lr is not None else rr), None
    idx = lv * n + rv
    val = table[idx]
    if val == UNKNOWN:
        return None, idx, idx
    return val, None, None


def propagate(table: list[int], n: int, instances: list[tuple[dict, Term, Term]],
              stats: dict, value_cap: int) -> None:
    """Unit-propagate eq1's ground instances until nothing changes.

    `value_cap` matters here, not just at branch time: propagation can force a
    cell to a value that exceeds the render cap — e.g. for `eq1: x = F(...)`
    with a *bare variable* on one side, forcing that root cell to equal x's own
    substituted domain value, which ranges over all of `Fin n`, not just
    `range(value_cap)`. That is the structural reason wide-domain search cannot
    help this equation family: see WIDE_DOMAIN_NARROW_RANGE below.
    """
    changed = True
    while changed:
        changed = False
        for env, lhs, rhs in instances:
            lv, _lr, lroot = eval_partial(lhs, env, table, n)
            rv, _rr, rroot = eval_partial(rhs, env, table, n)
            if lv is not None and rv is not None:
                if lv != rv:
                    raise Conflict
                continue
            # Exactly one side known and the other blocked at its own root:
            # that root cell is forced to the known side's value.
            if lv is not None and rroot is not None:
                if lv >= value_cap:
                    raise Conflict
                table[rroot] = lv
                stats["propagations"] += 1
                changed = True
            elif rv is not None and lroot is not None:
                if rv >= value_cap:
                    raise Conflict
                table[lroot] = rv
                stats["propagations"] += 1
                changed = True


def _instances(eq: dict, n: int) -> list[tuple[dict, Term, Term]]:
    variables = list(eq["variables"])
    lhs, rhs = eq["lhs"], eq["rhs"]
    out = []
    for values in product(range(n), repeat=len(variables)):
        out.append((dict(zip(variables, values)), lhs, rhs))
    return out


def search(eq1: dict, eq2: dict, n: int, *, deadline: float,
           stats: dict, value_cap: int | None = None) -> list[list[int]] | None:
    """Find an order-n model of eq1 refuting eq2, or None.

    `value_cap`: restrict every cell to `range(min(n, value_cap))`. Pass 10 to
    search only for tables the judge's `finOpTable` parser can render at any
    order — see the WIDE_DOMAIN_NARROW_RANGE note below for why that is a real,
    much larger search space and not just "order <= 10 renamed".
    """
    eq1_instances = _instances(eq1, n)
    eq2_vars = list(eq2["variables"])
    cap = n if value_cap is None else min(n, value_cap)

    # Commit to one violating assignment of eq2 at a time: far stronger pruning
    # than "find any model, then test eq2". The target assignment only makes
    # sense over values the search can actually place, so it is capped too.
    for target in product(range(cap), repeat=len(eq2_vars)):
        if time.monotonic() >= deadline:
            return None
        tenv = dict(zip(eq2_vars, target))
        table = [UNKNOWN] * (n * n)
        try:
            found = _branch(table, n, eq1_instances, eq2, tenv, deadline, stats,
                            value_cap=cap)
        except Conflict:
            continue
        if found is not None:
            return found
    return None


def _cell_choice(table: list[int], n: int,
                 instances: list[tuple[dict, Term, Term]],
                 eq2: dict, tenv: dict) -> int:
    """Most-constrained *ready* cell: the one blocking the most instances.

    Only ready cells (both operands known) are branch candidates — guessing a
    cell nothing currently needs generates isomorphic subtrees and no pruning.
    """
    blocking: dict[int, int] = {}
    for env, lhs, rhs in instances:
        for term in (lhs, rhs):
            _v, ready, _root = eval_partial(term, env, table, n)
            if ready is not None:
                blocking[ready] = blocking.get(ready, 0) + 1
    if not blocking:
        # eq1 is fully determined on the reachable part; keep the eq2 violation
        # reachable by filling what it still needs.
        for term in (eq2["lhs"], eq2["rhs"]):
            _v, ready, _root = eval_partial(term, tenv, table, n)
            if ready is not None:
                return ready
        return -1
    return max(blocking, key=lambda k: blocking[k])


def _branch(table: list[int], n: int, eq1_instances, eq2: dict,
            tenv: dict, deadline: float, stats: dict,
            value_cap: int) -> list[list[int]] | None:
    if time.monotonic() >= deadline:
        return None
    stats["nodes"] += 1
    work = table[:]
    propagate(work, n, eq1_instances, stats, value_cap)

    # Is the committed eq2 violation still achievable?
    lv, _lr, _lroot = eval_partial(eq2["lhs"], tenv, work, n)
    rv, _rr, _rroot = eval_partial(eq2["rhs"], tenv, work, n)
    if lv is not None and rv is not None and lv == rv:
        raise Conflict

    cell = _cell_choice(work, n, eq1_instances, eq2, tenv)
    if cell < 0:
        # Nothing more is reachable. eq1 holds on every cell it can see and the
        # eq2 violation must have materialised; unknown cells are unreachable
        # from these constraints, so any value works — fill with 0.
        if lv is None or rv is None or lv == rv:
            raise Conflict
        filled = [0 if v == UNKNOWN else v for v in work]
        return [filled[r * n:(r + 1) * n] for r in range(n)]

    # Exhaustive over values: no least-number heuristic. LNH is only sound when
    # nothing pins specific domain elements, and the committed eq2 violation
    # pins several — so it would make "no countermodel <= N" unsound, which is a
    # conclusion this tool is used to draw.
    for value in range(value_cap):
        trial = work[:]
        trial[cell] = value
        try:
            got = _branch(trial, n, eq1_instances, eq2, tenv, deadline, stats,
                         value_cap=value_cap)
        except Conflict:
            continue
        if got is not None:
            return got
    raise Conflict


# Order schedule, not `range(2, max)`. Measured on `hard2_0009`: order 7 burned
# the full 120 s budget and found nothing, while order 8 succeeded in **0.03 s**
# (40 search nodes). Difficulty is not monotonic in the order — it depends on how
# well the order fits the law's algebra. The `x = F(x, y-bar)` family that
# dominates our FALSE misses forces *quasigroups*, whose models cluster at
# highly-composite orders and prime powers, so those go first. Searching
# smallest-first wastes the whole budget on the hardest orders.
PREFERRED_ORDERS = (8, 9, 4, 6, 5, 3, 2, 7, 10, 11, 12, 16)

# Only orders <= 10 produce a *shippable* certificate. The judge builds the magma
# with `MemoFinOp.finOpTable`, whose parser keeps one value per digit character, so
# a cell holding `10` is read as two cells and the table shifts. Confirmed against
# the real judge (2026-07-29): a hand-verified `Fin 13` linear witness for
# `hard2_0051` came back `LEAN_REJECTED` with `decide` calling the conjunction
# false. Building the magma from a formula instead (`fun i j => 7 * i + 7 * j`)
# fails the proof policy — `HAdd.hAdd` / `HMul.hMul` are not on the allowlist —
# so `finOpTable` is the only sanctioned constructor and 10 is a hard ceiling.
#
# Searching above 10 is still useful *as knowledge* (it tells you a row is
# genuinely FALSE and why the solver cannot claim it), which is why this tool
# allows it and the solver does not.
SHIPPABLE_MAX_ORDER = 10


def order_schedule(min_order: int, max_order: int) -> list[int]:
    inside = [n for n in PREFERRED_ORDERS if min_order <= n <= max_order]
    extra = [n for n in range(min_order, max_order + 1) if n not in inside]
    return inside + extra


def find_countermodel(eq1: dict, eq2: dict, *, min_order: int = 2,
                      max_order: int = 9, per_order_budget: float = 30.0,
                      verbose: bool = False):
    """Countermodel search over `order_schedule`. Returns (n, table, stats) or None.

    Note this returns the first order that *works*, not the smallest that works.
    For a judge certificate that is the right trade: a `Fin 9` `decideFin!` cert is
    462 bytes against the judge's 10 KB cap and verifies in 14-16 s, so a larger
    witness costs nothing while finding one faster costs a lot less budget.
    """
    for n in order_schedule(min_order, max_order):
        stats = {"nodes": 0, "propagations": 0, "order": n}
        started = time.monotonic()
        try:
            table = search(eq1, eq2, n, deadline=started + per_order_budget,
                           stats=stats)
        except Conflict:
            table = None
        stats["seconds"] = round(time.monotonic() - started, 2)
        if verbose:
            print(f"    order {n}: {'FOUND' if table else 'none'} "
                  f"({stats['nodes']} nodes, {stats['propagations']} props, "
                  f"{stats['seconds']}s)", flush=True)
        if table is None:
            continue
        # Independent verification: never trust the search. A table can also be
        # rejected legitimately — cells left unreachable by the constraints get
        # filled with 0, and that fill can introduce a violation — so a failure
        # here means "keep looking", not "bug".
        v1 = oracles.equation_holds(eq1["lhs"], eq1["rhs"],
                                    list(eq1["variables"]), table)
        v2 = oracles.equation_holds(eq2["lhs"], eq2["rhs"],
                                    list(eq2["variables"]), table)
        if not v1 or v2:
            if verbose:
                print(f"    order {n}: candidate rejected by verification "
                      f"(eq1={v1}, eq2={v2}); continuing", flush=True)
            continue
        return n, table, stats
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _row_worker(row: dict, *, min_order: int, max_order: int, budget: float,
                verbose: bool = False) -> dict:
    """One row, in-process or in a pool worker."""
    rid = str(row["id"])
    started = time.monotonic()
    try:
        eq1 = S.parse_equation(str(row["equation1"]))
        eq2 = S.parse_equation(str(row["equation2"]))
    except (KeyError, ValueError) as exc:
        return {"id": rid, "found": False, "error": str(exc), "seconds": 0.0}
    try:
        found = find_countermodel(eq1, eq2, min_order=min_order,
                                  max_order=max_order,
                                  per_order_budget=budget, verbose=verbose)
    except RecursionError:
        return {"id": rid, "found": False, "error": "recursion",
                "seconds": round(time.monotonic() - started, 1)}
    elapsed = round(time.monotonic() - started, 1)
    if found is None:
        return {"id": rid, "found": False, "seconds": elapsed,
                "label": row.get("answer")}
    n, table, stats = found
    return {"id": rid, "found": True, "order": n, "table": table,
            "seconds": elapsed, "nodes": stats["nodes"],
            "label": row.get("answer"),
            # A witness above the ceiling is real mathematics but cannot be
            # turned into a certificate the judge will read back.
            "shippable": n <= SHIPPABLE_MAX_ORDER}


SETS = {
    "normal": REPO_ROOT / "data/stage2_official_problems/normal.jsonl",
    "hard1": REPO_ROOT / "data/stage2_official_problems/hard1.jsonl",
    "hard2": REPO_ROOT / "data/stage2_official_problems/hard2.jsonl",
    "hard3": REPO_ROOT / "data/stage2_official_problems/hard3.jsonl",
    "evaluation_normal": REPO_ROOT / "data/hf_cache/evaluation_normal.jsonl",
    "evaluation_hard": REPO_ROOT / "data/hf_cache/evaluation_hard.jsonl",
    "evaluation_extra_hard": REPO_ROOT / "data/hf_cache/evaluation_extra_hard.jsonl",
    "evaluation_order5": REPO_ROOT / "data/hf_cache/evaluation_order5.jsonl",
}


def load_all() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for path in SETS.values():
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                row = json.loads(line)
                out.setdefault(str(row["id"]), row)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", default="")
    ap.add_argument("--set", dest="set_name", default="")
    ap.add_argument("--false-only", action="store_true",
                    help="only rows whose ground-truth label is FALSE")
    ap.add_argument("--unsolved-only", action="store_true",
                    help="only rows the solver currently fails to solve")
    ap.add_argument("--min-order", type=int, default=2)
    ap.add_argument("--max-order", type=int, default=9)
    ap.add_argument("--budget", type=float, default=30.0,
                    help="seconds per order")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=1,
                    help=">1 fans rows out across processes")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    catalog = load_all()
    if args.ids:
        targets = [catalog[i] for i in args.ids.split(",") if i.strip() in catalog]
    elif args.set_name:
        path = SETS[args.set_name]
        targets = [json.loads(line) for line in
                   path.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        print("pass --ids or --set")
        return 2

    if args.false_only:
        targets = [t for t in targets if t.get("answer") is False]
    if args.unsolved_only:
        keep = []
        for t in targets:
            S.set_effort("fast")
            S.clear_term_caches()
            if S.solve_problem(t, false_time_budget=2.0) is None:
                keep.append(t)
        targets = keep
    if args.limit:
        targets = targets[: args.limit]

    sched = order_schedule(args.min_order, args.max_order)
    print(f"searching {len(targets)} row(s), order schedule {sched}, "
          f"{args.budget}s/order, workers={args.workers}\n", flush=True)

    results = []
    if args.workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        from functools import partial
        worker = partial(_row_worker, min_order=args.min_order,
                         max_order=args.max_order, budget=args.budget)
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for res in pool.map(worker, targets, chunksize=1):
                results.append(res)
                mark = (f"order {res['order']}" if res.get("found")
                        else f"none <= {args.max_order}")
                print(f"  {res['id']:<28} {mark:<16} {res['seconds']:>7}s", flush=True)
    else:
        for row in targets:
            print(f"{row['id']} (label={row.get('answer')})", flush=True)
            res = _row_worker(row, min_order=args.min_order,
                              max_order=args.max_order, budget=args.budget,
                              verbose=True)
            results.append(res)
            if res.get("found"):
                print(f"  -> COUNTERMODEL order {res['order']}: {res['table']}"
                      f"  ({res['seconds']}s)\n", flush=True)
            else:
                print(f"  -> none <= {args.max_order} ({res['seconds']}s)\n", flush=True)

    hits = sum(1 for r in results if r.get("found"))
    print(f"\nfound {hits}/{len(results)} countermodels")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(results, indent=2), encoding="utf-8")
        print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
