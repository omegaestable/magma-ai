"""Coincidence check for the 38249 skeleton (single rule R1, dualized L-form law
   x = y * (y * ((z * (x * x)) * y))).
Hand-derived instance: take u = J z (J x x) (the always-free product (z*(x*x))) and make
   y = J u (J (J a (J c c)) u)
so that the THIRD product of the chain, op(u, y), is itself an R1 redex (y encodes c by u)
and returns the payload c instead of the free term J u y.  The two outer products are then
free by size and the chain ends at J y (J y c) != x.
Also re-runs deep_tests on the DUAL law (gen/chk38249.py feeds the un-dualized R-form law to
the L-form model, which is why it reports 3000/3000 fails in 0.3 s).
Run: python gen/cex38249.py [N]"""
import sys, os
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from leangen import dual_pat

orig = normalise(parse_eq(catalog()[38249]))
law = ('x', dual_pat(orig[1]))
print("orig  :", orig)
print("dual  :", law)
rules = [([('TG', ('V',)), ('EQ', ('U',), ('A1', ('V',))), ('TG', ('A2', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A1', ('A2', ('V',))))), ('EQ', ('A1', ('A2', ('A1', ('A2', ('V',))))), ('A2', ('A2', ('A1', ('A2', ('V',)))))), ('EQ', ('U',), ('A2', ('A2', ('V',))))], ('A1', ('A2', ('A1', ('A2', ('V',))))), 'free')]

N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
C = cf.Closed(law, rules)
tested, fails = cf.deep_tests(C, law, N, 300, 11)
print("deep_tests on the DUAL law: tested", tested, "fails", len(fails))

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))
def which_rule(C, u, v):
    for i, (conds, e, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'

x = g(0); z = g(1); a = g(2); c = g(3)
u = J(z, J(x, x))
y = J(u, J(J(a, J(c, c)), u))
s = {'x': x, 'y': y, 'z': z}
C = cf.Closed(law, rules)
p1 = C.op(x, x);      print("x*x           :", which_rule(C, x, x), "=", show(p1))
p2 = C.op(z, p1);     print("z*(x*x)       :", which_rule(C, z, p1), "=", show(p2))
p3 = C.op(p2, y);     print("(z*(x*x))*y   :", which_rule(C, p2, y), "=", show(p3))
p4 = C.op(y, p3);     print("y*(...)       :", which_rule(C, y, p3), "=", show(p4))
p5 = C.op(y, p4);     print("y*(y*(...))   :", which_rule(C, y, p4), "=", show(p5))
A, B = law[1]
lhs = C.op(C.evp(A, s), C.evp(B, s))
print("evp result =", show(lhs))
print("x          =", show(x))
print("y          =", show(y), " sz", size(y))
print("LAW HOLDS" if lhs == x else "LAW FAILS on this instance")
print("fired rules:", C.fired)
