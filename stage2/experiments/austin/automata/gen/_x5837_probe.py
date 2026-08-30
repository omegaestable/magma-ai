"""Probe the concrete instances of each observed mode tuple for law 5837 and print the relations
that a Lean case analysis would need."""
import sys, os, random, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ_(U, A2(A1(A2(A2(V))))), EQ_(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R2p = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R3 = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
q = A1(U); xx = A1(q)
common = [EQ_(V, U), TG(U), TG(A2(U)), EQ_(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ_(xx, A2(A1(A2(q)))), EQ_(xx, A2(A2(q)))], xx, 'R4a')
R4b = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(q)))], xx, 'R4b')
R4bp = (common + [TG(A2(q)), EQ_(xx, A2(A2(q))), OPEQ(OP(xx, xx), A1(A2(q)))], xx, 'R4bp')
R4c = (common + [TG(xx), TG(A2(xx)), OPEQ(OP(A1(A2(xx)), xx), A2(q)), OPEQ(OP(A1(A2(xx)), xx), A1(A2(xx)))], xx, 'R4c')
RULES = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]

cat = catalog(); law = normalise(parse_eq(cat[5837]))
C = cf.Closed(law, RULES)
def op(a, b): return C.op(a, b)
def which(a, b):
    for i, (conds, x, tag) in enumerate(RULES):
        if C.check(conds, a, b):
            if C.ev(x, a, b) is not None: return i + 1
    return 'f'
def g(n): return ('g', n)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def isJ(t): return t[0] == 'J'
def show(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def inner(a, b): return op(a, op(op(b, a), a))
def enc(p, u, w): return op(p, inner(u, w))

base = [g(0), g(1), g(2)]
pool = list(base)
for a in base:
    for b in base:
        for t in (op(a, b), inner(a, b), ('J', a, b)):
            if t not in pool: pool.append(t)
for a in base:
    for b in base:
        for c in base:
            t = enc(a, b, c)
            if t not in pool: pool.append(t)

seen = {}
def rec(x, y, z):
    if max(size(x), size(y), size(z)) > 500: return
    try:
        P0 = op(z, y); P1 = op(P0, y); L3 = op(y, P1); E = op(x, L3); F = op(y, E)
    except RecursionError:
        return
    m = (which(z, y), which(P0, y), which(y, P1), which(x, L3), which(y, E))
    if m not in seen:
        seen[m] = (x, y, z, P0, P1, L3, E, F)

for x in pool:
    for y in pool:
        for z in pool:
            rec(x, y, z)
random.seed(7)
n = 0
t0 = time.time()
while n < 40000 and time.time() - t0 < 180:
    p, u, w, x = (random.choice(pool) for _ in range(4))
    y = enc(p, u, w)
    rec(x, y, u); rec(x, y, p); rec(p, y, u)
    z2 = inner(x, random.choice(pool))
    rec(x, enc(z2, z2, random.choice(pool)), z2)
    n += 4

print('modes', len(seen))
for m in sorted(seen, key=str):
    x, y, z, P0, P1, L3, E, F = seen[m]
    print('=' * 100)
    print('modes P0=%s P1=%s L3=%s E=%s F=%s   ok=%s' % (m[0], m[1], m[2], m[3], m[4], F == x))
    print('  sizes x=%d y=%d z=%d P0=%d P1=%d E=%d' % (size(x), size(y), size(z), size(P0), size(P1), size(E)))
    rel = []
    if E == y: rel.append('E = y')
    if E == ('J', x, L3): rel.append('E free')
    if z == y: rel.append('z = y')
    if x == a1(P1): rel.append('x = a1 P1')
    if P1 == a1(y): rel.append('P1 = a1 y')
    if P0 == a1(a2(y)): rel.append('P0 = a1(a2 y)')
    if P1 == ('J', P0, y): rel.append('P1 free')
    if P0 == ('J', z, y): rel.append('P0 free')
    if isJ(y) and a1(y) == a1(a2(y)): rel.append('a1 y = a1(a2 y)')
    if isJ(y) and op(a1(y), y) == a1(y): rel.append('op(a1 y) y = a1 y')
    if x == a1(a1(y)): rel.append('x = a1(a1 y)')
    if x == a2(y): rel.append('x = a2 y')
    if P1 == P0: rel.append('P1 = P0')
    print('  rel:', ', '.join(rel))
