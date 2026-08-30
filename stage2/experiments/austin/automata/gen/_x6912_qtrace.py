"""Trace one instance in the quotient free model of 6912."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import _x6912_fm as fm
from _x6912_fm import normalise, catalog, size
from laws import parse_eq
from _x6912_qcheck import show, law

g0 = ('g', 0); g1 = ('g', 1)
def K(u): return fm.K(u)
def J(u, v): return ('J', u, v)

F = fm.Free(law)
A, B = law[1]

def chain(s):
    print('instance', {k: show(v) for k, v in s.items()})
    def ev(p, ind='  '):
        if isinstance(p, str): return s[p]
        a, b = ev(p[0], ind), ev(p[1], ind)
        r = F.op(a, b)
        print('%s%-30s op(%s, %s) = %s' % (ind, str(p), show(a), show(b), show(r)))
        return r
    u = ev(A); v = ev(B)
    r = F.op(u, v)
    print('  FINAL op(%s, %s) = %s   expected %s   %s' % (show(u), show(v), show(r), show(s['x']),
          'OK' if r == s['x'] else '*** FAIL'))
    print('  conflicts', len(F.conflicts))
    for a, b, xs in F.conflicts[-3:]:
        print('    CONFLICT op(%s,%s) -> %s' % (show(a), show(b), [show(x) for x in xs]))

if __name__ == '__main__':
    P = J(g0, K(g0))
    chain({'y': K(g0), 'z': g0, 'x': K(P)})
    print()
    chain({'y': K(P), 'z': P, 'x': K(g0)})
