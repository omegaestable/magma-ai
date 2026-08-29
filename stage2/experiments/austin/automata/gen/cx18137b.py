import sys
sys.path.insert(0, 'C:\\Users\\nacho\\Documents\\GitHub\\magma-ai\\stage2\\experiments\\austin\\automata')
from freemodel import normalise, catalog, Free, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[18137]))
def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))
B = J(J(g(0), g(1)), g(1)); x = J(g(1), B); z = J(g(0), J(J(B, g(0)), g(0))); y = J(g(5), g(0))
s = {'x': x, 'y': y, 'z': z}
F = Free(law)
A = F.op(y, x); Bf = F.op(x, z); C = F.op(Bf, z); D = F.op(z, C); E = F.op(A, D)
print('free model: A =', show(A), '| B =', show(Bf), '| C free?', C == J(Bf, z), '| D free?', D == J(z, C))
print('  E =', show(E)); print('  E == x ?', E == x, '  (law violated by the free-model implementation if False)')
print('  op(g0, D) =', show(F.op(g(0), D)), ' conflicts', len(F.conflicts), 'spurious', F.spurious, 'unverified', F.unverified, 'bail', F.bail)
