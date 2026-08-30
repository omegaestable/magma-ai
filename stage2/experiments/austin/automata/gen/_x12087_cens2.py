"""Targeted: force N1 = op y x AND N3 = op x z to both decode, and report the rule each used
and the rule used at the final product.  Also report N2's status.
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
base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]

def enc(a, b, c):
    return C.op(C.op(C.op(a, b), c), C.op(b, c))

def st(u, v):
    r = C.op(u, v)
    return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))

cnt = collections.Counter()
bad = 0
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
for i in range(N):
    try:
        y = random.choice(base); p = random.choice(base); q = random.choice(base)
        x = enc(y, p, q)                      # op y x should decode to p
        if st(y, x) == 'F': continue
        mode = random.randrange(3)
        if mode == 0:
            p2 = random.choice(base)
        elif mode == 1:
            p2 = enc(x, random.choice(base), random.choice(base))   # op x p2 decodes
        else:
            p2 = enc(random.choice(base), random.choice(base), random.choice(base))
        Z = random.choice(base)
        z = enc(x, p2, Z)                     # op x z should decode to p2
        if st(x, z) == 'F': continue
        N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); R = C.op(y, V)
    except RecursionError:
        continue
    key = (st(y, x), st(N1, z), st(x, z), st(N2, N3), st(y, V))
    cnt[key] += 1
    if R != x:
        bad += 1
        if bad <= 3: print('BAD', key, {'x': size(x), 'y': size(y), 'z': size(z)})
print('bad', bad, 'hits', sum(cnt.values()))
for k, n in cnt.most_common(40):
    print('  %-34s %d' % (str(k), n))
