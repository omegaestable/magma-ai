# -*- coding: utf-8 -*-
"""Rung 11, the vacuous target made non-vacuous by CONSTRUCTION (rail 50).

`Aeqy`: chains in which  A = op z y = y  exactly.  60,000 random draws found 0 instances, so the
suite tested nothing about the root's `a1 v != u` guard in the one shape that could break it.

Construction (derived in NOTES_9663.md §5):
  R2 at (z,y) returns  xx = a2 (a2 (a2 z)).  Force xx = y by building z around y:
      Pz = E(beta, y)            needs  op beta y = E(beta,y)      (TAGE at (beta,y))
      Qz = (c, beta, Pz)
      z  = (c, alpha, Qz)
  R2's second certification is  op xx p = a2 v, i.e.  op y beta = a2 y.  Force it with DEC at (y,beta):
      beta = E(delta, F(a2 y, op (a2 y) y))       delta != y
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _s9_9663_lab5 as L

for a in sys.argv[1:]:
    if a.startswith('f:'): L.FEAT = set(x for x in a[2:].split(',') if x)
print('=== FEAT={%s} ===' % ','.join(sorted(L.FEAT)))
op, chain, prof, sz, show, tg, a1, a2 = L.op, L.chain, L.prof, L.sz, L.show, L.tg, L.a1, L.a2
G, J, E, F = L.G, L.J, L.E, L.F


def rt(rng, d, gens=4):
    if d <= 0 or rng.random() < .3: return G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens), rt(rng, d - 1, gens))


rng = random.Random(31337)
pool = [G(0), G(1), G(2), G(3)] + [rt(rng, 3) for _ in range(200)]
ys = [t for t in pool if tg(t) != 1] + [E(G(0), E(G(1), G(2))), E(G(0), J(G(1), G(2))),
                                        E(E(G(0), G(1)), E(G(1), G(2))), J(G(0), G(0))]

found = 0; tested = 0; bad = 0; wit = []
cells = collections.Counter()
for y in ys:
    if tg(y) == 1: continue
    try:
        w = op(a2(y), y)
    except RecursionError: continue
    for delta in (G(3), G(2), E(G(3), G(3)), J(G(3), G(3))):
        beta = E(delta, F(a2(y), w))
        try:
            if op(y, beta) != a2(y): continue          # DEC at (y,beta) must give a2 y
            Pz = op(beta, y)
            if Pz != E(beta, y): continue              # TAGE at (beta,y)
        except RecursionError: continue
        for c1 in ('J', 'E', 'F'):
            for c2 in ('J', 'E', 'F'):
                for alpha in (G(0), G(1), E(G(0), G(1))):
                    Qz = (c2, beta, Pz)
                    z = (c1, alpha, Qz)
                    try:
                        A = op(z, y)
                    except RecursionError: continue
                    if A != y: continue
                    found += 1
                    for x in pool[:60]:
                        try:
                            r = chain(x, y, z)[4]; pr = prof(x, y, z)
                        except RecursionError: continue
                        tested += 1
                        cells[pr] += 1
                        if r != x:
                            bad += 1
                            if len(wit) < 3: wit.append((x, y, z, r))

print('A == y constructions found: %d   chains tested: %d   BAD: %d' % (found, tested, bad))
for k, v in cells.most_common(8):
    print('   cell %-18s %d' % (','.join(k), v))
for x, y, z, r in wit:
    print(' BAD x=%s' % show(x)[:80]); print('     y=%s' % show(y)[:80])
    print('     z=%s' % show(z)[:120]); print('  -> r=%s' % show(r)[:80])
