import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

J, E = 'J', 'E'
TJ, TE = 2, 3

# W3 variants are toggled by V3EXTRA / W2 tightness by V2TIGHT for the sweep.
V2TIGHT = True
V3EXTRA = False


def W1(u, v):
    if tg(v) == TJ and a2(v) == u and tg(a1(v)) == TE and a2(a2(a1(v))) == u:
        return a1(a1(v))
    return None


def W4(u, v):
    if (tg(v) == TJ and a2(v) == u and tg(a1(v)) == TJ
            and tg(a2(a1(v))) == TJ and a2(a2(a1(v))) == u):
        return a1(a1(v))
    return None


def W2(u, v):
    if tg(v) == TJ and a2(a1(v)) == a2(v) and ((not V2TIGHT) or tg(a1(v)) == TJ):
        return (E, u, v)
    return None


def W5(u, v):
    if tg(v) == TJ and a2(v) == u and tg(a1(v)) == TJ and a2(a1(v)) == a2(u):
        return a1(a1(v))
    return None


def W3(u, v):
    if tg(v) == TE and a2(v) == u and tg(a1(v)) == TJ:
        if V3EXTRA and not (tg(a2(a1(v))) == TE and a2(a2(a1(v))) == u):
            return None
        return a1(a1(v))
    return None


rules = [('W1', W1), ('W4', W4), ('W2', W2), ('W5', W5), ('W3', W3)]

if __name__ == '__main__':
    import _x13764_v5 as me
    for t2 in (True, False):
        for e3 in (False, True):
            me.V2TIGHT = t2; me.V3EXTRA = e3
            print('V2TIGHT=%s V3EXTRA=%s' % (t2, e3), end='  ')
            f1, f2, f3 = validate(rules)
    print()
    me.V2TIGHT = True; me.V3EXTRA = False
    f1, f2, f3 = validate(rules)
    for lab, fs in (('exh', f1), ('deep', f2), ('coin', f3)):
        for (x, y, z) in fs[:3]:
            print('--- FAIL', lab)
            explain(rules, x, y, z)
