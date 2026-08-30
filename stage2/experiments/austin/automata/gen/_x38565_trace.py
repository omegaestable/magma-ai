"""_x38565_trace.py -- trace a chosen instance of law 38565 under a chosen rule set.
usage: python gen/_x38565_trace.py [rulesfile.py]   (rules literal taken from the file)
The instance is the seed-991 deep-test failure of the 3-rule minimised set."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
import trace as tr
import leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
FILE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'chk38565.py')
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open(FILE, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)

z = J(g(1), J(g(1), g(1)))
x = J(J(g(1), g(0)), J(g(1), J(g(1), g(0))))
y = J(J(z, J(x, z)), g(1))
s = {'x': x, 'y': y, 'z': z}

print('LAW', EQ, cat[EQ], 'dual L-form:', law)
print('RULES', FILE)
for i, r in enumerate(rules):
    print('  R%d %s' % (i + 1, cf.show_rule(r)))
print('INSTANCE', {k: tr.show(v) for k, v in s.items()})
T = tr.Tracing(law, rules)
A, B = law[1]


def evt(p):
    if isinstance(p, str):
        return s[p]
    a, b = evt(p[0]), evt(p[1])
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('  %-46s = %s   [%s]' % (str(p), tr.show(r) if size(r) < 60 else '<size %d>' % size(r),
                                   'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
              % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r


u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
print('  FINAL op(A,B) = %s  expected x = %s  [%s]'
      % (tr.show(r) if size(r) < 60 else '<size %d>' % size(r), tr.show(s['x']),
         'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
          % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
okr = [i + 1 for i, (conds, xx, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])

F = fm.Free(law)


def evs(p):
    if isinstance(p, str):
        return s[p]
    return F.op(evs(p[0]), evs(p[1]))


rs = F.op(evs(A), evs(B))
print('  SEMANTIC model: %s (conflicts %d)'
      % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)'
         % (tr.show(rs) if size(rs) < 60 else '<size %d>' % size(rs)), len(F.conflicts)))
