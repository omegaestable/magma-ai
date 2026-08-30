"""Configuration census for the 12087 law chain under the 4-rule model.

For each random (x,y,z): record which of N1=op y x, N2=op N1 z, N3=op x z, V=op N2 N3 are free,
and which rule fires at the final product op y V.
"""
import sys, os, random, collections
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('gen/rep12087/chk12087.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
TAGS = [r[2] for r in rules]

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
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
terms = [rand_term(random.randint(1, 4), 3) for _ in range(3000)]
# include encodings so decodes actually happen
pool = list(terms)
for i in range(3000):
    a, b, c = random.choice(terms), random.choice(terms), random.choice(terms)
    try:
        enc = C.op(C.op(C.op(a, b), c), C.op(b, c))   # ((y x) z)(x z) with y=a,x=b,z=c
        pool.append(enc)
    except RecursionError:
        pass

cnt = collections.Counter()
bad = 0
for i in range(40000):
    x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
    try:
        N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); R = C.op(y, V)
    except RecursionError:
        continue
    def st(u, v, r):
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    key = (st(y, x, N1), st(N1, z, N2), st(x, z, N3), st(N2, N3, V), st(y, V, R))
    cnt[key] += 1
    if R != x: bad += 1
print('bad', bad)
print('cfg  N1 N2 N3 V | final')
for k, n in cnt.most_common(40):
    print('  %-30s %d' % (str(k), n))
