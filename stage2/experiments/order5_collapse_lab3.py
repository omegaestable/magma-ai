"""Order-5 collapse lab, round 3: unfailing-completion inference power.

Two shipped restrictions this measures:

1. `_KBEquation.ori` is empty whenever neither side's variables contain the
   other's (`(z*z) = (z'*z')`, "all squares are equal").  Such an equation is
   then INERT: `crit_pairs` iterates `ori`, so it never superposes, and
   `rewrite_once`/`_reduce_with` iterate `ori`, so it never rewrites.  Real
   unfailing completion superposes with BOTH directions of every equation and
   filters the result with the instance-level ordering check that `crit_pairs`
   already performs (`if _kbo_gt(rhs_inst, lhs_inst): continue`).

2. `_rewrite_ground_unoriented` -- the fill trick that lets an unorientable
   equation rewrite -- is gated on `ground`, i.e. it only ever applies to the
   skolemised goal.  Filling the unbound target variables with the smallest
   variable of the matched subterm keeps the variable condition true, so the
   ordinary (non-ground) KBO check still guarantees termination, and the
   rewrite is a sound instance of the equation.

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
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

import solver as S  # noqa: E402
import order5_collapse_lab as L1  # noqa: E402
import order5_collapse_lab2 as L2  # noqa: E402


def _var_merges(variables):
    """Every set partition of `variables`, as a var -> representative map."""
    if not variables:
        return [{}]
    out = []
    first, rest = variables[0], variables[1:]
    for sub in _var_merges(rest):
        groups = {}
        for v, w in sub.items():
            groups.setdefault(w, []).append(v)
        out.append(dict(sub, **{first: first}))
        for rep in groups:
            out.append(dict(sub, **{first: rep}))
    return out


def _kb_order_gt_mirror(source, target, ground):
    """`_kb_order_gt` with the lexicographic tie-break taken RIGHT argument
    first instead of left.

    Still a valid KBO (equal symbol weights, the other argument status), but a
    *different* reduction ordering, so completion orients different equations
    and explores a different search -- the cheapest orthogonal diversification
    available, and it needs no mirroring of the certificate because the
    ordering is only used to decide orientations.
    """
    ssz = S.term_size(source)
    tsz = S.term_size(target)
    if ssz != tsz:
        return ssz > tsz
    if source[0] == "var" or target[0] == "var":
        return (ground and source[0] == "var" and target[0] == "var"
                and source[1] > target[1])
    if source[2] != target[2]:
        return _kb_order_gt_mirror(source[2], target[2], ground)
    return _kb_order_gt_mirror(source[1], target[1], ground)


_KB_ORDER_GT_SHIPPED = S._kb_order_gt


def set_order(mode):
    S._kb_order_gt = (_kb_order_gt_mirror if mode == "mirror"
                      else _KB_ORDER_GT_SHIPPED)


def sup_orientations(eq):
    """Both directions, always -- unfailing completion's superposition set."""
    if eq.lhs == eq.rhs:
        return ()
    return ((eq.lhs, eq.rhs, 1), (eq.rhs, eq.lhs, -1))


