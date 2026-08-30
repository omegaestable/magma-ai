"""Search for the smallest rule subset of the 13 extracted rules that survives the both-decoded census."""
import sys, os, random, collections, json, itertools, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
R = X.rules(exist=False)
TAGS = [r[2] for r in R]

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

def census(rules, N=1500, seed=5, basesize=3, gens=2):
    C = C2(law, rules)
    random.seed(seed)
    base = [rand_term(random.randint(1, basesize), gens) for _ in range(200)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def st(u, v):
        r = C.op(u, v)
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    bad = 0; hits = 0; cells = collections.Counter()
    for i in range(N):
        try:
            y = random.choice(base); p = random.choice(base); q = random.choice(base)
            x = enc(y, p, q)
            if st(y, x) == 'F': continue
            mode = random.randrange(3)
            if mode == 0: p2 = random.choice(base)
            elif mode == 1: p2 = enc(x, random.choice(base), random.choice(base))
            else: p2 = enc(random.choice(base), random.choice(base), random.choice(base))
            Z = random.choice(base)
            z = enc(x, p2, Z)
            if st(x, z) == 'F': continue
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); Rr = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        cells[(st(y, x), st(N1, z), st(x, z), st(N2, N3), st(y, V))] += 1
        if Rr != x: bad += 1
    return hits, bad, cells

base4 = [0, 1, 10, 3]      # free, B1l, B0l, B00l,B1l
t0 = time.time()
print('base4 alone:', census([R[i] for i in base4])[:2])
best = []
for j in range(13):
    if j in base4: continue
    idx = sorted(base4 + [j])
    h, b, c = census([R[i] for i in idx])
    print('  +%-2d %-24s hits=%d BAD=%d' % (j, TAGS[j], h, b), flush=True)
    if b == 0: best.append(idx)
print('OK 5-rule sets:', [[TAGS[i] for i in s] for s in best])
print('secs', round(time.time()-t0, 1))
json.dump(best, open('gen/_w3_12087_ok5.json', 'w'))
