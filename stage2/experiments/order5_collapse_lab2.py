"""Order-5 collapse lab, second round: normalise-before-cap and narrowed
superposition scopes.  MEASUREMENT ONLY.

The shipped `push()` applies `COMPLETION_MAX_SIZE` to the RAW critical pair.
Standard completion normalises the pair first and applies the limit to the
normal form -- and these hypotheses are strongly erasing (`F(x,y,z) -> x`), so a
weight-200 raw pair very often normalises to something tiny.  `normpush`
measures exactly that.
"""
from __future__ import annotations

import argparse
import heapq
import json
import os
import sys
import time
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "stage2", "solver"))
sys.path.insert(0, os.path.join(ROOT, "stage2", "experiments"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import solver as S  # noqa: E402
import order5_collapse_lab as L1  # noqa: E402


class Lab2Completion(L1.LabCompletion):
    """LabCompletion + normalise-at-push and a superposition scope.

      norm_push: 'off'      -- shipped: cap the raw pair
                 'over'     -- normalise only pairs that exceed the cap, then
                               re-check (only the pairs that would be lost pay)
                 'all'      -- normalise every generated pair (textbook)
      norm_push_limit: skip the rescue normalisation above this raw weight.
      sup_scope: 'all' (shipped) | 'axiom' (superpose the given only against
                 the axioms) | 'axiom_small' (axioms + weight <= sup_max_size)
    """

    def __init__(self, axioms, *, norm_push="off", norm_push_limit=10 ** 9,
                 sup_scope="all", **kw):
        self.norm_push = norm_push
        self.norm_push_limit = norm_push_limit
        self.sup_scope = sup_scope
        self.n_rescued = 0
        self.n_norm_calls = 0
        super().__init__(axioms, **kw)

    def _normalised_pair(self, lhs, rhs, chain):
        self.n_norm_calls += 1
        new_lhs, left_steps = self.normalize(lhs)
        new_rhs, right_steps = self.normalize(rhs)
        if new_lhs == new_rhs:
            return None
        full = ([(p, i, s, -d) for (p, i, s, d) in reversed(left_steps)]
                + chain + right_steps)
        return new_lhs, new_rhs, full

    def push(self, lhs, rhs, chain):
        weight = S.term_size(lhs) + S.term_size(rhs)
        if weight > self.max_weight_seen:
            self.max_weight_seen = weight
        if self.norm_push == "all" or (
                self.norm_push == "over" and weight > self.max_size
                and weight <= self.norm_push_limit):
            got = self._normalised_pair(lhs, rhs, chain)
            if got is None:
                return
            lhs, rhs, chain = got
            new_weight = S.term_size(lhs) + S.term_size(rhs)
            if weight > self.max_size >= new_weight:
                self.n_rescued += 1
            weight = new_weight
        if weight > self.max_size:
            self.n_dropped_size += 1
            return
        if len(self.passive) >= self.max_passive:
            self.n_dropped_full += 1
            return
        self.n_pushed += 1
        serial = next(self.counter)
        entry = (self.priority(lhs, rhs), serial, lhs, rhs, chain)
        heapq.heappush(self.passive, entry)
        if self.select != "weight":
            self.age_queue.append(entry)

    def superpose(self, eq):
        if self.sup_scope == "all":
            return super().superpose(eq)
        cap = self.sup_max_size
        if eq.weight > cap:
            return
        if self.sup_scope == "axiom":
            others = [self.eqs[i] for i in self.axiom_ids]
        else:
            others = [o for o in self.active
                      if o.chain is None or o.weight <= cap]
        for other in others:
            for (lhs, rhs, chain) in self.crit_pairs(eq, other):
                self.push(lhs, rhs, chain)
            if other.eid != eq.eid:
                for (lhs, rhs, chain) in self.crit_pairs(other, eq):
                    self.push(lhs, rhs, chain)


def run2(eq1, eq2, *, budget, want_cert=True, **kw):
    deadline = S.local_deadline(budget)
    t0 = time.time()
    comp = Lab2Completion([(eq1["lhs"], eq1["rhs"])], deadline=deadline, **kw)
    comp.seed()
    out = {"route": None, "cert_bytes": None, "collapse_eq": None}
    joined = comp.goal_join(eq2["lhs"], eq2["rhs"])
    if joined is not None:
        out["route"] = "join"
        if want_cert:
            code = S._kb_join_certificate(comp, joined, eq1, eq2)
            out["cert_bytes"] = len(code.encode()) if code else None
            out["cert"] = code
    while out["route"] is None and not comp.out_of_time():
        eq = comp.step()
        if eq is None:
            out["route"] = "saturated"
            break
        witness = S._kb_collapse_witness(eq)
        if witness is not None:
            _side, var, var_on_rhs = witness
            out["route"] = "collapse"
            out["collapse_eq"] = "%s = %s" % (S.term_to_lean(eq.lhs),
                                              S.term_to_lean(eq.rhs))
            out["collapse_weight"] = eq.weight
            out["collapse_deps"] = len(_KBdeps(comp, eq))
            if want_cert:
                code = S._kb_collapse_certificate(comp, eq, var, var_on_rhs, eq1, eq2)
                out["cert_bytes"] = len(code.encode()) if code else None
                out["cert"] = code
            break
        joined = comp.goal_join(eq2["lhs"], eq2["rhs"])
        if joined is not None:
            out["route"] = "join"
            out["join_deps"] = len(_KBdeps_chain(comp, joined))
            if want_cert:
                code = S._kb_join_certificate(comp, joined, eq1, eq2)
                out["cert_bytes"] = len(code.encode()) if code else None
                out["cert"] = code
            break
        comp.interreduce(eq)
        comp.superpose(eq)
    if out["route"] is None:
        out["route"] = "expired"
    out["seconds"] = round(time.time() - t0, 2)
    out["processed"] = comp.n_processed
    out["popped"] = comp.n_popped
    out["pushed"] = comp.n_pushed
    out["dropped_size"] = comp.n_dropped_size
    out["dropped_full"] = comp.n_dropped_full
    out["rescued"] = comp.n_rescued
    out["max_weight_seen"] = comp.max_weight_seen
    out["max_weight_used"] = comp.max_weight_used
    out["active"] = len(comp.active)
    out["passive"] = len(comp.passive)
    return out


def _KBdeps(comp, eq):
    r = S._KBRenderer(comp, [])
    return r.deps([((), eq.eid, {}, 1)], set())


def _KBdeps_chain(comp, chain):
    r = S._KBRenderer(comp, [])
    return r.deps(chain, set())


def run2_deepening(eq1, eq2, *, budget, want_cert=True,
                   ladder=(44, 88, 176, 352, 704, 1408, 2816), **kw):
    t0 = time.time()
    kw.pop("max_size", None)
    best, rungs = None, []
    for cap in ladder:
        left = budget - (time.time() - t0)
        if left <= 0.05:
            break
        res = run2(eq1, eq2, budget=left, want_cert=want_cert, max_size=cap, **kw)
        rungs.append((cap, res["route"], res["seconds"], res["processed"]))
        best = res
        if res["route"] in ("collapse", "join", "bridge"):
            break
        if res["route"] != "saturated":
            break
        if res["max_weight_seen"] <= cap:
            break
    best = best or {"route": "expired"}
    best["rungs"] = rungs
    best["seconds"] = round(time.time() - t0, 2)
    return best


NOCAP = dict(L1.NOCAP)
# Bounded active set: `active_full="ignore"` was measured to thrash (3.7 GB RSS
# and 9 min of CPU inside a 20 s budget) because `subsumed`/`rewrite_once`/
# `interreduce` are all O(|active|) and `subsumed` has no deadline poll at all.
BASE = dict(max_active=2000, max_passive=200000, active_full="stop")

VARIANTS = {
    "normover44": dict(BASE, max_size=44, norm_push="over"),
    "normover44_lim": dict(BASE, max_size=44, norm_push="over",
                           norm_push_limit=400),
    "normall44": dict(BASE, max_size=44, norm_push="all"),
    "normall60": dict(BASE, max_size=60, norm_push="all"),
    "normall88": dict(BASE, max_size=88, norm_push="all"),
    "normall120": dict(BASE, max_size=120, norm_push="all"),
    "axiom44": dict(BASE, max_size=44, sup_scope="axiom"),
    "axiom_norm": dict(BASE, max_size=44, sup_scope="axiom", norm_push="all"),
    "axsmall_norm": dict(BASE, max_size=60, sup_scope="axiom_small",
                         sup_max_size=40, norm_push="all"),
    "deep_norm": dict(BASE, norm_push="all", _deepen=True),
    "deep_normover": dict(BASE, norm_push="over", norm_push_limit=400,
                          _deepen=True),
    "deep_plain": dict(BASE, _deepen=True),
}


def job(args):
    row, variant, budget = args
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    kw = dict(VARIANTS[variant])
    runner = run2_deepening if kw.pop("_deepen", False) else run2
    try:
        res = runner(eq1, eq2, budget=budget, want_cert=False, **kw)
    except Exception as exc:  # noqa: BLE001
        res = {"route": "ERROR", "error": repr(exc)[:300], "seconds": 0}
    res["id"] = row["id"]
    res["variant"] = variant
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="normover44")
    ap.add_argument("--budget", type=float, default=60.0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--rows", default="collapse40")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = L1.pick_rows(args.rows)
    jobs = [(r, args.variant, args.budget) for r in rows]
    t0 = time.time()
    with Pool(args.procs) as pool:
        out = pool.map(job, jobs, chunksize=1)
    print("variant=%s budget=%s rows=%d WINS=%d (collapse=%d join=%d) wall=%.0fs"
          % (args.variant, args.budget, len(rows),
             sum(1 for r in out if r["route"] in ("collapse", "join")),
             sum(1 for r in out if r["route"] == "collapse"),
             sum(1 for r in out if r["route"] == "join"), time.time() - t0),
          flush=True)
    order = {"collapse": 0, "join": 1, "saturated": 2, "expired": 3, "ERROR": 4}
    for r in sorted(out, key=lambda r: (order.get(r["route"], 9), r.get("seconds", 0))):
        print("  %-22s %-10s %7.2fs proc=%-5s push=%-7s dropS=%-7s resc=%-6s"
              " maxw=%-5s usedw=%-4s act=%s"
              % (r["id"], r["route"], r.get("seconds", 0), r.get("processed", "-"),
                 r.get("pushed", "-"), r.get("dropped_size", "-"),
                 r.get("rescued", "-"), r.get("max_weight_seen", "-"),
                 r.get("max_weight_used", "-"), r.get("active", "-")), flush=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in out:
                fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
