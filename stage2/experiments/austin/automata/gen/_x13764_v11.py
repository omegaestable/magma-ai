"""Law 13764 model, rule set v11 (5 rules; W5/W6 merged into one total branch).

  SD u  :=  a1 (a1 u) = a2 u          ("u is a self-decoder": the A-step on u
                                        returns a2 u, so A = B = a2 u)

  W1 : tg v = 2, a2 v = u, tg (a1 v) = 3, a2 (a2 (a1 v)) = u      -> a1 (a1 v)
  W4 : tg v = 2, a2 v = u, tg (a1 v) = 2, tg (a2 (a1 v)) = 2,
       a2 (a2 (a1 v)) = u                                          -> a1 (a1 v)
  W2 : tg v = 2, tg (a1 v) = 2, a2 (a1 v) = a2 v                   -> E u v
  W56: SD u, tg v = 2, a2 v = u ->  if a2 (a1 v) = a2 u then a1 (a1 v)
                                                        else a2 (a2 u)
  W3 : tg v = 3, a2 v = u, tg (a1 v) = 2                           -> a1 (a1 v)
  else J u v
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x13764_lab import *

J, E = 'J', 'E'
TJ, TE = 2, 3


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
    if tg(v) == TJ and tg(a1(v)) == TJ and a2(a1(v)) == a2(v):
        return (E, u, v)
    return None


def W56(u, v):
    if tg(u) != 1 and a1(a1(u)) == a2(u) and tg(v) == TJ and a2(v) == u:
        return a1(a1(v)) if a2(a1(v)) == a2(u) else a2(a2(u))
    return None


def W3(u, v):
    if tg(v) == TE and a2(v) == u and tg(a1(v)) == TJ:
        return a1(a1(v))
    return None


rules = [('W1', W1), ('W4', W4), ('W2', W2), ('W56', W56), ('W3', W3)]

if __name__ == '__main__':
    f1, f2, f3 = validate(rules)
    for lab, fs in (('exh', f1), ('deep', f2), ('coin', f3)):
        for (x, y, z) in fs[:3]:
            print('--- FAIL', lab)
            explain(rules, x, y, z)
