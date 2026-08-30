"""find and explain deep-test failures of a named 21864 rule set."""
import sys, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, leangen, trace as TR
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x21864_rules as RR

show = TR.show
EQ = 21864
expr = sys.argv[1]
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
seeds = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else [77, 78, 91]
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
rules = eval(expr, vars(RR))
A, B = law[1]
nodes = ['A1', 'A', 'B1', 'B']
allf = []
for sd in seeds:
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, N, 900, sd)
    f = [q for q in f if q[1] != 'recursion']
    print('seed %d: tested %d fails %d' % (sd, t, len(f)))
    allf += [(s, r, sd) for s, r in f]
allf.sort(key=lambda q: sum(size(t) for t in q[0].values()))
for s, got, sd in allf[:6]:
    print('\n==== seed %d ====' % sd, {k: (show(v) if size(v) < 60 else '<%d>' % size(v)) for k, v in s.items()})
    T = TR.Tracing(law, rules)

    def evt(p):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b)
        T.trace_on = False
        w = T.log[-1][2] if T.log else None
        print('  %-30s = %s  [%s]' % (str(p), show(r) if size(r) < 60 else '<%d>' % size(r),
                                      'free' if w is None else 'R%d %s' % (w + 1, rules[w][2])))
        return r
    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    print('  FINAL = %s expect %s [%s]' % (show(r) if size(r) < 60 else '<%d>' % size(r),
          show(s['x']) if size(s['x']) < 60 else '<%d>' % size(s['x']),
          'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:8]:
        print('     GATE CUT %s at (%d,%d) vs (%d,%d)' % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, q in enumerate(rules) if TR.struct_ok(T, q[0], u, v)]
    print('  struct_ok', okr, [rules[i - 1][2] for i in okr])
    print('  u =', show(u) if size(u) < 90 else '<%d>' % size(u))
    print('  v =', show(v) if size(v) < 90 else '<%d>' % size(v))
