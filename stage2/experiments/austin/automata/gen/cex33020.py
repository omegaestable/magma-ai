"""cex33020.py : is `theorem law` in gen/rec33020.lean provable?  The skeleton's op models the L-form law 12883
(x = y * ((x * (z * (y * x))) * y)); the R-form law 33020 is served by op flipped, so `law` is the L-form statement.

NOTE gen/chk33020.py tests catalog()[33020] (the R-form text) against the L-form op, hence its 3000/3000 fails is
an orientation bug of the checker, not evidence.  This script tests against 12883, which is what `law` states.

Hand instances (see the report): R1 [free] fires on v = J (J x' (J z' (J u x'))) u whenever the SHAPE matches, without
checking that the inner product J u x' is op(u, x').  When x' itself encodes something by u, op(u, x') != J u x' and
R1 decodes a term that is not an encoding, after which the outer decode has no rule.
Run: python gen/cex33020.py [N_fuzz]
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf
import fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq
src = open(os.path.join(HERE, 'chk33020.py'), encoding='utf-8').read()
exec(src[src.index('rules = '):src.index('C = cf.Closed')])
lawL = normalise(parse_eq(catalog()[12883]))
lawR = normalise(parse_eq(catalog()[33020]))
print('L-form law 12883 normalised:', lawL)
print('R-form law 33020 normalised:', lawR)
for r in rules: print(' ', cf.show_rule(r))

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else 'J(%s, %s)' % (show(t[1]), show(t[2]))
def lean(t):
    return '(g %d)' % t[1] if t[0] == 'g' else '(J %s %s)' % (lean(t[1]), lean(t[2]))

def which_rule(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None: return 'R%d[%s]' % (i + 1, tag)
    return 'free'

def trace(C, R, s):
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(y, x); s2 = C.op(z, s1); s3 = C.op(x, s2); s4 = C.op(s3, y); T = C.op(y, s4)
    steps = [('s1=y*x', y, x, s1), ('s2=z*s1', z, s1, s2), ('s3=x*s2', x, s2, s3), ('s4=s3*y', s3, y, s4), ('T=y*s4', y, s4, T)]
    return ' | '.join('%s:%s->%s' % (n, which_rule(C, R, a, b), show(r)) for n, a, b, r in steps), T == x, T

# instance 1: y1 = T(g0,g1,g2) evaluated freely (encodes g0 by g1); y = J y1 (J g2 (J g1 y1)) has the R1 shape for
# u = g1 but J g1 y1 != op(g1, y1) = g0
y1 = J(J(g(0), J(g(2), J(g(1), g(0)))), g(1))
I1 = {'x': g(1), 'y': J(y1, J(g(2), J(g(1), y1))), 'z': g(1)}
# instance 2: x'' = y1 again; y = J x'' (J g2 g0) = the genuine encoding shape with the inner product decoded;
# s2 = x'' (R2, correct), s3 = op(g1, x'') = g0 fires, s4 = J g0 y and no rule decodes (y, J g0 y)
I2 = {'x': g(1), 'y': J(y1, J(g(2), g(0))), 'z': g(1)}

C = cf.Closed(lawL, rules)
for name, s in (('I1', I1), ('I2', I2)):
    tr, ok, T = trace(C, rules, s)
    print('\n%s: x=%s  y=%s  z=%s' % (name, show(s['x']), show(s['y']), show(s['z'])))
    print('   ', tr)
    print('    law holds:', ok, '  T =', show(T))
    print('    lean: x := %s\n          y := %s\n          z := %s' % (lean(s['x']), lean(s['y']), lean(s['z'])))

# the correctly oriented deep tests (what chk33020.py should have run) and the structured fuzz
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
t0 = time.time()
C = cf.Closed(lawL, rules)
tested, fails = cf.deep_tests(C, lawL, N, 120, 11)
print('\ndeep tests vs 12883 (seed 11):', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
for s, l in fails[:3]:
    print('   fail sizes x,y,z =', size(s['x']), size(s['y']), size(s['z']), '->', trace(C, rules, s)[0])
t0 = time.time()
C = cf.Closed(lawL, rules)
tested, fails = fz.fuzz(C, lawL, rules, N, seed=7)
print('structured fuzz vs 12883 (seed 7):', tested, 'fails', len(fails), 'secs', round(time.time() - t0, 1))
shown = 0
for s, l in fails:
    if shown >= 3: break
    if l == 'recursion': continue
    print('   fail sizes x,y,z =', size(s['x']), size(s['y']), size(s['z']), '->', trace(C, rules, s)[0]); shown += 1
# the smallest fuzz failure, for the report
best = None
for s, l in fails:
    if l == 'recursion': continue
    tot = sum(size(t) for t in s.values())
    if best is None or tot < best[0]: best = (tot, s)
if best is not None:
    s = best[1]
    print('smallest fuzz failure: x=%s y=%s z=%s' % (show(s['x']), show(s['y']), show(s['z'])))
    print('   ', trace(C, rules, s)[0])
