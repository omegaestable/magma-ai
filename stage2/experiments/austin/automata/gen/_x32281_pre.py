"""40037-style check: at EVERY chain product, does any rule's TAG precondition hold while only its
recomputation guard blocks the fire?  (a rule pinned by a guard alone can fire at the wrong product)"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v
def tagonly(conds): return [c for c in conds if c[0] == 'TG' or (c[0] == 'EQ' and not any(
    e[0] == 'OP' for e in _sub(c[1]) + _sub(c[2])))]
def _sub(e):
    out = [e]
    for a in e[1:]:
        if isinstance(a, tuple): out += _sub(a)
    return out

C = cf.Closed(LAW, RULES)
cnt = collections.Counter()
rg = random.Random(7)
def rnd(n, gens):
    if n <= 1 or rg.random() < 0.25: return g(rg.choice(gens))
    k = rg.randrange(1, max(2, n - 1))
    return J(rnd(k, gens), rnd(n - 1 - k, gens))
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
POOL = [(x, y, z) for x in G + E1 for y in G + E1 + E2 for z in G + E1[:4]]
POOL += [(rnd(rg.choice([5, 21, 41]), [0, 1, 2, 8]), rg.choice(E1 + E2), rg.choice(G)) for _ in range(3000)]
for (x, y, z) in POOL:
    try:
        P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); C.op(z, S)
    except RecursionError:
        continue
    for nm, (u, v) in (('P', (x, y)), ('Q', (P, y)), ('A', (z, Q)), ('S', (A, y)), ('T', (z, S))):
        for i, (conds, xe, tag) in enumerate(RULES):
            tagsok = C.check(tagonly(conds), u, v)
            fires = C.check(conds, u, v) and C.ev(xe, u, v) is not None
            if fires: cnt['%s FIRES R%d' % (nm, i + 1)] += 1
            elif tagsok: cnt['%s tags-only R%d (guard blocks)' % (nm, i + 1)] += 1
print('triples', len(POOL))
for k in sorted(cnt): print('   %-30s %d' % (k, cnt[k]))
