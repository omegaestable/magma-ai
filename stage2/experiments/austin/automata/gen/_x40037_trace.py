"""Trace the failing instances of 40037 (reuses trace.Tracing / trace.struct_ok verbatim).

usage: _x40037_trace.py [index]   -- index into gen/_x40037_fails.pkl
       _x40037_trace.py --rules <chkfile> [index]
"""
import sys, os, pickle
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, leangen, trace as tr
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
show = tr.show

args = [a for a in sys.argv[1:]]
rulefile = os.path.join(HERE, 'gen', 'chk%d.py' % EQ)
if '--rules' in args:
    i = args.index('--rules'); rulefile = args[i + 1]; del args[i:i + 2]
idx = int(args[0]) if args else 0

src = open(rulefile, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
print('rules from', rulefile, len(rules))

with open(os.path.join(HERE, 'gen', '_x40037_fails.pkl'), 'rb') as f:
    fails = pickle.load(f)
fails = [f for f in fails if f[1] != 'recursion']
fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
s, got = fails[idx][0], fails[idx][1]
print('INSTANCE', {k: show(v) for k, v in s.items()})
print('sizes   ', {k: size(v) for k, v in s.items()})

T = tr.Tracing(law, rules)
A, B = law[1]


def evt(p, depth=0):
    if isinstance(p, str):
        return s[p]
    a, b = evt(p[0], depth + 1), evt(p[1], depth + 1)
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(a, b)
    T.trace_on = False
    which = T.log[-1][2] if T.log else None
    print('  %-42s = %s   [%s]' % (str(p), show(r) if size(r) < 70 else '<size %d>' % size(r),
                                   'free' if which is None else 'R%d %s' % (which + 1, rules[which][2])))
    for e, a2, b2, u2, v2 in T.cuts[:4]:
        print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
              % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
    return r


u = evt(A); v = evt(B)
T.trace_on = True; T.log = []; T.cuts = []
r = T.op(u, v); T.trace_on = False
print('  FINAL op(A,B) = %s  expected x = %s  [%s]'
      % (show(r) if size(r) < 70 else '<size %d>' % size(r), show(s['x']) if size(s['x']) < 70 else '<size %d>' % size(s['x']),
         'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)))
for e, a2, b2, u2, v2 in T.cuts[:8]:
    print('      GATE CUT: %s at pair sizes (%d,%d) vs (u,v) sizes (%d,%d)'
          % (cf.show_expr(e), size(a2), size(b2), size(u2), size(v2)))
okr = [i + 1 for i, (conds, x, tag) in enumerate(rules) if tr.struct_ok(T, conds, u, v)]
print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])

F = fm.Free(law)


def evs(p):
    if isinstance(p, str):
        return s[p]
    return F.op(evs(p[0]), evs(p[1]))


rs = F.op(evs(A), evs(B))
print('  SEMANTIC model: %s (conflicts %d)'
      % ('law HOLDS' if rs == s['x'] else 'law FAILS too (got %s)' % (show(rs) if size(rs) < 70 else '<size %d>' % size(rs)),
         len(F.conflicts)))

# structure dump of u and v
def dump(name, t, path='', depth=0):
    if depth > 5 or t[0] == 'g':
        print('    %-18s %s' % (name + path, show(t) if size(t) < 60 else '<size %d>' % size(t)))
        return
    print('    %-18s %s' % (name + path, show(t) if size(t) < 60 else '<size %d>' % size(t)))
    dump(name, t[1], path + '.1', depth + 1)
    dump(name, t[2], path + '.2', depth + 1)


print('  --- u ---'); dump('u', u)
print('  --- v ---'); dump('v', v)
