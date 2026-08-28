"""Order-5 TRUE-by-collapse lab: prototype completion strategies.

MEASUREMENT ONLY -- nothing here is imported by the solver. LabCompletion
subclasses solver._KBCompletion so every variant keeps the shipped renderer and
certificate path; a winning variant ports as a small diff to the real class.

Usage:
  python stage2/experiments/order5_collapse_lab.py --variant nocap --budget 60
"""
from __future__ import annotations

import argparse
import heapq
import json
import os
import sys
import time
from collections import deque
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "stage2", "solver"))
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import solver as S  # noqa: E402

CLASSIFY = os.path.join(ROOT, "stage2/results/order5-classification-2026-08-27.jsonl")
SWEEP = os.path.join(ROOT, "stage2/results/order5-sweep-20k-2026-08-25-ALL-failures.jsonl")

_TERM_SIZE = S.term_size
_KB_ORDER_GT = S._kb_order_gt
_KB_VAR_COUNTS = S._kb_var_counts


def fast_kbo_gt(source, target, ground=False):
    """`_kbo_gt` with the size short-circuit hoisted above the variable check.

    `_kb_order_gt` returns `source_size > target_size` whenever the sizes
    differ, so a strictly smaller source is False no matter what the variable
    condition says -- and the variable condition is the expensive half
    (`_kb_var_counts` was 3.3 s of a 15 s profile).  Semantically identical.
    """
    ssz = _TERM_SIZE(source)
    tsz = _TERM_SIZE(target)
    if ssz < tsz:
        return False
    if not ground:
        have = dict(_KB_VAR_COUNTS(source))
        for var, need in _KB_VAR_COUNTS(target):
            if have.get(var, 0) < need:
                return False
    if ssz > tsz:
        return True
    return _KB_ORDER_GT(source, target, ground)


class LabCompletion(S._KBCompletion):
    """Shipped completion with a pluggable passive-queue / superposition policy.

    New knobs versus the shipped class:
      max_size        -- pair weight cap (shipped 44).  10**9 disables it.
      max_passive     -- shipped drops every pair once the queue is full, which
                         silently truncates the search to "the first N pairs
                         ever generated"; here a full queue evicts nothing but
                         the incoming pair only when it is heavier than the cap.
      sup_max_size    -- only superpose with active equations at or below this
                         weight (bounds the quadratic cost without losing the
                         heavy equation as a rewrite rule).
      select          -- 'weight' (shipped best-first) | 'ratio:N' pick-given.
      prio            -- 'weight' | 'goalweight' (collapse-directed).
      active_full     -- 'stop' (shipped: kills the run) | 'ignore' | 'evict'.
    """

    def __init__(self, axioms, *, deadline, max_size=44, max_active=400,
                 max_passive=40000, sup_max_size=10 ** 9, select="weight",
                 prio="weight", active_full="stop", varw=3, bareb=12,
                 fastkbo=False):
        self.select = select
        self.prio_mode = prio
        self.active_full = active_full
        self.sup_max_size = sup_max_size
        self.varw = varw
        self.bareb = bareb
        self.age_queue = deque()
        self.dead = set()
        self.since_age = 0
        self.ratio = 5
        if select.startswith("ratio:"):
            self.ratio = int(select.split(":", 1)[1])
        self.n_pushed = 0
        self.n_dropped_size = 0
        self.n_dropped_full = 0
        self.n_popped = 0
        self.n_processed = 0
        self.max_weight_seen = 0
        self.max_weight_used = 0
        super().__init__(axioms, deadline=deadline, max_size=max_size,
                         max_active=max_active, max_passive=max_passive)

    def priority(self, lhs, rhs):
        w = _TERM_SIZE(lhs) + _TERM_SIZE(rhs)
        if self.prio_mode == "weight":
            return w
        nv = len(S.term_vars(lhs) | S.term_vars(rhs))
        bonus = self.bareb if (lhs[0] == "var" or rhs[0] == "var") else 0
        return w + self.varw * nv - bonus

    def push(self, lhs, rhs, chain):
        weight = _TERM_SIZE(lhs) + _TERM_SIZE(rhs)
        if weight > self.max_weight_seen:
            self.max_weight_seen = weight
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

    def _pop(self):
        if self.select == "weight":
            if not self.passive:
                return None
            return heapq.heappop(self.passive)
        self.since_age += 1
        if self.since_age > self.ratio:
            self.since_age = 0
            while self.age_queue:
                entry = self.age_queue.popleft()
                if entry[1] in self.dead:
                    continue
                self.dead.add(entry[1])
                return entry
        while self.passive:
            entry = heapq.heappop(self.passive)
            if entry[1] in self.dead:
                continue
            self.dead.add(entry[1])
            return entry
        while self.age_queue:
            entry = self.age_queue.popleft()
            if entry[1] in self.dead:
                continue
            self.dead.add(entry[1])
            return entry
        return None

    def step(self):
        while True:
            if self.out_of_time():
                return None
            entry = self._pop()
            if entry is None:
                return None
            self.n_popped += 1
            _prio, _serial, lhs, rhs, chain = entry
            new_lhs, left_steps = self.normalize(lhs)
            new_rhs, right_steps = self.normalize(rhs)
            if new_lhs == new_rhs:
                continue
            full = ([(p, i, s, -d) for (p, i, s, d) in reversed(left_steps)]
                    + chain + right_steps)
            key = S._kb_canon_eq(new_lhs, new_rhs)
            if key in self.seen or self.subsumed(new_lhs, new_rhs):
                continue
            self.seen.add(key)
            eq = S._KBEquation(self.next_id, new_lhs, new_rhs, full)
            self.next_id += 1
            self.eqs[eq.eid] = eq
            self.active.append(eq)
            self.n_processed += 1
            if eq.weight > self.max_weight_used:
                self.max_weight_used = eq.weight
            if len(self.active) > self.max_active:
                if self.active_full == "stop":
                    self.expired = True
                elif self.active_full == "evict":
                    worst = max((e for e in self.active if e.chain is not None),
                                key=lambda e: e.weight, default=None)
                    if worst is not None and worst is not eq:
                        self.active.remove(worst)
            return eq

    def superpose(self, eq):
        cap = self.sup_max_size
        if eq.weight > cap:
            return
        for other in list(self.active):
            if other.weight > cap:
                continue
            for (lhs, rhs, chain) in self.crit_pairs(eq, other):
                self.push(lhs, rhs, chain)
            if other.eid != eq.eid:
                for (lhs, rhs, chain) in self.crit_pairs(other, eq):
                    self.push(lhs, rhs, chain)


