"""Full wave-3 validation of the 5-rule candidates for 12087."""
import sys, os, random, collections, json, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, smallcheck as sc
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

def census(rules, N, seed, basesize, gens, deep2=False):
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, basesize), gens) for _ in range(200)]
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
    bad = 0; hits = 0; cells = collections.Counter(); worst = None
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
        k = (st(y, x), st(N1, z), st(x, z), st(N2, N3), st(y, V))
        cells[k] += 1
        if Rr != x:
            bad += 1
            t = size(x)+size(y)+size(z)
            if worst is None or t < worst[0]: worst = (t, x, y, z, k)
    return hits, bad, cells, worst

CAND = {'A_fflf': [0,1,3,5,10], 'B_ffll': [0,1,3,6,10], 'full13': list(range(13))}
for name, idx in CAND.items():
    rules = [R[i] for i in idx]
    t0 = time.time()
    print('=== %s  tags=%s' % (name, [TAGS[i] for i in idx]), flush=True)
    # 1. exhaustive small terms
    n1, f1 = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=5)
    n2, f2 = sc.exhaustive(cf.Closed(law, rules), law, 5, 2, limit=5)
    print('   exhaustive 9/1: %d fails=%d ; 5/2: %d fails=%d' % (n1, len(f1), n2, len(f2)), flush=True)
    # 2. rv.run_tests
    fails = rv.run_tests(law, rules, [3,4,5], 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = collections.Counter(f[2] for f in real)
    print('   run_tests fails=%d real=%d kinds=%s (%.1fs)' % (len(fails), len(real), dict(kinds), time.time()-t0), flush=True)
    for f in real[:3]: print('     ', f[2], f[3], {k: size(v) for k,v in f[0].items()}, flush=True)
    # 3. deep_tests 20k x 3 seeds
    for sd in (101, 202, 303, 404):
        C = cf.Closed(law, rules); t, ff = cf.deep_tests(C, law, 20000, 300, sd)
        rr = [q for q in ff if q[1] != 'recursion']
        print('   deep20k seed %d tested=%d fails=%d real=%d' % (sd, t, len(ff), len(rr)), flush=True)
    # 4. census on several seeds / shapes
    for (sd, bs, g, d2) in [(5,3,2,False),(7,3,2,False),(11,2,3,False),(13,3,2,True),(17,4,2,False)]:
        h, b, c, w = census(rules, 1500, sd, bs, g, d2)
        print('   census seed=%d base<=%d gens=%d deep2=%s hits=%d BAD=%d' % (sd, bs, g, d2, h, b), flush=True)
        if b:
            print('      cells:', dict(c.most_common(5)), flush=True)
            print('      worst sizes', w[0], flush=True)
    print('   total %.1fs' % (time.time()-t0), flush=True)
