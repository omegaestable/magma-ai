#!/usr/bin/env python3
"""Offline (z3) finite-countermodel finder for magma implication rows.

Diagnosis tool only -- z3 is NOT importable in the submission sandbox.  Its
purpose is to produce witness TABLES that can then be shipped as data
(content-keyed, like FP_WITNESS_TABLES), and to give the propagation search a
ground truth to be measured against.

Every table it returns is re-validated with the solver's own
`table_is_counterexample` (exhaustive), `table_is_renderable` and
`witness_decide_is_affordable` before being reported.
"""
from __future__ import annotations

import argparse
import itertools
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
import solver as S  # noqa: E402

ORDERS: tuple[int, ...] = ()
TIMEOUT_MS = 60_000


def _term(f, term, env):
    if term[0] == "var":
        return env[str(term[1])]
    return f(_term(f, term[1], env), _term(f, term[2], env))


def z3_counter(eq1, eq2, n, timeout_ms):
    import z3
    f = z3.Function("f", z3.IntSort(), z3.IntSort(), z3.IntSort())
    s = z3.Solver()
    s.set(timeout=timeout_ms)
    for a in range(n):
        for b in range(n):
            s.add(f(a, b) >= 0, f(a, b) < n)
    for vals in itertools.product(range(n), repeat=len(eq1["variables"])):
        env = {v: z3.IntVal(x) for v, x in zip(eq1["variables"], vals)}
        s.add(_term(f, eq1["lhs"], env) == _term(f, eq1["rhs"], env))
    refs = []
    for vals in itertools.product(range(n), repeat=len(eq2["variables"])):
        env = {v: z3.IntVal(x) for v, x in zip(eq2["variables"], vals)}
        refs.append(_term(f, eq2["lhs"], env) != _term(f, eq2["rhs"], env))
    s.add(z3.Or(refs))
    t0 = time.time()
    r = s.check()
    dt = round(time.time() - t0, 2)
    if r == z3.sat:
        m = s.model()
        tab = [[int(str(m.evaluate(f(a, b), model_completion=True))) for b in range(n)]
               for a in range(n)]
        return "sat", dt, tab
    return ("unsat" if r == z3.unsat else "timeout"), dt, None


def work(row):
    eq1 = S.parse_equation(str(row["equation1"]))
    eq2 = S.parse_equation(str(row["equation2"]))
    out = {"id": row["id"], "equation1": row["equation1"],
           "equation2": row["equation2"], "eq1_id": row.get("eq1_id"),
           "eq2_id": row.get("eq2_id"), "per_order": {}}
    for n in ORDERS:
        st, dt, tab = z3_counter(eq1, eq2, n, TIMEOUT_MS)
        out["per_order"][str(n)] = {"status": st, "s": dt}
        if st == "sat":
            ok = bool(S.table_is_counterexample(eq1, eq2, tab))
            out["per_order"][str(n)]["verified"] = ok
            if ok:
                widest = max(len(eq1["variables"]), len(eq2["variables"]))
                out["order"] = n
                out["table"] = tab
                out["renderable"] = bool(S.table_is_renderable(tab))
                out["decide_affordable"] = bool(
                    S.witness_decide_is_affordable(eq1, eq2, tab))
                out["decide_applications"] = n ** widest
                out["verdict"] = "FALSE"
                return out
    if all(v["status"] == "unsat" for v in out["per_order"].values()):
        out["verdict"] = "no_counter_in_range"
    else:
        out["verdict"] = "unresolved"
    return out


def _init(orders, timeout_ms):
    global ORDERS, TIMEOUT_MS
    ORDERS = orders
    TIMEOUT_MS = timeout_ms


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--orders", default="5,6,7,8,9")
    ap.add_argument("--timeout", type=float, default=60.0, help="seconds per (row, order)")
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ids", default=None)
    args = ap.parse_args()

    orders = tuple(int(x) for x in args.orders.split(","))
    rows = [json.loads(l) for l in args.rows.read_text(encoding="utf-8").splitlines() if l.strip()]
    if args.ids:
        want = set(args.ids.split(","))
        rows = [r for r in rows if r["id"] in want]
    print(f"{len(rows)} rows, orders {orders}, {args.timeout}s/order, {args.procs} procs",
          flush=True)
    t0 = time.time()
    done = []
    with Pool(args.procs, initializer=_init,
              initargs=(orders, int(args.timeout * 1000))) as pool, \
            args.out.open("w", encoding="utf-8") as fh:
        for rec in pool.imap_unordered(work, rows):
            done.append(rec)
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            if len(done) % 10 == 0:
                nf = sum(1 for d in done if d["verdict"] == "FALSE")
                print(f"  {len(done)}/{len(rows)} FALSE={nf} "
                      f"({time.time()-t0:.0f}s)", flush=True)
    from collections import Counter
    print(json.dumps(Counter(d["verdict"] for d in done)))
    print(json.dumps(Counter(str(d.get("order")) for d in done if d["verdict"] == "FALSE")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
