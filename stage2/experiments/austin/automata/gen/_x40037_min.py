"""Validated-removal minimiser for a 40037 rule subset (PLAYBOOK_REPAIR.md §6).

usage: _x40037_min.py 1,2,3,4,5,6,14,10
Drops one rule at a time (least-fired first), keeps the drop only if the FULL validator still passes;
final assert on fresh seeds.
"""
import sys, os, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq
import _x40037_rules as R

EQ = 40037
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
idx = [int(i) for i in sys.argv[1].split(',')]
rules = [R.ALL[i - 1] for i in idx]
label = {id(r): 'R%d[%s]' % (i, r[2]) for i, r in zip(idx, rules)}

C = cf.Closed(law, rules)
cf.deep_tests(C, law, 1500, 120, 991)
import fuzz as fz
fz.fuzz(C, law, rules, 6000, seed=992)
order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
keep = list(rules)
dropped = []
for i in order:
    r = rules[i]
    if r[2] == 'free':
        continue
    trial = [q for q in keep if q is not r]
    if not trial:
        continue
    t0 = time.time()
    f = rv.run_tests(law, trial, [3, 4, 5], 3000, 12000)
    f = [q for q in f if q[1] != 'recursion']
    if f:
        print('  KEEP  %-22s (fired %d)  %d fails  %.0fs' % (label[id(r)], C.fired.get(i, 0), len(f), time.time() - t0), flush=True)
        continue
    keep = trial; dropped.append(label[id(r)])
    print('  DROP  %-22s (fired %d) -> %d rules  %.0fs' % (label[id(r)], C.fired.get(i, 0), len(keep), time.time() - t0), flush=True)
print('minimised %d -> %d rules, dropped %s' % (len(rules), len(keep), dropped))
print('kept:', [label[id(r)] for r in keep])
f = rv.run_tests(law, keep, [77, 78], 3000, 12000)
f = [q for q in f if q[1] != 'recursion']
print('fresh-seed validation:', len(f), 'fails')
for sd in (40037, 987654, 555, 31337):
    C2 = cf.Closed(law, keep)
    tested, ff = cf.deep_tests(C2, law, 20000, 600, sd)
    ff = [q for q in ff if q[1] != 'recursion']
    print('  deep_tests seed %d: %d tested, %d fails' % (sd, tested, len(ff)), flush=True)
