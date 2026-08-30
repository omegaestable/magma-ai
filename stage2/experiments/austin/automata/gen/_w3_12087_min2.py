# -*- coding: utf-8 -*-
"""Lever 3, done properly: minimise the closedform2 11-rule set against the BOTH-DECODED census
(the oracle that actually killed S6), not the 16-cell tree (which accepts rep4 and is therefore unsound
as an acceptance test)."""
import sys, os, random, collections, json, time
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import closedform as cf, closedform2 as cf2, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
R1 = cf.Extractor(law).rules(exist=False)
R2, _info = cf2.extract(law)
S7 = [R1[i] for i in [0, 1, 2, 3, 5, 8, 10]]


class C2(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules); self.ruleof = {}
    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None; ri = None
        for i, (conds, xx, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(xx, u, v)
                if r is not None:
                    res = r; ri = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        else: self.ruleof[key] = ri
        self.memo[key] = res
        return res


def census(rules, N, seed, deep2=False):
    """the both-decoded construction of gen/_x12087_cens3.py: keep only trials in which op(y,x) AND
    op(x,z) actually decode.  This is the oracle that showed rep4 (649/2000) and S6 FALSE."""
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def st(u, v):
        r = C.op(u, v)
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    if deep2:
        pool = list(base)
        for _ in range(400):
            try: pool.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
            except RecursionError: pass
        base = pool
    bad = 0; hits = 0
    for i in range(N):
        try:
            y = random.choice(base); p = random.choice(base); q = random.choice(base)
            x = enc(y, p, q)
            if st(y, x) == 'F': continue
            mode = random.randrange(4)
            if mode == 0: p2 = random.choice(base)
            elif mode == 1: p2 = enc(x, random.choice(base), random.choice(base))
            elif mode == 2: p2 = enc(random.choice(base), random.choice(base), random.choice(base))
            else: p2 = enc(random.choice(base), x, random.choice(base))
            Z = random.choice(base)
            z = enc(x, p2, Z) if random.random() < 0.8 else enc(random.choice(base), p2, Z)
            if st(x, z) == 'F': continue
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); Rr = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        if Rr != x: bad += 1
    return hits, bad


def ok(rules, N=900, seeds=(5, 13, 23)):
    n1, f1 = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=1)
    if f1: return False
    for sd in seeds:
        h, b = census(rules, N, sd, deep2=False)
        if b: return False
    h, b = census(rules, N, 13, deep2=True)
    return b == 0


# sanity: the oracle must REJECT rep4 and ACCEPT S7
rep4 = [R1[i] for i in [0, 1, 10, 3]]
print('oracle sanity: rep4 ok=%s (must be False) ; S7 ok=%s (must be True)' % (ok(rep4), ok(S7)), flush=True)

for start_name, start in (('cf2_11', list(R2)), ('S7', list(S7))):
    keep = list(start); removed = []; changed = True
    while changed:
        changed = False
        for i in range(len(keep) - 1, -1, -1):
            if keep[i][2] == 'free': continue
            trial = keep[:i] + keep[i + 1:]
            if ok(trial):
                removed.append(keep[i][2]); keep = trial; changed = True
                print('  [%s] dropped %-24s -> %d rules' % (start_name, removed[-1], len(keep)), flush=True)
                break
    print('MINIMAL from %s: %d rules %s' % (start_name, len(keep), [r[2] for r in keep]), flush=True)
    json.dump([r[2] for r in keep], open(os.path.join(D, 'gen', '_w3_12087_min_%s.json' % start_name), 'w'))
