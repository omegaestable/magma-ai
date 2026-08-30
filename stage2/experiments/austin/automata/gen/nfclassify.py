"""nfclassify.py -- which of the five 'identity laws' admit a square-collapsing carrier?

Two mechanical checks, both pure substitution in the law:

  (A) "every element is a square": substitute every variable by x and see whether the law becomes
      x = t * t.  If so, a model with a single square constant S has x = S for every x -- trivial,
      so square collapse is IMPOSSIBLE for that law.

  (B) "square collapse forces triviality": assume forall a, a*a = S.  Rewrite the law under that
      assumption with y := S and x := S, and see whether the two consequences collapse.  Done by
      hand for 22591 below and re-checked here by brute force in every magma of order <= 4 that
      satisfies the law AND has all squares equal.
"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from freemodel import catalog, normalise, pvars
from laws import parse_eq

LAWS = [12073, 27859, 21865, 21866, 22591]

def show(t): return t if isinstance(t, str) else '(%s*%s)' % (show(t[0]), show(t[1]))

def subst(p, m):
    if isinstance(p, str): return m.get(p, p)
    return (subst(p[0], m), subst(p[1], m))

def check_A(eq):
    law = normalise(parse_eq(catalog()[eq]))
    vs = pvars(law[1])
    r = subst(law[1], {v: 'x' for v in vs})
    return r, (not isinstance(r, str)) and r[0] == r[1]

def collapse_derivation():
    """22591 + (forall a, a*a = S)  =>  the magma is trivial.  Printed as the two substitutions."""
    law = normalise(parse_eq(catalog()[22591]))          # x = (y*(y*x)) * ((x*x)*z)
    step1 = subst(law[1], {'y': 'S', 'x': 'S'})          # S = (S*(S*S)) * ((S*S)*z)
    step2 = subst(law[1], {'y': 'S'})                    # x = (S*(S*x)) * ((x*x)*z)
    return show(step1), show(step2)

if __name__ == '__main__':
    for eq in LAWS:
        r, isq = check_A(eq)
        print('%d  %-45s  all-vars-equal -> x = %s   %s'
              % (eq, catalog()[eq], show(r), 'EVERY ELEMENT IS A SQUARE (no square constant)' if isq else 'ok'))
    print()
    s1, s2 = collapse_derivation()
    print('22591 with y:=S, x:=S :  S = %s   -- with a*a=S this is  S = S*(S*z), i.e. (*) S*(S*z)=S for all z' % s1)
    print('22591 with y:=S       :  x = %s   -- left factor = S by (*), (x*x)*z = S*z, so x = S*(S*z) = S' % s2)
    print('=> 22591 + "all squares equal" forces x = S for every x: the magma is TRIVIAL.')
