"""Invariant probe for the uniform 3-rule 40037 model.

Records, over every decoded pair (u,v) the evaluator ever produces (exhaustive small terms + all four
fuzzers + deep random), whether these hold:
   I1  sz u < sz v
   I2  sz (a1 v) < sz (a2 v)
   I3  sz (op u v) < sz (a2 v)
   I4  a1 (a2 v) = u   (the "s3 free" reading)
and the (s1,s2,s3,s4,s5) mode census of the law's own chain.

usage: _x40037_inv.py 15,17,18 [N]
"""
import sys, os, collections, itertools
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in sys.argv[1].split(',')]
rules = [R.ALL[i - 1] for i in idx]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8000

viol = collections.Counter()
ex = {}
ndec = [0]


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


class Probe(cf.Closed):
    def op(self, u, v):
        r = super().op(u, v)
        if r != ('J', u, v):
            ndec[0] += 1
            if not (size(u) < size(v)):
                viol['I1'] += 1; ex.setdefault('I1', (u, v))
            if not (size(a1(v)) < size(a2(v))):
                viol['I2'] += 1; ex.setdefault('I2', (u, v))
            if not (size(r) < size(a2(v))):
                viol['I3'] += 1; ex.setdefault('I3', (u, v))
            if not (a1(a2(v)) == u):
                viol['I4'] += 1; ex.setdefault('I4', (u, v))
        return r


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


C = Probe(law, rules)
tab = collections.Counter()
bad = []


def run(x, y, z):
    s1 = C.op(y, x); s2 = C.op(s1, y); s3 = C.op(z, s2); s4 = C.op(x, s3); s5 = C.op(z, s4)
    k = ('F' if s1 == ('J', y, x) else 'D', 'F' if s2 == ('J', s1, y) else 'D',
         'F' if s3 == ('J', z, s2) else 'D', 'F' if s4 == ('J', x, s3) else 'D',
         'F' if s5 == ('J', z, s4) else 'D')
    tab[k] += 1
    if s5 != x:
        bad.append(((x, y, z), k))


pool = sc.terms_upto(9, 1) + sc.terms_upto(5, 2)
pool = list(dict.fromkeys(pool))
for x, y, z in itertools.product(pool, repeat=3):
    if max(size(x), size(y), size(z)) > 9:
        continue
    try:
        run(x, y, z)
    except RecursionError:
        pass
print('exhaustive done, decoded pairs so far', ndec[0], flush=True)

SEEN = []


class Rec(Probe):
    def evp(self, p, s):
        if p is law[1][1]:
            SEEN.append(dict(s))
        return super().evp(p, s)


for sd in (3, 4, 5, 40037, 7):
    for fn, isfuzz in ((fz.fuzz, True), (fz.closure_fuzz, False), (fz.critical_fuzz, False)):
        C2 = Rec(law, rules)
        try:
            if isfuzz:
                fn(C2, law, rules, N, seed=sd)
            else:
                fn(C2, law, N, seed=sd)
        except RecursionError:
            pass
print('fuzz assignments', len(SEEN), flush=True)
for s in SEEN:
    try:
        run(s['x'], s['y'], s['z'])
    except (RecursionError, KeyError):
        pass

print('decoded pairs seen', ndec[0])
print('invariant violations', dict(viol))
for k, (u, v) in ex.items():
    print('  %s: u=%s' % (k, show(u)[:70]), ' v=%s' % show(v)[:70])
print('%-24s %s' % ('(s1,s2,s3,s4,s5)', 'count'))
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('%-24s %d' % (str(k), c))
print('law failures', len(bad))
for (x, y, z), k in bad[:3]:
    print('  ', k, 'x=%s' % show(x)[:70], 'y=%s' % show(y)[:70], 'z=%s' % show(z)[:70])
