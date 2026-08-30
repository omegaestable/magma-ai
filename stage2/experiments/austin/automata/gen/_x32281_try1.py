"""Hand-designed small rule sets for 32281.

Law modelled by op (dualised L-form):   x = Y * ((Y * ((x*Z)*Z)) * Z)
chain:  s1 = x*Z ; s2 = s1*Z ; s3 = Y*s2 ; s4 = s3*Z ; op(Y, s4) = x

If s4 and s3 are free:  v = J (J u s2) Z,  so Z = v.2, s2 = v.1.2.
  * s2 free, s1 free  -> x = v.1.2.1.1                       (R1, "FFFF")
  * s1 or s2 decoded  -> x is the DECODER of a reading with encoding Z,
                         so (level 0) x = Z.1.1 = v.2.1.1, verified by
                         op(op(x,Z),Z) = s2                  (R2)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf

S3 = A1(V)          # s3 (when s4 free)
ZZ = A2(V)          # Z
S2 = A2(A1(V))      # s2 (when s3 free)
S1 = A1(S2)         # s1 (when s2 free)

R1 = ([TG(V), TG(S3), EQ_(U, A1(S3)), TG(S2), TG(S1),
       EQ_(A2(S1), A2(S2)), EQ_(A2(S1), ZZ)],
      A1(S1), 'free')

X2 = A1(A1(ZZ))     # x = Z.1.1
R2 = ([TG(V), TG(S3), EQ_(U, A1(S3)), TG(ZZ), TG(A1(ZZ)),
       OPEQ(OP(OP(X2, ZZ), ZZ), S2)],
      X2, 'decZ')

if __name__ == '__main__':
    for r in (R1, R2):
        print(cf.show_rule(r))
    print()
    report(LAW, [R1], seeds=(3,), N=800, NF=3000, tag='R1     ')
    report(LAW, [R1, R2], seeds=(3,), N=800, NF=3000, tag='R1+R2  ')
    report(LAW, [R1, R2], seeds=(3, 4, 5), N=3000, NF=12000, tag='R1+R2 FULL')
