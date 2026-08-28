#!/usr/bin/env python3
"""Does the shipped randomized repair search (`local_model_counterexample`)
reach orders 6-9?  LOCAL_MODEL_SIZES is (4, 5) (+6 above `fast`), so orders 7+
are never attempted by any tier.  This measures what raising it would buy and
what it would cost, with positive controls (rows with a known order-7 witness)
and negative controls (rows z3 proves have no eq1-model at all <= 7)."""
from __future__ import annotations

import argparse
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "stage2" / "solver"))
import solver as S  # noqa: E402

SIZES: tuple[int, ...] = ()
BUDGET = 15.0
SEEDS = 1


def work(row):
    eq1 = S.parse_equation(str(row["equation1"]))
    eq2 = S.parse_equation(str(row["equation2"]))
    rec = {"id": row["id"], "per_size": {}}
    t_all = time.monotonic()
    for n in SIZES:
        for seed in range(SEEDS):
            t0 = time.monotonic()
            got = S.local_model_counterexample(eq1, eq2, sizes=(n,),
                                               time_budget=BUDGET, seed=seed)
            dt = round(time.monotonic() - t0, 1)
            if got:
                rec["per_size"][str(n)] = {"found": True, "s": dt, "seed": seed}
                rec["order"] = n
                rec["table"] = got[1]
                rec["verified"] = bool(S.table_is_counterexample(eq1, eq2, got[1]))
                rec["total_s"] = round(time.monotonic() - t_all, 1)
                return rec
            rec["per_size"].setdefault(str(n), {"found": False, "s": 0.0})
            rec["per_size"][str(n)]["s"] = round(
                rec["per_size"][str(n)]["s"] + dt, 1)
    rec["total_s"] = round(time.monotonic() - t_all, 1)
    return rec


def _init(sizes, budget, seeds):
    global SIZES, BUDGET, SEEDS
    SIZES, BUDGET, SEEDS = sizes, budget, seeds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rows", type=Path, required=True)
    ap.add_argument("--sizes", default="6,7,8")
    ap.add_argument("--budget", type=float, default=15.0)
    ap.add_argument("--seeds", type=int, default=1)
    ap.add_argument("--procs", type=int, default=3)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    sizes = tuple(int(x) for x in args.sizes.split(","))
    rows = [json.loads(l) for l in args.rows.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"{len(rows)} rows sizes={sizes} budget={args.budget}s seeds={args.seeds}",
          flush=True)
    t0 = time.time()
    found = 0
    with Pool(args.procs, initializer=_init,
              initargs=(sizes, args.budget, args.seeds)) as pool, \
            args.out.open("w", encoding="utf-8") as fh:
        for rec in pool.imap_unordered(work, rows):
            if rec.get("verified"):
                found += 1
            fh.write(json.dumps(rec) + "\n")
            fh.flush()
            print(f"  {rec['id']}: order={rec.get('order')} {rec['total_s']}s "
                  f"(cum found {found})", flush=True)
    print(f"FOUND {found}/{len(rows)} in {time.time()-t0:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
