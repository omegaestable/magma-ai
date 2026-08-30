"""Candidate model for law 13764 (= dual of 32294):  x = y * ((x * ((z*y)*y)) * y).

Carrier: free term algebra with generators `g n` and TWO binary constructors
`J` (free product) and `E` (the marked "C-node").  Accessors tg/a1/a2 are total.
`op` is an ordered if-chain of pure shape tests -- NO recursion, no msr gate.

Chain of the law:  A = z*y, B = A*y, C = x*B, D = C*y, and y*D must be x.
Generic (no coincidence):  A = J z y, B = J (J z y) y, C = E x B, D = J C y,
and W1 reads x back out of D.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

J, E = 'J', 'E'
TJ, TE = 2, 3


def W1(u, v):
    """v = J (E x B) u with a2 B = u   ->  x      [main decode]"""
    if tg(v) == TJ and a2(v) == u and tg(a1(v)) == TE and a2(a2(a1(v))) == u:
        return a1(a1(v))
    return None


def W4(u, v):
    """v = J (J x (J p u)) u           ->  x      [B stayed free]"""
    if (tg(v) == TJ and a2(v) == u and tg(a1(v)) == TJ
            and tg(a2(a1(v))) == TJ and a2(a2(a1(v))) == u):
        return a1(a1(v))
    return None


def W2(u, v):
    """v = J (J p q) q                 ->  E u v  [builds C]"""
    if tg(v) == TJ and tg(a1(v)) == TJ and a2(a1(v)) == a2(v):
        return (E, u, v)
    return None


def W5(u, v):
    """u self-decoding, v = J (J/E x (a2 u)) u  -> x   [A = B = a2 u branch]"""
    if (a1(a1(u)) == a2(u) and tg(v) == TJ and a2(v) == u
            and tg(a1(v)) != 1 and a2(a1(v)) == a2(u)):
        return a1(a1(v))
    return None


def W6(u, v):
    """u = J (E z R) z with a2 R = z ( so A = B = z ), and C = op(x,z) itself
    decoded, i.e. C = a1(a1 z) and x = a2 z.  Read x back out of u."""
    if (tg(u) == TJ and tg(a1(u)) == TE and a1(a1(u)) == a2(u)
            and a2(a2(a1(u))) == a2(u)
            and tg(v) == TJ and a2(v) == u and a1(v) == a1(a1(a2(u)))):
        return a2(a2(u))
    return None


def W3(u, v):
    """v = E (J x _) u                 ->  x      [y had the W2 shape]"""
    if tg(v) == TE and a2(v) == u and tg(a1(v)) == TJ:
        return a1(a1(v))
    return None


rules = [('W1', W1), ('W4', W4), ('W2', W2), ('W5', W5), ('W6', W6), ('W3', W3)]

if __name__ == '__main__':
    f1, f2, f3 = validate(rules)
    for lab, fs in (('exh', f1), ('deep', f2), ('coin', f3)):
        for (x, y, z) in fs[:3]:
            print('--- FAIL', lab)
            explain(rules, x, y, z)
