"""Validated-removal minimisation for the repaired 6912 rule set (PLAYBOOK_REPAIR §6)."""
import sys, os, json, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import importlib
rep = importlib.import_module('gen._x6912_rep') if False else None
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import _x6912_rep as R

law = R.law
which = sys.argv[1] if len(sys.argv) > 1 else 'bare'
rules = R.VARIANTS[which]

C = cf.Closed(law, rules)
cf.deep_tests(C, law, 4000, 300, 991)
print('firing counts:', {rules[i][2]: C.fired.get(i, 0) for i in range(len(rules))}, flush=True)

order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules); dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    t0 = time.time()
    bad = rv.run_tests(law, trial, [3, 4, 5], 3000, 12000)
    bad = [b for b in bad if b[1] != 'recursion']
    if bad:
        print('  KEEP  %-18s (fired %d)  %d fails  %.0fs' % (r[2], C.fired.get(i, 0), len(bad), time.time() - t0), flush=True)
        continue
    keep = trial; dropped.append(r[2])
    print('  DROP  %-18s (fired %d) -> %d rules  %.0fs' % (r[2], C.fired.get(i, 0), len(keep), time.time() - t0), flush=True)
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped), flush=True)
print('KEPT:', [r[2] for r in keep], flush=True)
fresh = rv.run_tests(law, keep, [77, 78], 3000, 12000)
fresh = [f for f in fresh if f[1] != 'recursion']
print('fresh-seed validation fails:', len(fresh), flush=True)
json.dump([list(map(repr, [r[0], r[1], r[2]])) for r in keep], open('gen/_x6912_kept_%s.json' % which, 'w'))
import pickle
pickle.dump(keep, open('gen/_x6912_kept_%s.pkl' % which, 'wb'))
