import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
A, B = law[1]

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

w = ('g', 0)
y = ('J', ('J', ('J', w, ('g',1)), w), w)
x = ('J', ('J', ('g', 1), y), y)
z = x
P = ('J', ('g',1), y)

F = fm.Free(law, maxdepth=60)
r = F.op(x, z)
print('semantic op(x,z) =', show(r), 'expected P=', show(P), 'match?', r == P, 'or free J(x,z)?', r == ('J',x,z))
print('conflicts', len(F.conflicts), 'cycles', F.cycles, 'bail', F.bail)

s = {'x': x, 'y': y, 'z': z}
def evs(p):
    if isinstance(p, str): return s[p]
    return F.op(evs(p[0]), evs(p[1]))
lhs = evs(A)
rhs = evs(B)
print('u (A val) =', show(lhs)[:200])
print('v (B val) =', show(rhs))
final = F.op(lhs, rhs)
print('semantic FINAL =', show(final), 'expected x=', show(x), 'match?', final == x)
print('conflicts', len(F.conflicts))
