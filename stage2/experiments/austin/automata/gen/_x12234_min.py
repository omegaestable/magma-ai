"""Validated-removal minimisation of the 12234 DSL rule set (PLAYBOOK_REPAIR sec 6)."""
import sys, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 12234
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk12234.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

C = cf.Closed(law, rules)
cf.deep_tests(C, law, 1500, 120, 991)
order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
print('firing counts', {rules[i][2]: C.fired.get(i, 0) for i in range(len(rules))})
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    t0 = time.time()
    if rv.run_tests(law, trial, [3, 4, 5], 3000, 12000):
        print('  KEEP  %-10s (fired %d) %.1fs' % (r[2], C.fired.get(i, 0), time.time() - t0), flush=True)
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-10s (fired %d) -> %d rules' % (r[2], C.fired.get(i, 0), len(keep)), flush=True)
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped))
if len(keep) < len(rules):
    print('fresh-seed validation fails:', len(rv.run_tests(law, keep, [77, 78], 3000, 12000)))
