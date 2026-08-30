"""Law 12073:  x = y * (((y*x)*x) * (z*z))    -- quotient carrier with the square constant E."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qmod import Model, E, sz, show, run_tests, exhaustive, deep, closure_fuzz, critical_fuzz

LAW = ('x', ('y', ((('y', 'x'), 'x'), ('z', 'z'))))


def r_sq(u, v, op):
    if u == v:
        return E
    return None


def r_dec(u, v, op):
    # v = J(J(P, x), E) with op(u,x) = P   -> x
    if v[0] == 'J' and v[2] == E and v[1][0] == 'J':
        P, x = v[1][1], v[1][2]
        if op(u, x) == P:
            return x
    return None


RULES = [r_sq, r_dec]


def M():
    return Model(RULES)


if __name__ == '__main__':
    m = M()
    n, f = exhaustive(m, LAW, 7, 1)
    print('exh 7/1', n, len(f))
    for s, r in f[:6]:
        print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r)
