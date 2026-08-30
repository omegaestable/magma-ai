# -*- coding: utf-8 -*-
"""Anchored carrier for law 9663:  x = y * ((z*y) * (x*(x*y)))
Carrier = IMAGE of the free magma under evaluation in _x9663_lab4's four-constructor model.
Q1: how big is the image, and which shapes are FORGED (in the term algebra, not in the image)?
Q2: is the residual open cell's witness op-built or forged?
usage: python _anch_9663.py [wsize] [ngens]"""
import sys, collections, itertools, random
sys.path.insert(0, '.')
sys.setrecursionlimit(100000)
import _x9663_lab4 as L
from _x9663_lab4 import op, chain, prof, sz, show, G, J, E, F, tg, a1, a2, terms, enc

WS = int(sys.argv[1]) if len(sys.argv) > 1 else 4
NG = int(sys.argv[2]) if len(sys.argv) > 2 else 2

# ---- image by W-size
by = {1: [G(i) for i in range(NG)]}
seen = set(by[1])
for s in range(2, WS + 1):
    out = []
    for i in range(1, s):
        for a in by.get(i, []):
            for b in by.get(s - i, []):
                try:
                    r = op(a, b)
                except RecursionError:
                    continue
                if r not in seen:
                    seen.add(r); out.append(r)
    by[s] = out
pool = [t for s in sorted(by) for t in by[s]]
print('image by W-size %s  total %d  ctors %s'
      % ({s: len(by[s]) for s in sorted(by)}, len(pool),
         dict(collections.Counter(t[0] for t in pool))), flush=True)

IMG = set(pool)

def is_img(t, memo={}):
    """t in the image?  structural: t is a generator, or op(a1 t, a2 t) == t with both in image,
    or t is a decode result (then it equals some subterm already in the image)."""
    if t in memo: return memo[t]
    memo[t] = False                       # cycle guard
    if tg(t) == 1:
        memo[t] = True; return True
    a, b = a1(t), a2(t)
    r = False
    if is_img(a, memo) and is_img(b, memo):
        try:
            r = (op(a, b) == t)
        except RecursionError:
            r = False
    memo[t] = r
    return r

# sanity: everything enumerated must pass is_img
bad = [t for t in pool if not is_img(t)]
print('is_img() sanity: %d/%d enumerated terms rejected by the structural test' % (len(bad), len(pool)))
for t in bad[:3]: print('   ', show(t)[:120])

# ---- how much of the term algebra is FORGED?
allt = terms(7, NG)
inimg = [t for t in allt if is_img(t)]
print('term algebra size<=7 over %d gens: %d terms, %d in image (%.1f%%), %d FORGED'
      % (NG, len(allt), len(inimg), 100.0 * len(inimg) / len(allt), len(allt) - len(inimg)))
cf = collections.Counter(t[0] for t in allt if not is_img(t))
ci = collections.Counter(t[0] for t in inimg)
print('   forged by head ctor:', dict(cf), '  in-image by head ctor:', dict(ci))

# ---- Q2: the residual open cell
x = G(2) if NG > 2 else G(0)
gg = x
y = F(gg, J(gg, gg))
print('\nOPEN CELL witness: x=%s  y=%s' % (show(x), show(y)))
print('   y in image? ', is_img(y), '   op(%s,%s) = %s' % (show(gg), show(J(gg, gg)), show(op(gg, J(gg, gg)))))
print('   J(g,g) in image? ', is_img(J(gg, gg)), ' = op(g,g) =', show(op(gg, gg)))
for z in [G(0), G(1)]:
    P, Q, A, C, R = chain(x, y, z)
    print('   z=%s prof=%s -> R=%s  (x=%s)  OK=%s' % (show(z), ','.join(prof(x, y, z)), show(R)[:80], show(x), R == x))
