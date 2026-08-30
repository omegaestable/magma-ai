"""PRODUCER FUZZ for law 11081.

The standard validator draws (x,y,z) and evaluates the law.  This one goes the other way: it collects
every pair (u,v) at which some rule FIRES anywhere in a battery, then plants that pair at the (z,y)
slot and at the (y,x) slot of the law and tests the law there.  That is what caught the hole in the
minimised 5-rule set which `revalidate.run_tests` on three seeds called clean.

usage:  python gen/_x11081_zy.py 1,2,4,8,9  [per_branch]
"""
import sys, collections, time, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 11081
cat = catalog()
law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
allrules = ns['rules']
IDX = [int(t) for t in sys.argv[1].split(',')]
rules = [allrules[i - 1] for i in IDX]
PER = int(sys.argv[2]) if len(sys.argv) > 2 else 400
A, B = law[1]


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i + 1
    return 0


byb = collections.defaultdict(list)
t0 = time.time()
for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                 ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                 ('deep3', lambda C: cf.deep_tests(C, law, 3000, 240, 3)),
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
        b = branch(C, u, v)
        if b and len(byb[b]) < PER:
            byb[b].append((u, v))
print('collected firing pairs per branch:', {k: len(v) for k, v in sorted(byb.items())},
      '%.0fs' % (time.time() - t0), flush=True)

random.seed(11)
pool = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))] + [rand_term(3) for _ in range(10)]
fails = collections.Counter()
tests = 0
for b, prs in sorted(byb.items()):
    for (u, v) in prs:
        for slot in ('zy', 'yx'):
            for t in pool:
                C = cf.Closed(law, rules)
                s = {'x': t, 'y': v, 'z': u} if slot == 'zy' else {'x': v, 'y': u, 'z': t}
                try:
                    got = C.op(C.evp(A, s), C.evp(B, s))
                except RecursionError:
                    continue
                tests += 1
                if got != s['x']:
                    fails[(b, slot)] += 1
print('producer-fuzz tests: %d   failures by (branch, slot): %s   %.0fs'
      % (tests, dict(fails), time.time() - t0))
print('TOTAL FAILURES', sum(fails.values()))
