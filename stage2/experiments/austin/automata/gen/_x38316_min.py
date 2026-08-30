"""Validated-removal minimisation of the 10-rule model for 38316 (PLAYBOOK_REPAIR §6)."""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

C = cf.Closed(law, rules)
cf.deep_tests(C, law, 1500, 120, 991)
print('firing counts after 1500 deep:', {rules[i][2]: c for i, c in sorted(C.fired.items())}, flush=True)

order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    t0 = time.time()
    f = rv.run_tests(law, trial, [3, 4, 5], 3000, 12000)
    if f:
        print('  KEEP  %-12s (fired %d)  %d fails  %.0fs' % (r[2], C.fired.get(i, 0), len(f), time.time() - t0), flush=True)
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-12s (fired %d) -> %d rules  %.0fs' % (r[2], C.fired.get(i, 0), len(keep), time.time() - t0), flush=True)
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped), flush=True)
print('kept:', [r[2] for r in keep])
f = rv.run_tests(law, keep, [77, 78], 3000, 12000)
print('fresh-seed validation fails:', len(f), flush=True)
import json
open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x38316_keep.json', 'w').write(
    json.dumps([r[2] for r in keep]))
