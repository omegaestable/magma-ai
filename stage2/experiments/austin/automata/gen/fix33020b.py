"""fix33020b.py : the REFINED repair of the 33020/12883 rule set (R4 recomputed s2 = x*(y*x) at a measure that can
exceed msr(y, J s3 y) when sz x > sz s3 -- instance I4 -- so its firing conditions are inlined instead: R4a = s2 fired
through R2full, R4b = s2 fired through R3full; every inlined product has both arguments inside y, hence gate-safe).
Run: python gen/fix33020b.py [N]
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[12883]))

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
X = A1(A1(V)); Z = A1(A2(A1(V))); S1 = OP(U, X)
R2f = ([('TG', V), ('TG', A1(V)), ('TG', A2(A1(V))), ('EQ', U, A2(V)),
        ('OPEQ', S1, A2(A2(A1(V)))), ('OPEQ', OP(Z, A2(A2(A1(V)))), A2(A1(V))),
        ('OPEQ', OP(X, A2(A1(V))), A1(V)), ('OPEQ', OP(A1(V), U), V)], X, 'R2full')
R3f = ([('TG', V), ('TG', A1(V)), ('EQ', U, A2(V)), ('TG', S1),
        ('OPEQ', OP(A2(S1), S1), A2(A1(V))), ('OPEQ', OP(X, A2(A1(V))), A1(V)), ('OPEQ', OP(A1(V), U), V)], X, 'R3full')
XU = A2(A1(U))
R4full = ([('TG', V), ('EQ', U, A2(V)), ('TG', U), ('TG', A1(U)), ('TG', A1(A1(U))), ('TG', A2(U)),
        ('EQ', A1(V), A1(A1(A1(U)))), ('EQ', A1(V), A2(A2(U))),
        ('OPEQ', OP(U, XU), JJ(U, XU)), ('OPEQ', OP(XU, JJ(U, XU)), A1(U)), ('OPEQ', OP(XU, A1(U)), A1(V)), ('OPEQ', OP(A1(V), U), V)], XU, 'R4full')
# s2 = x*(y*x) fired to y.1 through R2full at (x, J y x), inlined
R4a = ([('TG', V), ('EQ', U, A2(V)), ('TG', U), ('TG', A1(U)), ('TG', A2(U)),
        ('OPEQ', OP(U, XU), JJ(U, XU)),                       # s1 = y*x free
        ('OPEQ', OP(XU, A1(U)), A2(A2(U))),                   # R2full@(x, J y x): op(x, y.1) == y.2.2
        ('OPEQ', OP(A1(A2(U)), A2(A2(U))), A2(U)),            #                    op(y.2.1, y.2.2) == y.2
        ('OPEQ', OP(A1(U), A2(U)), U),                        #                    op(y.1, y.2) == y
        ('OPEQ', OP(XU, A1(U)), A1(V)),                       # s3 = x*s2 == v.1 (any firing type)
        ('OPEQ', OP(A1(V), U), V)], XU, 'R4a')                # s4 = s3*y free
# s2 = x*(y*x) fired to y.1 through R3full at (x, J y x), inlined
S3 = OP(XU, A1(U))
R4b = ([('TG', V), ('EQ', U, A2(V)), ('TG', U), ('TG', A1(U)),
        ('OPEQ', OP(U, XU), JJ(U, XU)),
        ('TG', S3), ('OPEQ', OP(A2(S3), S3), A2(U)),          # R3full@(x, J y x): J?op(x, y.1) & op(op(x,y.1).2, op(x,y.1)) == y.2
        ('OPEQ', OP(A1(U), A2(U)), U),
        ('OPEQ', S3, A1(V)), ('OPEQ', OP(A1(V), U), V)], XU, 'R4b')
REFINED = [R2f, R3f, R4a, R4b]

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t): return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))
y1 = J(J(g(0), J(g(2), J(g(1), g(0)))), g(1))
cy = J(y1, J(g(2), g(0)))
I1 = {'x': g(1), 'y': J(y1, J(g(2), J(g(1), y1))), 'z': g(1)}
I2 = {'x': g(1), 'y': cy, 'z': g(1)}
x3 = J(g(1), J(g(1), J(g(0), g(1))))
I3 = {'x': x3, 'y': J(g(0), g(1)), 'z': x3}
xb = J(g(1), g(1)); s2b = J(J(g(0), J(g(2), J(xb, g(0)))), xb)
I4 = {'x': xb, 'y': J(s2b, J(g(2), g(0))), 'z': xb}                  # sz x = 3 > sz s3 = 1: R4full's gate blocks
I5 = {'x': cy, 'y': J(J(g(0), cy), J(g(2), g(1))), 'z': cy}          # s3 = cy*(J g0 cy) fires through R4 itself (type B)

def which_rule(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return tag
    return 'free'
def trace(C, R, s):
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(y, x); s2 = C.op(z, s1); s3 = C.op(x, s2); s4 = C.op(s3, y); T = C.op(y, s4)
    steps = [('s1', y, x), ('s2', z, s1), ('s3', x, s2), ('s4', s3, y), ('T', y, s4)]
    return ' | '.join('%s:%s' % (n, which_rule(C, R, a, b)) for n, a, b in steps), T == x

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
for name, R in (('R2full,R3full,R4full', [R2f, R3f, R4full]), ('REFINED R2full,R3full,R4a,R4b', REFINED)):
    C = cf.Closed(law, R)
    print('\n==', name)
    for iname, s in (('I1', I1), ('I2', I2), ('I3', I3), ('I4', I4), ('I5', I5)):
        print('  ', iname, trace(C, R, s))
    tot = nf = 0; t0 = time.time(); shown = 0; smallest = None
    for seed in (11, 12, 13, 14, 21, 22):
        C = cf.Closed(law, R)
        tested, fails = cf.deep_tests(C, law, N, 120, seed)
        tot += tested; nf += len(fails)
        for s, l in fails:
            if l == 'recursion': continue
            if shown < 2: print('   deep fail sizes', {k: size(t) for k, t in s.items()}, trace(C, R, s)[0]); shown += 1
            if smallest is None or sum(size(t) for t in s.values()) < smallest[0]: smallest = (sum(size(t) for t in s.values()), s)
    print('   deep tests', tot, 'fails', nf, 'secs', round(time.time() - t0, 1))
    tot = nf = 0; t0 = time.time(); shown = 0
    for seed in (7, 8, 9):
        C = cf.Closed(law, R)
        tested, fails = fz.fuzz(C, law, R, N, seed=seed)
        tot += tested; nf += len(fails)
        for s, l in fails:
            if l == 'recursion': continue
            if shown < 2: print('   fuzz fail sizes', {k: size(t) for k, t in s.items()}, trace(C, R, s)[0]); shown += 1
            if smallest is None or sum(size(t) for t in s.values()) < smallest[0]: smallest = (sum(size(t) for t in s.values()), s)
    print('   structured fuzz', tot, 'fails', nf, 'secs', round(time.time() - t0, 1))
    if smallest is not None:
        s = smallest[1]
        print('   smallest failure: x=%s y=%s z=%s' % (show(s['x']), show(s['y']), show(s['z'])))
        print('      ', trace(C, R, s)[0])
if '--rules' in sys.argv:
    for r in REFINED: print(cf.show_rule(r))
