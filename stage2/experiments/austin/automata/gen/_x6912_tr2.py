"""Trace failures of a chosen 6912 rule-set variant on its own deep-test failures."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, trace as TR
from freemodel import size
import _x6912_rep as R
import _x6912_rep2 as R2

law = R.law
which = sys.argv[1] if len(sys.argv) > 1 else 'four16'
NSHOW = int(sys.argv[2]) if len(sys.argv) > 2 else 3
rules = dict(list(R.VARIANTS.items()) + list(R2.VAR.items()))[which]
print('rules:', [r[2] for r in rules])

fails = []
for sd in (1234, 4321):
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 8000, 400, sd)
    fails += [x for x in f if x[1] != 'recursion']
    if len(fails) > 30: break
print('fails:', len(fails))
fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
A, B = law[1]
seen = set()
shown = 0
for s, got in fails:
    key = tuple(sorted((k, size(v)) for k, v in s.items()))
    if key in seen: continue
    seen.add(key)
    shown += 1
    if shown > NSHOW: break
    print('---- ', {k: TR.show(v) if size(v) < 90 else '<%d>' % size(v) for k, v in s.items()})
    T = TR.Tracing(law, rules)
    def evt(p):
        if isinstance(p, str): return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b); T.trace_on = False
        w = T.log[-1][2] if T.log else None
        print('   %-34s = %s  [%s]' % (str(p), TR.show(r) if size(r) < 70 else '<%d>' % size(r),
              'free' if w is None else 'R%d %s' % (w + 1, rules[w][2])))
        return r
    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    w = T.log[-1][2] if T.log else None
    print('   FINAL = %s expected %s [%s]' % (TR.show(r) if size(r) < 70 else '<%d>' % size(r),
          TR.show(s['x']) if size(s['x']) < 70 else '<%d>' % size(s['x']),
          'free' if w is None else 'R%d %s' % (w + 1, rules[w][2])))
