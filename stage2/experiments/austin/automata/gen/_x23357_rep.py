"""Repair for law 23357  x = ((y*x)*y)*(x*(y*z))   (both-compound; L-side A = (y*x)*y, R-side B = x*(y*z)).

The generated 9-rule package leaves 5 `value:exh9/1` failures, all in the **Bs** mode (the whole
right node B = x*(y*z) is decoded, so `v` is a payload and neither x nor the inner product B1 = y*z
is readable from `v`).  In that mode the rule has to certify

        exists z.  op(x, op(y, z)) = v                                              (*)

with u = J (J y x) y giving y = u.1.1 = u.2 and x = u.1.2.  The generated R4/R5 discharge (*) only by
the sufficient condition `y = v` (then C := op(y,z) can be made literally the required encoding).
The two missing ways to satisfy (*) are the EXISTENTIAL DECODER: `z` is unconstrained, so any
C in Range(op(y, .)) is admissible, and Range(op(y,.)) has two more elements than `J y _`:

  NA  y = J (J y3 C) y3   ==>  C = y.1.2 is in Range(op(y,.))  [take z := J C (J y3 zz); R1 fires at
      (y,z) and returns y.1.2].  C is COMPUTABLE from u, so the whole of (*) collapses to one guard
      `op(u.1.2, u.1.1.1.2) == v` and every way op(x,C) can decode is covered at once.
      -> fails #2 #3 #4 (there op(x,C) fires R1 resp. R4).

  NB  y = J p q  ==>  every C with op(q,C) = p is in Range(op(y,.))  [z := J C (J q zz), R6 fires].
      With q = x this is op(x,C) = p, which is (*) itself, so p = v; and such a C exists whenever x
      has the free A-shape J (J y'' v) y'' (take C := J v (J y'' zz), R1 fires at (x,C)).
      Hence the purely structural guard  y = J v x  &  x = J (J y'' v) y''.
      -> fails #0 #1.

Both new rules are appended (Closed.op fires the FIRST match, so nothing earlier is stolen).
NA's nested pair (x, C) is a pair of proper subterms of u, so its msr gate is always below msr u v.
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23357
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e)
EQ_ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)
OP = lambda a, b: ('OP', a, b)

u1 = A1(U)
u11 = A1(u1)          # y
u12 = A2(u1)          # x
u2 = A2(U)

TOP = [TG(U), TG(u1), EQ_(u11, u2)]

NA = (TOP + [TG(u11), TG(A1(u11)), EQ_(A1(A1(u11)), A2(u11)),
             OPEQ(OP(u12, A2(A1(u11))), V)],
      u12, 'Bs|ex:Qa')

NB = (TOP + [TG(u12), TG(A1(u12)), EQ_(A1(A1(u12)), A2(u12)), EQ_(V, A2(A1(u12))),
             TG(u11), EQ_(A1(u11), V), EQ_(A2(u11), u12)],
      u12, 'Bs|ex:Qb')


def base_rules():
    src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
               encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


# R12: the "b free, v decoded" hole found by gen/_x23357_gaps.py / _x23357_hunt.py.
# When op(x, b) decodes through rule 4/5 at (x, b), those rules force  b = a1 (a1 x) = a2 x,  so the
# inner product IS recoverable from u: z := a2 (a2 x), b := a2 x.  The guard then certifies the whole of
# (*) by computing it:  op(x, a2 x) == v, with a1 (a2 x) = y saying b really is a free product op(y, z).
NC = (TOP + [TG(A2(u12)), EQ_(A1(A2(u12)), u11),
             OPEQ(OP(u12, A2(u12)), V)],
      u12, 'Bs|ex:Qc')

_all = base_rules() + [NA, NB, NC]
# FINAL ORDER: every L-type rule (result a2 (a1 u), precondition tg u = 2 & tg (a1 u) = 2 &
# a1 (a1 u) = a2 u) before every R-type rule (result a1 v, precondition tg v = 2).  With that order
# "some L-branch condition holds" already forces op u v = a2 (a1 u), because every earlier branch
# returns the same value -- which is what makes the Lean `law` proof affordable.
# generated order: 0..4 = R1..R5 (L), 5..8 = R6..R9 (R), 9,10 = NA,NB (L), 11 = NC (L)
rules = [_all[i] for i in [0, 1, 2, 3, 4, 9, 10, 11, 5, 6, 7, 8]]

if __name__ == '__main__':
    for i, r in enumerate(rules):
        print('R%-2d' % (i + 1), cf.show_rule(r))
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    fails = [f for f in fails if f[1] != 'recursion']
    from collections import Counter
    print('run_tests value fails', len(fails), Counter(f[2] for f in fails))
    for f in fails[:6]:
        print('  ', f[2], f[0])
