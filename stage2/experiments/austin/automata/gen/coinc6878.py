import sys, os
sys.path.insert(0, 'C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
law = normalise(parse_eq(catalog()[6878]))
print('law rhs pattern:', law)
exec(open('C:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk6878.py').read().split('rules = ')[1].split('\nC = ')[0].join(['rules = ', '']))

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    return '(%s %s)' % (show(t[1]), show(t[2]))

def run(name, s):
    C = cf.Closed(law, rules)
    val = C.evp(law[1], s)
    ok = val == s['x']
    print('%s: %s' % (name, 'OK' if ok else 'FAIL'))
    for k in ('x', 'y', 'z'):
        print('   %s = %s' % (k, show(s[k])))
    if not ok:
        print('   T(x,y,z) = %s' % show(val))
        # trace the products
        zx = C.op(s['z'], s['x']); xy = C.op(s['x'], s['y'])
        print('   z*x = %s' % show(zx)); print('   x*y = %s' % show(xy))
        p = C.op(zx, xy); print('   (z*x)*(x*y) = %s' % show(p))
        q = C.op(s['y'], p); print('   y*(..) = %s' % show(q))
        r = C.op(s['y'], q); print('   y*(y*(..)) = %s' % show(r))
    return ok

# instance A: x is R1-shaped by z (x encodes x'' by z), y is R1-shaped by x (y encodes y'' by x)
z = g(0); zp = g(3); xpp = g(5); y1 = g(4); ypp = g(6)
x = J(z, J(J(zp, xpp), J(xpp, z)))
y = J(x, J(J(y1, ypp), J(ypp, x)))
run('A (x enc by z, y enc by x)', {'x': x, 'y': y, 'z': z})

# instance B: only y is R1-shaped by x (z*x free)
x = g(5)
y = J(x, J(J(y1, ypp), J(ypp, x)))
run('B (y enc by x only)', {'x': x, 'y': y, 'z': z})

# instance C: only x is R1-shaped by z
x = J(z, J(J(zp, xpp), J(xpp, z)))
y = g(7)
run('C (x enc by z only)', {'x': x, 'y': y, 'z': z})

# instance D: same as A but with z = y-ish coincidences: z = x
x = J(g(0), J(J(zp, xpp), J(xpp, g(0))))
y = J(x, J(J(y1, ypp), J(ypp, x)))
run('D (A with z := x)', {'x': x, 'y': y, 'z': x})
