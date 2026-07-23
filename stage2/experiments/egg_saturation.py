"""Ground equality saturation prototype ("mini-egg") — dev experiment only.

Validated 2026-07-23: cracks 29/67 of the then-current TRUE-miss rows and 4/9
ETP explicit edges the CP closure provably cannot traverse, with 0/25 false
positives on ETP-FALSE pairs. Evidence and port rails:
`stage2/results/2026-07-23-spotcheck-batches-and-egg-frontier-study.md`.
Saturation-only — proof extraction (proof forest -> T/S/C h-instance
exact_expr, kernel-checked) is the port's main work item.

Structured after reading the ETP MagmaEgg proofs. Key structural facts lifted
from the real proofs:

1. every auxiliary term is a PRODUCT OF TWO EARLIER TERMS (v4 = x*v3, ...),
   so the candidate universe is the product-closure of the goal subterms;
2. eq1 is applied (expansion) only AT pool terms, with free vars drawn from
   the pool, cheapest instantiations first;
3. contraction (big-side pattern -> small side) is applied exhaustively —
   it has no free vars and only merges;
4. congruence closure by batched rebuild (egg's approach).
Saturation-only; proof extraction is a later, mechanical step.
"""
from __future__ import annotations
import time
from itertools import product


class EGraph:
    def __init__(self):
        self.parent: list[int] = []
        self.size_rep: list[int] = []
        self.enodes: dict[tuple, int] = {}

    def find(self, a: int) -> int:
        while self.parent[a] != a:
            self.parent[a] = self.parent[self.parent[a]]
            a = self.parent[a]
        return a

    def canon(self, node: tuple) -> tuple:
        if node[0] == "op":
            return ("op", self.find(node[1]), self.find(node[2]))
        return node

    def add_node(self, node: tuple, size: int) -> int:
        node = self.canon(node)
        cid = self.enodes.get(node)
        if cid is not None:
            cid = self.find(cid)
            if size < self.size_rep[cid]:
                self.size_rep[cid] = size
            return cid
        cid = len(self.parent)
        self.parent.append(cid)
        self.size_rep.append(size)
        self.enodes[node] = cid
        return cid

    def add_term(self, term) -> int:
        if term[0] == "var":
            return self.add_node(term, 1)
        a = self.add_term(term[1])
        b = self.add_term(term[2])
        sz = self.size_rep[self.find(a)] + self.size_rep[self.find(b)] + 1
        return self.add_node(("op", a, b), sz)

    def merge(self, a: int, b: int) -> bool:
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.parent[a] = b
        self.size_rep[b] = min(self.size_rep[b], self.size_rep[a])
        return True

    def rebuild(self):
        """Recanonicalize all enodes; merge congruent duplicates to fixpoint."""
        changed = True
        while changed:
            changed = False
            fresh: dict[tuple, int] = {}
            for node, cid in self.enodes.items():
                node2 = self.canon(node)
                cid = self.find(cid)
                other = fresh.get(node2)
                if other is None:
                    fresh[node2] = cid
                elif self.find(other) != cid:
                    self.merge(other, cid)
                    changed = True
            self.enodes = fresh

    def class_nodes(self) -> dict[int, list[tuple]]:
        by: dict[int, list[tuple]] = {}
        for node, cid in self.enodes.items():
            by.setdefault(self.find(cid), []).append(self.canon(node))
        return by

    def ematch(self, pattern, cid: int, subst: dict, by_class):
        cid = self.find(cid)
        if pattern[0] == "var":
            v = pattern[1]
            bound = subst.get(v)
            if bound is not None:
                if self.find(bound) == cid:
                    yield subst
                return
            s2 = dict(subst)
            s2[v] = cid
            yield s2
            return
        for node in by_class.get(cid, ()):
            if node[0] != "op":
                continue
            for s1 in self.ematch(pattern[1], node[1], subst, by_class):
                yield from self.ematch(pattern[2], node[2], s1, by_class)

    def instantiate(self, pattern, subst: dict) -> int:
        if pattern[0] == "var":
            return self.find(subst[pattern[1]])
        a = self.instantiate(pattern[1], subst)
        b = self.instantiate(pattern[2], subst)
        sz = self.size_rep[self.find(a)] + self.size_rep[self.find(b)] + 1
        return self.add_node(("op", a, b), sz)


def pattern_vars(t, acc=None):
    if acc is None:
        acc = set()
    if t[0] == "var":
        acc.add(t[1])
    else:
        pattern_vars(t[1], acc)
        pattern_vars(t[2], acc)
    return acc


def subterms(t, acc):
    acc.append(t)
    if t[0] == "op":
        subterms(t[1], acc)
        subterms(t[2], acc)
    return acc


