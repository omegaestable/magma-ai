"""Law 12073:  x = y * (((y*x)*x) * (z*z))   -- FINAL candidate.

Carrier: g i | E | J u v          (E is a constant: the value of every square)
op u v =
  R1 SQ     u = v                          -> E                       (one square: z drops out)
  R2 DEC    v = ((a*b)*E),  op u b = a     -> b                       (generic decoder)
  R3 SELF   v = (d*E), u != E, op E u = d  -> u                       (x = u : first product is E)
  R4 SCODE  v = (u*E),  u != E             -> ((op E u)*E)            (x = the self-code of u)
  R5                                       -> u*v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import Model, E, sz, show

LAW = ('x', ('y', ((('y', 'x'), 'x'), ('z', 'z'))))


def J(a, b):
    return ('J', a, b)


def r1(u, v, op):
    return E if u == v else None


def r2(u, v, op):
    """DEC: v = ((a*b)*E), op u b = a  ->  b"""
    if v[0] == 'J' and v[2] == E and v[1][0] == 'J':
        a, b = v[1][1], v[1][2]
        if not (u == E and b == E) and op(u, b) == a:
            return b
    return None


def r3(u, v, op):
    """GSC: v = (w*E), op u w = E  ->  ((E*w)*E)"""
    if v[0] == 'J' and v[2] == E:
        w = v[1]
        if not (u == E and w == E) and op(u, w) == E:
            return ('J', ('J', E, w), E)
    return None


def r4(u, v, op):
    """SELF: v = (d*E), op E u = d, u != E  ->  u"""
    if v[0] == 'J' and v[2] == E and u != E and op(E, u) == v[1]:
        return u
    return None


RULES = [r1, r2, r3, r4]


def M(rules=None):
    return Model(rules if rules is not None else RULES)


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y'], ['z'], sizes=((9, 1), (5, 2), (5, 3)), big=(11, 1, 5))
