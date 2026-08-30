"""Is even the 13-rule set a model?  Deeper encoding pools, several seeds; plus how many rules each depth needs."""
import sys, os, random, collections, json, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
R = X.rules(exist=False)
RE = X.rules(exist=True)
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

def census(rules, N, seed, gens_deep):
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def st(u, v):
        r = C.op(u, v)
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    pool = list(base)
    for _ in range(gens_deep):
        nxt = []
        for _ in range(250):
            try: nxt.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
            except RecursionError: pass
        pool = pool + nxt
    base = pool
    bad = 0; hits = 0; cells = collections.Counter(); badcells = collections.Counter()
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
            bad += 1; badcells[k] += 1
    return hits, bad, cells, badcells

for name, rules in [('full13', R), ('exist%d' % len(RE), RE)]:
    for gd in (1, 2, 3):
        for sd in (13, 23, 31):
            t0 = time.time()
            try:
                h, b, c, bc = census(rules, 900, sd, gd)
            except RecursionError:
                print('%-8s gens_deep=%d seed=%d RecursionError' % (name, gd, sd), flush=True); continue
            print('%-8s gens_deep=%d seed=%-3d hits=%d BAD=%d  (%.0fs)' % (name, gd, sd, h, b, time.time()-t0), flush=True)
            if b: print('     badcells', dict(bc.most_common(5)), flush=True)
            print('     cells', dict(c.most_common(6)), flush=True)
