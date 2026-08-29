"""Coincidence-targeted check of the 7701 rule set (level-2 decoder holes).

x is drawn from terms that ENCODE a payload by z (so z*x decodes), then y is drawn
so that y encodes a payload by q2 = x*(z*x); the deep random tests never hit that.
"""
import sys, itertools
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq

law = normalise(parse_eq(catalog()[7701]))
exec(open('C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk7701.py').read().split('rules = ')[1].split('\nC = ')[0].join(['rules = ', '']))
C = cf.Closed(law, rules)
print('law', law)

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

# encode payload x0 (with helper z0) by u, the R1 shape: v = J u (J (J x0 (J z0 x0)) u)
def enc(u, x0, z0): return J(u, J(J(x0, J(z0, x0)), u))

rhs = law[1]
def run(x, y, z, label):
    s = {'x': x, 'y': y, 'z': z}
    r = C.evp(rhs, s)
    q1 = C.op(z, x); q2 = C.op(x, q1); q3 = C.op(q2, y); q4 = C.op(y, q3); q5 = C.op(y, q4)
    ok = (r == x)
    print('%s: %s' % (label, 'OK' if ok else 'FAIL'))
    if not ok:
        print('  x =', show(x)); print('  y =', show(y)); print('  z =', show(z))
        print('  z*x =', show(q1)); print('  x*(z*x) =', show(q2)); print('  (..)*y =', show(q3))
        print('  y*(..) =', show(q4)); print('  y*(y*(..)) =', show(q5))
    return ok

# hand-derived instance
z = g(0)
x = enc(z, g(1), g(2))           # x encodes g1 by z=g0, so z*x = g1
q2 = C.op(x, C.op(z, x))
y = enc(q2, g(3), g(4))          # y encodes g3 by q2
run(x, y, z, 'hand instance (x encodes by z; y encodes by x*(z*x))')

# systematic: small pool of generators, x from enc(z, ., .) and plain, y from enc(q2, ., .) and enc-of-enc
fails = 0; tested = 0
pool = [g(0), g(1), g(2)]
for z in pool:
    for x0 in pool:
        for z0 in pool:
            for x in [enc(z, x0, z0), J(z, J(J(x0, J(z0, x0)), z)), enc(z, J(x0, z0), z0)]:
                q1 = C.op(z, x); q2 = C.op(x, q1)
                for y0 in pool:
                    for yz in pool + [q2, x, z]:
                        for y in [enc(q2, y0, yz), enc(q2, enc(q2, y0, yz), yz), J(q2, J(J(y0, C.op(yz, y0)), q2)), enc(x, y0, yz), enc(z, y0, yz)]:
                            tested += 1
                            if not run(x, y, z, 'sys z=%s x=%s y=%s' % (show(z), show(x), show(y))):
                                fails += 1
                                if fails > 5: break
                        if fails > 5: break
                    if fails > 5: break
                if fails > 5: break
            if fails > 5: break
        if fails > 5: break
    if fails > 5: break
print('systematic tested', tested, 'fails', fails)
