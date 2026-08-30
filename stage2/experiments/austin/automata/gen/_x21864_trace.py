"""trace a SPECIFIC instance of law <eq> under a given rule set (default gen/chk<eq>.py).

usage: python gen/_x21864_trace.py <eq> [<rulesfile>] [--which N]
Instances come from the exhaustive small-term failures (which trace.py does not look at).
Reuses trace.Tracing / trace.struct_ok verbatim.
"""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, smallcheck as sc, leangen, trace as TR
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

show = TR.show

EQ = int(sys.argv[1])
rf = None
_skip = False
for i, a in enumerate(sys.argv[2:]):
    if _skip:
        _skip = False
        continue
    if a.startswith('--'):
        _skip = True
        continue
    rf = a
which = int(sys.argv[sys.argv.index('--which') + 1]) if '--which' in sys.argv else 0
nf = int(sys.argv[sys.argv.index('--nf') + 1]) if '--nf' in sys.argv else 1

cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

path = rf or ('gen/chk%d.py' % EQ)
src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('law', law, 'rules', len(rules), 'from', path)

n, f = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=40)
f = [q for q in f if q[1] != 'recursion']
f.sort(key=lambda q: sum(size(t) for t in q[0].values()))
print('exhaustive 9/1: %d assignments, %d fails' % (n, len(f)))
for i, (s, r) in enumerate(f[:12]):
    print('  [%d]' % i, {k: show(v) for k, v in s.items()})

for idx in range(which, min(which + nf, len(f))):
    s, got = f[idx]
    print('\n==== INSTANCE %d ====' % idx, {k: show(v) for k, v in s.items()})
    T = TR.Tracing(law, rules)
    A, B = law[1]

    def evt(p):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b)
        T.trace_on = False
        w = T.log[-1][2] if T.log else None
        print('  %-40s = %s   [%s]' % (str(p), show(r) if size(r) < 70 else '<size %d>' % size(r),
                                       'free' if w is None else 'R%d %s' % (w + 1, rules[w][2])))
        for e, a2, b2, u2, v2 in T.cuts[:4]:
            print('      GATE CUT: %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
        return r

    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    print('  FINAL op(A,B) = %s  expected x = %s  [%s]' % (show(r) if size(r) < 70 else '<size %d>' % size(r),
          show(s['x']), 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('      GATE CUT: %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if TR.struct_ok(T, conds, u, v)]
    print('  structurally-holding rules at final pair:', okr, [rules[i - 1][2] for i in okr])
    F = fm.Free(law)

    def evs(p):
        if isinstance(p, str):
            return s[p]
        return F.op(evs(p[0]), evs(p[1]))
    rs = F.op(evs(A), evs(B))
    print('  SEMANTIC: %s (conflicts %d)' % ('HOLDS' if rs == s['x'] else 'FAILS too (got %s)' %
          (show(rs) if size(rs) < 70 else '<size %d>' % size(rs)), len(F.conflicts)))
