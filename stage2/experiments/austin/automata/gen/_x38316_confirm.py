"""Independent confirmation that the 10-rule repaired model for 38316 is FALSE on the hunt instance."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
print('law', law)
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

z, y1, W3, A1 = g(2), g(0), g(1), g(3)
W2 = J(W3, y1); w = J(z, W2); y = J(y1, J(w, z)); A = J(A1, z); q = J(y, A); x = J(q, y)
s = {'x': x, 'y': y, 'z': z}
A_pat, B_pat = law[1]
for name, rules in (('10-rule', ALL),
                    ('5-rule V0', [r for r in ALL if r[2].startswith('V0')])):
    C = cf.Closed(law, rules)
    lhs = C.op(C.evp(A_pat, s), C.evp(B_pat, s))
    print('%-10s  evp law value == x ?  %s   (sizes: x=%d lhs=%d)' % (name, lhs == x, size(x), size(lhs)))
    # also check the semantic free model on the same instance
print('x =', sh(x))
print('y =', sh(y))
print('z =', sh(z))
