"""Targeted positive control for the ONE guard the per-cell map leaves unexplained.

Cell (AF,UF,BD,VF) is served exclusively by rule 3 `A0s,B1s|rd:A0`, whose second op-guard is
    a1 (a2 u) = op (a2 (a2 u)) (a2 v)      i.e.   a1 y = op (a2 y) B .
When B decodes through rule 1 at (y,z) we have  y = J (J y1 x1) y1,  z = J x1 (J y1 z1),  B = x1,
so that guard reads  J y1 x1 = op y1 x1  --  it demands the INNER product op y1 x1 be FREE.
So construct exactly the case where it is NOT: draw (y1,x1) from a decoding pair.
If no rule then fires at the top, the model is false and this is the witness.
"""
import sys, random, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size, rand_term
import importlib.util
spec = importlib.util.spec_from_file_location('_f4', D + '/gen/_w3_23357_f4.py')
m = importlib.util.module_from_spec(spec)
argv = list(sys.argv); sys.argv = [sys.argv[0]]
spec.loader.exec_module(m)
law, rules = m.law, m.rules
TAGS = [r[2] for r in rules]
show = tr.show
J = lambda a, b: ('J', a, b)
G = lambda n: ('g', n)

rng = random.Random(int(argv[1]) if len(argv) > 1 else 3)
C0 = cf.Closed(law, rules)
pool = [G(i) for i in range(4)]
for d in range(3):
    for u, v in fz.instances(rules, pool, 14, d, C0):
        for t in (u, v):
            if size(t) <= 60 and t not in pool: pool.append(t)
        try:
            r = C0.op(u, v)
            if size(r) <= 60 and r not in pool: pool.append(r)
        except RecursionError: pass
for _ in range(200):
    t = rand_term(rng.randint(1, 4), 3)
    if t not in pool: pool.append(t)

# decoding pairs (y1, x1): op y1 x1 != J y1 x1
DEC = []
for a in pool:
    for b in pool:
        try:
            if C0.op(a, b) != J(a, b): DEC.append((a, b))
        except RecursionError: pass
print('pool %d   decoding pairs %d' % (len(pool), len(DEC)), flush=True)

zz = [t for t in pool if size(t) <= 12]
xs = [G(7), G(8)] + [t for t in pool if size(t) <= 9]
bad = []; n = 0; cells = collections.Counter(); g2holds = 0; b_dec = 0
for (y1, x1) in DEC[:900]:
    y = J(J(y1, x1), y1)
    for z1 in zz[:6]:
        z = J(x1, J(y1, z1))
        for x in xs[:6]:
            C = cf.Closed(law, rules)
            try:
                A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B); top = C.op(U, V)
            except RecursionError:
                continue
            n += 1
            if B != J(y, z): b_dec += 1
            cells[(('AD' if A != J(y, x) else 'AF'), ('UD' if U != J(A, y) else 'UF'),
                   ('BD' if B != J(y, z) else 'BF'), ('VD' if V != J(x, B) else 'VF'))] += 1
            try:
                if C.op(y1, x1) == J(y1, x1): g2holds += 1
            except RecursionError: pass
            if top != x:
                bad.append((x, y, z, top))
print('tested %d   B decoded in %d   (inner op y1 x1 free in %d)' % (n, b_dec, g2holds), flush=True)
for k, c in cells.most_common(8):
    print('   %-24s %d' % (str(k), c), flush=True)
print('LAW FAILURES:', len(bad), flush=True)
for (x, y, z, top) in sorted(bad, key=lambda t: sum(size(q) for q in t[:3]))[:2]:
    print('  x =', show(x)[:200], flush=True)
    print('  y =', show(y)[:300], flush=True)
    print('  z =', show(z)[:300], flush=True)
    print('  got', show(top)[:200], flush=True)
