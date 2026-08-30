"""32281: add the s3-decoded rule (pattern DDDF)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2, S3, ZZ, S2, S1, X2
import closedform as cf

# s3 = op(u, s2) DECODED, s4 free:  v = J s3 Z,  x = Z.1.1, verify the whole chain
R3 = ([TG(V), TG(ZZ), TG(A1(ZZ)),
       OPEQ(OP(U, OP(OP(X2, ZZ), ZZ)), A1(V))],
      X2, 'dec3')

RULES = [R1, R2, R3]

if __name__ == '__main__':
    for r in RULES:
        print(cf.show_rule(r))
    report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag='R1+R2+R3 [3,4,5]')
    report(LAW, RULES, seeds=(77, 78), N=3000, NF=12000, tag='R1+R2+R3 [77,78]')
    for sd in (101, 202, 303, 404, 505):
        C = cf.Closed(LAW, RULES)
        t, f = cf.deep_tests(C, LAW, 20000, 300, sd)
        print('deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)
