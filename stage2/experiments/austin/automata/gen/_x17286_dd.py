"""_x17286_dd.py -- construct the (A decoded, P decoded) cell of law 17286's chain by hand.
Random deep tests reach it only by an accident (1 in ~60,000)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
sys.setrecursionlimit(30000)
import closedform as cf
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 17286
law = normalise(parse_eq(catalog()[EQ]))
RULES = cf.Extractor(law).rules(exist=False)
g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def show(x, cap=45):
    if size(x) > cap: return '<sz%d>' % size(x)
    return 'g%d' % x[1] if x[0] == 'g' else '(%s*%s)' % (show(x[1], 9999), show(x[2], 9999))


def encB(p, w):
    """free value of z*(z*(p*z)) with z:=w; op(J(_,p), encB(p,w)) = p by R1"""
    return J(w, J(w, J(p, w)))


def chain(rules, x, y, z):
    C = cf.Closed(law, rules)
    A = C.op(y, x); P = C.op(x, z); Q = C.op(z, P); B = C.op(z, Q); top = C.op(A, B)
    cell = ''.join('D' if b else 'f' for b in (A != J(y, x), P != J(x, z), Q != J(z, P), B != J(z, Q)))
    return top, cell, (A, P, Q, B)


def sem(x, y, z):
    F = fm.Free(law)
    A = F.op(y, x); P = F.op(x, z); Q = F.op(z, P); B = F.op(z, Q); top = F.op(A, B)
    return top, len(F.conflicts)


print('== generic (A dec, P dec) instance ==')
# A = op(y,x) decodes to pa via R1  =>  y = J(qy,pa), x = encB(pa, wa)
# P = op(x,z) decodes to px via R1  =>  x = J(_,px)  (px = a2 x = J(wa,J(pa,wa))), z = encB(px, w)
pa = g(5); wa = g(6); qy = g(7); w = g(8)
y = J(qy, pa)
x = encB(pa, wa)                     # = J(wa, J(wa, J(pa,wa)))
px = x[2]                            # a2 x = J(wa, J(pa,wa))
z = encB(px, w)
top, cell, (A, P, Q, B) = chain(RULES, x, y, z)
print('x =', show(x), 'sz', size(x))
print('y =', show(y))
print('z =', show(z), 'sz', size(z))
print('A =', show(A), ' P =', show(P), ' Q =', show(Q), ' B =', show(B))
print('cell =', cell, ' top =', show(top), ' want', show(x), '->', 'OK' if top == x else '**FAIL**')
st, nc = sem(x, y, z)
print('SEMANTIC top =', show(st), 'ok=', st == x, 'conflicts=', nc)

print()
print('== variations ==')
for name, (pa, wa, qy, w) in [
        ('gens', (g(5), g(6), g(7), g(8))),
        ('pa=J', (J(g(5), g(9)), g(6), g(7), g(8))),
        ('wa=J', (g(5), J(g(6), g(9)), g(7), g(8))),
        ('w=J', (g(5), g(6), g(7), J(g(8), g(9)))),
        ('qy=J', (g(5), g(6), J(g(7), g(9)), g(8)))]:
    y = J(qy, pa); x = encB(pa, wa); px = x[2]; z = encB(px, w)
    top, cell, _ = chain(RULES, x, y, z)
    st, nc = sem(x, y, z)
    print('%-8s cell=%s closed=%s semantic=%s conflicts=%d' %
          (name, cell, 'OK' if top == x else 'FAIL', 'OK' if st == x else 'FAIL', nc))