class Lab3Completion(L2.Lab2Completion):

    def __init__(self, axioms, *, sup_ori="shipped", rw_unoriented=False,
                 seed_merges=False, **kw):
        self.sup_ori = sup_ori
        self.rw_unoriented = rw_unoriented
        self.seed_merges = seed_merges
        self.n_unoriented_rewrites = 0
        self.n_merge_seeds = 0
        super().__init__(axioms, **kw)
        if seed_merges:
            self._add_merge_instances()

    def _add_merge_instances(self):
        """Add every variable-merging instance of the axiom as a derived equation.

        An instance is logically redundant (it is subsumed by the axiom), but a
        *bounded* search is not closed under instantiation: merging y into x
        turns a weight-200 general self-overlap into a much smaller one that
        fits under the weight cap.  Rendering is free -- the instance carries
        the chain `[((), axiom, merge, 1)]`, which `_KBRenderer` emits as
        `have hlemN : ... := h <merged args>`.
        """
        base = self.eqs[self.axiom_ids[0]]
        variables = sorted(S.term_vars(base.lhs) | S.term_vars(base.rhs))
        for merge in _var_merges(variables):
            if all(v == w for v, w in merge.items()):
                continue
            subst = {v: ("var", w) for v, w in merge.items()}
            lhs = S.instantiate_term(base.lhs, subst)
            rhs = S.instantiate_term(base.rhs, subst)
            if lhs == rhs:
                continue
            key = S._kb_canon_eq(lhs, rhs)
            if key in self.seen:
                continue
            self.seen.add(key)
            eq = S._KBEquation(self.next_id, lhs, rhs,
                               [((), base.eid, dict(subst), 1)])
            self.next_id += 1
            self.eqs[eq.eid] = eq
            self.active.append(eq)
            self.n_merge_seeds += 1

    # ---- superposition with all orientations -----------------------------
    def crit_pairs(self, first, second):
        if self.sup_ori == "shipped":
            return super().crit_pairs(first, second)
        out = []
        first_ori = sup_orientations(first)
        second_ori = sup_orientations(second)
        for (lhs1, rhs1, dir1) in first_ori:
            for (lhs2_raw, rhs2_raw, dir2) in second_ori:
                tag = "#%d" % next(self.counter)
                lhs2 = S._kb_rename(lhs2_raw, tag)
                rhs2 = S._kb_rename(rhs2_raw, tag)
                for path in S._kb_nonvar_paths(lhs1):
                    if self.out_of_time():
                        return out
                    unified = S._kb_unify(S.term_at_path(lhs1, path), lhs2, {})
                    if unified is None:
                        continue
                    lhs1_inst = S._kb_resolve(lhs1, unified)
                    rhs1_inst = S._kb_resolve(rhs1, unified)
                    if S._kbo_gt(rhs1_inst, lhs1_inst):
                        continue
                    lhs2_inst = S._kb_resolve(lhs2, unified)
                    rhs2_inst = S._kb_resolve(rhs2, unified)
                    if S._kbo_gt(rhs2_inst, lhs2_inst):
                        continue
                    new_lhs = S._kb_resolve(
                        S.replace_subterm(lhs1, path, rhs2), unified)
                    if new_lhs == rhs1_inst:
                        continue
                    subst2 = {var: S._kb_resolve(("var", var + tag), unified)
                              for var in (S.term_vars(lhs2_raw) | S.term_vars(rhs2_raw))}
                    subst1 = {var: S._kb_resolve(("var", var), unified)
                              for var in (S.term_vars(first.lhs) | S.term_vars(first.rhs))}
                    out.append((new_lhs, rhs1_inst,
                                [(path, second.eid, subst2, -dir2),
                                 ((), first.eid, subst1, dir1)]))
        return out

    # ---- rewriting with unorientable equations ---------------------------
    def rewrite_once(self, term, ground):
        found = super().rewrite_once(term, ground)
        if found is not None or ground or not self.rw_unoriented:
            return found
        for path in S.subterm_paths_tuple(term):
            sub = S.term_at_path(term, path)
            if sub[0] != "op":
                continue
            if self.out_of_time():
                return None
            got = self._rewrite_unoriented(term, path, sub)
            if got is not None:
                self.n_unoriented_rewrites += 1
                return got
        return None

    def _rewrite_unoriented(self, term, path, sub):
        """`_rewrite_ground_unoriented`, but for a non-ground term.

        Filling the unbound target variables with the smallest variable of the
        matched subterm makes `vars(image) <= vars(sub)`, so the ordinary
        variable condition holds and `_kbo_gt(sub, image)` (non-ground) is the
        same reduction ordering the oriented path uses -- termination is
        preserved and the step is a sound instance of the equation.
        """
        sub_mask = S._kb_shape_mask(sub)
        sub_size = S.term_size(sub)
        fill = ("var", min(S.term_vars(sub)))
        for eq in self.active:
            present = {d for (_l, _r, d) in eq.ori}
            for (pat, target, direction) in ((eq.lhs, eq.rhs, 1),
                                             (eq.rhs, eq.lhs, -1)):
                if direction in present:
                    continue
                if S.term_size(pat) > sub_size or (S._kb_shape_mask(pat) & ~sub_mask):
                    continue
                subst = {}
                if not S.match_term(pat, sub, subst):
                    continue
                for var in sorted(S.term_vars(target) - set(subst)):
                    subst[var] = fill
                image = S.instantiate_term(target, subst)
                if image == sub or not S._kbo_gt(sub, image):
                    continue
                return (S.replace_subterm(term, path, image),
                        (path, eq.eid, subst, direction))
        return None


