import sys, random
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
import closedform as cf
from freemodel import normalise, catalog, Free, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[18137]))
rules = [([('TG', ('U',)), ('TG', ('V',)), ('TG', ('A2', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('EQ', ('A2', ('U',)), ('A1', ('A1', ('A2', ('V',))))), ('EQ', ('A1', ('V',)), ('A2', ('A1', ('A2', ('V',))))), ('EQ', ('A1', ('V',)), ('A2', ('A2', ('V',))))], ('A2', ('U',)), 'free'), ([('TG', ('U',)), ('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('A1', ('V',)), ('A2', ('A2', ('V',)))), ('OPEQ', ('OP', ('A2', ('U',)), ('A1', ('V',))), ('A1', ('A2', ('V',))))], ('A2', ('U',)), 'B10s'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('EQ', ('A1', ('V',)), ('A2', ('A1', ('A2', ('V',))))), ('EQ', ('A1', ('V',)), ('A2', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('TG', ('A2', ('A1', ('A1', ('A2', ('V',)))))), ('TG', ('A1', ('A2', ('A1', ('A1', ('A2', ('V',))))))), ('EQ', ('U',), ('A1', ('A1', ('A2', ('A1', ('A1', ('A2', ('V',)))))))), ('EQ', ('A1', ('A1', ('A1', ('A2', ('V',))))), ('A2', ('A1', ('A2', ('A1', ('A1', ('A2', ('V',)))))))), ('EQ', ('A1', ('A1', ('A1', ('A2', ('V',))))), ('A2', ('A2', ('A1', ('A1', ('A2', ('V',)))))))], ('A1', ('A1', ('A2', ('V',)))), 'As')]
C = cf.Closed(law, rules)
F = Free(law)

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

print('law', law)
# hand instance: A = y*x fires R2 (its inner product op(y.2, x.1) is non-free)
x1 = J(g(2), J(J(g(1), g(2)), g(2)))     # encodes g1 by (g0 g1): op((g0 g1), x1) = g1
x = J(x1, J(g(1), x1))                   # encodes (g0 g1) by y=(g3 (g0 g1)) via R2
y = J(g(3), J(g(0), g(1)))
z = g(5)
s = {'x': x, 'y': y, 'z': z}
A = C.op(y, x); B = C.op(x, z); Cc = C.op(B, z); D = C.op(z, Cc); E = C.op(A, D)
print('skeleton: A =', show(A)); print('  B =', show(B)); print('  C =', show(Cc)); print('  D =', show(D))
print('  E =', show(E)); print('  E == x ?', E == x)
print('  evp agrees:', C.evp(law[1], s) == E)
# same instance in the true free model
Af = F.op(y, x); Ef = F.ev(law[1], s)
print('free model: A =', show(Af), ' E == x ?', Ef == x, ' conflicts', len(F.conflicts))
