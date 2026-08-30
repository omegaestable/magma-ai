import sys, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C = cf.Closed(law, rules)
J = lambda a, b: ('J', a, b); g = lambda i: ('g', i)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(xx, u, v)
            if r is not None: return i
    return -1
g0, g1 = g(0), g(1)
x = J(g0, J(g0, J(J(g0, g0), g0)))
y = J(J(g0, g0), g0)
print('x', sh(x), 'y', sh(y), 'which(y,x)', which(y, x), 'op(y,x)', sh(C.op(y, x)))
A = J(g0, J(g0, g0)); w = J(A, J(A, g0)); z = J(w, J(w, g0))
print('A', sh(A), 'w', sh(w))
print('op(a2 x, A) =', sh(C.op(x[2], A)), ' target a1 x =', sh(x[1]), 'which', which(x[2], A))
print('op(a2 x, w) =', sh(C.op(x[2], w)), 'which', which(x[2], w))
print('which(x,z)', which(x, z), 'op(x,z)', sh(C.op(x, z)))
# what does the R3 guard need at (x,z)?
print('a1 z', sh(z[1]), 'a1(a2 z)', sh(z[2][1]))
print('op(a2 x, a1 z) =', sh(C.op(x[2], z[1])), 'want a1 x =', sh(x[1]))
