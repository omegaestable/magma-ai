"""Instrument the level-3 / descent instances: which rule fires at each chain product, and does
IMG (inimg (op z y) y) hold there?  (The earlier census missed the ROOT product C = J A Q.)"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
import q9663c as M
inimg, _lvl2, op = M.inimg, M._lvl2, M.op

def which(u, v):
    if v[0] == 'J':
        A, Q = v[1], v[2]
        if inimg(A, u):
            if Q[0] == 'J' and op(Q[1], u) == Q[2]: return 'W1'
            if u[0] == 'J' and u[1][0] == 'J' and _lvl2(u, Q, u[1][2]): return 'W2'
            if u[0] == 'J' and u[2][0] == 'J' and u[2][2][0] == 'J' and _lvl2(u, Q, u[2][2][2]): return 'W3'
    return 'free'

g0, g1 = G(0), G(1)
base = [g0, g1, J(g0, g0), J(g0, g1), J(g1, g0), J(g0, J(g0, g0)), J(J(g0, g0), g0)]
root = collections.Counter(); Az = collections.Counter(); imgbad = 0; n = 0
for A1 in base:
    for s in base[:4]:
        for t in base[:4]:
            x = J(s, J(A1, t))
            if not inimg(A1, x): continue
            for w2 in base[:4]:
                for A2 in base[:4]:
                    if not inimg(A2, x): continue
                    w_ = J(A2, J(w2, op(w2, x)))
                    y2 = J(A1, J(w_, op(w_, x)))
                    if op(x, y2) != w_ or op(x, w_) != w2: continue
                    for z in base[:4] + [x, y2]:
                        n += 1
                        P = op(x, y2); Q = op(x, P); A = op(z, y2); C = op(A, Q)
                        root[which(y2, C)] += 1
                        Az[which(z, y2)] += 1
                        if not inimg(A, y2): imgbad += 1
print('level-3 instances n=%d' % n)
print('  rule at the ROOT product op(y,C) :', dict(root))
print('  rule at op(z,y)                  :', dict(Az))
print('  IMG (inimg (op z y) y) counterexamples:', imgbad)
