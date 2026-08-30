"""FULL case tree for 12087: force each of the four chain products N1,N2,N3,V to decode, by construction.

chain: N1 = op(y,x)  N2 = op(N1,z)  N3 = op(x,z)  V = op(N2,N3)  R = op(y,V)
enc(a,b,c) = op(op(op(a,b),c), op(b,c))   decodes to b under a.
To force op(P,Q) to decode we build Q = enc(P, ...).  N1 and N3 are directly constructible that way
(x = enc(y,..), z = enc(x,..)); N2 needs z = enc(N1,..) and V needs N3 = enc(N2,..) which is not free to
choose -- so we ALSO search for them by biased sampling and report which cells are reachable at all.
"""
import sys, os, random, collections, json, time
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
R = X.rules(exist=False)
SETS = {'S7': [0,1,2,3,5,8,10], 'full13': list(range(13))}

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

def run(name, idx, N, seed):
    rules = [R[i] for i in idx]
    C = C2(law, rules); random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(150)]
    def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
    pool = list(base)
    for _ in range(300):
        try: pool.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
        except RecursionError: pass
    def fr(u, v): return C.op(u, v) == ('J', u, v)
    cells = collections.Counter(); bad = collections.Counter(); worst = {}
    def trial(y, x, z):
        N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); Rr = C.op(y, V)
        key = tuple('F' if fr(*p) else 'D' for p in ((y,x),(N1,z),(x,z),(N2,N3)))
        cells[key] += 1
        if Rr != x:
            bad[key] += 1
            t = size(x)+size(y)+size(z)
            if key not in worst or t < worst[key][0]: worst[key] = (t, y, x, z)
    for i in range(N):
        try:
            mode = i % 6
            y = random.choice(pool)
            if mode == 0:                                   # generic
                x = random.choice(pool); z = random.choice(pool)
            elif mode == 1:                                 # N1 decodes
                x = enc(y, random.choice(pool), random.choice(pool)); z = random.choice(pool)
            elif mode == 2:                                 # N3 decodes
                x = random.choice(pool); z = enc(x, random.choice(pool), random.choice(pool))
            elif mode == 3:                                 # N1 and N3 decode
                x = enc(y, random.choice(pool), random.choice(pool))
                z = enc(x, random.choice(pool), random.choice(pool))
            elif mode == 4:                                 # N2 decodes: z = enc(op(y,x), ..)
                x = random.choice(pool)
                z = enc(C.op(y, x), random.choice(pool), random.choice(pool))
            else:                                           # N1 and N2 decode
                x = enc(y, random.choice(pool), random.choice(pool))
                z = enc(C.op(y, x), random.choice(pool), random.choice(pool))
            trial(y, x, z)
        except RecursionError:
            continue
    print('%-8s seed=%d' % (name, seed), flush=True)
    for k in sorted(cells, key=lambda k: -cells[k]):
        print('   N1=%s N2=%s N3=%s V=%s   n=%-6d BAD=%d' % (k[0], k[1], k[2], k[3], cells[k], bad.get(k, 0)), flush=True)
    for k, w in worst.items():
        print('   WORST %s sizes y=%d x=%d z=%d' % (str(k), size(w[1]), size(w[2]), size(w[3])), flush=True)
        json.dump({'y': w[1], 'x': w[2], 'z': w[3]}, open('gen/_w3_12087_tree_bad.json', 'w'))
    return sum(bad.values())

tot = 0
for name, idx in SETS.items():
    for sd in (5, 19):
        tot += run(name, idx, 6000, sd)
print('TOTAL BAD', tot)
