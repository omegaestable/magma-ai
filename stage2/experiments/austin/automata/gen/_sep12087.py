# -*- coding: utf-8 -*-
"""THE PAIR DIFF applied to law 12087's residual cell, driven by CONSTRUCTED adversaries.

A random sweep is VACUOUS here: 15,000 random triples give 0 failures on a model its own oracle
kills at 945/4,000.  (Recorded as a vacuity finding about sepfind's default generator -- exactly
the positive-control failure that hid law 8485's counterexample.)  The constructions that reach
the cell are enc-based: H3 (y a genuine encoding by x), the level-k descent (z a tower of
encodings by x), and large junk in the slot no rule constrains.

usage: python _sep12087.py [mode]   mode = all | rootinner
"""
import sys, random, collections
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
import _w3_12087_lab_v11 as L
from sepfind import analyze

op, chain, prof, tg, a1, a2, sz, show = L.op, L.chain, L.prof, L.tg, L.a1, L.a2, L.sz, L.show
MODE = sys.argv[1] if len(sys.argv) > 1 else 'all'
BRS = ('D', 'T', 'F')

GOOD = {b: set() for b in BRS}
BAD = {b: set() for b in BRS}
ROOTMAP = {}
tot = collections.Counter()
firing = collections.Counter()


def pairsof(x, y, z):
    N1 = op(y, x); N2 = op(N1, z); N3 = op(x, z); V = op(N2, N3)
    return [(y, x), (N1, z), (x, z), (N2, N3), (y, V)]


def test(x, y, z, tag):
    try:
        R = chain(x, y, z)[-1]
        p = prof(x, y, z)
        prs = pairsof(x, y, z)
    except RecursionError:
        return
    ok = (R == x)
    tot[tag] += 1
    if not ok:
        tot[tag + ':BAD'] += 1
    ROOTMAP.setdefault(prs[-1], set()).add(x)
    for idx, pr in enumerate(prs):
        b = p[idx]
        firing[(tag, idx, b)] += 1
        if b not in GOOD:
            continue
        if MODE == 'all':
            (GOOD if ok else BAD)[b].add(pr)
        else:
            if idx == 4 and ok:
                GOOD[b].add(pr)
            elif idx != 4 and not ok:
                BAD[b].add(pr)


def enc(a, b, c):
    return op(op(op(a, b), c), op(b, c))


def rt(rng, d, gens, pool):
    if d <= 0 or rng.random() < 0.3:
        return ('g', rng.randrange(gens))
    return (rng.choice(('J', 'E')), rt(rng, d - 1, gens, pool), rt(rng, d - 1, gens, pool))


rng = random.Random(7)
small = [rt(rng, 2, 3, None) for _ in range(60)]
big = [rt(rng, 6, 3, None) for _ in range(60)]

# --- C1 deep random (control: the battery that returns 0)
for _ in range(6000):
    test(rng.choice(small + big), rng.choice(small + big), rng.choice(small + big), 'deep')

# --- C2 H3: y is a genuine encoding whose junk slot is x
n = 0
for _ in range(4000):
    j = rng.choice(small); w = rng.choice(small); x = rng.choice(small + big)
    try:
        y = enc(j, w, x)
    except RecursionError:
        continue
    n += 1
    test(x, y, rng.choice(small + big), 'H3')
    test(w, y, x, 'H3b')
print('  H3 encodings built: %d' % n, flush=True)

# --- C3 level-k descent: z a tower of encodings by x
d = 0
for _ in range(1500):
    x = rng.choice(small); p = rng.choice(small); q = rng.choice(small + big)
    try:
        z1 = enc(x, p, q); z2 = enc(x, z1, q); z3 = enc(x, z2, q)
    except RecursionError:
        continue
    d += 1
    for zz, tag in ((z1, 'L1'), (z2, 'L2'), (z3, 'L3')):
        test(x, rng.choice(small), zz, 'desc:' + tag)
        test(x, zz, rng.choice(small), 'descY:' + tag)
print('  descent towers built: %d' % d, flush=True)

# --- C4 the law's own RHS as y (a genuine decode target for the root)
for _ in range(1200):
    x = rng.choice(small); y = rng.choice(small); z = rng.choice(small + big)
    try:
        yy = enc(y, x, z)
    except RecursionError:
        continue
    test(x, yy, z, 'selfenc')
    test(x, y, enc(x, rng.choice(small), z), 'zenc')

print('chains by construction: %s' % dict(tot), flush=True)
for b in BRS:
    print('\n===== branch %r  (mode=%s)' % (b, MODE))
    analyze(GOOD[b], BAD[b], tg, a1, a2, sz, op, show, rootmap=ROOTMAP if b == BRS[0] else None)
print('\nper-construction firing (tag,pos,branch) -> n, top 24:')
for k, v in sorted(firing.items(), key=lambda kv: -kv[1])[:24]:
    print('   %-28s %d' % (str(k), v))
