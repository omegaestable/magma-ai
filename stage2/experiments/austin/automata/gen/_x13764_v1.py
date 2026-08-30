import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

J, E = 'J', 'E'
TJ, TE = 2, 3


def W1(u, v):
    # v = J (E x B) u  with  a2 B = u        -> x        [the decode]
    if tg(v) == TJ and a2(v) == u and tg(a1(v)) == TE and a2(a2(a1(v))) == u:
        return a1(a1(v))
    return None


def W2(u, v):
    # v = J w q  with a2 w = q               -> E u v    [C = x * B]
    if tg(v) == TJ and a2(a1(v)) == a2(v):
        return (E, u, v)
    return None


def W3(u, v):
    # v = E (J x _) u                        -> x        [derailed final, y = J w q]
    if tg(v) == TE and tg(a1(v)) == TJ and a2(v) == u:
        return a1(a1(v))
    return None


rules = [('W1', W1), ('W2', W2), ('W3', W3)]

if __name__ == '__main__':
    f1, f2, f3 = validate(rules)
    for lab, fs in (('exh', f1), ('deep', f2), ('coin', f3)):
        for (x, y, z) in fs[:2]:
            print('--- FAIL', lab)
            explain(rules, x, y, z)