def run3(eq1, eq2, *, budget, want_cert=True, order="shipped", **kw):
    set_order(order)
    deadline = S.local_deadline(budget)
    t0 = time.time()
    comp = Lab3Completion([(eq1["lhs"], eq1["rhs"])], deadline=deadline, **kw)
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
            out["collapse_deps"] = len(L2._KBdeps(comp, eq))
            if want_cert:
                code = S._kb_collapse_certificate(comp, eq, var, var_on_rhs, eq1, eq2)
                out["cert_bytes"] = len(code.encode()) if code else None
                out["cert"] = code
            break
        joined = comp.goal_join(eq2["lhs"], eq2["rhs"])
        if joined is not None:
            out["route"] = "join"
            out["join_deps"] = len(L2._KBdeps_chain(comp, joined))
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
    out["rescued"] = comp.n_rescued
    out["unoriented_rewrites"] = comp.n_unoriented_rewrites
    out["merge_seeds"] = comp.n_merge_seeds
    out["max_weight_seen"] = comp.max_weight_seen
    out["max_weight_used"] = comp.max_weight_used
    out["active"] = len(comp.active)
    out["passive"] = len(comp.passive)
    return out


def run3_deepening(eq1, eq2, *, budget, want_cert=True,
                   ladder=(44, 88, 176, 352, 704), **kw):
    # `order` is forwarded through run3 by **kw.
    t0 = time.time()
    kw.pop("max_size", None)
    best, rungs = None, []
    for cap in ladder:
        left = budget - (time.time() - t0)
        if left <= 0.05:
            break
        res = run3(eq1, eq2, budget=left, want_cert=want_cert, max_size=cap, **kw)
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


# max_passive kept small: the term helpers are all unbounded lru_caches and a
# worker that never calls S.clear_term_caches() between rows reached 2.7 GB.
BASE = dict(max_active=2000, max_passive=30000, active_full="stop")

VARIANTS = {
    "base44": dict(BASE, max_size=44),
    "supall44": dict(BASE, max_size=44, sup_ori="all"),
    "rwuno44": dict(BASE, max_size=44, rw_unoriented=True),
    "both44": dict(BASE, max_size=44, sup_ori="all", rw_unoriented=True),
    "both60": dict(BASE, max_size=60, sup_ori="all", rw_unoriented=True),
    "both_norm44": dict(BASE, max_size=44, sup_ori="all", rw_unoriented=True,
                        norm_push="all"),
    "both_deep": dict(BASE, sup_ori="all", rw_unoriented=True, _deepen=True),
    "supall_deep": dict(BASE, sup_ori="all", _deepen=True),
    "rwuno_deep": dict(BASE, rw_unoriented=True, _deepen=True),
    "both_norm_deep": dict(BASE, sup_ori="all", rw_unoriented=True,
                           norm_push="all", _deepen=True),
    "merge44": dict(BASE, max_size=44, seed_merges=True),
    "merge_norm44": dict(BASE, max_size=44, seed_merges=True, norm_push="all"),
    "merge_deep": dict(BASE, seed_merges=True, norm_push="all", _deepen=True),
    "all_deep": dict(BASE, seed_merges=True, norm_push="all", sup_ori="all",
                     rw_unoriented=True, _deepen=True),
    "merge_uno_deep": dict(BASE, seed_merges=True, norm_push="all",
                           rw_unoriented=True, _deepen=True),
    "merge_supall_deep": dict(BASE, seed_merges=True, norm_push="all",
                              sup_ori="all", _deepen=True),
    "merge_supall_plain": dict(BASE, max_size=44, seed_merges=True,
                               norm_push="all", sup_ori="all"),
    "mirror_deep": dict(BASE, seed_merges=True, norm_push="all",
                        sup_ori="all", order="mirror", _deepen=True),
    "mirror_plain_deep": dict(BASE, order="mirror", _deepen=True),
}


def job(args):
    row, variant, budget = args
    S.clear_term_caches()
    eq1 = S.parse_equation(row["equation1"])
    eq2 = S.parse_equation(row["equation2"])
    kw = dict(VARIANTS[variant])
    runner = run3_deepening if kw.pop("_deepen", False) else run3
    try:
        res = runner(eq1, eq2, budget=budget, want_cert=False, **kw)
    except Exception as exc:  # noqa: BLE001
        res = {"route": "ERROR", "error": repr(exc)[:300], "seconds": 0}
    res["id"] = row["id"]
    res["variant"] = variant
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default="both44")
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
        print("  %-22s %-10s %7.2fs proc=%-5s deps=%-4s uno=%-6s dropS=%-7s"
              " maxw=%-5s act=%s"
              % (r["id"], r["route"], r.get("seconds", 0), r.get("processed", "-"),
                 r.get("collapse_deps", r.get("join_deps", "-")),
                 r.get("unoriented_rewrites", "-"), r.get("dropped_size", "-"),
                 r.get("max_weight_seen", "-"), r.get("active", "-")), flush=True)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for r in out:
                fh.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()
