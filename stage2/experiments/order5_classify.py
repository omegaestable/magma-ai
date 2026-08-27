"""Classify a sample of order-5 misses: z3 countermodels / eq1-satisfiability
at n=2..7, FP-library witnesses, and collapse provers. Measurement only."""
from __future__ import annotations

import itertools
import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "stage2", "solver"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "experiments", "completion"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "tests"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
FAIL = os.path.join(ROOT, "stage2/results/order5-sweep-20k-2026-08-25-ALL-failures.jsonl")
TRI = os.path.join(ROOT, "stage2/results/order5-misses-oracle-triage-2026-08-26.jsonl")
FPL = os.path.join(ROOT, "stage2/results/teorth-finitepoly-library.jsonl")
OUT = os.path.join(ROOT, "stage2/results/order5-classification-2026-08-27.jsonl")
Z3_TIMEOUT_MS = 60_000
PROVER_BUDGET = 120.0


def load(p):
    return [json.loads(line) for line in open(p, encoding="utf-8") if line.strip()]


def z3_term(f, term, env):
    if term[0] == "var":
        return env[str(term[1])]
    return f(z3_term(f, term[1], env), z3_term(f, term[2], env))


def z3_run(eq1, eq2, n, want_counter):
    import z3
    f = z3.Function("f", z3.IntSort(), z3.IntSort(), z3.IntSort())
    s = z3.Solver()
    s.set(timeout=Z3_TIMEOUT_MS)
    for a in range(n):
        for b in range(n):
            s.add(f(a, b) >= 0, f(a, b) < n)
    for vals in itertools.product(range(n), repeat=len(eq1["variables"])):
        env = {v: z3.IntVal(x) for v, x in zip(eq1["variables"], vals)}
        s.add(z3_term(f, eq1["lhs"], env) == z3_term(f, eq1["rhs"], env))
    if want_counter:
        refs = []
        for vals in itertools.product(range(n), repeat=len(eq2["variables"])):
            env = {v: z3.IntVal(x) for v, x in zip(eq2["variables"], vals)}
            refs.append(z3_term(f, eq2["lhs"], env) != z3_term(f, eq2["rhs"], env))
        s.add(z3.Or(refs))
    t0 = time.time()
    r = s.check()
    dt = time.time() - t0
    if r == z3.sat:
        m = s.model()
        table = [[int(str(m.evaluate(f(a, b), model_completion=True))) for b in range(n)]
                 for a in range(n)]
        return "sat", dt, table
    return ("unsat" if r == z3.unsat else "timeout"), dt, None


def kb2_collapse(eq1_text, budget, max_size, max_active):
    """kb2 Completion; success = a derived equation of collapse shape (one side a
    variable absent from the other, or two distinct variables)."""
    from kb2 import Completion, tvars
    from solve_row import parse_eq
    lhs, rhs = parse_eq(eq1_text)
    comp = Completion([(lhs, rhs)], max_size=max_size, max_active=max_active)
    t0 = time.time()

    def collapse(e):
        for a, b in ((e.lhs, e.rhs), (e.rhs, e.lhs)):
            if a[0] == "v" and a[1] not in tvars(b):
                return True
        return False

    for a in list(comp.active):
        for b in list(comp.active):
            for (cl, cr, ch) in comp.crit_pairs(a, b):
                comp.push(cl, cr, ch, "cp")
    n = 0
    while time.time() - t0 < budget:
        e = comp.step()
        if e is None:
            return {"result": "saturated", "processed": n,
                    "seconds": round(time.time() - t0, 2), "active": len(comp.active)}
        n += 1
        if collapse(e):
            return {"result": "collapse", "eq": repr(e), "processed": n,
                    "seconds": round(time.time() - t0, 2)}
        comp.interreduce(e)
        for other in list(comp.active):
            for (cl, cr, ch) in comp.crit_pairs(e, other):
                comp.push(cl, cr, ch, "cp")
            if other.id != e.id:
                for (cl, cr, ch) in comp.crit_pairs(other, e):
                    comp.push(cl, cr, ch, "cp")
    return {"result": "budget", "processed": n, "seconds": round(time.time() - t0, 2),
            "active": len(comp.active), "passive": len(comp.passive)}


