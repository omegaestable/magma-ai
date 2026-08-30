"""Reproduce the rep4 census failure concretely and find the smallest failing instance."""
import sys, os, random, collections
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 12087
cat = catalog(); law = normalise(parse_eq(cat[EQ]))

def loadrules(path):
    src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}; exec(src, ns); return ns['rules']

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

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s.%s)' % (show(t[1]), show(t[2]))

rules4 = loadrules('gen/rep12087/chk12087.py')
rules3 = loadrules('gen/chk12087.py')
X = cf.Extractor(law)
rules13 = X.rules(exist=False)
print('tags4 ', [r[2] for r in rules4])
print('tags3 ', [r[2] for r in rules3])
print('tags13', [r[2] for r in rules13])

def hunt(name, rules, N, seed):
    C = C2(law, rules)
    random.seed(seed)
    base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]
    def enc(a, b, c):
        return C.op(C.op(C.op(a, b), c), C.op(b, c))
    def st(u, v):
        r = C.op(u, v)
        return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
    best = None
    cnt = collections.Counter(); bad = 0; hits = 0
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
            N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); R = C.op(y, V)
        except RecursionError:
            continue
        hits += 1
        key = (st(y, x), st(N1, z), st(x, z), st(N2, N3), st(y, V))
        cnt[key] += 1
        if R != x:
            bad += 1
            tot = size(x) + size(y) + size(z)
            if best is None or tot < best[0]: best = (tot, x, y, z, key, R)
    print('%-8s nrules=%d hits=%d BAD=%d' % (name, len(rules), hits, bad), flush=True)
    for k, n in cnt.most_common(6): print('    %-30s %d' % (str(k), n))
    if best:
        tot, x, y, z, key, R = best
        print('  SMALLEST BAD total=%d sizes x=%d y=%d z=%d key=%s' % (tot, size(x), size(y), size(z), key))
        print('   y =', show(y)); print('   x =', show(x)); print('   z =', show(z)); print('   got =', show(R))
        import json; json.dump({'x': x, 'y': y, 'z': z}, open('gen/_w3_12087_bad.json', 'w'))
    return best

hunt('rep4', rules4, 2000, 5)
hunt('rules3', rules3, 2000, 5)
hunt('full13', rules13, 2000, 5)
