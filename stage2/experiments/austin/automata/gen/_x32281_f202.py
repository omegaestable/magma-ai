import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1, R2
import closedform as cf
from freemodel import size

RULES = [R1, R2]
C = cf.Closed(LAW, RULES)
t, f = cf.deep_tests(C, LAW, 20000, 300, 202)
print('tested', t, 'fails', len(f))

def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

for s, r in f:
    print({k: size(v) for k, v in s.items()})
    for k, v in s.items():
        print('  ', k, '=', sh(v))
    print('   got', ('recursion' if r == 'recursion' else sh(r)))
    if r == 'recursion':
        continue
    x, Y, Z = s['x'], s['z'], s['y']   # LAW pattern ('x', ('z', (('z', (('x','y'),'y')), 'y')))
    s1 = C.op(x, Z); s2 = C.op(s1, Z); s3 = C.op(Y, s2); s4 = C.op(s3, Z); top = C.op(Y, s4)
    def fr(rr, a, b): return rr[0] == 'J' and rr[1] == a and rr[2] == b
    print('   pattern', ''.join('F' if fr(rr, a, b) else 'D' for rr, a, b in
                                ((s1, x, Z), (s2, s1, Z), (s3, Y, s2), (s4, s3, Z))))
    for nm, val in (('s1', s1), ('s2', s2), ('s3', s3), ('s4', s4), ('top', top)):
        print('   ', nm, '=', sh(val) if size(val) < 60 else '<size %d>' % size(val))
