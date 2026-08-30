"""Constructive search for a counterexample to INJ / UNI on the 4-rule 12087 model.

UNI: for a fixed v, at most one u has op u v != J u v.
Build v from the R3 side (v = J (op (op u' X) Z) (J X Z)) and from the R4 side, then test every
plausible other u.
"""
import sys, os, random, itertools
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('gen/rep12087/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

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
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; ri = i; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        else: self.ruleof[key] = ri
        self.memo[key] = res
        return res

C = C2(law, rules)
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 1)

def subterms(t, acc):
    acc.append(t)
    if t[0] == 'J': subterms(t[1], acc); subterms(t[2], acc)
    return acc

def dec(u, v):
    try: r = C.op(u, v)
    except RecursionError: return None
    return None if r == ('J', u, v) else r

pool = [rand_term(random.randint(1, 3), 3) for _ in range(400)]
# encodings, to get decodable terms in the pool
enc = []
for i in range(1500):
    a, b, c = random.choice(pool), random.choice(pool), random.choice(pool)
    try:
        e = C.op(C.op(C.op(a, b), c), C.op(b, c))
    except RecursionError:
        continue
    enc.append(e)
pool2 = pool + enc

found = 0
tested = 0
for trial in range(60000):
    up = random.choice(pool2); X = random.choice(pool2); Z = random.choice(pool2)
    try:
        W = C.op(up, X); A = C.op(W, Z)
    except RecursionError:
        continue
    v = ('J', A, ('J', X, Z))
    r0 = dec(up, v)
    if r0 is None: continue
    tested += 1
    cands = set(subterms(v, [])) | set(pool2[:120])
    for u2 in cands:
        if u2 == up: continue
        r1 = dec(u2, v)
        if r1 is not None:
            found += 1
            print('UNI VIOLATION: v sz', size(v), 'u1 sz', size(up), 'rule', C.ruleof.get((up, v)),
                  'u2 sz', size(u2), 'rule', C.ruleof.get((u2, v)), 'r0 sz', size(r0), 'r1 sz', size(r1))
            if found > 5: sys.exit(0)
print('constructed decodable v:', tested, 'UNI violations:', found)
