"""Does the SEMANTIC free model of law 38316 hold on the counterexample instance?"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import freemodel as fm, leangen
from freemodel import normalise, catalog, size, Free
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
F = Free(law)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

z, y1, W3, A1 = g(2), g(0), g(1), g(3)
W2 = J(W3, y1); w = J(z, W2); y = J(y1, J(w, z)); A = J(A1, z); q = J(y, A); x = J(q, y)
s = {'x': x, 'y': y, 'z': z}
A_pat, B_pat = law[1]
try:
    lhs = F.op(F.ev(A_pat, s), F.ev(B_pat, s))
    print('semantic law holds on the instance?', lhs == x, 'size', size(lhs))
    if lhs != x:
        print('lhs =', sh(lhs))
except Exception as e:
    print('semantic evaluation raised', type(e).__name__, e)

# chain values
a = F.op(z, x); b = F.op(y, a); c = F.op(b, y); d = F.op(x, c); top = F.op(y, d)
for nm, t in (('a', a), ('b', b), ('c', c), ('d', d), ('top', top)):
    print(' %-3s size %-4d %s' % (nm, size(t), sh(t) if size(t) < 40 else '<big>'))
print('x =', sh(x))
