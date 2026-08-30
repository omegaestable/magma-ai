"""_x38565_dd.py -- construct the (s1 decoded, s3 decoded) case of law 38565's chain by hand
and test candidate rule sets on it.  Random deep tests never reach it."""
import sys, os, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def encfree(a, b, c):
    """the free value of  b*(b*((c*(a*c))*b))  -- assumes all inner products free"""
    s1 = J(a, c); s2 = J(c, s1); s3 = J(s2, b)
    return J(b, s3)


# --- the instance ---
# op(x, z) decodes to x'' : z must be the free encoding with y:=x, x:=x'', z:=z''
x = g(0)
xpp = J(g(1), g(1))          # payload of the inner reading; a2 xpp = g1 != z, so P3 will fail
zpp = g(2)
z = encfree(xpp, x, zpp)     # = J x (J (J zpp (J xpp zpp)) x)


def build(rules):
    C = cf.Closed(law, rules)
    s1 = C.op(x, z)
    s2 = C.op(z, s1)
    return C, s1, s2


C0, s1, s2 = build([full[i] for i in (0, 1, 6)])
print('z  =', show(z))
print('s1 = op(x,z) =', show(s1), ' (want', show(xpp), ')')
print('s2 = op(z,s1) =', show(s2))
# op(s2, y) must decode: y = free encoding with y:=s2, x:=w, z:=z3
w = g(1)
z3 = g(2)
y = encfree(w, s2, z3)
print('y  = size', size(y))

SETS = {'A(3)': (0, 1, 6), 'A+10(4)': (0, 1, 6, 10), 'full(30)': tuple(range(30))}
for name, idx in SETS.items():
    rules = [full[i] for i in idx]
    C = cf.Closed(law, rules)
    a = C.op(x, z); b = C.op(z, a); c = C.op(b, y); d = C.op(y, c); top = C.op(y, d)
    print('%-9s s1=%s s1dec=%s  s3dec=%s  top=%s  %s' % (
        name, show(a) if size(a) < 20 else '<sz %d>' % size(a), a != J(x, z), c != J(b, y),
        show(top) if size(top) < 20 else '<sz %d>' % size(top),
        'OK' if top == x else '**FAIL**'))

F = fm.Free(law)
a = F.op(x, z); b = F.op(z, a); c = F.op(b, y); d = F.op(y, c); top = F.op(y, d)
print('semantic  top=%s  %s  conflicts=%d' % (show(top) if size(top) < 20 else '<sz %d>' % size(top),
                                              'OK' if top == x else '**FAIL**', len(F.conflicts)))
