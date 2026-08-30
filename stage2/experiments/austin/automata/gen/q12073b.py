"""Law 12073:  x = y * (((y*x)*x) * (z*z))

Carrier: g i | E | Q u | J u v      (E = the common square, Q = the "* E" tag, J = free product)
op:
  R1  u = v            -> E                     (all squares are ONE element: kills the z-dependence)
  R2  v = E            -> Q u
  R3  v = Q (J a b), op(u,b) = a  -> b          (decoder)
  R4..  repairs
  R5  otherwise        -> J u v
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = ['Q']
from qmod import Model, E, sz, show, exhaustive, deep, closure_fuzz, critical_fuzz

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
        if w[0] == 'J' and op(u, w[2]) == w[1]:
            return w[2]
    return None


def r4(u, v, op):
    # x = E case: the chain is  Q u, Q Q u, Q Q Q u  and the decoder must return E
    if v == Q(Q(Q(u))):
        return E
    return None


RULES = [r1, r2, r3, r4]


def M(rules=None):
    return Model(rules or RULES)


if __name__ == '__main__':
    import qmod
    for ms, g in ((7, 1), (9, 1), (6, 2), (5, 3)):
        n, f = exhaustive(M(), LAW, ms, g, limit=4000)
        seen = []
        for s, r in f:
            k = (show(s['x']), show(s['y']))
            if k not in [a for a, _ in seen]:
                seen.append((k, (s, r)))
        print('exh %d/%d  n=%d fails=%d  distinct(x,y)=%d' % (ms, g, n, len(f), len(seen)))
        for k, (s, r) in seen[:8]:
            print('   FAIL x=%s y=%s z=%s -> %s' % (show(s['x']), show(s['y']), show(s['z']),
                                                    show(r) if r != 'recursion' else r))
