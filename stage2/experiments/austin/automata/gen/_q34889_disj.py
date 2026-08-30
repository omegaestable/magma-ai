"""Are DEC and SELFE ever simultaneously applicable?  And does SELFE only ever fire with tg(a1 v) != 2?"""
import sys, os, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import E, sz, show, terms_upto
from q34889 import M, J, msr

Mo = M()

def dec_app(u, v):
    if u == v: return False
    m = msr(u, v)
    if v[0] == 'J' and v[2] == E:
        w = v[1]
        if w[0] == 'J':
            a, b = w[1], w[2]
            if not (a == E and b == E) and msr(u, a) < m and Mo.op(u, a) == b: return True
    return False

def self_app(u, v):
    if u == v: return False
    m = msr(u, v)
    if v[0] == 'J' and v[2] == E:
        w = v[1]
        if u[0] == 'J' and u[1] == w and msr(E, w) < m and Mo.op(E, w) == u[2]: return True
    return False

pool = terms_upto(9, 2)
print('pool', len(pool))
both = []; selfe = []; sJ = []
n = 0
for u in pool:
    for v in pool:
        n += 1
        d, s = dec_app(u, v), self_app(u, v)
        if d and s: both.append((u, v))
        if s:
            selfe.append((u, v))
            if v[1][0] == 'J': sJ.append((u, v))
print('pairs', n, 'DEC&SELFE both applicable:', len(both), '| SELFE applicable:', len(selfe),
      '| of those with tg(a1 v)=2:', len(sJ))
for u, v in both[:5]: print('   BOTH u=%s v=%s' % (show(u), show(v)))
for u, v in sJ[:5]: print('   SELFE with J body u=%s v=%s' % (show(u), show(v)))
for u, v in selfe[:8]: print('   SELFE u=%s v=%s' % (show(u), show(v)))
