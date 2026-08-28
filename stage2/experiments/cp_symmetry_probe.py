#!/usr/bin/env python3
"""Prototype: symmetry-broken constraint countermodel search (diagnosis only).

Two provably-sound reductions on top of the shipped `_cp_search`:

1. CANONICAL TARGET.  The shipped search commits to one violating assignment
   `t` of eq2's variables at a time, looping over `n ** |eq2 vars|` of them
   depth-first.  The whole constraint system is invariant under any permutation
   of the carrier, so if `(T, t)` is a witness then `(sigma T, sigma t)` is one
   too: only the restricted-growth-string representatives of `t` need to be
   tried.  n=7, 3 vars: 343 -> 5.

2. LEAST NUMBER HEURISTIC.  At any node let `U` be the elements occurring in
   `t`, in an assigned cell's index, or in an assigned cell's value.  Every
   assigned index and every propagated value is in `U` by construction (see
   `_cp_eval`: a cell index is built from already-known values), so any
   permutation fixing `U` pointwise fixes the partial table -- hence the values
   outside `U` are interchangeable and only the smallest need be tried when
   branching.  Sound only when value_cap == n (a cap below n breaks the
   symmetry group), so it is disabled otherwise.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import product
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
import solver as S  # noqa: E402

_CELL_UNKNOWN = S._CELL_UNKNOWN


def canonical_targets(k: int, cap: int):
    """Restricted growth strings of length k with values < cap."""
    def rec(prefix, hi):
        if len(prefix) == k:
            yield tuple(prefix)
            return
        for v in range(min(hi + 1, cap - 1) + 1):
            yield from rec(prefix + [v], max(hi, v))
    if k == 0:
        yield ()
        return
    yield from rec([], -1)


def cp_search2(eq1, eq2, n, deadline, budget, *, lnh=True, canon=True,
               stats=None):
    instances = S._cp_instances(eq1, n)
    eq2_vars = list(eq2["variables"])
    eq2_lhs, eq2_rhs = eq2["lhs"], eq2["rhs"]
    cap = n
    _eval = S._cp_eval
    _prop = S._cp_propagate

    def branch(table, used):
        budget[0] -= 1
        if budget[0] <= 0:
            return None
        if deadline is not None and time.monotonic() >= deadline:
            return None
        work = table[:]
        if not _prop(work, n, instances, cap):
            return None
        # recompute `used` after propagation: propagation only writes values
        # that already occur, so `used` is unchanged, but assert-free cheapness
        # matters more than elegance here.
        lv, _lr, _lroot = _eval(eq2_lhs, tenv, work, n)
        rv, _rr, _rroot = _eval(eq2_rhs, tenv, work, n)
        if lv is not None and rv is not None and lv == rv:
            return None
        blocking = {}
        for env, lhs, rhs in instances:
            for term in (lhs, rhs):
                _v, ready, _root = _eval(term, env, work, n)
                if ready is not None:
                    blocking[ready] = blocking.get(ready, 0) + 1
        cell = -1
        if blocking:
            cell = max(blocking, key=lambda k: blocking[k])
        else:
            for term in (eq2_lhs, eq2_rhs):
                _v, ready, _root = _eval(term, tenv, work, n)
                if ready is not None:
                    cell = ready
                    break
        if cell < 0:
            if lv is None or rv is None or lv == rv:
                return None
            filled = [0 if v == _CELL_UNKNOWN else v for v in work]
            return [filled[r * n:(r + 1) * n] for r in range(n)]
        if lnh:
            fresh = min((v for v in range(cap) if v not in used), default=None)
            values = sorted(used) + ([fresh] if fresh is not None else [])
        else:
            values = list(range(cap))
        for value in values:
            trial = work[:]
            trial[cell] = value
            got = branch(trial, used | {value})
            if got is not None:
                return got
        return None

    targets = (canonical_targets(len(eq2_vars), cap) if canon
               else product(range(cap), repeat=len(eq2_vars)))
    ntargets = 0
    for target in targets:
        ntargets += 1
        if budget[0] <= 0:
            return None
        if deadline is not None and time.monotonic() >= deadline:
            return None
        tenv = dict(zip(eq2_vars, target))
        found = branch([_CELL_UNKNOWN] * (n * n), set(target))
        if found is not None:
            if stats is not None:
                stats["targets"] = ntargets
            return found
    if stats is not None:
        stats["targets"] = ntargets
        stats["exhausted"] = True
    return None


def run_variant(eq1, eq2, orders, per_order_budget, mode):
    """mode: 'shipped' | 'canon' | 'canon+lnh'"""
    for n in orders:
        dl = time.monotonic() + per_order_budget
        budget = [S.CONSTRAINT_MAX_NODES]
        if mode == "shipped":
            tab = S._cp_search(eq1, eq2, n, dl, budget)
        else:
            tab = cp_search2(eq1, eq2, n, dl, budget,
                             lnh=(mode == "canon+lnh"), canon=True)
        if tab is not None and S.table_is_counterexample(eq1, eq2, tab):
            return n, tab
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--orders", default="5,6,7,8")
    ap.add_argument("--budget", type=float, default=45.0)
    ap.add_argument("--modes", default="shipped,canon+lnh")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--filter", default=None)
    args = ap.parse_args()

    orders = tuple(int(x) for x in args.orders.split(","))
    rows = [json.loads(l) for l in args.rows.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.filter:
        rows = [r for r in rows if r.get("triage") == args.filter]
    out = []
    for row in rows:
        eq1 = S.parse_equation(row["equation1"])
        eq2 = S.parse_equation(row["equation2"])
        rec = {"id": row["id"]}
        for mode in args.modes.split(","):
            t0 = time.monotonic()
            got = run_variant(eq1, eq2, orders, args.budget, mode)
            rec[mode] = {"found": got[0] if got else None,
                         "seconds": round(time.monotonic() - t0, 1),
                         "table": got[1] if got else None}
        out.append(rec)
        print(json.dumps({k: (v if not isinstance(v, dict) else
                              {kk: vv for kk, vv in v.items() if kk != "table"})
                          for k, v in rec.items()}), flush=True)
    if args.out:
        args.out.write_text("\n".join(json.dumps(r) for r in out), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
