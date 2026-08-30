import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf
from freemodel import size

rules = gen_rules()
fails, real = report(LAW, rules, seeds=(3,), N=1500, NF=6000, tag='FULL26')

def sh(t):
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

C = cf.Closed(LAW, rules)
A, B = LAW[1]
# smallest failing instances
real.sort(key=lambda f: sum(size(v) for v in f[0].values()))
for s, r, kind, sd in real[:5]:
    print('---', kind, {k: size(v) for k, v in s.items()})
    for k, v in s.items():
        print('   ', k, '=', sh(v))
    print('    got', sh(r) if r != 'recursion' else r, ' expected x')
