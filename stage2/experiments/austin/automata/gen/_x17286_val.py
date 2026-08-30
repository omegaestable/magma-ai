"""_x17286_val.py -- wave-3 validation standard for the repaired 17286 rule set (BASE + R8b)."""
import sys, os, time, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
BASE = cf.Extractor(law).rules(exist=False)
g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e); A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b); JE = lambda a, b: ('J', a, b)
P_ = A2(A2(V)); X_ = JE(A1(P_), P_)
R8b = ([('TG', V), ('TG', A2(V)), ('EQ', A1(V), A1(A2(V))), ('TG', P_),
        ('OPEQ', OP(U, A1(P_)), A2(P_)), ('OPEQ', OP(X_, A1(V)), P_)], X_, 'DDb')
RULES = BASE + [R8b]


def show(x, cap=45):
    if size(x) > cap: return '<sz%d>' % size(x)
    return 'g%d' % x[1] if x[0] == 'g' else '(%s*%s)' % (show(x[1], 9999), show(x[2], 9999))


def encB(p, w): return J(w, J(w, J(p, w)))


def chain(rules, x, y, z):
    C = cf.Closed(law, rules)
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    return top, ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q))), C


t0 = time.time()
print('== 1. rv.run_tests seeds [3,4,5], 3000 deep / 12000 fuzz ==', flush=True)
f = rv.run_tests(law, RULES, [3, 4, 5], 3000, 12000)
print('   fails: %d  (%.0f s)' % (len(f), time.time() - t0), flush=True)
for s, r, kind, sd in f[:5]:
    print('    kind=%s seed=%s' % (kind, sd), {k: show(vv, 22) for k, vv in s.items()})

print('== 2. cf.deep_tests 20000 on 5 seeds ==', flush=True)
for sd in (11, 101, 1009, 20260829, 121016):
    C = cf.Closed(law, RULES)
    n, ff = cf.deep_tests(C, law, 20000, 300, sd)
    print('   seed %-9d tested %5d fails %d  (%.0f s)' % (sd, n, len(ff), time.time() - t0), flush=True)
    for s, r in ff[:3]:
        print('      ', r if isinstance(r, str) else show(r), {k: show(vv, 22) for k, vv in s.items()})

print('== 3. the case tree: constructed instances per cell ==', flush=True)
CASES = []
tt = J(g(1), g(0)); ss = J(tt, J(tt, J(g(0), tt))); vv0 = J(ss, J(ss, g(0)))
CASES.append(('diag', vv0, vv0, vv0))
for name, (pa, wa, qy, w) in [
        ('DD-gens', (g(5), g(6), g(7), g(8))),
        ('DD-paJ', (J(g(5), g(9)), g(6), g(7), g(8))),
        ('DD-waJ', (g(5), J(g(6), g(9)), g(7), g(8))),
        ('DD-wJ', (g(5), g(6), g(7), J(g(8), g(9)))),
        ('DD-qyJ', (g(5), g(6), J(g(7), g(9)), g(8))),
        ('DD-deep', (encB(g(5), g(9)), g(6), g(7), g(8))),
        ('DD-deep2', (encB(J(g(5), g(4)), g(9)), J(g(6), g(3)), g(7), g(8)))]:
    y = J(qy, pa); x = encB(pa, wa); z = encB(x[2], w)
    CASES.append((name, x, y, z))
x1 = g(6); Aq = g(5); tail = J(x1, J(Aq, x1))
CASES.append(('DD-r2fl', J(x1, tail), J(g(7), Aq), encB(tail, g(8))))
# A dec only, P dec only, all free
CASES.append(('A-dec', encB(g(5), g(6)), J(g(1), g(5)), g(2)))
CASES.append(('P-dec', J(g(4), g(5)), g(1), encB(g(5), g(6))))
CASES.append(('free', g(0), g(1), g(2)))
for name, x, y, z in CASES:
    try:
        top, cell, C = chain(RULES, x, y, z)
        print('   %-9s cell=%s %s  fired=%s' % (name, cell, 'OK' if top == x else '**FAIL**',
                                                sorted(C.fired)))
    except RecursionError:
        print('   %-9s RECURSION' % name)

print('== 4. shape sweep 15^3 ==', flush=True)
GENS = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(g(0), g(0)),
        encB(g(0), g(1)), encB(g(1), g(0)), encB(g(0), g(0)),
        J(g(2), g(0)), J(g(3), encB(g(0), g(1))), encB(J(g(0), g(1)), g(2)),
        encB(g(0), J(g(1), g(2))), J(g(1), encB(g(0), g(1))[2]), encB(encB(g(0), g(1)), g(2))]
seen = {}; bad = []
for x, y, z in itertools.product(GENS, repeat=3):
    try:
        top, cell, _ = chain(RULES, x, y, z)
    except RecursionError:
        continue
    seen[cell] = seen.get(cell, 0) + 1
    if top != x: bad.append((cell, x, y, z, top))
for k in sorted(seen): print('   %s %d' % (k, seen[k]))
print('   failures:', len(bad))
for b in bad[:8]:
    print('     ', b[0], 'x=', show(b[1]), 'y=', show(b[2]), 'z=', show(b[3]), '->', show(b[4]))
print('total %.0f s' % (time.time() - t0))
