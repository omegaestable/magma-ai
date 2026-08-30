"""Which chain products decode?  Exhaustive small terms + deep random, for a rule subset.

usage: _x40037_modes.py 1,2,3,4,5,6,13 [--deep N]
prints the (s1,s2,s3,s4) free/decoded mode vector counts and any law failure.
"""
import sys, os, collections, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in sys.argv[1].split(',')]
rules = [R.ALL[i - 1] for i in idx]
NDEEP = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 20000


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


C = cf.Closed(law, rules)
tab = collections.Counter()
bad = []


def run(x, y, z):
    s1 = C.op(y, x)
    s2 = C.op(s1, y)
    s3 = C.op(z, s2)
    s4 = C.op(x, s3)
    s5 = C.op(z, s4)
    k = ('F' if s1 == ('J', y, x) else 'D',
         'F' if s2 == ('J', s1, y) else 'D',
         'F' if s3 == ('J', z, s2) else 'D',
         'F' if s4 == ('J', x, s3) else 'D',
         'F' if s5 == ('J', z, s4) else 'D')
    tab[k] += 1
    if s5 != x:
        bad.append(((x, y, z), k))


pool = [] if '--noexh' in sys.argv else (sc.terms_upto(9, 1) + sc.terms_upto(5, 2))
pool = list(dict.fromkeys(pool))
n = 0
for x, y, z in itertools.product(pool, repeat=3):
    if max(size(x), size(y), size(z)) > 9:
        continue
    n += 1
    try:
        run(x, y, z)
    except RecursionError:
        pass
print('exhaustive assignments', n)

import random, freetest2 as ft, fuzz as fz


class Shim:
    pass


F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
random.seed(12345)
dpool = []
for i in range(NDEEP):
    s = ft.nested_triple(F, dpool)
    if max(size(t) for t in s.values()) > 120:
        continue
    for t in s.values():
        if size(t) <= 40 and len(dpool) < 400:
            dpool.append(t)
    try:
        run(s['x'], s['y'], s['z'])
    except RecursionError:
        pass

print('%-24s %s' % ('(s1,s2,s3,s4,s5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('%-24s %d' % (str(k), c))
print('law failures', len(bad))
for (x, y, z), k in bad[:3]:
    print('  ', k, 'x=%s y=%s z=%s' % (show(x), show(y), show(z)))
