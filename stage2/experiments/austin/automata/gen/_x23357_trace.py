"""Trace the exhaustive-small failures of law 23357 with a given rule set."""
import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, smallcheck as sc, leangen, trace as tr
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23357
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
show = tr.show


def load_rules(path):
    src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def explain(law, rules, s):
    A, B = law[1]
    T = tr.Tracing(law, rules)

    def evt(p, depth=0):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0], depth + 1), evt(p[1], depth + 1)
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b)
        T.trace_on = False
        which = T.log[-1][2] if T.log else None
        print('  %-34s = %s   [%s]' % (str(p), show(r) if size(r) < 70 else '<size %d>' % size(r),
                                       'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
        for e, a2, b2, u2, v2 in T.cuts[:4]:
            print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
                  % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
        return r

    print('INSTANCE', {k: show(v) for k, v in s.items()})
    u = evt(A); v = evt(B)
    print('  u =', show(u))
    print('  v =', show(v))
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    print('  FINAL op(A,B) = %s  expected x = %s  [%s]'
          % (show(r) if size(r) < 70 else '<size %d>' % size(r), show(s['x']),
             'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
              % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
    print('  structural-hold rules:', okr, [rules[i - 1][2] for i in okr])
    F = fm.Free(law)

    def evs(p):
        if isinstance(p, str):
            return s[p]
        return F.op(evs(p[0]), evs(p[1]))
    rs = F.op(evs(A), evs(B))
    print('  SEMANTIC: %s' % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)'
                              % (show(rs) if size(rs) < 70 else '<size %d>' % size(rs))))
    return u, v


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk23357.py'
    rules = load_rules(path)
    fails = rv.run_tests(law, rules, [3], 400, 800)
    fails = [f for f in fails if f[1] != 'recursion']
    print('fails', len(fails))
    fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    for f in fails[:6]:
        print('=' * 70)
        explain(law, rules, f[0])