def saturate(eq1, goal_lhs, goal_rhs, *,
             rounds=30, time_budget=20.0,
             pool_max=36, expand_targets=14, free_pool=12,
             expand_cap=900, max_enodes=60000):
    """eq1 = (lhs_pattern, rhs_pattern) with UPPERCASE vars."""
    eg = EGraph()
    L = eg.add_term(goal_lhs)
    R = eg.add_term(goal_rhs)

    # pool seed: all goal subterms
    pool: list[int] = []
    for t in subterms(goal_lhs, []) + subterms(goal_rhs, []):
        cid = eg.add_term(t)
        if cid not in pool:
            pool.append(cid)

    lhs_p, rhs_p = eq1
    orientations = []
    for a, b in ((lhs_p, rhs_p), (rhs_p, lhs_p)):
        free = sorted(pattern_vars(b) - pattern_vars(a))
        orientations.append((a, b, free))

    deadline = time.monotonic() + time_budget
    stats = {"rounds": 0, "applied": 0}
    done: set = set()

    for rnd in range(rounds):
        stats["rounds"] = rnd + 1
        if time.monotonic() > deadline or len(eg.enodes) > max_enodes:
            break

        # widen the expansion frontier as the universe grows, so the done-set
        # cannot starve later rounds
        expand_targets = min(pool_max, 10 + 6 * rnd)
        free_pool = min(18, 8 + 2 * rnd)

        # 1. grow pool: products of current pool members
        cur = sorted({eg.find(c) for c in pool}, key=lambda c: eg.size_rep[c])
        pool = cur[:pool_max]
        prods = []
        for p in pool[:expand_targets]:
            for q in pool[:expand_targets]:
                sz = eg.size_rep[p] + eg.size_rep[q] + 1
                prods.append(eg.add_node(("op", p, q), sz))
        for c in prods:
            c = eg.find(c)
            if c not in pool and len(pool) < pool_max:
                pool.append(c)

        by_class = eg.class_nodes()

        # 2. exhaustive contractions + matched expansions (no free-var choice)
        apps = []
        for oi, (a, b, free) in enumerate(orientations):
            # A bare-variable LHS matches every class; the MagmaEgg proofs
            # only ever expand at pool terms, so restrict those targets.
            if a[0] == "var":
                classes = pool[:expand_targets]
            else:
                classes = list(by_class)
            for cid in classes:
                if time.monotonic() > deadline:
                    break
                for subst in eg.ematch(a, cid, {}, by_class):
                    key = (oi, cid, tuple(sorted((v, eg.find(c)) for v, c in subst.items())), ())
                    if not free:
                        if key in done:
                            continue
                        apps.append((0, key, cid, b, subst))
                    else:
                        # 3. free vars from pool, cheapest first
                        for combo in product(pool[:free_pool], repeat=len(free)):
                            s2 = dict(subst)
                            s2.update(zip(free, combo))
                            key2 = key[:3] + (tuple(eg.find(c) for c in combo),)
                            if key2 in done:
                                continue
                            cost = sum(eg.size_rep[eg.find(c)] for c in s2.values())
                            apps.append((cost, key2, cid, b, s2))
        apps.sort(key=lambda x: x[0])

        merged_any = False
        capped = False
        applied_now = 0
        for cost, key, cid, rhs, subst in apps:
            if applied_now > expand_cap and cost > 0:
                capped = True
                break
            if time.monotonic() > deadline or len(eg.enodes) > max_enodes:
                capped = True
                break
            if key in done:
                continue
            done.add(key)
            applied_now += 1
            rhs_cid = eg.instantiate(rhs, subst)
            if eg.merge(cid, rhs_cid):
                merged_any = True
                stats["applied"] += 1
                if eg.find(L) == eg.find(R):
                    break
        eg.rebuild()

        if eg.find(L) == eg.find(R):
            break
        if not merged_any and not capped:
            break

    stats["enodes"] = len(eg.enodes)
    stats["classes"] = len({eg.find(i) for i in range(len(eg.parent))})
    return eg.find(L) == eg.find(R), stats


if __name__ == "__main__":
    import sys
    from pathlib import Path
    REPO = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO / "stage2" / "solver"))
    import solver as S

    eqs = [l.strip() for l in (REPO / "data/exports/equations.txt").read_text(encoding="utf-8").splitlines() if l.strip()]

    def upper(eq):
        def walk(t):
            if t[0] == "var":
                return ("var", t[1].upper())
            return ("op", walk(t[1]), walk(t[2]))
        return walk(eq["lhs"]), walk(eq["rhs"])

    EDGES = [
        ("Eq1057=>Eq4 (proj!)", 1057, 4),
        ("Eq1695=>Eq1932", 1695, 1932),
        ("Eq2398=>Eq2567", 2398, 2567),
        ("Eq2666=>Eq2860", 2666, 2860),
        ("Eq1703=>Eq2113", 1703, 2113),
        ("Eq3561=>Eq3577", 3561, 3577),
        ("Eq2042=>Eq2893", 2042, 2893),
        ("Eq1491=>Eq359", 1491, 359),
        ("Eq3051=>Eq3082", 3051, 3082),
    ]
    for name, a, b in EDGES:
        eq1 = S.parse_equation(eqs[a - 1])
        eq2 = S.parse_equation(eqs[b - 1])
        t0 = time.monotonic()
        ok, st = saturate(upper(eq1), eq2["lhs"], eq2["rhs"])
        dt = time.monotonic() - t0
        print(f"{name:24s} proved={'YES' if ok else 'no '} {dt:6.1f}s {st}", flush=True)
