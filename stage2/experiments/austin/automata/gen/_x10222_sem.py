"""Probe the smallest semantic-free-model failure of 10222.

y = g0*g0, x = g0, z = (g0*g0)*((g0*g0)*g0)
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

law = normalise(parse_eq(catalog()[10222]))
print('law', law)
A, B = law[1]

def T(s):
    return s if isinstance(s, tuple) else None

a = ('g', 0)
s2 = ('J', a, a)                      # g0*g0
z = ('J', s2, ('J', s2, a))           # (g0*g0)*((g0*g0)*g0)

def show(t):
    if t is None: return 'None'
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s*%s)' % (show(t[1]), show(t[2]))

F = fm.Free(law)
print('op(g0, z) =', show(F.op(a, z)))
print('op(z, s2) =', show(F.op(z, s2)))
print('op(a, s2) =', show(F.op(a, s2)))

for name, (x, y, zz) in [('smallest', (a, s2, z))]:
    F = fm.Free(law)
    env = {'x': x, 'y': y, 'z': zz}
    Q = F.op(F.op(zz, y), y)   # (z*y)*y  -- careful: A=y, B=((x*y)*((z*y)*y))
    print('--- %s ---' % name)
    q1 = F.op(zz, y); print('  op(z,y)      =', show(q1))
    r1 = F.op(q1, y); print('  op(op(z,y),y)=', show(r1))
    p1 = F.op(x, y);  print('  op(x,y)      =', show(p1))
    v = F.op(p1, r1); print('  v=op(P,R)    =', show(v))
    top = F.op(y, v); print('  op(y,v)      =', show(top), ' expected', show(x))
    print('  counters', dict(tainted=F.tainted, escapes=F.escapes, spurious=F.spurious,
                             unverified=F.unverified, cycles=F.cycles, bail=F.bail,
                             rbail=F.rbail, cuts=F.cuts, rcycles=F.rcycles,
                             conflicts=len(F.conflicts), junk_readings=F.junk_readings))
