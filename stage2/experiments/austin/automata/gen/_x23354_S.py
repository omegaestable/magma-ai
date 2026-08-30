"""Is  op u v decoded -> sz(op u v) < sz u  really true?  Construct a big-payload R3 decode."""
import sys
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
u = J(g0, J(J(g0, g0), g0))
for Wbig in [g0, J(g0, g1), J(J(g1, g1), J(g1, J(g1, g1))), J(J(J(g1,g1),J(g1,g1)), J(J(g1,g1),J(g1,g1)))]:
    A = J(g0, J(g0, Wbig))
    v = J(A, J(A, g0))
    r = C.op(u, v)
    print('sz u=%d  sz(a1 v)=%d  rule=%d  op(u,v)=%s  == a1 v? %s   S holds? %s'
          % (size(u), size(A), which(u, v), sh(r)[:60], r == A, size(r) < size(u) if r != J(u, v) else 'free'))
    print('   inner op(a2 u, a1 v) =', sh(C.op(u[2], A))[:60], ' want a1 u =', sh(u[1]), 'rule', which(u[2], A))
