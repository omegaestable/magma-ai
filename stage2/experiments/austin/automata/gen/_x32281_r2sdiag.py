import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf
from freemodel import size
ZZ = A2(V); X2 = A1(A1(ZZ)); T2 = OP(OP(X2, ZZ), ZZ)
R2s = ([TG(V), TG(ZZ), TG(A1(ZZ)), TG(A1(V)), EQ_(U, A1(A1(V))), OPEQ(T2, A2(A1(V)))], X2, 'dec3s')
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
for sd in (111, 222):
    C = cf.Closed(LAW, [R1, R2s])
    t, f = cf.deep_tests(C, LAW, 20000, 400, sd)
    print('seed', sd, 'tested', t, 'fails', len(f))
    for s, r in f:
        print('   kind', 'recursion' if r == 'recursion' else 'VALUE')
        print('   ', {k: sh(v)[:160] for k, v in s.items()})
        if r != 'recursion': print('    got', sh(r)[:160])
