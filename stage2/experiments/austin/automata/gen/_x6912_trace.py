"""Trace a specific failing instance of 6912 (from gen/_x6912_fails.json), like trace.py does."""
import sys, os, json, ast
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, trace as TR
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 6912
IDX = int(sys.argv[1]) if len(sys.argv) > 1 else 0
RULEFILE = sys.argv[2] if len(sys.argv) > 2 else 'gen/chk6912.py'

cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
src = open(RULEFILE, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

fl = json.load(open('gen/_x6912_fails.json', encoding='utf-8'))
rec = fl[IDX]
s = {k: ast.literal_eval(v) for k, v in rec['s'].items()}
print('INSTANCE kind=%s seed=%s' % (rec['kind'], rec['seed']))
for k in ('x', 'y', 'z'):
    print('  %s = %s   (size %d)' % (k, TR.show(s[k]) if size(s[k]) < 200 else '<big>', size(s[k])))

T = TR.Tracing(law, rules)
A, B = law[1]

def evt(p, ind='  '):
    if isinstance(p, str):
        return s[p]
    a, b = evt(p[0], ind), evt(p[1], ind)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('%s%-40s = %s   [%s]' % (ind, str(p), TR.show(r) if size(r) < 70 else '<size %d>' % size(r),
                                   'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('%s    GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (ind, cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r

u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
print('  FINAL op(A,B) = %s  expected x = %s  [%s]' % (TR.show(r) if size(r) < 70 else '<size %d>' % size(r),
      TR.show(s['x']), 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
for e, a2, b2, u2, v2 in T.cuts[:10]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if TR.struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])
F = fm.Free(law)
def evs(p):
    if isinstance(p, str): return s[p]
    return F.op(evs(p[0]), evs(p[1]))
rs = F.op(evs(A), evs(B))
print('  SEMANTIC model: %s (conflicts %d)' % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)' % (TR.show(rs) if size(rs) < 70 else '<size %d>' % size(rs)), len(F.conflicts)))
