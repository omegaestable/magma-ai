"""Trace one instance of law 38316 under a candidate rule set: chain products, firing rules,
and which structural conditions hold at the final pair.

usage: _x38316_diag.py <setname> [instance_index]
"""
import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
src = open(GEN + 'chkrep38316.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
name = sys.argv[1] if len(sys.argv) > 1 else 'cand'
if name == 'all':
    RULES = ALL
else:
    ns2 = {}; exec(open(GEN + '_x38316_rules_%s.py' % name, encoding='utf-8').read(), ns2); RULES = ns2['rules']
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None:
            return i
    return -1
def struct_hold(u, v):
    """rules whose non-OPEQ conditions hold"""
    out = []
    for i, (conds, xx, tag) in enumerate(C.rules):
        st = [c for c in conds if c[0] != 'OPEQ']
        if C.check(st, u, v):
            out.append(tag)
    return out

y = g(0)
z = J(J(g(0), g(0)), J(J(J(g(0), g(2)), J(J(g(1), g(0)), J(g(0), g(0)))), J(g(0), g(2))))
x = J(J(g(0), z), J(g(0), g(0)))

a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
print('x  =', sh(x))
print('y  =', sh(y))
print('z  =', sh(z))
for nm, (u, v) in (('a=op(z,x)', (z, x)), ('b=op(y,a)', (y, a)), ('c=op(b,y)', (b, y)),
                   ('d=op(x,c)', (x, c)), ('top=op(y,d)', (y, d))):
    r = C.op(u, v); i = which(u, v)
    print('%-12s rule %-3s size %-4d %s' % (nm, TAGS[i] if i >= 0 else 'free', size(r),
                                            sh(r) if size(r) < 60 else '<big>'))
print('expected top = x (size %d), got size %d, ok=%s' % (size(x), size(top), top == x))
print('struct-hold at top pair:', struct_hold(y, d))
print('a2 d      =', sh(C.ev(('A2', ('V',)), y, d)) if d[0] == 'J' else 'n/a')
print('a1 d      =', sh(d[1]) if d[0] == 'J' else 'n/a')
print('a1 y      =', sh(y[1]) if y[0] == 'J' else 'n/a (generator)')
