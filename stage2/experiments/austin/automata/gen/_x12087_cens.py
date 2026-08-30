"""Targeted configuration census for the 12087 law chain (4-rule model).

Bias x,y,z to be encodings so that N1/N2/N3 decode, and record for each product which rule fired
(F = free, 0..3 = rule index).  Prints every distinct (N1,N2,N3,V,final) pattern with counts.
"""
import sys, os, random, collections
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
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
base = [rand_term(random.randint(1, 3), 3) for _ in range(600)]

def encode(a, b, c):
    """the law's RHS for y=a, x=b, z=c -- decodes to b under a"""
    return C.op(C.op(C.op(a, b), c), C.op(b, c))

pool = list(base)
for i in range(4000):
    try:
        pool.append(encode(random.choice(pool), random.choice(pool), random.choice(pool)))
    except RecursionError:
        pass
# a second generation, so encodings of encodings exist
gen2 = []
for i in range(3000):
    try:
        gen2.append(encode(random.choice(pool), random.choice(pool), random.choice(pool)))
    except RecursionError:
        pass
pool = pool + gen2

cnt = collections.Counter()
bad = 0
N = 120000
for i in range(N):
    x = random.choice(pool); y = random.choice(pool); z = random.choice(pool)
    try:
        N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); R = C.op(y, V)
    except RecursionError:
        continue
    def st(u, v, r):
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    key = (st(y, x, N1), st(N1, z, N2), st(x, z, N3), st(N2, N3, V), st(y, V, R))
    cnt[key] += 1
    if R != x:
        bad += 1
        if bad <= 3: print('BAD', key, {'x': size(x), 'y': size(y), 'z': size(z)})
print('tested', N, 'bad', bad)
print('cfg (N1 N2 N3 V | final)')
for k, n in cnt.most_common(60):
    print('  %-34s %d' % (str(k), n))
