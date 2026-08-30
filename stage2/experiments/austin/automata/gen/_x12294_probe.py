"""Probe the smallest exhaustive failure of law 12294 in the SEMANTIC free model."""
import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12294
law = normalise(parse_eq(catalog()[EQ]))
print('law', law)
F = fm.Free(law)

def show(t):
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(%s*%s)' % (show(t[1]), show(t[2]))

a = ('g', 0)
def J(p, q): return ('J', p, q)

y = J(J(a, a), a)
z = J(y, J(a, a))
x = a
print('x', show(x), 'y', show(y), 'z', show(z))

s = {'x': x, 'y': y, 'z': z}
A, B = law[1]

def ev(p):
    if isinstance(p, str):
        return s[p]
    l = ev(p[0]); r = ev(p[1])
    c0 = F.cuts
    res = F.op(l, r)
    free = (res == J(l, r))
    print('  op(%s , %s) = %s   %s  cuts+%d' % (show(l), show(r), show(res), 'FREE' if free else 'DECODE', F.cuts - c0))
    return res

va = ev(A); vb = ev(B)
print('A =', show(va))
print('B =', show(vb))
c0 = F.cuts
top = F.op(va, vb)
print('TOP op(A,B) =', show(top), 'expected', show(x), 'cuts+%d' % (F.cuts - c0))
print('cuts total', F.cuts, 'rcycles', F.rcycles, 'conflicts', len(F.conflicts), 'tainted', F.tainted)

# is (va, vb) actually a reading?  ask the reader directly, ungated
print('--- direct readings of the root pattern against (A,B) ---')
G = fm.Free(law)
G.bound = None
cnt = 0
for sol in G.readings(law[1], J(va, vb), {}):
    cnt += 1
    print('  reading', {k: show(v) for k, v in sol.items() if k in ('x', 'y', 'z')})
    if cnt > 5:
        break
print('n readings (root as J pattern):', cnt)
