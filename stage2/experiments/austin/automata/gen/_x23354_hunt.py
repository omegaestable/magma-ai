"""Targeted hunt: x that has BOTH a left-decode and a right-decode (23354, 4-rule model).
Constructed from the structural analysis: x = J p (J p B) with RD*(a2 x) via Rb."""
import sys, itertools, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
C = cf.Closed(law, rules)
J = lambda a, b: ('J', a, b)
g = lambda i: ('g', i)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(xx, u, v)
            if r is not None: return i
    return -1

g0, g1 = g(0), g(1)
# x with a1 x = g0 and a2 x = J g0 (J (J g0 g0) g0)  (the (II) shape)
x = J(g0, J(g0, J(J(g0, g0), g0)))
# left decode: y = J (J p g0) p  fires R1 on (y, x)
y = J(J(g0, g0), g0)
# right decode: z = J w (J w t), w = J A (J A s), A = J g0 (J g0 r)
for r, s, t in itertools.product([g0, g1, J(g0, g1)], repeat=3):
    A = J(g0, J(g0, r))
    w = J(A, J(A, s))
    z = J(w, J(w, t))
    F = C.op(x, z)
    W = C.op(y, x)
    if which(x, z) < 0 or which(y, x) < 0:
        continue
    U = C.op(W, y); V = C.op(x, F); root = C.op(U, V)
    print('r=%s s=%s t=%s | W=%s [%d] F=%s [%d] U free=%s V free=%s root ok=%s [%d]'
          % (sh(r), sh(s), sh(t), sh(W), which(y, x), sh(F), which(x, z),
             U == J(W, y), V == J(x, F), root == x, which(U, V)))
    if root != x:
        print('   COUNTEREXAMPLE  x=%s' % sh(x)); print('   y=%s' % sh(y)); print('   z=%s' % sh(z))
        print('   got %s' % sh(root))
        break