def work(row):
    import solver as S
    fp = load(FPL)
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    out = {"id": row["id"], "triage": row["triage"], "equation1": row["equation1"],
           "equation2": row["equation2"], "z3": {}}
    eq1_any_model = False
    eq1_all_unsat = True
    found = None
    for n in range(2, 8):
        st, dt, tab = z3_run(eq1, eq2, n, False)
        rec = {"eq1_only": st, "eq1_only_s": round(dt, 2)}
        if st == "sat":
            eq1_any_model = True
            rec["eq1_model_nontrivial"] = any(tab[a][b] != tab[0][0] for a in range(n) for b in range(n))
        if st != "unsat":
            eq1_all_unsat = False
        if st == "sat" and found is None:
            cst, cdt, ctab = z3_run(eq1, eq2, n, True)
            rec["counter"] = cst
            rec["counter_s"] = round(cdt, 2)
            if cst == "sat":
                rec["table"] = ctab
                rec["table_is_counterexample"] = bool(S.table_is_counterexample(eq1, eq2, ctab))
                rec["witness_check"] = bool(S.witness_check(eq1, eq2, ctab))
                if rec["witness_check"]:
                    found = (n, ctab)
        else:
            rec["counter"] = "skipped(eq1 " + st + ")"
        out["z3"][str(n)] = rec
        if found:
            break
    out["eq1_any_model_le7"] = eq1_any_model
    out["eq1_unsat_all_le7"] = eq1_all_unsat
    if found:
        out["verdict_guess"] = "FALSE_verified"
        out["table"] = found[1]
        out["table_order"] = found[0]
    else:
        if eq1_any_model:
            hits = []
            for e in fp:
                if S.witness_check(eq1, eq2, e["table"]):
                    hits.append(e["name"])
                    if len(hits) >= 3:
                        break
            out["fp_library_hits"] = hits
            if hits:
                out["verdict_guess"] = "FALSE_verified_fp"
                out["table"] = next(e["table"] for e in fp if e["name"] == hits[0])
                out["table_order"] = len(out["table"])
        if "verdict_guess" not in out:
            if eq1_all_unsat:
                out["verdict_guess"] = "TRUE_by_collapse_likely"
            elif eq1_any_model:
                out["verdict_guess"] = "eq1_has_models_no_counter_le7"
            else:
                out["verdict_guess"] = "unknown_z3_timeouts"
            if eq1_all_unsat or not eq1_any_model:
                xy = S.parse_equation("x = y")
                pv = {}
                t0 = time.time()
                r = S.completion_prove(eq1, xy, time_budget=PROVER_BUDGET)
                pv["completion_prove_xy"] = {"result": r[0] if r else None,
                                            "seconds": round(time.time() - t0, 2),
                                            "bytes": len(r[1]) if r else None}
                t0 = time.time()
                r = S.egg_saturate_prove(eq1, xy, time_budget=PROVER_BUDGET)
                pv["egg_xy"] = {"result": bool(r), "seconds": round(time.time() - t0, 2),
                                "bytes": len(r) if r else None}
                try:
                    pv["kb2_60_2000"] = kb2_collapse(row["equation1"], PROVER_BUDGET, 60, 2000)
                except Exception as ex:  # noqa: BLE001
                    pv["kb2_60_2000"] = {"result": "error", "error": repr(ex)[:200]}
                out["provers"] = pv
    return out


def main():
    rows = load(FAIL)
    tri = {r["id"]: r["oracle_triage"] for r in load(TRI)}
    for r in rows:
        r["triage"] = tri.get(r["id"])
    cc = [r for r in rows if r["triage"] == "collapse_candidate"]
    ns = [r for r in rows if r["triage"] == "no_small_countermodel"]

    def spread(lst, k):
        return [lst[int(i * len(lst) / k)] for i in range(k)]

    sample = spread(cc, 40) + spread(ns, 20)
    print("sampled", len(sample), "collapse", len(cc), "nosmall", len(ns), flush=True)
    done = set()
    if os.path.exists(OUT):
        done = {json.loads(line)["id"] for line in open(OUT, encoding="utf-8") if line.strip()}
    todo = [r for r in sample if r["id"] not in done]
    with Pool(6) as pool, open(OUT, "a", encoding="utf-8") as fh:
        for res in pool.imap_unordered(work, todo):
            fh.write(json.dumps(res, ensure_ascii=False) + "\n")
            fh.flush()
            print(res["id"], res["triage"], res["verdict_guess"],
                  {k: (v["eq1_only"], v.get("counter")) for k, v in res["z3"].items()},
                  res.get("provers", {}).get("kb2_60_2000", {}).get("result"), flush=True)


if __name__ == "__main__":
    main()