def run_deepening(eq1, eq2, *, budget, want_cert=True, ladder=(44, 88, 176, 352,
                  704, 1408, 2816), **kw):
    """Iterative deepening on the pair-weight cap.

    18 of the 40 collapse rows saturate in < 1 s at cap 44 having generated
    only 1-34 pairs, with the dropped pairs reaching weight 200-1810.  For
    those rows the cap *is* the whole wall and a restart costs ~0 s; for the
    rows that expire instead, the ladder never advances, so nothing regresses.
    """
    t0 = time.time()
    kw.pop("max_size", None)
    best = None
    rungs = []
    for cap in ladder:
        left = budget - (time.time() - t0)
        if left <= 0.05:
            break
        res = run_completion(eq1, eq2, budget=left, want_cert=want_cert,
                             max_size=cap, **kw)
        rungs.append((cap, res["route"], res["seconds"], res["processed"]))
        best = res
        if res["route"] in ("collapse", "join", "bridge"):
            break
        if res["route"] != "saturated":
            break
        if res["max_weight_seen"] <= cap:
            break  # genuinely saturated: nothing was dropped
    best = best or {"route": "expired"}
    best["rungs"] = rungs
    best["seconds"] = round(time.time() - t0, 2)
    return best


def run_completion(eq1, eq2, *, budget, want_cert=True, fastkbo=True, **kw):
    if fastkbo:
        S._kbo_gt = fast_kbo_gt
    deadline = S.local_deadline(budget)
    t0 = time.time()
    comp = LabCompletion([(eq1["lhs"], eq1["rhs"])], deadline=deadline, **kw)
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
            if want_cert:
                code = S._kb_collapse_certificate(comp, eq, var, var_on_rhs, eq1, eq2)
                out["cert_bytes"] = len(code.encode()) if code else None
                out["cert"] = code
            break
        joined = comp.goal_join(eq2["lhs"], eq2["rhs"])
        if joined is not None:
            out["route"] = "join"
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
    out["max_weight_seen"] = comp.max_weight_seen
    out["max_weight_used"] = comp.max_weight_used
    out["active"] = len(comp.active)
    out["passive"] = len(comp.passive)
    return out


