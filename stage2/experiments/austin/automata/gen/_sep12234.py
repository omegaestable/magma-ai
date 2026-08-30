# -*- coding: utf-8 -*-
"""THE PAIR DIFF applied to law 12234, driven by the carrier lab's OWN batteries.

Law: x = y*(((z*x)*y)*(x*y));  chain A=z*x, B=A*y, C=x*y, D=B*C, root=y*D.
`_x12234_carrier.py`'s §"K23 -- the decisive experiment" claims the open cell is NOT closable by
another rule on this carrier.  This measures whether that is a HARD collision (the same (u,v) at
two positions, which no guard and no carrier can separate) or a GUARD GAP.

usage: python _sep12234.py [ruleset] [mode]   e.g.  python _sep12234.py K21 rootinner
"""
import sys, random, collections
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
import _x12234_carrier as L
from sepfind import analyze

WHICH = sys.argv[1] if len(sys.argv) > 1 else 'K21'
MODE = sys.argv[2] if len(sys.argv) > 2 else 'all'
rules = L.REGISTRY[WHICH]()
op, opr = L.mk_op(rules)
tg, a1, a2, sz, show = L.tg, L.a1, L.a2, L.sz, L.show
NAMES = [nm for nm, _ in rules] + ['F']

GOOD = {b: set() for b in NAMES}
BAD = {b: set() for b in NAMES}
ROOTMAP = {}
tot = collections.Counter()
firing = collections.Counter()


def test(x, y, z, tag):
    try:
        R, p, mid = L.chain(opr, x, y, z)
    except RecursionError:
        return
    A, B, C, D = mid
    prs = [(z, x), (A, y), (x, y), (B, C), (y, D)]
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


# --- battery 1: exhaustive size<=5, 2 gens (the lab's own oracle 1)
ts = L.gen_terms(5, 2)
for y in ts:
    for x in ts:
        for z in ts:
            test(x, y, z, 'exh')

# --- battery 2: the level-k descent with large junk (the lab's oracle 3, the non-vacuous one)
for lv in (1, 2, 3):
    for bj in (False, True):
        rng = random.Random(700 + lv)
        small = [L.rand_term(rng, rng.randrange(1, 4), 2) for _ in range(120)]
        big = [L.rand_term(rng, rng.randrange(5, 8), 4) for _ in range(120)]
        junk = big if bj else small
        for _ in range(400):
            y = rng.choice(small)
            x = rng.choice(small)
            for _ in range(lv):
                x = L.enc(op, rng.choice(junk), x, y)
                if sz(x) > 400:
                    break
            for z in (y, a2(x), a1(x), rng.choice(junk), a2(a2(x)), x):
                test(x, y, z, 'desc%d%s' % (lv, 'B' if bj else ''))

# --- battery 3: deep random
for sd in (101, 202, 303):
    rng = random.Random(sd)
    for _ in range(20000):
        test(L.rand_term(rng, rng.randrange(6), 3), L.rand_term(rng, rng.randrange(6), 3),
             L.rand_term(rng, rng.randrange(6), 3), 'deep')

print('=== %s (%d rules), mode=%s' % (WHICH, len(rules), MODE))
print('chains: %s' % dict(tot), flush=True)
first = True
for b in NAMES:
    if not GOOD[b] and not BAD[b]:
        continue
    print('\n===== rule %r' % b)
    analyze(GOOD[b], BAD[b], tg, a1, a2, sz, op, show, rootmap=ROOTMAP if first else None)
    first = False
print('\nper-construction firing (tag,pos,rule), top 20:')
for k, v in sorted(firing.items(), key=lambda kv: -kv[1])[:20]:
    print('   %-30s %d' % (str(k), v))
