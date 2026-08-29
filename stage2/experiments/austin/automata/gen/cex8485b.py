"""cex8485b.py : second hole class for gen/rec8485.lean (law 8485, x = y * (x * (((z*x)*y)*y))) and the
measure obstruction to repairing it.  key y = J g0 T with T = J (J (J g1 g0) g0) g0 (y encodes g0 by g0),
z = T, x = J (J (J g2 T) T) T.  Then z*x = J T x is free, (z*x)*y = g0 (y encodes g0 by J T x through
T = (J T x).1), ((z*x)*y)*y = g0, x*g0 free, and y * (J x g0) must return x.  Any rule that verifies
`op(J y.2 x, y) == y.1` needs a recursive call whose msr exceeds msr(y, J x g0)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk8485.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[8485]))
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
C = cf.Closed(law, rules); F = fm.Free(law)
def which_rule(u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'
def trace(M, s, rules_known):
    x, y, z = s['x'], s['y'], s['z']
    P = M.op(z, x); Q = M.op(P, y); R = M.op(Q, y); S = M.op(x, R); T = M.op(y, S)
    steps = [('P=z*x', z, x, P), ('Q=P*y', P, y, Q), ('R=Q*y', Q, y, R), ('S=x*R', x, R, S), ('T=y*S', y, S, T)]
    if rules_known:
        return ' | '.join('%s:%s(sz %d)' % (n, which_rule(a, b), size(r)) for n, a, b, r in steps), T == x
    return ' | '.join('%s:%s(sz %d)' % (n, 'free' if r == ('J', a, b) else 'DEC', size(r)) for n, a, b, r in steps), T == x
e = J(g(1), g(0)); T = J(J(e, g(0)), g(0)); y = J(g(0), T); z = T
gg = J(J(g(2), T), T); x = J(gg, T)
s = {'x': x, 'y': y, 'z': z}
print('sizes x,y,z =', size(x), size(y), size(z))
print('closed-form:', trace(C, s, True))
print('free-model :', trace(F, s, False))
# the verification a repaired rule would need at the last step, and the msr gate
v = J(x, g(0)); cand = J(y[2], x)
print('msr(y, v) =', cf.msr(y, v), ' msr(J y.2 x, y) =', cf.msr(cand, y), ' gate passes:', cf.msr(cand, y) < cf.msr(y, v))
print('free op(J y.2 x, y) =', F.op(cand, y), ' (should be y.1 = g0)')
