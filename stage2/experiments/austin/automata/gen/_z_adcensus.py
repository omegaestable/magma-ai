"""For law 38316 / cand7: at every DECODED chain product (u,v), record whether Adig-LEFT
(tg (a2 v) = 2 and a2 (a2 v) = u) holds, or only Adig-RIGHT (a2 v = a1 u).
Also records whether the d product (op x c) ever decodes.
usage: _z_adcensus.py [rules] [N]
"""
import sys, os, random, itertools
from collections import Counter
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
sys.setrecursionlimit(100000)
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import freetest2 as ft

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = D + '/gen/'
name = sys.argv[1] if len(sys.argv) > 1 else 'cand7'
ns2 = {}
exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns2)
RULES = ns2['rules']
C = cf.Closed(law, RULES)
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)

cnt = Counter()
bad = []


def ad(u, v):
    """classify a decoded pair"""
    a2v = v[2] if v[0] == 'J' else v
    a1u = u[1] if u[0] == 'J' else u
    left = a2v[0] == 'J' and a2v[2] == u
    right = a2v == a1u
    return 'L' if left else ('R' if right else 'NEITHER')


def rec(x, y, z, fam):
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    except RecursionError:
        return
    if top != x:
        bad.append((x, y, z, fam))
    slots = [('a', z, x), ('b', y, a), ('c', b, y), ('d', x, c), ('t', y, d)]
    for nm, u, v in slots:
        if C.op(u, v) != J(u, v):
            cnt[(nm, ad(u, v))] += 1
        else:
            cnt[(nm, 'free')] += 1


def enc(u, P, Z):
    a = C.op(Z, P); b = C.op(u, a); c = C.op(b, u); return J(P, c)


G = [g(i) for i in range(5)]
small = G[:3] + [J(g(0), g(1)), J(g(1), g(2)), J(g(2), g(0))]

# family A: random deep triples
class Shim:
    pass
F = Shim(); F.vars = ['x', 'y', 'z']; F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
random.seed(int(sys.argv[3]) if len(sys.argv) > 3 else 5)
pool = []
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
for _ in range(N):
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 200:
        continue
    rec(s['x'], s['y'], s['z'], 'rand')
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400:
            pool.append(t)

# family B: encoder-built, k levels
for k in (1, 2, 3):
    for y, Z in itertools.product(small, small):
        P = g(4)
        for _ in range(k):
            P = enc(y, P, Z)
            if size(P) > 3000:
                break
        else:
            if size(P) <= 3000:
                for zz in small:
                    rec(P, y, zz, 'enc%d' % k)

# family C: y = J x x, x = J p q, and the "y = a1 x, z = a2 x" family
for p in small:
    for q in small:
        x = J(p, q)
        rec(x, p, q, 'split')
        rec(x, J(x, x), q, 'yjxx')
        rec(x, p, J(q, q), 'zbig')
        for w in small:
            rec(x, enc(w, p, q), w, 'encY')

print('law failures:', len(bad))
for k, n in sorted(cnt.items()):
    print(' ', k, n)
