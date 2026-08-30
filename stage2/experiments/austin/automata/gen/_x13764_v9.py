"""Law 13764 model, rule set v9 (6 rules).  See _x13764_v8 for the narrative."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

J, E = 'J', 'E'
TJ, TE = 2, 3


def W1(u, v):
    """v = J (E x B) u, a2 B = u   ->  x"""
    if tg(v) == TJ and a2(v) == u and tg(a1(v)) == TE and a2(a2(a1(v))) == u:
        return a1(a1(v))
    return None


def W4(u, v):
    """v = J (J x (J p u)) u       ->  x"""
    if (tg(v) == TJ and a2(v) == u and tg(a1(v)) == TJ
            and tg(a2(a1(v))) == TJ and a2(a2(a1(v))) == u):
        return a1(a1(v))
    return None


def W2(u, v):
    """v = J (J p q) q             ->  E u v"""
    if tg(v) == TJ and tg(a1(v)) == TJ and a2(a1(v)) == a2(v):
        return (E, u, v)
    return None


def W5(u, v):
    """a1(a1 u) = a2 u, v = J C u with a2 C = a2 u   ->  a1 C"""
    if (a1(a1(u)) == a2(u) and tg(v) == TJ and a2(v) == u
            and tg(a1(v)) != 1 and a2(a1(v)) == a2(u)):
        return a1(a1(v))
    return None


def W6(u, v):
    """a1(a1 u) = a2 u, v = J C u with C = a1(a1(a2 u))  ->  a2 (a2 u)"""
    if (a1(a1(u)) == a2(u) and tg(v) == TJ and a2(v) == u
            and a1(v) == a1(a1(a2(u)))):
        return a2(a2(u))
    return None


def W3(u, v):
    """v = E (J x _) u             ->  x"""
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
