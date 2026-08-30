"""Law 12073:  x = y * (((y*x)*x) * (z*z))     -- quotient carrier, iteration 3.

Carrier: g i | E | Q u | J u v.
  R1  u = v                                              -> E        (ONE square: kills z)
  R2  v = E                                              -> Q u      ("* E" tag)
  R3  v = Q (J a b), (u,b) != (E,E), op(u,b) = a         -> b        (decoder)
  R4  v = Q (Q (Q u))                                    -> E        (x = E)
  R5  v = Q u                                            -> Q(J E u) (x = the self-code of u)
  R6  otherwise                                          -> J u v
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = ['Q']
from qmod import Model, E, sz, show, exhaustive, deep, closure_fuzz, critical_fuzz, run_tests

LAW = ('x', ('y', ((('y', 'x'), 'x'), ('z', 'z'))))


def Q(u):
    return ('Q', u)


def r1(u, v, op):
    return E if u == v else None


def r2(u, v, op):
    return Q(u) if v == E else None


def r3(u, v, op):
    if v[0] == 'Q':
        w = v[1]
        if w[0] == 'J' and not (u == E and w[2] == E) and op(u, w[2]) == w[1]:
            return w[2]
    return None


def r4(u, v, op):
    return E if v == Q(Q(Q(u))) else None


def r5(u, v, op):
    return Q(('J', E, u)) if v == Q(u) else None


RULES = [r1, r2, r3, r4, r5]


def M(rules=None):
    return Model(rules if rules is not None else RULES)


if __name__ == '__main__':
    import qcheck
    qcheck.check(M, LAW, ['x', 'y'], ['z'])
