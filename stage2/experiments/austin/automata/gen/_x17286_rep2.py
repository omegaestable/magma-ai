"""_x17286_rep2.py -- repair candidates for the (A dec, P dec) cell of law 17286, compared."""
import sys, os, time
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

P_ = A2(A2(V))                       # v.2.2  = P
X_ = JE(A1(P_), P_)                  # J(P.1, P) = the recovered x
PRE = [('TG', V), ('TG', A2(V)), ('EQ', A1(V), A1(A2(V))), ('TG', P_)]
GX = ('OPEQ', OP(X_, A1(V)), P_)                        # op(X, z) == P

R8a = (PRE + [('TG', A2(P_)), ('EQ', A1(P_), A2(A2(P_))), ('EQ', U, A1(A2(P_))), GX], X_, 'DDa')
R8b = (PRE + [('OPEQ', OP(U, A1(P_)), A2(P_)), GX], X_, 'DDb')
R8c = (PRE + [('OPEQ', OP(U, A1(P_)), A2(P_)), GX,
              ('OPEQ', OP(A1(V), P_), A2(V)), ('OPEQ', OP(A1(V), A2(V)), V)], X_, 'DDc')


def show(x, cap=45):
    if size(x) > cap: return '<sz%d>' % size(x)
    return 'g%d' % x[1] if x[0] == 'g' else '(%s*%s)' % (show(x[1], 9999), show(x[2], 9999))


def encB(p, w): return J(w, J(w, J(p, w)))


def chain(rules, x, y, z):
    C = cf.Closed(law, rules)
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    return top, ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q)))


t = J(g(1), g(0)); s = J(t, J(t, J(g(0), t))); v = J(s, J(s, g(0)))
CASES = [('diag', v, v, v)]
for name, (pa, wa, qy, w) in [
        ('gens', (g(5), g(6), g(7), g(8))),
        ('pa=J', (J(g(5), g(9)), g(6), g(7), g(8))),
        ('wa=J', (g(5), J(g(6), g(9)), g(7), g(8))),
        ('w=J', (g(5), g(6), g(7), J(g(8), g(9)))),
        ('qy=J', (g(5), g(6), J(g(7), g(9)), g(8))),
        ('deep', (encB(g(5), g(9)), g(6), g(7), g(8)))]:
    y = J(qy, pa); x = encB(pa, wa); px = x[2]; z = encB(px, w)
    CASES.append((name, x, y, z))
# an A-decode through R2 (x's tail is an op), generic (not the diagonal)
x1 = g(6); Aq = g(5)
tail = J(x1, J(Aq, x1))                    # op(A,x1) free
xx = J(x1, tail)
yy = J(g(7), Aq)
zz = encB(tail, g(8))
CASES.append(('r2fl', xx, yy, zz))

for lbl, R in (('base', BASE), ('+R8a', BASE + [R8a]), ('+R8b', BASE + [R8b]), ('+R8c', BASE + [R8c])):
    out = []
    for name, x, y, z in CASES:
        try:
            top, cell = chain(R, x, y, z)
            out.append('%s:%s%s' % (name, cell, 'OK' if top == x else '**F**'))
        except RecursionError:
            out.append('%s:REC' % name)
    print('%-6s %s' % (lbl, '  '.join(out)))

print()
seeds = [EQ * 7 + 3, EQ * 7 + 14]
for lbl, R in (('+R8a', BASE + [R8a]), ('+R8b', BASE + [R8b]), ('+R8c', BASE + [R8c])):
    t0 = time.time()
    f = rv.run_tests(law, R, seeds, 3000, 12000)
    print('%s full validator: %d fails (%.0f s)' % (lbl, len(f), time.time() - t0))
    for s, r, kind, sd in f[:4]:
        print('    kind=%s seed=%s' % (kind, sd), {k: show(vv, 22) for k, vv in s.items()})
