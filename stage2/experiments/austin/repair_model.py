"""Partial term models with iterated critical-pair repair.

Rules R = [(L_i, r_i)], L_0 = T, r_0 = x.  Carrier: terms over leaves + JUNK.
op(a, b): t = node(a, b)
   - first rule whose LHS matches t (structural, nonlinear-consistent) -> eval(r_i, bindings)
   - else if t is an instance of a proper non-variable subterm of some L_i -> t
   - else JUNK
Repair loop: compute critical pairs between rule LHSs (unification), reduce
both sides under the current rules, orient the bigger side to the smaller as a
new rule; re-check eq1 exhaustively over the reachable universe; stop when it
holds, or when the rule count / round cap is hit.
"""
from __future__ import annotations
import json, sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from austin_z3 import parse, variables  # noqa: E402
from term_model import (to_term, match, subst, unify, resolve, rename, positions,  # noqa: E402
                        replace, size, _vars, _inst)

JUNK = ('J',)


class Model:
    def __init__(self, text):
        l, r = parse(text)
        self.x = l[1]
        self.T = to_term(r)
        self.vars = variables(l, variables(r, []))
        self.rules = [(self.T, ('v', self.x))]
        self._refresh()

    def _refresh(self):
        subs = set()
        for L, _ in self.rules:
            for pos, t in positions(L):
                if pos:
                    subs.add(t)
        # most specific first so a node keeps the richest structure
        self.subpats = sorted(subs, key=lambda t: -size(t))

    def op(self, a, b, depth=0):
        t = ('n', a, b)
        if depth > 50:
            raise RuntimeError('op recursion')
        for L, r in self.rules:
            sub = {}
            if match(L, t, sub):
                return self.eval(r, sub, depth + 1)
        for P in self.subpats:
            if match(P, t, {}):
                return t
        return JUNK

    def eval(self, term, env, depth=0):
        if term[0] == 'v':
            return env[term[1]]
        if term[0] == 'L' or term[0] == 'J':
            return term
        return self.op(self.eval(term[1], env, depth), self.eval(term[2], env, depth), depth)

    def universe(self, gens=2, depth=2, cap=400):
        elems = {('L', i) for i in range(gens)} | {JUNK}
        for _ in range(depth):
            new = set()
            lst = list(elems)
            for a in lst:
                for b in lst:
                    try:
                        e = self.op(a, b)
                    except RuntimeError:
                        continue
                    if e not in elems:
                        new.add(e)
            elems |= new
            if not new or len(elems) > cap:
                break
        return sorted(elems, key=lambda e: (size(e) if e[0] == 'n' else 0, str(e)))[:cap]

    def check_law(self, elems, limit=1, rounds=600, seed=0):
        import random
        rng = random.Random(seed)
        bad = []
        pool = list(elems)

        def fill_pattern(pat, fills, depth):
            if pat[0] == 'v':
                if pat[1] not in fills:
                    fills[pat[1]] = self.random_elem(rng, pool, depth)
                return fills[pat[1]]
            return self.op(fill_pattern(pat[1], fills, depth), fill_pattern(pat[2], fills, depth))

        cps = self.cp_substitutions()
        tests = []
        # (a) exhaustive over the small universe
        for vals in itertools.product(elems[:12], repeat=len(self.vars)):
            tests.append(dict(zip(self.vars, vals)))
        # (b) critical-pair-derived assignments with random fillings
        for _ in range(rounds):
            if cps and rng.random() < 0.7:
                sigma = rng.choice(cps)
                fills = {}
                env = {}
                for v in self.vars:
                    pat = sigma.get(v, ('v', v))
                    try:
                        env[v] = fill_pattern(pat, fills, 2)
                    except RuntimeError:
                        env = None
                        break
                if env is None:
                    continue
            else:
                env = {v: self.random_elem(rng, pool, 3) for v in self.vars}
            tests.append(env)
        for env in tests:
            try:
                got = self.eval(self.T, env)
            except RuntimeError:
                got = 'LOOP'
            if got != env[self.x]:
                bad.append((env, got))
                if len(bad) >= limit:
                    break
        return bad

    def random_elem(self, rng, pool, depth):
        """A random element: from the pool, or a random sub-pattern instance."""
        if depth <= 0 or rng.random() < 0.4:
            return rng.choice(pool)
        P = rng.choice(self.subpats)
        fills = {}

        def go(pat):
            if pat[0] == 'v':
                if pat[1] not in fills:
                    fills[pat[1]] = self.random_elem(rng, pool, depth - 1)
                return fills[pat[1]]
            return self.op(go(pat[1]), go(pat[2]))
        try:
            return go(P)
        except RuntimeError:
            return rng.choice(pool)

    def cp_substitutions(self):
        """Unifiers of T's proper subterms with any rule LHS, restricted to T's variables."""
        out = []
        for j, (L2, _) in enumerate(self.rules):
            L2r = rename(L2, f"_{j}")
            for pos, sub_t in positions(self.T):
                if not pos:
                    continue
                sub = {}
                if unify(sub_t, L2r, sub):
                    out.append({v: resolve(('v', v), sub) for v in self.vars})
        return out

    def realisable(self, p):
        """Every non-variable subterm is an instance of a rule sub-pattern (buildable without junk)."""
        for pos, t in positions(p):
            if not any(match(P, t, {}) for P in self.subpats) and not any(match(L, t, {}) for L, _ in self.rules):
                return False
        return True

    # ---- rewriting on patterns (terms with variables) for critical pairs
    def reduce(self, t, fuel=60):
        """Innermost normalisation of a pattern under the rules (variables inert)."""
        if t[0] != 'n':
            return t
        l = self.reduce(t[1], fuel); r = self.reduce(t[2], fuel)
        t = ('n', l, r)
        for L, rr in self.rules:
            sub = {}
            if match(L, t, sub):
                if fuel <= 0:
                    return t
                return self.reduce(subst(rr, sub), fuel - 1)
        return t

    def critical_pairs(self):
        out = []
        for i, (L1, r1) in enumerate(self.rules):
            for j, (L2, r2) in enumerate(self.rules):
                L2r, r2r = rename(L2, f"_{j}"), rename(r2, f"_{j}")
                for pos, sub_t in positions(L1):
                    if not pos and i == j:
                        continue
                    sub = {}
                    if unify(sub_t, L2r, sub):
                        p1 = self.reduce(resolve(r1, sub))
                        p2 = self.reduce(resolve(replace(L1, pos, r2r), sub))
                        if p1 != p2:
                            out.append((p1, p2))
        return out

    def repair_round(self, max_rules):
        added = 0
        for p1, p2 in self.critical_pairs():
            big, small = (p2, p1) if size(p2) >= size(p1) else (p1, p2)
            if big[0] != 'n':
                continue  # cannot orient a variable
            # variables of small must occur in big
            if not set(v[1] for v in _vars(small)) <= set(v[1] for v in _vars(big)):
                continue
            if any(L == big for L, _ in self.rules):
                continue
            if not self.realisable(big):
                continue
            self.rules.append((big, small))
            added += 1
            if len(self.rules) >= max_rules:
                break
        self._refresh()
        return added


