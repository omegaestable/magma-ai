"""Take every pair (z,y) at which branch 5 fires (or alpha/beta both fail) and test the law on it."""
import sys, collections, time, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
rules = [allrules[i - 1] for i in (1, 2, 4, 8, 9)]


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i + 1
    return 0


bad = []
t0 = time.time()
for name, mk in (('deep3', lambda C: cf.deep_tests(C, law, 3000, 240, 3)),
                 ('fuzz3', lambda C: fz.fuzz(C, law, rules, 12000, seed=103)),
                 ('clos3', lambda C: fz.closure_fuzz(C, law, 12000, seed=203)),
                 ('crit3', lambda C: fz.critical_fuzz(C, law, 12000, seed=303)),
                 ('fuzz4', lambda C: fz.fuzz(C, law, rules, 12000, seed=104)),
                 ('clos4', lambda C: fz.closure_fuzz(C, law, 12000, seed=204)),
                 ('crit4', lambda C: fz.critical_fuzz(C, law, 12000, seed=304)),
                 ('fuzz5', lambda C: fz.fuzz(C, law, rules, 12000, seed=105)),
                 ('clos5', lambda C: fz.closure_fuzz(C, law, 12000, seed=205)),
                 ('crit5', lambda C: fz.critical_fuzz(C, law, 12000, seed=305))):
    C = cf.Closed(law, rules)
    mk(C)
    for (u, v) in list(C.memo.keys()):
        if branch(C, u, v) == 5:
            bad.append((u, v))
    print('%-6s cumulative branch-5 pairs: %d  %.0fs' % (name, len(bad), time.time() - t0), flush=True)

print('branch-5 pairs found:', len(bad))
random.seed(11)
pool = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))]
fails = 0
for (z, y) in bad:
    pool2 = list(pool) + [rand_term(3) for _ in range(20)] + [z, y]
    for x in pool2:
        C = cf.Closed(law, rules)
        s = {'x': x, 'y': y, 'z': z}
        try:
            got = C.op(C.evp(law[1][0], s), C.evp(law[1][1], s))
        except RecursionError:
            continue
        if got != x:
            fails += 1
            if fails <= 3:
                print('LAW FAILS  |x|=%d |y|=%d |z|=%d' % (size(x), size(y), size(z)))
print('law failures over branch-5 (z,y) pairs x pool:', fails)
