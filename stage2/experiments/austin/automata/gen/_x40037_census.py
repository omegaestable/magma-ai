"""Mode census over the FUZZ generators (not just random deep tests).

Records, for every assignment the four fuzzers try, whether each chain product of
   s1 = op y x, s2 = op s1 y, s3 = op z s2, s4 = op x s3, s5 = op z s4
is free or decoded, and which rule fired at s5.

usage: _x40037_census.py 1,2,14 [N]
"""
import sys, os, collections
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, fuzz as fz, smallcheck as sc, itertools
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in sys.argv[1].split(',')]
rules = [R.ALL[i - 1] for i in idx]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000

SEEN = []


class Rec(cf.Closed):
    def evp(self, p, s):
        if p is law[1][1]:
            SEEN.append(dict(s))
        return super().evp(p, s)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


for sd in (3, 4, 5, 40037):
    for fn, kw in ((fz.fuzz, dict(rules=rules)), (fz.closure_fuzz, {}), (fz.critical_fuzz, {})):
        C = Rec(law, rules)
        try:
            if kw:
                fn(C, law, rules, N, seed=sd)
            else:
                fn(C, law, N, seed=sd)
        except RecursionError:
            pass
print('assignments recorded', len(SEEN))

C = cf.Closed(law, rules)
tab = collections.Counter()
bad = []
which = {}


def run(x, y, z):
    s1 = C.op(y, x); f1 = s1 == ('J', y, x)
    s2 = C.op(s1, y); f2 = s2 == ('J', s1, y)
    s3 = C.op(z, s2); f3 = s3 == ('J', z, s2)
    s4 = C.op(x, s3); f4 = s4 == ('J', x, s3)
    s5 = C.op(z, s4); f5 = s5 == ('J', z, s4)
    k = tuple('F' if f else 'D' for f in (f1, f2, f3, f4, f5))
    tab[k] += 1
    if s5 != x:
        bad.append(((x, y, z), k))
    return k


pool = sc.terms_upto(7, 1) + sc.terms_upto(5, 2)
pool = list(dict.fromkeys(pool))
for x, y, z in itertools.product(pool, repeat=3):
    try:
        run(x, y, z)
    except RecursionError:
        pass
for s in SEEN:
    try:
        run(s['x'], s['y'], s['z'])
    except (RecursionError, KeyError):
        pass

print('%-24s %s' % ('(s1,s2,s3,s4,s5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('%-24s %d' % (str(k), c))
print('law failures', len(bad))
for (x, y, z), k in bad[:3]:
    print('  ', k, 'x=%s' % show(x)[:80], 'y=%s' % show(y)[:80], 'z=%s' % show(z)[:80])
