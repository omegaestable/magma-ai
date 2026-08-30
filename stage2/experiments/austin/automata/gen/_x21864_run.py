"""validate + classify a named rule set from gen/_x21864_rules.py

usage: python gen/_x21864_run.py <eq> <expr>       e.g.  21864 "GEN + [R4b]"
"""
import sys, os, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import closedform as cf, leangen, trace as TR, revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq
import _x21864_rules as RR

show = TR.show
EQ = int(sys.argv[1])
expr = sys.argv[2]
DEEP = int(sys.argv[3]) if len(sys.argv) > 3 else 3000
FUZ = int(sys.argv[4]) if len(sys.argv) > 4 else 12000
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
rules = eval(expr, vars(RR))
print('law', law, ' rules', len(rules), ':', expr)
for i, r in enumerate(rules):
    print('  R%-2d %s' % (i + 1, cf.show_rule(r)))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], DEEP, FUZ)
c = collections.Counter('%s:%s' % (f[2], 'rec' if f[1] == 'recursion' else 'value') for f in fails)
vf = [f for f in fails if f[1] != 'recursion']
print('FAILS total %d  value %d  %s   (%.1fs)' % (len(fails), len(vf), dict(c), time.time() - t0))
if not vf:
    for sd in (77, 78, 91):
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, 20000, 600, sd)
        f = [q for q in f if q[1] != 'recursion']
        print('  deep20k seed %d: tested %d fails %d' % (sd, t, len(f)))
    sys.exit(0)

A, B = law[1]
nodes = []


def walk(p, name):
    if isinstance(p, str):
        return
    walk(p[0], name + '0'); walk(p[1], name + '1')
    nodes.append(name)


walk(A, 'A'); walk(B, 'B')
vf.sort(key=lambda q: sum(size(t) for t in q[0].values()))
cnt = collections.Counter(); ex = {}
for s, got, kind, sd in vf:
    T = TR.Tracing(law, rules)
    tags = []

    def evt(p):
        if isinstance(p, str):
            return s[p]
        a, b = evt(p[0]), evt(p[1])
        T.trace_on = True; T.log = []
        r = T.op(a, b)
        T.trace_on = False
        w = T.log[-1][2] if T.log else None
        tags.append('free' if w is None else 'R%d' % (w + 1))
        return r
    try:
        u = evt(A); v = evt(B)
        T.trace_on = True; T.log = []; T.cuts = []
        r = T.op(u, v); T.trace_on = False
    except RecursionError:
        continue
    fin = 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)
    okr = tuple(i + 1 for i, q in enumerate(rules) if TR.struct_ok(T, q[0], u, v))
    key = (tuple(tags), fin, okr, len(T.cuts) > 0)
    cnt[key] += 1
    ex.setdefault(key, (s, kind, u, v))
for key, n in cnt.most_common():
    tags, fin, okr, cut = key
    s, kind, u, v = ex[key]
    print('%3d  %s | final=%s ok=%s cut=%s [%s] %s' % (
        n, ' '.join('%s:%s' % (a, b) for a, b in zip(nodes, tags)), fin, list(okr), cut, kind,
        {k: (show(t) if size(t) < 40 else '<%d>' % size(t)) for k, t in s.items()}))
    print('      u=%s' % (show(u) if size(u) < 60 else '<%d>' % size(u)))
    print('      v=%s' % (show(v) if size(v) < 60 else '<%d>' % size(v)))
