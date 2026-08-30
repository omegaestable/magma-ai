"""32281: ONE recursive rule for the whole decoder descent.

For the pair (u, v) with  w := a2 v,  A := a1 v :
  R1 : the fully free reading                       x = a1 (a1 (a2 (a1 v)))
  R3 : x is the level-0 decoder of w                x = a1 (a1 w)
  R5 : x is a deeper decoder of w.  Then op x m = a1 w with
       m := op (op (a1 (a1 (a2 w))) (a2 w)) (a2 w)  (R3's own guard on the pair (x,w)),
       so (u, J (op u (op (a1 w) m)) m) is a reading of the SAME x with the
       strictly smaller parameter m  ->  x = op u (J (op u (op (a1 w) m)) m).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf

ZZ = A2(V)                       # w
W0 = A2(ZZ)                      # a2 w
B0 = A1(A1(W0))                  # a1 (a1 (a2 w))
MM = OP(OP(B0, W0), W0)          # m
S2R = OP(A1(ZZ), MM)             # op (a1 w) m
AR = OP(U, S2R)
VR = JJ(AR, MM)
RES = OP(U, VR)

R5 = ([TG(V), TG(ZZ), TG(W0), TG(A1(W0)),
       OPEQ(OP(U, OP(OP(RES, ZZ), ZZ)), A1(V))],
      RES, 'rec')

RULES = [R1, R3, R5]

if __name__ == '__main__':
    for r in RULES:
        print(cf.show_rule(r))
    report(LAW, RULES, seeds=(3, 4, 5), N=2000, NF=8000, tag='R1+R3+R5 [3,4,5]')
    for sd in (101, 202):
        C = cf.Closed(LAW, RULES)
        t, f = cf.deep_tests(C, LAW, 20000, 400, sd)
        print('deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)
