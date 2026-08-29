"""cex8485.py : hand instance on which the shipped rules of gen/rec8485.lean may violate law 8485
x = y * (x * (((z * x) * y) * y)).  Take w = z*x free and y = w * (((q*w)*w)*w) (y encodes w by w),
so (z*x)*y = w and ((z*x)*y)*y = w: the outer product y * (x * w) must return x but no rule can
recover z (R4 reads z only through x.2.1.2, and x is a generator)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk8485.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
law = normalise(parse_eq(catalog()[8485]))
print('law', law)
def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
C = cf.Closed(law, rules)
def which_rule(u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'
def trace(s):
    x, y, z = s['x'], s['y'], s['z']
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R); T = C.op(y, S)
    return ' | '.join('%s:%s' % (n, which_rule(a, b)) for n, a, b in
                      [('P=z*x', z, x), ('Q=P*y', P, y), ('R=Q*y', Q, y), ('S=x*R', x, R), ('T=y*S', y, S)]), T == x, T
x = g(0); z = g(1); w = J(z, x); q = g(2)
y = J(w, J(J(J(q, w), w), w))
s = {'x': x, 'y': y, 'z': z}
print('closed-form trace:', trace(s))
F = fm.Free(law)
def ftrace(s):
    x, y, z = s['x'], s['y'], s['z']
    P = F.op(z, x); Q = F.op(P, y); R = F.op(Q, y); S = F.op(x, R); T = F.op(y, S)
    return [P, Q, R, S, T], T == x
print('free-model trace:', ftrace(s))
print('evp closed:', C.evp(law[1], s) == x, ' evp free:', F.ev(law[1], s) == x)
