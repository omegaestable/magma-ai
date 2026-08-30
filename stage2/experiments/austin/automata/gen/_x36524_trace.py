"""Trace failing instances of a rule set for law 36524 (reuses trace.Tracing / trace.struct_ok).

Usage: python gen/_x36524_trace.py [rulesfile] [seed] [N]
  rulesfile: a python file defining `rules` (default gen/chk36524.py)
"""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, leangen, trace as tr
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 36524
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))

rf = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'gen', 'chk36524.py')
seed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
N = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
src = open(rf, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
print('rules from', rf, len(rules))

C = cf.Closed(law, rules)
t, f = cf.deep_tests(C, law, N, 300, seed)
fails = [x for x in f if x[1] != 'recursion']
print('tested', t, 'fails', len(fails))
if not fails:
    sys.exit(0)
fails.sort(key=lambda z: sum(size(q) for q in z[0].values()))
s, got = fails[0]
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
    print('  %-42s = %s   [%s]' % (str(p), tr.show(r) if size(r) < 70 else '<size %d>' % size(r),
                                   'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('      GATE CUT: %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r

u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
print('  FINAL = %s  expected x = %s  [%s]' % (tr.show(r) if size(r) < 70 else '<size %d>' % size(r),
      tr.show(s['x']) if size(s['x']) < 70 else '<size %d>' % size(s['x']),
      'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
for e, a2, b2, u2, v2 in T.cuts[:6]:
    print('      GATE CUT: %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
print('  struct-hold rules at final pair:', okr, [rules[i - 1][2] for i in okr])
F = fm.Free(law)
def evs(p):
    if isinstance(p, str): return s[p]
    return F.op(evs(p[0]), evs(p[1]))
rs = F.op(evs(A), evs(B))
print('  SEMANTIC: %s (conflicts %d)' % ('HOLDS' if rs == s['x'] else 'FAILS too (got size %d)' % size(rs), len(F.conflicts)))
print()
print('u =', tr.show(u) if size(u) < 200 else '<size %d>' % size(u))
print('v =', tr.show(v) if size(v) < 200 else '<size %d>' % size(v))
