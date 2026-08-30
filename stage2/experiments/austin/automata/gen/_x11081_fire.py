"""Which of law 11081's 24 rules ever fire, anywhere, across the FULL validator battery."""
import sys, collections, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 11081
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']

total = collections.Counter()
t0 = time.time()
for ms, g in ((9, 1), (5, 2)):
    C = cf.Closed(law, rules)
    sc.exhaustive(C, law, ms, g, limit=25)
    for i, n in C.fired.items():
        total[i] += n
    print('exh%d/%d done %.0fs' % (ms, g, time.time() - t0), flush=True)
for sd in (3, 4, 5):
    C = cf.Closed(law, rules); cf.deep_tests(C, law, 3000, 240, sd)
    for i, n in C.fired.items():
        total[i] += n
    C = cf.Closed(law, rules); fz.fuzz(C, law, rules, 12000, seed=sd + 100)
    for i, n in C.fired.items():
        total[i] += n
    C = cf.Closed(law, rules); fz.closure_fuzz(C, law, 12000, seed=sd + 200)
    for i, n in C.fired.items():
        total[i] += n
    C = cf.Closed(law, rules); fz.critical_fuzz(C, law, 12000, seed=sd + 300)
    for i, n in C.fired.items():
        total[i] += n
    print('seed', sd, 'done %.0fs' % (time.time() - t0), flush=True)

print('firing counts over the whole battery:')
for i in range(len(rules)):
    print('  R%-3d %-28s %d' % (i + 1, rules[i][2], total.get(i, 0)))
print('never fire:', [i + 1 for i in range(len(rules)) if not total.get(i, 0)])
