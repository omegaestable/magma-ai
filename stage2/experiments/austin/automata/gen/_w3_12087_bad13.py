"""Isolate the single BAD instance of census seed=13 deep2=True for candidate A; is it a cycle artifact?"""
import sys, os, random, collections, json
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
import freemodel as fm
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
X = cf.Extractor(law)
R = X.rules(exist=False)
rules = [R[i] for i in [0,1,3,5,10]]

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

C = C2(law, rules); random.seed(13)
base = [rand_term(random.randint(1, 3), 2) for _ in range(200)]
def enc(a, b, c): return C.op(C.op(C.op(a, b), c), C.op(b, c))
def st(u, v):
    r = C.op(u, v)
    return 'F' if r == ('J', u, v) else str(C.ruleof.get((u, v)))
pool = list(base)
for _ in range(400):
    try: pool.append(enc(random.choice(pool), random.choice(pool), random.choice(pool)))
    except RecursionError: pass
base = pool
found = []
for i in range(1500):
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
    if Rr != x:
        found.append((x, y, z, (st(y,x), st(N1,z), st(x,z), st(N2,N3), st(y,V))))
print('found', len(found), 'cycles seen so far', C.cycles)
for (x, y, z, k) in found:
    print('  key', k, 'sizes x=%d y=%d z=%d' % (size(x), size(y), size(z)))
    # re-evaluate on a FRESH evaluator (no shared memo) and count cycles
    for name, rr in [('A5', rules), ('full13', R)]:
        C3 = C2(law, rr)
        try:
            r = C3.op(C3.op(C3.op(C3.op(y, x), z), C3.op(x, z)) and C3.op(C3.op(C3.op(y,x),z), C3.op(x,z)), None) if False else None
        except Exception: pass
        C3 = C2(law, rr)
        try:
            N1 = C3.op(y, x); N2 = C3.op(N1, z); N3 = C3.op(x, z); V = C3.op(N2, N3); Rr = C3.op(y, V)
            print('    %-8s ok=%s cycles=%d key=%s' % (name, Rr == x, C3.cycles,
                  (('F' if C3.op(y,x)==('J',y,x) else str(C3.ruleof.get((y,x)))),
                   ('F' if C3.op(N1,z)==('J',N1,z) else str(C3.ruleof.get((N1,z)))),
                   ('F' if C3.op(x,z)==('J',x,z) else str(C3.ruleof.get((x,z)))),
                   ('F' if C3.op(N2,N3)==('J',N2,N3) else str(C3.ruleof.get((N2,N3)))),
                   ('F' if C3.op(y,V)==('J',y,V) else str(C3.ruleof.get((y,V)))))))
        except RecursionError:
            print('    %-8s RecursionError' % name)
    # semantic free model check
    try:
        F = fm.Free(law) if hasattr(fm, 'Free') else None
    except Exception:
        F = None
    json.dump({'x': x, 'y': y, 'z': z}, open('gen/_w3_12087_bad13.json', 'w'))
