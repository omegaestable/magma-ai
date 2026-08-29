import sys, os
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[12234]))
RULES = [([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('A2', ('V',))), ('EQ', ('A2', ('A1', ('A1', ('V',)))), ('A1', ('A2', ('V',)))), ('EQ', ('U',), ('A2', ('A2', ('V',))))], ('A2', ('A1', ('A1', ('V',)))), 'free'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('TG', ('A1', ('A1', ('V',)))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('V',)))), ('U',)), ('A2', ('V',)))], ('A2', ('A1', ('A1', ('V',)))), 'B1l'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('A2', ('V',))))), ('A1', ('A2', ('V',)))), ('A1', ('A1', ('V',))))], ('A1', ('A2', ('V',))), 'B00l'), ([('TG', ('V',)), ('TG', ('A1', ('V',))), ('EQ', ('U',), ('A2', ('A1', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A2', ('V',))), ('TG', ('A2', ('A1', ('U',)))), ('TG', ('A1', ('A2', ('A1', ('U',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A2', ('A1', ('U',))))), ('A2', ('A1', ('U',)))), ('A1', ('A1', ('V',))))], ('A2', ('A1', ('U',))), 'B00l,B1l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A1', ('V',))), ('TG', ('A2', ('A1', ('U',)))), ('EQ', ('A1', ('A2', ('V',))), ('A2', ('A2', ('A1', ('U',)))))], ('A1', ('A2', ('V',))), 'B0l'), ([('TG', ('V',)), ('TG', ('A2', ('V',))), ('EQ', ('U',), ('A2', ('A2', ('V',)))), ('TG', ('U',)), ('TG', ('A1', ('U',))), ('OPEQ', ('OP', ('A2', ('A1', ('U',))), ('U',)), ('A1', ('V',))), ('TG', ('A1', ('A2', ('V',)))), ('TG', ('A1', ('A1', ('A2', ('V',))))), ('OPEQ', ('OP', ('A2', ('A1', ('A1', ('A2', ('V',))))), ('A1', ('A2', ('V',)))), ('A2', ('A1', ('U',))))], ('A1', ('A2', ('V',))), 'B0l,B00l')]

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

C = cf.Closed(law, RULES)
print('law', law)
# hand-built instance: x is an R5-shaped encoding of g2 by z (z at x.2.2, not x.1.2)
Ap = J(g(4), g(2))                                  # A' = q * x''  (free)
z  = J(J(J(g(3), g(0)), Ap), J(g(0), Ap))           # z encodes g0 by A' (R1 shape)  -> op(A', z) = g0
x  = J(g(0), J(g(2), z))                            # x = J (op(A',z)) (J g2 z): R5 shape w.r.t. z -> op(z, x) = g2
y  = g(1)
print('op(Ap,z) =', show(C.op(Ap, z)))
A = C.op(z, x); print('A = op(z,x) =', show(A))
B = C.op(A, y); print('B = op(A,y) =', show(B))
Cc = C.op(x, y); print('C = op(x,y) =', show(Cc))
D = C.op(B, Cc); print('D = op(B,C) =', show(D))
R = C.op(y, D); print('y*D =', show(R))
print('LAW HOLDS' if R == x else 'LAW FAILS: x =', show(x))
s = {'x': x, 'y': y, 'z': z}
print('evp check:', C.evp(law[1], s) == x)
# what the structured fuzzer sees
import fuzz as fz
t, f = fz.fuzz(cf.Closed(law, RULES), law, RULES, 12000, seed=12234)
print('fuzz tested', t, 'fails', len(f))
for s2, r in f[:3]:
    print({k: show(v) for k, v in s2.items()}, '->', show(r) if isinstance(r, tuple) else r)
