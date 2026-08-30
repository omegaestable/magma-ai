"""Do the collisions survive on a carrier RESTRICTED to terms the model itself builds?

`op` produces `J u v` only when tg v = 1, and E/F only with tg v != 1, so a term like
J(_, E(..)) is UNREACHABLE.  If every collision involves an unreachable term, the anchored
carrier (restricted to the image of op, with well-formedness as the position separator) kills them.
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _x9663_lab4 as L
from _x9663_lab4 import op, sz, show, tg, a1, a2, G, J, E, F

def wf(t):
    """t is producible by op (recursively)."""
    if tg(t) == 1: return True
    if not (wf(a1(t)) and wf(a2(t))): return False
    return op(a1(t), a2(t)) == t

def rt(rng, d, gens=3):
    if d <= 0 or rng.random() < .3: return G(rng.randrange(gens))
    return (rng.choice(('J', 'E', 'F')), rt(rng, d - 1, gens), rt(rng, d - 1, gens))

rng = random.Random(99)
raw = [G(0), G(1), G(2)] + [rt(rng, 3) for _ in range(400)]
for p in [G(0), G(1), G(2), J(G(0), G(0)), E(G(0), G(1))]:
    for xx in [G(0), G(1), G(2), J(G(0), G(1))]:
        raw.append(F(p, J(p, xx)))
# a genuinely reachable pool: close the generators under op
reach = [G(0), G(1), G(2)]
for _ in range(3):
    new = []
    for a in reach[:40]:
        for b in reach[:40]:
            try: new.append(op(a, b))
            except RecursionError: pass
    reach = list(dict.fromkeys(reach + new))
reach = [t for t in reach if sz(t) <= 25][:420]

def collide(pool, label):
    forced = collections.defaultdict(set); n = 0
    for u in pool:
        for x in pool:
            try:
                P = op(x, u); Q = op(x, P)
            except RecursionError: continue
            for z in pool[:24]:
                try:
                    A = op(z, u); C = op(A, Q)
                except RecursionError: continue
                forced[(u, C)].add(x); n += 1
    coll = {k: v for k, v in forced.items() if len(v) > 1}
    print('%-22s pool=%-4d entries=%-9d keys=%-8d COLLISIONS=%d' % (label, len(pool), n, len(forced), len(coll)))
    return coll

c1 = collide(raw, 'raw (junk allowed)')
bad_wf = 0
for (u, C), xs in c1.items():
    for x in xs:
        if not wf(x): bad_wf += 1; break
print('  of those, %d of %d involve an UNREACHABLE x' % (bad_wf, len(c1)))
c2 = collide(reach, 'reachable only')
for (u, C), xs in list(c2.items())[:2]:
    print('  STILL COLLIDES u=%s C=%s' % (show(u)[:50], show(C)[:50]))
    print('     x in {%s}' % ', '.join(show(t)[:45] for t in list(xs)[:3]))
