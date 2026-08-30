"""Trace one assignment of 10222 under a chosen rule set.

python gen/_x10222_tr.py <ruleset> <x> <y> <z>
terms in a tiny syntax: 0/1/2 = g0/g1/g2 ; (a,b) as nested lists via eval of a python expr using G(n)/Jn.
Simpler: the assignments are hard-coded below by name.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, trace as tr
from freemodel import normalise, catalog, size
from laws import parse_eq

def g(n): return ('g', n)
def J(a, b): return ('J', a, b)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OP(a, b): return ('OP', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

law = normalise(parse_eq(catalog()[10222]))
X = cf.Extractor(law)
base = X.rules(exist=False, level2=False)
Aprime = ([TG(V), TG(A1(V)), EQ(U, A2(A1(V))), TG(A2(V)), EQ(U, A2(A2(V)))], A1(A1(V)), 'B10e')

SETS = {'base': base, 'base+Ae': base + [Aprime]}

a = g(0); s2 = J(a, a); z7 = J(s2, J(s2, a))
CASES = {
    'c1': dict(x=a, y=s2, z=z7),
    'c2': dict(x=a, y=s2, z=s2),
    'c3': dict(x=g(1), y=s2, z=s2),
}

which = sys.argv[1] if len(sys.argv) > 1 else 'base+Ae'
case = sys.argv[2] if len(sys.argv) > 2 else 'c2'
rules = SETS[which]; s = CASES[case]
print('ruleset %s (%d rules)  case %s' % (which, len(rules), {k: show(v) for k, v in s.items()}))
T = tr.Tracing(law, rules)
A, B = law[1]

def evt(p, ind='  '):
    if isinstance(p, str):
        return s[p]
    aa, bb = evt(p[0], ind), evt(p[1], ind)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(aa, bb)
    T.trace_on = False
    w = T.log[-1][2] if T.log else None
    print('%s%-34s = %s   [%s]' % (ind, str(p), show(r) if size(r) < 60 else '<size %d>' % size(r),
                                   'free' if w is None else 'R%d %s' % (w, rules[w][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('%s    GATE CUT %s sizes (%d,%d) vs (%d,%d)' % (ind, cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r

u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
w = T.log[-1][2] if T.log else None
print('  FINAL op(u,v) = %s   expected %s   [%s]' % (show(r) if size(r) < 60 else '<size %d>' % size(r),
                                                     show(s['x']), 'free' if w is None else 'R%d %s' % (w, rules[w][2])))
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('    GATE CUT %s sizes (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
ok = [i for i, (c, x2, t2) in enumerate(rules) if tr.struct_ok(T, c, u, v)]
print('  structural-hold rules:', ok, [rules[i][2] for i in ok])
