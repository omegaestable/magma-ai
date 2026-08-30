"""Anchored carrier for law 11081:  x = y*((x*(y*x))*(z*y))
Carrier = IMAGE of the free magma under evaluation in the lab-4 term model (v17..v20).
usage: python _anch_11081.py [ver] [wsize] [ngens] [sample]"""
import sys, collections, itertools, random
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
from _x11081_lab4 import Model, chain, prof, terms, sz, show, g, J, E, F, K, D2, tg, a1, a2
from _anch_lib import image

VER   = sys.argv[1] if len(sys.argv) > 1 else 'v20'
WSIZE = int(sys.argv[2]) if len(sys.argv) > 2 else 4
NG    = int(sys.argv[3]) if len(sys.argv) > 3 else 2
SAMP  = int(sys.argv[4]) if len(sys.argv) > 4 else 0

M = Model(VER, fuel=10**9)
by, seen = image(M, ngens=NG, wsize=WSIZE, cap=10**6, gmk=g)
pool = [t for s in sorted(by) for t in by[s]]
print('VER=%s ngens=%d wsize=%d  image %s total %d  ctors %s'
      % (VER, NG, WSIZE, {s: len(by[s]) for s in sorted(by)}, len(pool),
         dict(collections.Counter(t[0] for t in pool))), flush=True)

fails = []; profs = collections.Counter(); tot = 0
if SAMP:
    rng = random.Random(12345)
    it = ((rng.choice(pool), rng.choice(pool), rng.choice(pool)) for _ in range(SAMP))
else:
    it = itertools.product(pool, pool, pool)
for (x, y, z) in it:
    try:
        A, B, C, D, R = chain(M, x, y, z); p = prof(M, x, y, z)
    except RecursionError:
        continue
    tot += 1; profs[p] += 1
    if R != x:
        fails.append((x, y, z, R, p))
print('IMAGE sweep: %d chains, %d FAILS' % (tot, len(fails)), flush=True)
print('  branch profiles (top 10):', dict(profs.most_common(10)))
print('  branch-firing census by position:',
      {i: dict(collections.Counter(p[i] for p in profs.elements())) for i in range(5)})
if fails:
    print('  failing profiles:', dict(collections.Counter(f[4] for f in fails).most_common(8)))
    fails.sort(key=lambda f: sz(f[0]) + sz(f[1]) + sz(f[2]))
    for (x, y, z, R, p) in fails[:3]:
        print('FAIL profile %s' % (str(p),))
        for nm, t in (('x', x), ('y', y), ('z', z), ('R', R)):
            print('   %s (sz %d) = %s' % (nm, sz(t), show(t)[:200]))
