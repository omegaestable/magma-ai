"""Case table for law 40037: which chain products decode, and which rule closes the final one.

chain (u=z):  s1 = op y x ; s2 = op s1 y ; s3 = op z s2 ; s4 = op x s3 ; goal op z s4 = x
Every rule returns a1 v, so each si is either  J <left> <right>  (free) or  a1 <right>  (decoded).
"""
import sys, os, random, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, trace as tr
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
rules = R.RULES

N = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
random.seed(seed)

import freetest2 as ft
from freemodel import pvars

T = tr.Tracing(law, rules)


class Shim:
    pass


F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: T.evp(p, s)


def prod(a, b):
    T.trace_on = True; T.log = []
    r = T.op(a, b)
    T.trace_on = False
    w = T.log[-1][2] if T.log else None
    return r, w


tab = collections.Counter()
bad = collections.Counter()
pool = []
tested = 0
while tested < N:
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120:
        continue
    tested += 1
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400:
            pool.append(t)
    try:
        x, y, z = s['x'], s['y'], s['z']
        s1, w1 = prod(y, x)
        s2, w2 = prod(s1, y)
        s3, w3 = prod(z, s2)
        s4, w4 = prod(x, s3)
        s5, w5 = prod(z, s4)
    except RecursionError:
        continue
    key = tuple('F' if w is None else 'R%d' % (w + 1) for w in (w1, w2, w3, w4, w5))
    tab[key] += 1
    if s5 != x:
        bad[key] += 1

print('instances', tested, 'law failures', sum(bad.values()))
print('%-34s %8s %8s' % ('(s1,s2,s3,s4,final)', 'count', 'FAILS'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('%-34s %8d %8d' % (str(k), c, bad.get(k, 0)))
