"""32281: recursive rule that reads the inner payload P off the FREE part of v.

At the outer pair (u,v) with w = a2 v, A = a1 v, the chain is
   P = op x w,  Q = op P w,  A = op u Q,  v = J A w.
If A and Q are free then P = a1 (a2 (a1 v)) is ACCESSIBLE, and w's own reading is
   w = J (op x m) (a2 w)   with   m = op (op P (a2 w)) (a2 w),
so x is the decoder of m -- one level shallower -- and
   x = op u (J (op u (op (a1 w) m)) m).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3           # level-0 decoder rule
from _x32281_try5 import R5           # recursion with m built from a1(a1(a2 w))
import closedform as cf

ZZ = A2(V)                 # w
W0 = A2(ZZ)                # a2 w
PACC = A1(A2(A1(V)))       # P  = a1 (a2 (a1 v))
MS = OP(OP(PACC, W0), W0)  # m
RES6 = OP(U, JJ(OP(U, OP(A1(ZZ), MS)), MS))

R6 = ([TG(V), TG(A1(V)), TG(A2(A1(V))), TG(ZZ), TG(W0),
       OPEQ(OP(U, OP(OP(RES6, ZZ), ZZ)), A1(V))],
      RES6, 'rec6')

if __name__ == '__main__':
    for name, RULES in (('R1+R3+R6   ', [R1, R3, R6]),
                        ('R1+R3+R5+R6', [R1, R3, R5, R6])):
        print('===', name)
        for r in RULES:
            print('   ', cf.show_rule(r))
        report(LAW, RULES, seeds=(3, 4), N=1500, NF=6000, tag=name)
