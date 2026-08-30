"""Chain-case table for the MINIMISED 5-rule model of law 11081, over the full validator battery.

For every assignment the battery evaluates the law at, record which rule fired at each of
A=op(y,x), B=op(x,A), C=op(z,y), D=op(B,C) and at the final op(y,D).
"""
import sys, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
IDX = [1, 2, 4, 8, 9]
rules = [allrules[i - 1] for i in IDX]           # renumbered 1..5 in the emitted Lean
A, B = law[1]

seen = []


class Rec(cf.Closed):
    def evp(self, p, s):
        if p is B or p is A:
            seen.append(dict(s))
        return cf.Closed.evp(self, p, s)


def which(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            e = C.ev(x, u, v)
            if e is not None:
                return 'P%d' % (i + 1)
    return '.'


cases = collections.Counter()
t0 = time.time()
batches = []
for ms, g in ((9, 1), (5, 2)):
    C = Rec(law, rules); seen.clear()
    sc.exhaustive(C, law, ms, g, limit=25)
    batches.append((C, list(seen)))
    print('exh%d/%d %d assignments %.0fs' % (ms, g, len(seen), time.time() - t0), flush=True)
for sd in (3, 4, 5):
    for name, fn in (('deep', lambda C: cf.deep_tests(C, law, 3000, 240, sd)),
                     ('fuzz', lambda C: fz.fuzz(C, law, rules, 12000, seed=sd + 100)),
                     ('clos', lambda C: fz.closure_fuzz(C, law, 12000, seed=sd + 200)),
                     ('crit', lambda C: fz.critical_fuzz(C, law, 12000, seed=sd + 300))):
        C = Rec(law, rules); seen.clear()
        fn(C)
        batches.append((C, list(seen)))
        print('%s seed %d: %d assignments %.0fs' % (name, sd, len(seen), time.time() - t0), flush=True)

bad = 0
for C, ss in batches:
    for s in ss:
        try:
            x, y, z = s['x'], s['y'], s['z']
            a = C.op(y, x); b = C.op(x, a); c = C.op(z, y); d = C.op(b, c); r = C.op(y, d)
        except RecursionError:
            continue
        if r != x:
            bad += 1
        cases[(which(C, y, x), which(C, x, a), which(C, z, y), which(C, b, c), which(C, y, d))] += 1
print('law failures over the battery:', bad)
print('%-6s %-6s %-6s %-6s %-6s %s' % ('A', 'B', 'C', 'D', 'top', 'count'))
for k, n in cases.most_common(60):
    print('%-6s %-6s %-6s %-6s %-6s %d' % (k[0], k[1], k[2], k[3], k[4], n))
