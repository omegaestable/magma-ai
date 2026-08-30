"""_x33020_tr.py : print the full chain of the 12883 model on the hand instances, with every product's
value and the rule that fired, so the case structure of `theorem law` can be read off."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

cat = catalog(); orig = normalise(parse_eq(cat[33020]))
law = ('x', leangen.dual_pat(orig[1]))
src = open(os.path.join(HERE, 'repair33020', 'chk33020.py'), encoding='utf-8').read()
ns = {}
exec(src[src.index('rules = '):src.index('C = cf.Closed')], {'cf': cf}, ns)
rules = ns['rules']

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
y1 = J(J(g(0), J(g(2), J(g(1), g(0)))), g(1)); cy = J(y1, J(g(2), g(0)))
x3 = J(g(1), J(g(1), J(g(0), g(1)))); xb = J(g(1), g(1)); s2b = J(J(g(0), J(g(2), J(xb, g(0)))), xb)
INST = {'I2': {'x': g(1), 'y': cy, 'z': g(1)},
        'I4': {'x': xb, 'y': J(s2b, J(g(2), g(0))), 'z': xb},
        'I5': {'x': cy, 'y': J(J(g(0), cy), J(g(2), g(1))), 'z': cy}}

def which(C, u, v):
    for i, (conds, e, tag) in enumerate(rules):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d' % (i + 1)
    return 'free'

C = cf.Closed(law, rules)
for k, s in INST.items():
    x, y, z = s['x'], s['y'], s['z']
    s1 = C.op(y, x); s2 = C.op(z, s1); s3 = C.op(x, s2); s4 = C.op(s3, y); T = C.op(y, s4)
    print('===', k)
    print('  x  =', sh(x)); print('  y  =', sh(y)); print('  z  =', sh(z))
    for nm, a, b, r in (('s1', y, x, s1), ('s2', z, s1, s2), ('s3', x, s2, s3), ('s4', s3, y, s4), ('T ', y, s4, T)):
        print('  %s = op(%s, %s)\n       = %s   [%s]' % (nm, sh(a), sh(b), sh(r), which(C, a, b)))
    print('  T == x ?', T == x)
    print('  a1 y =', sh(y[1]) if y[0] == 'J' else '-', ' a2 y =', sh(y[2]) if y[0] == 'J' else '-')
    if y[0] == 'J' and y[1][0] == 'J':
        print('  a2(a1 y) =', sh(y[1][2]), '   == x ?', y[1][2] == x)
        print('  a1 y == s2 ?', y[1] == s2)
    if y[0] == 'J' and y[2][0] == 'J':
        print('  a2(a2 y) =', sh(y[2][2]), '   == s3 ?', y[2][2] == s3)
