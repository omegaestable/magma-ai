"""_x17286_rep.py -- candidate repair of law 17286's model: the (A dec, P dec) cell.

The hole: op(y,x) decoded AND op(x,z) decoded -> x is not a projection of either argument of the
top product.  But when op(y,x) decodes, x always has the shape J(x1, x.2) whose tail x.2 is the
encoding, and when op(x,z) decodes through the u-side family, P = a2 x -- so x = J(P.1, P).

R8:  J?v & J?v.2 & v.1 = v.2.1 & J?v.2.2 & J?v.2.2.2 & v.2.2.1 = v.2.2.2.2 & u = v.2.2.2.1
     & op(J(v.2.2.1, v.2.2), v.1) == v.2.2      ->   J(v.2.2.1, v.2.2)
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf, revalidate as rv
import freemodel as fm
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

P_ = A2(A2(V))                       # v.2.2
X_ = JE(A1(P_), P_)                  # J(P.1, P)
R8 = ([('TG', V), ('TG', A2(V)), ('EQ', A1(V), A1(A2(V))), ('TG', P_),
       ('TG', A2(P_)), ('EQ', A1(P_), A2(A2(P_))), ('EQ', U, A1(A2(P_))),
       ('OPEQ', OP(X_, A1(V)), P_)], X_, 'DD')

RULES = BASE + [R8]
print('R8:', cf.show_rule(R8))


def show(x, cap=45):
    if size(x) > cap: return '<sz%d>' % size(x)
    return 'g%d' % x[1] if x[0] == 'g' else '(%s*%s)' % (show(x[1], 9999), show(x[2], 9999))


def encB(p, w): return J(w, J(w, J(p, w)))


def chain(rules, x, y, z):
    C = cf.Closed(law, rules)
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    return top, ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q)))


print('\n-- the constructed DD instances --')
CASES = []
for name, (pa, wa, qy, w) in [
        ('gens', (g(5), g(6), g(7), g(8))),
        ('pa=J', (J(g(5), g(9)), g(6), g(7), g(8))),
        ('wa=J', (g(5), J(g(6), g(9)), g(7), g(8))),
        ('w=J', (g(5), g(6), g(7), J(g(8), g(9)))),
        ('qy=J', (g(5), g(6), J(g(7), g(9)), g(8))),
        ('deep', (encB(g(5), g(9)), g(6), g(7), g(8)))]:
    y = J(qy, pa); x = encB(pa, wa); px = x[2]; z = encB(px, w)
    CASES.append((name, x, y, z))
    for lbl, R in (('base', BASE), ('R8', RULES)):
        top, cell = chain(R, x, y, z)
        print('%-6s %-5s cell=%s %s' % (name, lbl, cell, 'OK' if top == x else 'FAIL'))

# the deep-test instance
t = J(g(1), g(0)); s = J(t, J(t, J(g(0), t))); v = J(s, J(s, g(0)))
for lbl, R in (('base', BASE), ('R8', RULES)):
    top, cell = chain(R, v, v, v)
    print('%-6s %-5s cell=%s %s' % ('diag', lbl, cell, 'OK' if top == v else 'FAIL'))

print('\n-- full validator on the repaired set --')
seeds = [EQ * 7 + 3, EQ * 7 + 14]
f = rv.run_tests(law, RULES, seeds, 3000, 12000)
print('run_tests(3 phases, 2 seeds): %d fails' % len(f))
for s, r, kind, sd in f[:6]:
    print('   kind=%s seed=%s' % (kind, sd), {k: show(vv, 25) for k, vv in s.items()})
