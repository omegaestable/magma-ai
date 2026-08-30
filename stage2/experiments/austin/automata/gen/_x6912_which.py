"""Which rule does the 4-rule set need?  Find its failing instances, then trace them
under the full 15-rule set and report the rules that fire at each product."""
import sys, os, pickle
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, trace as TR
from freemodel import size
import _x6912_rep as R

law = R.law
full = R.VARIANTS['bare']
sub_tags = set(sys.argv[1].split(',')) if len(sys.argv) > 1 else {'free', 'B11l', 'B1l,B11v', 'B1v-struct'}
sub = [r for r in full if r[2] in sub_tags]
print('subset:', [r[2] for r in sub])

fails = []
for sd in (1234, 4321, 20260829):
    C = cf.Closed(law, sub)
    t, f = cf.deep_tests(C, law, 20000, 600, sd)
    fails += [x for x in f if x[1] != 'recursion']
print('subset fails:', len(fails))
fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))

A, B = law[1]
for s, got in fails[:4]:
    print('---- instance', {k: TR.show(v) if size(v) < 80 else '<%d>' % size(v) for k, v in s.items()})
    T = TR.Tracing(law, full)
    def evt(p):
        if isinstance(p, str): return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b); T.trace_on = False
        w = T.log[-1][2] if T.log else None
        print('   %-38s = %s  [%s]' % (str(p), TR.show(r) if size(r) < 60 else '<%d>' % size(r),
              'free' if w is None else 'R%d %s' % (w + 1, full[w][2])))
        return r
    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    w = T.log[-1][2] if T.log else None
    print('   FINAL = %s expected %s [%s]' % (TR.show(r) if size(r) < 60 else '<%d>' % size(r),
          TR.show(s['x']) if size(s['x']) < 60 else '<%d>' % size(s['x']),
          'free' if w is None else 'R%d %s' % (w + 1, full[w][2])))
