"""Candidate repair of the 5837 rule set: R1-R3 (shipped) + R4a/b/c (the `op u u` decode the generator missed).
Validates with deep_tests (several seeds) and with the hole family constructed explicitly.  Single process."""
import sys, os, time, random
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[5837]))
U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)
R1 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), TG(A1(A2(A2(V)))), EQ(U, A2(A1(A2(A2(V))))), EQ(U, A2(A2(A2(V))))], A1(V), 'free')
R2 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A1(A2(A2(V))))], A1(V), 'B110l')
R3 = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(U), TG(A2(U)), OPEQ(OP(A1(A2(U)), U), A2(A2(V))), OPEQ(OP(A1(A2(U)), U), A1(A2(U)))], A1(V), 'B11l,B110l')
# R4: v = u, u = J q (J q _) with op(q, u) = q (u encodes q by q), q = I(x, w) = x*((w*x)*x) read three ways; -> x = q.1
q = A1(U); x = A1(q)
common = [EQ(V, U), TG(U), TG(A2(U)), EQ(A1(U), A1(A2(U))), OPEQ(OP(A1(U), U), A1(U)), TG(q)]
R4a = (common + [TG(A2(q)), TG(A1(A2(q))), EQ(x, A2(A1(A2(q)))), EQ(x, A2(A2(q)))], x, 'R4a')
R4b = (common + [TG(A2(q)), EQ(x, A2(A2(q))), TG(x), TG(A2(x)), OPEQ(OP(A1(A2(x)), x), A1(A2(q)))], x, 'R4b')
R4c = (common + [TG(x), TG(A2(x)), OPEQ(OP(A1(A2(x)), x), A2(q)), OPEQ(OP(A1(A2(x)), x), A1(A2(x)))], x, 'R4c')
R2p = ([TG(V), TG(A2(V)), EQ(U, A1(A2(V))), TG(A2(A2(V))), EQ(U, A2(A2(A2(V)))), OPEQ(OP(U, U), A1(A2(A2(V))))], A1(V), 'R2p')
R4bp = (common + [TG(A2(q)), EQ(x, A2(A2(q))), OPEQ(OP(x, x), A1(A2(q)))], x, 'R4bp')
rules = [R1, R2, R2p, R3, R4a, R4b, R4bp, R4c]
for r in rules: print(cf.show_rule(r))
C = cf.Closed(law, rules)
A, B = law[1]
def g(n): return ('g', n)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))
def op(a, b): return C.op(a, b)
def inner(a, b): return op(a, op(op(b, a), a))
def enc(p, u, w): return op(p, inner(u, w))
def lawval(x, y, z):
    q1 = op(z, y); q2 = op(q1, y); q3 = op(y, q2); q4 = op(x, q3); return op(y, q4), (q1, q2, q3, q4)

t0 = time.time()
for seed in (11, 1, 2, 3, 4, 5):
    tested, fails = cf.deep_tests(C, law, 20000, 240, seed)
    print('deep_tests seed', seed, 'tested', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
    for s, r in fails[:3]:
        print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if isinstance(r, tuple) else r)

base = [g(0), g(1), g(2)]
P1 = list(base)
for a in base:
    for b in base:
        for t in (op(a, b), inner(a, b)):
            if t not in P1: P1.append(t)
for a in base:
    for b in base:
        for c in base:
            t = enc(a, b, c)
            if t not in P1: P1.append(t)
fails = {}
def test(x, y, z, tag):
    if max(size(x), size(y), size(z)) > 400: return
    r, qq = lawval(x, y, z)
    if r != x:
        key = (show(x), show(y), show(z))
        if key not in fails: fails[key] = (tag, show(r), [show(t) for t in qq])
n = 0
# the hole family: z = I(x, w2), y = enc(z, z, w)
for x in P1:
    for w2 in P1:
        z = inner(x, w2)
        for w in P1:
            y = enc(z, z, w)
            test(x, y, z, 'hole'); n += 1
print('hole family triples', n, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
# the general critical family: y = enc(p, u, w), z = u, x anything (sampled)
random.seed(1)
n = 0
while n < 200000 and time.time() - t0 < 400:
    p, u, w, x = (random.choice(P1) for _ in range(4))
    y = enc(p, u, w)
    test(x, y, u, 'crit'); n += 1
    test(x, y, p, 'crit2'); n += 1
print('critical family triples', n, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
# full level-1 cube
n = 0
for x in P1:
    for y in P1:
        for z in P1:
            test(x, y, z, 'L1'); n += 1
print('level-1 cube', n, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
for k, v in list(fails.items())[:8]:
    print('FAIL[%s] x=%s\n   y=%s\n   z=%s\n   result=%s\n   q1..q4=%s' % (v[0], k[0], k[1], k[2], v[1], ' | '.join(v[2])))
print('fired', C.fired, 'distinct fails', len(fails))
