"""Trace the five known exh9/1 failures of law 23357 (hardcoded instances, no re-search)."""
import sys, os, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, trace as tr
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 23357
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
show = tr.show

G = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)

FAILS = [
    dict(y=J(G(0), J(J(G(0), G(0)), G(0))),
         x=J(J(G(0), G(0)), G(0)),
         z=J(J(G(0), J(G(0), G(0))), G(0))),
    dict(y=J(G(0), J(J(G(0), G(0)), G(0))),
         x=J(J(G(0), G(0)), G(0)),
         z=J(J(G(0), J(G(0), J(G(0), G(0)))), G(0))),
    dict(y=J(J(J(G(0), G(0)), G(0)), J(G(0), G(0))),
         x=J(J(G(0), J(J(G(0), G(0)), G(0))), G(0)),
         z=J(G(0), J(J(G(0), G(0)), G(0)))),
    dict(y=J(J(J(G(0), G(0)), G(0)), J(G(0), G(0))),
         x=J(J(G(0), J(J(G(0), G(0)), G(0))), G(0)),
         z=J(G(0), J(J(G(0), G(0)), J(G(0), G(0))))),
    dict(y=J(J(G(0), J(G(0), J(G(0), G(0)))), G(0)),
         x=J(J(G(0), G(0)), G(0)),
         z=J(J(G(0), J(G(0), G(0))), J(G(0), G(0)))),
]


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
        print('  %-34s = %s   [%s]' % (str(p), show(r) if size(r) < 90 else '<size %d>' % size(r),
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
          % (show(r) if size(r) < 90 else '<size %d>' % size(r), show(s['x']),
             'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:6]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
              % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
    print('  structural-hold rules:', okr, [rules[i - 1][2] for i in okr])
    if os.environ.get('SEM'):
        F = fm.Free(law)


        def evs(p):
            if isinstance(p, str):
                return s[p]
            return F.op(evs(p[0]), evs(p[1]))
        rs = F.op(evs(A), evs(B))
        print('  SEMANTIC: %s' % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)'
                                  % (show(rs) if size(rs) < 90 else '<size %d>' % size(rs))))
    return u, v


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk23357.py'
    rules = load_rules(path)
    which = [int(a) for a in sys.argv[2:]] or list(range(len(FAILS)))
    for i in which:
        print('=' * 74)
        print('FAIL #%d' % i)
        explain(law, rules, FAILS[i])
