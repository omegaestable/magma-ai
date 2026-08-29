"""Coincidence check for the 5837 skeleton: the hand-derived instance
   z = J x (J (J w x) x),   y = J z (J z (J (J w' z) z))
i.e. in the free model  z = x*((w*x)*x),  y = z*(z*((w'*z)*z)).
Evaluates the law x = y*(x*(y*((z*y)*y))) with the shipped rule set (gen/chk5837.py's rules)."""
import sys, os
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq
law = normalise(parse_eq(catalog()[5837]))
rules = [([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('TG', ('A1', ('A2', ('A2', ('V',))))), ('EQ', ('U',), ('A2', ('A1', ('A2', ('A2', ('V',)))))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',)))))], ('A1', ('V',)), 'free'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('A2', ('A2', ('V',)))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',))))), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A1', ('A2', ('A2', ('V',)))))], ('A1', ('V',)), 'B110l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A1', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A2', ('U',))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A2', ('A2', ('V',)))), ('OPEQ', ('OP', ('A1', ('A2', ('U',))), ('U',)), ('A1', ('A2', ('U',))))], ('A1', ('V',)), 'B11l,B110l')]
C = cf.Closed(law, rules)
print("law", law)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))

x = g(0); w = g(1); w2 = g(2)
z = J(x, J(J(w, x), x))
y = J(z, J(z, J(J(w2, z), z)))
s = {'x': x, 'y': y, 'z': z}
q1 = C.op(z, y); print("z*y        =", show(q1))
q2 = C.op(q1, y); print("(z*y)*y    =", show(q2))
q3 = C.op(y, q2); print("y*((z*y)*y)=", show(q3))
q4 = C.op(x, q3); print("x*(...)    =", show(q4))
r = C.op(y, q4); print("y*(x*(...))=", show(r))
A, B = law[1]
lhs = C.op(C.evp(A, s), C.evp(B, s))
print("evp result =", show(lhs))
print("x          =", show(x))
print("LAW HOLDS" if lhs == x else "LAW FAILS on this instance")
print("fired rules:", C.fired)
