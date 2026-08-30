"""Law 21866:  x = (y*(z*x)) * (x*(x*w))     (implies 21865, which is the w:=z instance)

Carrier: the plain free magma  g i | J u v.  Reading:  u = (y*(z*x)),  v = (x*(x*w)).
Both are read structurally, so op needs NO nested calls at all:
    op ((y*(z*a)) , (a*(a*w))) = a          -- a = v.1, checked against u.2.2 and v.2.1
    op u v = J u v                          -- otherwise
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import Model, E, sz, show

LAW = ('x', (('y', ('z', 'x')), ('x', ('x', 'w'))))


def r1(u, v, op):
    # v = (a * (a * w)),  u = (y * (z * a))
    if v[0] == 'J' and v[2][0] == 'J' and v[2][1] == v[1]:
        return v[1]
    return None


RULES = [r1]


def M(rules=None):
    return Model(rules if rules is not None else RULES)


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y', 'z', 'w'], [], sizes=((5, 1), (5, 2)), big=(7, 1, 3))
