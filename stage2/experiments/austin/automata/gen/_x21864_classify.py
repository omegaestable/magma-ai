"""Classify every failing instance of a 21864-style both-compound law by which chain products decoded.

usage: python gen/_x21864_classify.py <eq> [rulesfile]
"""
import sys, os, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, smallcheck as sc, leangen, trace as TR, revalidate as rv
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

show = TR.show
EQ = int(sys.argv[1])
path = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else ('gen/chk%d.py' % EQ)
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('law', law, 'rules', len(rules), 'from', path)

fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
fails = [f for f in fails if f[1] != 'recursion']
print('total value fails', len(fails))
fails.sort(key=lambda q: sum(size(t) for t in q[0].values()))

A, B = law[1]
nodes = []


def walk(p, name):
    if isinstance(p, str):
        return
    walk(p[0], name + '0'); walk(p[1], name + '1')
    nodes.append((name, p))


walk(A, 'A'); walk(B, 'B')
print('chain nodes', [n for n, _ in nodes])

cnt = collections.Counter()
examples = {}
for s, got, kind, sd in fails:
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
    except RecursionError:
        continue
    T.trace_on = True; T.log = []; T.cuts = []
    r = T.op(u, v); T.trace_on = False
    fin = 'free' if not T.log or T.log[-1][2] is None else 'R%d' % (T.log[-1][2] + 1)
    okr = tuple(i + 1 for i, (conds, x, tag) in enumerate(rules) if TR.struct_ok(T, conds, u, v))
    ncuts = len(T.cuts)
    key = (tuple(tags), fin, okr, ncuts > 0)
    cnt[key] += 1
    if key not in examples:
        examples[key] = (s, kind)

order = [n for n, _ in nodes]
for key, n in cnt.most_common():
    tags, fin, okr, cut = key
    s, kind = examples[key]
    print('%3d  %s | final=%s struct_ok=%s cut=%s  [%s] %s' % (
        n, ' '.join('%s:%s' % (a, b) for a, b in zip(order, tags)), fin, list(okr), cut, kind,
        {k: (show(v) if size(v) < 40 else '<%d>' % size(v)) for k, v in s.items()}))