NOCAP = dict(max_size=10 ** 9, max_active=10 ** 9, max_passive=400000,
             active_full="ignore")

VARIANTS = {
    "shipped": dict(max_size=44, max_active=400, fastkbo=False),
    "shipped_fast": dict(max_size=44, max_active=400),
    "esc": dict(max_size=60, max_active=2000),
    "esc_big": dict(max_size=60, max_active=2000, max_passive=400000),
    "big": dict(max_size=200, max_active=2000, max_passive=400000),
    "nocap": dict(NOCAP),
    "nocap_slow": dict(NOCAP, fastkbo=False),
    "ratio": dict(NOCAP, select="ratio:5"),
    "ratio2": dict(NOCAP, select="ratio:2"),
    "goal": dict(NOCAP, select="ratio:5", prio="goalweight"),
    "goalpure": dict(NOCAP, prio="goalweight"),
    "sup44": dict(NOCAP, sup_max_size=44),
    "sup60": dict(NOCAP, sup_max_size=60),
    "sup80": dict(NOCAP, sup_max_size=80),
    "sup60_ratio": dict(NOCAP, sup_max_size=60, select="ratio:5"),
    "sup60_goal": dict(NOCAP, sup_max_size=60, select="ratio:5", prio="goalweight"),
    # --- iterative deepening on the pair-weight cap ---
    "deepen": dict(NOCAP, _deepen=True),
    "deepen_a2k": dict(max_active=2000, max_passive=400000, active_full="stop",
                       _deepen=True),
    "deepen_sup": dict(NOCAP, sup_max_size=60, _deepen=True),
    "deepen_goal": dict(NOCAP, prio="goalweight", _deepen=True),
}


def job(args):
    row, variant, budget = args
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    kw = dict(VARIANTS[variant])
    runner = run_deepening if kw.pop("_deepen", False) else run_completion
    try:
        res = runner(eq1, eq2, budget=budget, want_cert=False, **kw)
    except Exception as exc:  # noqa: BLE001
        res = {"route": "ERROR", "error": repr(exc)[:300], "seconds": 0}
    res["id"] = row["id"]
    res["variant"] = variant
    return res


def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def pick_rows(spec):
    if spec == "collapse40":
        return [r for r in load(CLASSIFY) if r["triage"] == "collapse_candidate"]
    if spec == "nosmall20":
        return [r for r in load(CLASSIFY) if r["triage"] != "collapse_candidate"]
    return load(spec)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="shipped")
    ap.add_argument("--budget", type=float, default=60.0)
    ap.add_argument("--procs", type=int, default=4)
    ap.add_argument("--rows", default="collapse40")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    rows = pick_rows(args.rows)
    jobs = [(r, args.variant, args.budget) for r in rows]
    t0 = time.time()
    with Pool(args.procs) as pool:
        out = pool.map(job, jobs, chunksize=1)
    wins = [r for r in out if r["route"] in ("collapse", "join", "bridge")]
    print("variant=%s budget=%s rows=%d WINS=%d (collapse=%d join=%d) wall=%.0fs"
          % (args.variant, args.budget, len(rows), len(wins),
             sum(1 for r in out if r["route"] == "collapse"),
             sum(1 for r in out if r["route"] == "join"), time.time() - t0))
    order = {"collapse": 0, "join": 1, "saturated": 2, "expired": 3, "ERROR": 4}
    for r in sorted(out, key=lambda r: (order.get(r["route"], 9), r.get("seconds", 0))):
        print("  %-22s %-10s %7.2fs proc=%-5s pop=%-6s push=%-7s dropS=%-7s"
              " dropF=%-7s maxw=%-5s usedw=%-4s act=%s"
              % (r["id"], r["route"], r.get("seconds", 0), r.get("processed", "-"),
                 r.get("popped", "-"), r.get("pushed", "-"),
                 r.get("dropped_size", "-"), r.get("dropped_full", "-"),
                 r.get("max_weight_seen", "-"), r.get("max_weight_used", "-"),
                 r.get("active", "-")))
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in out:
                fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
