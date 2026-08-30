"""Wave-3 validation of the 6-rule 10218 model: exhaustive sweep + chained encodings + a census of
WHICH rule fires at WHICH chain product (a rule firing away from the root is the 40037 risk shape).

law 10218 (not dualized):  x = y * ((x*y) * ((z*x)*y))
chain:  t1 = op x y   t2 = op z x   t3 = op t2 y   t4 = op t1 t3   t5 = op y t4  ( = x )
R1 encoding:  enc(x,y,z) = J (J x y) (J (J z x) y)   with   op y (enc x y z) = x
"""
import sys, os, itertools, time, collections, importlib.util, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 10218
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
spec = importlib.util.spec_from_file_location('chk', os.path.join(HERE, 'gen', 'rep10218', 'chk10218.py'))
src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {'__name__': 'chk'}
exec(compile(src, spec.origin, 'exec'), ns)
rules = ns['rules']
print('law', law, 'rules', len(rules), flush=True)
WHICH = {}
class Which(cf.Closed):
    def op(self, u, v):
        k = (u, v)
        if k in self.memo: return self.memo[k]
        r = super().op(u, v)
        if r != ('J', u, v) and k not in WHICH:
            for i, rl in enumerate(rules):
                sub = cf.Closed(law, rules); sub.memo = self.memo
                if sub.check(rl[0], u, v): WHICH[k] = i; break
            else: WHICH[k] = -1
        return r
C = Which(law, rules)
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def enc(x, y, z): return J(J(x, y), J(J(z, x), y))
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
tab = collections.Counter(); pos = collections.Counter(); bad = []; first = {}
def run(x, y, z):
    t1 = C.op(x, y); t2 = C.op(z, x); t3 = C.op(t2, y); t4 = C.op(t1, t3); t5 = C.op(y, t4)
    names = ('t1', 't2', 't3', 't4', 't5')
    args = ((x, y), (z, x), (t2, y), (t1, t3), (y, t4))
    vals = (t1, t2, t3, t4, t5)
    m = []
    for nm, a, val in zip(names, args, vals):
        if val == J(*a): m.append('F')
        else:
            r = WHICH.get(a, -1) + 1
            m.append('R%d' % r); pos[(nm, r)] += 1
    m = tuple(m)
    tab[m] += 1; first.setdefault(m, (x, y, z))
    if t5 != x: bad.append(((x, y, z), m))
# 1. exhaustive
pool = sc.terms_upto(9, 1) + sc.terms_upto(7, 2)
pool = list(dict.fromkeys(pool))
t0 = time.time(); n = 0
for x, y, z in itertools.product(pool, repeat=3):
    try: run(x, y, z); n += 1
    except RecursionError: pass
print('exhaustive %d assignments, %d fails, %.0fs' % (n, len(bad), time.time() - t0), flush=True)
# 2. chained encodings
base = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(J(g(0), g(1)), g(2))]
lvl1 = list(dict.fromkeys(enc(a, b, c) for a, b, c in itertools.product(base, repeat=3)))
rng = random.Random(10218)
lvl2 = [enc(rng.choice(base + lvl1), rng.choice(base + lvl1), rng.choice(base + lvl1)) for _ in range(400)]
lvl2 = [t for t in lvl2 if size(t) <= 300]
CASES = []
for e in lvl1:                                   # x an encoding -> t1 = op x y may decode
    yy = e[1][2]
    for z in base: CASES.append((e, yy, z))
    for z in lvl1[:30]: CASES.append((e, yy, z))
for e in lvl1:                                   # z or y an encoding
    for x in base[:4]:
        CASES.append((x, e[1][2], e)); CASES.append((x, e, base[0])); CASES.append((e, e[1][2], e))
for a, b, c, d in itertools.product(base[:4], repeat=4):   # nested: x = enc(enc(..))
    inner = enc(a, b, c); CASES.append((enc(inner, d, a), d, c)); CASES.append((inner, c, enc(a, b, d)))
big = base + lvl1 + lvl2
for _ in range(6000):
    t = (rng.choice(big), rng.choice(big), rng.choice(big))
    if sum(size(s) for s in t) <= 500: CASES.append(t)
t0 = time.time(); n2 = 0
for x, y, z in CASES:
    try: run(x, y, z); n2 += 1
    except RecursionError: pass
print('constructed %d assignments, %d fails total, %.0fs' % (n2, len(bad), time.time() - t0), flush=True)
print()
print('%-30s %s' % ('(t1,t2,t3,t4,t5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1])[:12]:
    print('  %-28s %d' % (str(k), c))
print()
print('rule firings by chain position (position, rule#) -> count:')
for k, c in sorted(pos.items()): print('   %-12s %d' % (str(k), c))
print()
print('LAW FAILURES', len(bad))
for (x, y, z), m in bad[:4]:
    print('  ', m); print('    x =', show(x)[:200]); print('    y =', show(y)[:200]); print('    z =', show(z)[:200])
