"""Evaluate the 23354 chain on the (II) instances found by _x23354_good.py, with the 3-rule model."""
import sys, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules4 = ns['rules']
NR = int(sys.argv[1]) if len(sys.argv) > 1 else 3
rules = rules4[:NR] if NR == 3 else rules4
C = cf.Closed(law, rules)

def sh(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s*%s)' % (sh(t[1]), sh(t[2]))

def which(u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None: return i
    return -1

g0 = ('g', 0); g1 = ('g', 1); g2 = ('g', 2)
J = lambda a, b: ('J', a, b)
x = J(g0, J(J(g0, g0), g0))
z = J(J(g0, J(g0, g0)), J(J(g0, J(g0, g0)), g0))
for y in [g0, g1, J(g0, g1), J(g1, g0), x, z, J(J(g0,g1),g0), J(J(g1,x),g1)]:
    W = C.op(y, x); U = C.op(W, y); F = C.op(x, z); V = C.op(x, F); root = C.op(U, V)
    print('y=%-16s W=%-12s [%d] U free=%s [%d]  F=%-14s [%d] V=%-10s [%d] root=%-10s [%d] OK=%s'
          % (sh(y), sh(W), which(y, x), U == J(W, y), which(W, y), sh(F), which(x, z),
             sh(V), which(x, F), sh(root), which(U, V), root == x))
print('x =', sh(x))
