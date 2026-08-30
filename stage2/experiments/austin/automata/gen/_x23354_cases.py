"""Case table at the root of law 23354: which of W=op(y,x) / F=op(x,z) decoded, whether
U=op(W,y) and V=op(x,F) are free, and which rule fired at the root."""
import sys, os, random, time, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
import freemodel as fm
import freetest2 as ft
from freemodel import normalise, catalog, size, pvars
from laws import parse_eq

EQ = 23354
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

def which(C, u, v):
    """index of the rule that fires at (u,v), or -1"""
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i
    return -1

N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 7
random.seed(seed)
C = cf.Closed(law, rules)
class Shim: pass
F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
pool = []
tab = collections.Counter()
bad = []
t0 = time.time()
tested = 0
while tested < N and time.time() - t0 < 300:
    s = ft.nested_triple(F, pool)
    if max(size(t) for t in s.values()) > 120: continue
    x, y, z = s['x'], s['y'], s['z']
    try:
        W = C.op(y, x); U = C.op(W, y)
        Fv = C.op(x, z); V = C.op(x, Fv)
        root = C.op(U, V)
        rw = which(C, y, x); rf = which(C, x, z)
        ru = which(C, W, y); rv = which(C, x, Fv)
        rr = which(C, U, V)
    except RecursionError:
        tested += 1; continue
    tested += 1
    for t in s.values():
        if size(t) <= 40 and len(pool) < 400: pool.append(t)
    key = (rw, rf, ru, rv, rr, root == x)
    tab[key] += 1
    if root != x and len(bad) < 5:
        bad.append(s)
print('tested', tested, 'secs', round(time.time() - t0, 1))
print('key = (rule at (y,x), rule at (x,z), rule at (W,y), rule at (x,F), rule at root, correct)')
for k, c in sorted(tab.items(), key=lambda kv: -kv[1]):
    print('  ', k, c)
print('bad', len(bad))
for s in bad:
    print('   ', {k: fm.show(v) if hasattr(fm, 'show') else str(v) for k, v in s.items()})
