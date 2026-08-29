"""hole9667.py : evaluate the suspected level-2 counterexample of the generated rule set for law 9667.

Law 9667: x = y * ((z * y) * (x * (y * y))).
Suspect: R2 recovers z through a2 (a1 y), i.e. through w = J z' z (the R1 shape of op z y); when op z y
itself fired R2, a1 y = w = op q z, which need not be free.  Take z = J (J c q) (J d (J q q)) so that
op q z = d (R1), y = J d (J (J z z) (J z z)); then op z y = J z z by R2, but the outer product cannot see it.
"""
import sys, os
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[9667]))
rules = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('A2', ('V',))), ('TG', ('A2', ('A2', ('V',)))), ('EQ', ('U',), ('A1', ('A2', ('A2', ('V',))))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',)))))], ('A1', ('A2', ('V',))), 'free'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('TG', ('A2', ('A2', ('V',)))), ('EQ', ('U',), ('A1', ('A2', ('A2', ('V',))))), ('EQ', ('U',), ('A2', ('A2', ('A2', ('V',))))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A1', ('V',)))], ('A1', ('A2', ('V',))), 'B0l')]
print('law', law)
C = cf.Closed(law, rules)

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

c, q, d = g(1), g(2), g(0)
z = J(J(c, q), J(d, J(q, q)))
xp = J(z, z)
y = J(d, J(xp, J(z, z)))
x = g(1)
s = {'x': x, 'y': y, 'z': z}
print('z  =', show(z))
print('y  =', show(y))
print('x  =', show(x))
print('op q z          =', show(C.op(q, z)), '  (expect d = g0 via R1)')
print('op z y          =', show(C.op(z, y)), '  (expect J z z via R2)')
print('op y y          =', show(C.op(y, y)))
yy = C.op(y, y)
print('op x (y*y)      =', show(C.op(x, yy)))
P = C.op(z, y); Q = C.op(x, yy)
PQ = C.op(P, Q)
print('op (z*y) (x*(y*y)) free?', PQ == J(P, Q))
res = C.op(y, PQ)
print('law lhs value   =', show(res) if res[0] == 'g' else ('J y ... (free)' if res == J(y, PQ) else show(res)))
print('LAW HOLDS?', res == x)
print('evp check      :', C.evp(law[1], s) == s[law[0]])
print('fired', C.fired)
