"""Is the open TAGF2 cell FIXABLE, or is it a collision (22591-style)?

The law forces  op u (op A Q) = x  whenever  Q = op x (op x u).  If two DIFFERENT x give the same
(u, op A Q), no rule can fix it -- op is a function of the pair.  Search for that.
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
from _x9663_lab4 import op, sz, show, tg, a1, a2, G, J, E, F

def rt(rng, d, gens=3):
    if d <= 0 or rng.random() < .3: return G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens), rt(rng, d - 1, gens))

rng = random.Random(99)
pool = [G(0), G(1), G(2)] + [rt(rng, 3) for _ in range(400)]
# the open-cell family and its neighbours
fam = []
for p in [G(0), G(1), G(2), J(G(0), G(0)), E(G(0), G(1))]:
    for xx in [G(0), G(1), G(2), J(G(0), G(1))]:
        fam.append(F(p, J(p, xx)))
pool += fam

forced = collections.defaultdict(set)
n = 0
for u in pool:
    for x in pool:
        try:
            P = op(x, u); Q = op(x, P)
        except RecursionError: continue
        for z in pool[:24]:
            A = op(z, u)
            try: C = op(A, Q)
            except RecursionError: continue
            forced[(u, C)].add(x); n += 1
coll = {k: v for k, v in forced.items() if len(v) > 1}
print('forced entries built: %d pairs, %d distinct (u,C) keys, COLLISIONS=%d' % (n, len(forced), len(coll)))
for (u, C), xs in list(coll.items())[:3]:
    print('  COLLISION u=%s' % show(u)[:80]); print('            C=%s' % show(C)[:80])
    print('            x in {%s}' % ', '.join(show(t)[:40] for t in list(xs)[:4]))
# and specifically the open cell
y = F(G(2), J(G(2), G(2)))
xs = {x for x in pool if (lambda P: op(x, P) if True else None)(op(x, y)) == G(2)}
print('open cell: y=%s ; x with op x (op x y) = g2 :' % show(y))
print('   %s' % ', '.join(show(t)[:40] for t in list(xs)[:8]))
