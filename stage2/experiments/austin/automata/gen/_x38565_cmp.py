"""_x38565_cmp.py -- closed-form vs semantic free model on the failing instance's chain."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'chk38565.py')
src = open(FILE, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
z = J(g(1), J(g(1), g(1)))
x = J(J(g(1), g(0)), J(g(1), J(g(1), g(0))))
y = J(J(z, J(x, z)), g(1))
s = {'x': x, 'y': y, 'z': z}

C = cf.Closed(law, rules)
F = fm.Free(law)


def ev(o, p):
    if isinstance(p, str):
        return s[p]
    return o.op(ev(o, p[0]), ev(o, p[1]))


A, B = law[1]
chain = [('x', 'z'), ('z', ('x', 'z')), (('z', ('x', 'z')), 'y'), ('y', (('z', ('x', 'z')), 'y')),
         ('y', ('y', (('z', ('x', 'z')), 'y')))]
for p in chain:
    cv = ev(C, p); fv = ev(F, p)
    tag = 'SAME' if cv == fv else '**DIFF**'
    print('%-46s closed=%s' % (str(p), show(cv) if size(cv) < 50 else '<sz %d>' % size(cv)))
    print('%-46s free  =%s   %s' % ('', show(fv) if size(fv) < 50 else '<sz %d>' % size(fv), tag))
print('expected x =', show(x))
# some extra probes
probes = [(z, J(z, J(x, z))), (J(g(1), g(1)), g(1))]
for (a, b) in probes:
    ca, fa = C.op(a, b), F.op(a, b)
    print('probe op(%s, %s): closed=%s free=%s %s' % (show(a) if size(a) < 30 else '<sz>',
          show(b) if size(b) < 40 else '<sz>', show(ca) if size(ca) < 40 else '<sz>',
          show(fa) if size(fa) < 40 else '<sz>', 'SAME' if ca == fa else '**DIFF**'))
