# -*- coding: utf-8 -*-
"""THE PAIR DIFF applied to law 11081's residual cell, driven by the PORTED ADVERSARY.

The random sweep never reaches 11081's open cell (0 BAD in 20,000).  The constructions that DO
reach it are the ported adversary of `_anch_11081_force.py` (P1 forceD, P2 forceB2, P3 H3, P4
level-k), every term of which is op-built.  This feeds those constructions into sepfind.analyze.

usage: python _sep11081.py [ver] [branch]   e.g.  python _sep11081.py v20 1
"""
import sys, collections, random
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
from _x11081_lab4 import Model, chain, prof, terms, sz, show, g, tg, a1, a2
from _anch_lib import image
from sepfind import analyze

VER = sys.argv[1] if len(sys.argv) > 1 else 'v20'
BR = sys.argv[2] if len(sys.argv) > 2 else '1'
MODE = sys.argv[3] if len(sys.argv) > 3 else 'all'
M = Model(VER, fuel=10 ** 9)
by, seen = image(M, ngens=3, wsize=4, cap=10 ** 6, gmk=g)
small = [t for s in sorted(by) if s <= 3 for t in by[s]]
print('VER=%s branch=%s  image small pool %d' % (VER, BR, len(small)), flush=True)

GOODP, BADP = set(), set()
ROOTMAP = {}
tot = [0, 0]


def pairsof(x, y, z):
    A = M.op(y, x); B = M.op(x, A); C = M.op(z, y); D = M.op(B, C)
    return [(y, x), (x, A), (z, y), (B, C), (y, D)]


def test(x, y, z):
    try:
        R = chain(M, x, y, z)[-1]
        p = prof(M, x, y, z)
        prs = pairsof(x, y, z)
    except RecursionError:
        return
    tot[0] += 1
    ok = (R == x)
    if not ok:
        tot[1] += 1
    ROOTMAP.setdefault(prs[-1], set()).add(x)
    for idx, pr in enumerate(prs):
        if str(p[idx]) != BR:
            continue
        if MODE == 'all':
            (GOODP if ok else BADP).add(pr)
        elif MODE == 'rootinner':
            # GOOD = the branch firing at the ROOT of a succeeding chain (it must keep firing there)
            # BAD  = the branch firing at an INNER slot of a failing chain (it must stop firing there)
            if idx == 4 and ok:
                GOODP.add(pr)
            elif idx != 4 and not ok:
                BADP.add(pr)


def enc(u, p, j):
    try:
        inner = M.op(u, p); L = M.op(p, inner); Rr = M.op(j, u); v = M.op(L, Rr)
        if not (tg(v) != 1 and a1(v) == L and a2(v) == Rr):
            return None
        if M.op(u, v) != p:
            return None
    except RecursionError:
        return None
    return v


# P1 forceD
for x in small:
    for y in small:
        try:
            A = M.op(y, x); B = M.op(x, A)
        except RecursionError:
            continue
        for q in small[:8]:
            try:
                z = M.op(q, M.op(B, q))
            except RecursionError:
                continue
            test(x, y, z)
# P2 forceB2
for pz in small[:6]:
    for kz in small[:5]:
        for wz in small[:4]:
            z = enc(kz, pz, wz)
            if z is None:
                continue
            for P in small[:4]:
                try:
                    y = M.op(M.op(P, M.op(z, P)), pz)
                except RecursionError:
                    continue
                for x in small[:6]:
                    test(x, y, z); test(x, y, P); test(y, z, x); test(x, z, y)
# P3 H3
for x in small[:8]:
    for p in small[:6]:
        for j in small[:4]:
            y = enc(x, p, j)
            if y is None:
                continue
            for z in small[:8]:
                test(x, y, z); test(p, y, z); test(x, z, y)
# P4 level-k
for x in small[:5]:
    for p in small[:4]:
        for j in small[:3]:
            y1 = enc(x, p, j)
            if y1 is None:
                continue
            y2 = enc(x, y1, j)
            if y2 is None:
                continue
            y3 = enc(x, y2, j)
            for z in small[:6]:
                test(x, y2, z); test(x, z, y2)
                if y3 is not None:
                    test(x, y3, z); test(x, z, y3)
# P5 deep op-built
rng = random.Random(7)
deep = list(small)
for _ in range(3000):
    a = rng.choice(deep); b = rng.choice(deep)
    try:
        deep.append(M.op(a, b))
    except RecursionError:
        break
    if len(deep) > 900:
        deep = deep[-900:] + small
for _ in range(20000):
    test(rng.choice(deep), rng.choice(deep), rng.choice(deep))

print('chains %d, failing %d' % (tot[0], tot[1]), flush=True)
analyze(GOODP, BADP, tg, a1, a2, sz, M.op, show, rootmap=ROOTMAP)
