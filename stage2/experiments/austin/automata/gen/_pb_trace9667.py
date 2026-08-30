"""_pb_trace9667.py -- trace.py's report, run against a chosen rules file (here 9667's GENERATED set,
which trace.py itself cannot reach because gen/chk9667.py already holds the repaired set).
Same code path: trace.Tracing + trace.struct_ok."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
import trace as tr
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 9667
FILE = sys.argv[1] if len(sys.argv) > 1 else 'chk9667_gen0.py'
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open(os.path.join(HERE, FILE), encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
c, q, d = g(1), g(2), g(0)
z = J(J(c, q), J(d, J(q, q)))
y = J(d, J(J(z, z), J(z, z)))
s = {'x': g(1), 'y': y, 'z': z}

print('LAW', EQ, cat[EQ], '(dualized)' if dualized else '')
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
    print('  %-40s = %s   [%s]' % (str(p), tr.show(r) if size(r) < 60 else '<size %d>' % size(r),
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
okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])
