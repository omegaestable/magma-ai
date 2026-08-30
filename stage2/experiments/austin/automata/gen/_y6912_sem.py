"""_y6912_sem.py : trace law 6912's single semantic free-model failure, step by step.

`python smallcheck.py 6912 9 1` reports exactly one failure:
    y = ((g0*g0)*(g0*(g0*g0)))   z = g0   x = (g0*g0)
This script evaluates the law's chain in `freemodel.Free` and prints every product, so the forced
coincidence can be read off and checked by hand (the NOTES_34889 method).
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.setrecursionlimit(60000)
from freemodel import Free, normalise, catalog, size
from laws import parse_eq

EQ = 6912
law = normalise(parse_eq(catalog()[EQ]))
print('law', law)


def show(t):
    if t[0] == 'g':
        return 'g%d' % t[1] if t[1] >= 0 else 'JUNK'
    return '(%s*%s)' % (show(t[1]), show(t[2]))


def J(a, b):
    return ('J', a, b)


g0 = ('g', 0)
c = J(g0, g0)
y = J(c, J(g0, c))
z = g0
x = c

F = Free(law)
A, B = law[1]
print('A pattern', A, ' B pattern', B)

s = {'x': x, 'y': y, 'z': z}
print('instance', {k: show(v) for k, v in s.items()})


def ev(p, ind='  '):
    if isinstance(p, str):
        return s[p]
    a = ev(p[0], ind); b = ev(p[1], ind)
    r = F.op(a, b)
    print('%sop(%s, %s) = %s%s' % (ind, show(a), show(b), show(r) if size(r) < 70 else '<size %d>' % size(r),
                                   '   [FREE]' if r == ('J', a, b) else '   *** DECODE'))
    return r


u = ev(A); v = ev(B)
r = F.op(u, v)
print('FINAL op(%s, %s) = %s' % (show(u) if size(u) < 40 else '<%d>' % size(u),
                                 show(v) if size(v) < 70 else '<%d>' % size(v),
                                 show(r) if size(r) < 90 else '<size %d>' % size(r)))
print('expected x = %s   %s' % (show(x), 'OK' if r == x else '*** FAIL'))
print('conflicts %d cycles %d cuts %d bail %d rbail %d spurious %d unverified %d tainted %d'
      % (len(F.conflicts), F.cycles, F.cuts, F.bail, F.rbail, F.spurious, F.unverified, F.tainted))
for a, b, xs in F.conflicts[:6]:
    print('  CONFLICT op(%s, %s) -> %s' % (show(a) if size(a) < 40 else '<%d>' % size(a),
                                           show(b) if size(b) < 40 else '<%d>' % size(b),
                                           [show(t) if size(t) < 40 else '<%d>' % size(t) for t in xs]))
