"""trace a specific assignment of law 9663 through a chosen rule set (reuses trace.Tracing)."""
import sys, os, json
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, trace as tr, freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x9663_rules as R

LAW = normalise(parse_eq(catalog()[9663]))
show = tr.show

def parse(s):
    """parse '(g0*(g0*g0))' into a term"""
    s = s.strip()
    if s.startswith('g'):
        return ('g', int(s[1:]))
    assert s[0] == '(' and s[-1] == ')', s
    d = 0
    for i, c in enumerate(s[1:-1], 1):
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif c == '*' and d == 0:
            return ('J', parse(s[1:i]), parse(s[i + 1:-1]))
    raise ValueError(s)


def run(rules, s, label=''):
    print('=== %s ===' % label)
    print('INSTANCE', {k: show(v) for k, v in s.items()})
    T = tr.Tracing(LAW, rules)
    A, B = LAW[1]

    def evt(p):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(a, b)
        T.trace_on = False
        which = T.log[-1][2] if T.log else None
        print('  %-34s = %s   [%s]' % (str(p), show(r) if size(r) < 70 else '<size %d>' % size(r),
                                       'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
        for e, a2, b2, u2, v2 in T.cuts[:4]:
            print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' %
                  (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
        return r
    u = evt(A); v = evt(B)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    print('  FINAL op(A,B) = %s  expected x = %s  [%s]' %
          (show(r) if size(r) < 70 else '<size %d>' % size(r), show(s['x']),
           'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
    for e, a2, b2, u2, v2 in T.cuts[:8]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)' %
              (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
    print('  structural-hold rules at final pair:', okr, [rules[i - 1][2] for i in okr])
    print('  u =', show(u), ' sz', size(u))
    print('  v =', show(v) if size(v) < 90 else '<size %d>' % size(v), ' sz', size(v))
    F = fm.Free(LAW)

    def evs(p):
        if isinstance(p, str):
            return s[p]
        return F.op(evs(p[0]), evs(p[1]))
    rs = F.op(evs(A), evs(B))
    print('  SEMANTIC: %s (conflicts %d, cuts %d)' %
          ('HOLDS' if rs == s['x'] else 'FAILS too (got %s)' % (show(rs) if size(rs) < 70 else '<size %d>' % size(rs)),
           len(F.conflicts), F.cuts))


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'gen'
    rules = R.G if name == 'gen' else R.SETS[name]
    s = {'y': parse(sys.argv[2]), 'z': parse(sys.argv[3]), 'x': parse(sys.argv[4])}
    run(rules, s, name)
