"""Positive and negative controls for the order-5 collapse prototypes (rail 5c).

Positive controls -- rows the SHIPPED completion engine already serves.  A
candidate variant must still serve every one of them (route may change, a win
may not become a loss).

Negative controls -- rows with a known FALSE answer.  Two things are checked:
  soundness  the variant must NEVER report a collapse/join on them (a derived
             collapse on a row with a finite countermodel would be a bug), and
  cost       how long the variant burns before giving up, since the shipped
             engine's placement depends on its loss being cheap.

MEASUREMENT ONLY.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "stage2", "solver"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "experiments"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "tests"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import solver as S  # noqa: E402
import oracles  # noqa: E402
import order5_collapse_lab3 as L3  # noqa: E402

PROBLEMS = os.path.join(ROOT, "data", "stage2_official_problems")


def load_jsonl(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def shipped(args):
    row, budget = args
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    t0 = time.time()
    try:
        got = S.completion_prove(eq1, eq2, time_budget=budget, escalate=True)
    except Exception as exc:  # noqa: BLE001
        return dict(row, route="ERROR:" + repr(exc)[:120], seconds=0)
    return {"id": row["id"], "equation1": row["equation1"],
            "equation2": row["equation2"], "answer": row.get("answer"),
            "route": got[0] if got else None,
            "bytes": len(got[1].encode()) if got else None,
            "seconds": round(time.time() - t0, 2)}


def candidate(args):
    row, variant, budget = args
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    kw = dict(L3.VARIANTS[variant])
    runner = L3.run3_deepening if kw.pop("_deepen", False) else L3.run3
    try:
        res = runner(eq1, eq2, budget=budget, want_cert=True, **kw)
    except Exception as exc:  # noqa: BLE001
        return {"id": row["id"], "route": "ERROR", "error": repr(exc)[:200],
                "seconds": 0}
    kernel = None
    if res.get("cert"):
        try:
            oracles.check_true_lemma_chain_certificate(res["cert"], eq1, eq2)
            kernel = "OK"
        except Exception as exc:  # noqa: BLE001
            kernel = "FAIL:" + str(exc)[:140]
    out = {k: v for k, v in res.items() if k != "cert"}
    out["id"] = row["id"]
    out["kernel"] = kernel
    out["answer"] = row.get("answer")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("build", "check"), default="build")
    ap.add_argument("--variant", default="merge_deep")
    ap.add_argument("--budget", type=float, default=20.0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--rows", default=None, help="jsonl of rows for check mode")
    ap.add_argument("--limit", type=int, default=400)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    if args.mode == "build":
        pool_rows = []
        for name in ("normal", "hard2", "hard3"):
            pool_rows.extend(load_jsonl(os.path.join(PROBLEMS, name + ".jsonl")))
        pool_rows = pool_rows[:args.limit]
        jobs = [(r, args.budget) for r in pool_rows]
        with Pool(args.procs) as pool:
            got = pool.map(shipped, jobs, chunksize=4)
        wins = [g for g in got if g["route"]]
        print("scanned %d rows, shipped completion serves %d"
              % (len(pool_rows), len(wins)))
        from collections import Counter
        print(Counter(g["route"] for g in wins))
        with open(args.out, "w", encoding="utf-8") as fh:
            for g in wins:
                fh.write(json.dumps(g) + "\n")
        return

    rows = load_jsonl(args.rows)
    jobs = [(r, args.variant, args.budget) for r in rows]
    t0 = time.time()
    with Pool(args.procs) as pool:
        got = pool.map(candidate, jobs, chunksize=1)
    served = [g for g in got if g["route"] in ("collapse", "join", "bridge")]
    bad_kernel = [g for g in got if g.get("kernel", "OK") not in (None, "OK")]
    false_hits = [g for g in served if str(g.get("answer")).lower() in ("false", "0")]
    print("variant=%s rows=%d served=%d kernel_fail=%d FALSE_rows_claimed_TRUE=%d "
          "wall=%.0fs" % (args.variant, len(rows), len(served), len(bad_kernel),
                          len(false_hits), time.time() - t0))
    for g in got:
        print("  %-24s %-10s %7.2fs kernel=%s answer=%s"
              % (g["id"], g["route"], g.get("seconds", 0), g.get("kernel"),
                 g.get("answer")))
    with open(args.out, "w", encoding="utf-8") as fh:
        for g in got:
            fh.write(json.dumps(g) + "\n")


if __name__ == "__main__":
    main()