def refute(m, eq2_text, elems):
    l, r = parse(eq2_text)
    l, r = to_term(l), to_term(r)
    vs = variables(parse(eq2_text)[0], variables(parse(eq2_text)[1], []))
    for vals in itertools.product(elems[:12], repeat=len(vs)):
        env = dict(zip(vs, vals))
        try:
            if m.eval(l, env) != m.eval(r, env):
                return env
        except RuntimeError:
            return None
    return None


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    max_rules = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    groups = {}
    for r in rows:
        groups.setdefault(r['equation1'], []).append(r)
    wins = 0
    for eq1_text, rs in groups.items():
        m = Model(eq1_text)
        tag = rs[0].get('eq1_id', rs[0]['id'])
        status = 'open'
        for rnd in range(6):
            elems = m.universe(gens=2, depth=depth)
            bad = m.check_law(elems, limit=1)
            if not bad:
                status = f'HOLDS with {len(m.rules)} rules over {len(elems)} elems'
                break
            added = m.repair_round(max_rules)
            if added == 0 or len(m.rules) >= max_rules:
                status = f'fails ({len(m.rules)} rules, {len(elems)} elems, no more repairs)' if added == 0 else f'fails at rule cap {len(m.rules)}'
                break
        line = f"{tag}: {eq1_text} | {status}"
        if status.startswith('HOLDS'):
            wins += 1
            refs = [(r['id'], refute(m, r['equation2'], elems) is not None) for r in rs]
            line += f" | refutes {refs} | rules={[(str(L)[:60], str(r_)[:30]) for L, r_ in m.rules[1:]]}"
        print(line, flush=True)
    print('laws with a repaired model:', wins, '/', len(groups))


if __name__ == '__main__':
    main()
