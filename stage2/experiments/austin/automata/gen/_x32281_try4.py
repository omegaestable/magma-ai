"""32281: level-1 relocation rule R4, then re-attack.

Hierarchy of decoder locations for the reading (x, Z):
  level 0 : x = a1 (a1 Z)                              -- R3 uses this
  level 1 : x = a1 (a1 M),  M = op (op (a1 (a1 (a2 Z))) (a2 Z)) (a2 Z)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2
from _x32281_try2 import R3
import closedform as cf

ZZ = A2(V)              # Z
Z0 = A2(ZZ)             # a2 Z
B0 = A1(A1(Z0))         # a1 (a1 (a2 Z))
MM = OP(OP(B0, Z0), Z0)  # M
X4 = A1(A1(MM))

R4 = ([TG(V), TG(ZZ), TG(Z0), TG(A1(Z0)), TG(MM), TG(A1(MM)),
       OPEQ(OP(U, OP(OP(X4, ZZ), ZZ)), A1(V))],
      X4, 'dec4')

RULES = [R1, R3, R4]

if __name__ == '__main__':
    for r in RULES:
        print(cf.show_rule(r))
    report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag='R1+R3+R4 [3,4,5]')
    for sd in (101, 202, 303):
        C = cf.Closed(LAW, RULES)
        t, f = cf.deep_tests(C, LAW, 20000, 300, sd)
        print('deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)
