"""Test a named SUBSET of law 11081's 24 rules against the full validator.

usage:  python gen/_x11081_sub.py 1,2,8      [seeds]
"""
import sys, os, json, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
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

idx = [int(t) for t in sys.argv[1].split(',')]
rules = [allrules[i - 1] for i in idx]
seeds = [int(t) for t in sys.argv[2].split(',')] if len(sys.argv) > 2 else [3, 4, 5]
print('subset', idx, 'seeds', seeds)
t0 = time.time()
fails = rv.run_tests(law, rules, seeds, 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests: %d fails (%d real) in %.1fs' % (len(fails), len(real), time.time() - t0))
kinds = {}
for s, r, kind, sd in real:
    kinds[kind] = kinds.get(kind, 0) + 1
print('kinds', kinds)
for s, r, kind, sd in real[:4]:
    print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()})
    print('     ', json.dumps({k: cf.fm.show(v) if hasattr(cf.fm, 'show') else str(v) for k, v in s.items()})[:600])
if not real:
    C = cf.Closed(law, rules)
    for sd in (777, 778):
        t, f = cf.deep_tests(C, law, 20000, 300, sd)
        print('  deep20k seed', sd, 'tested', t, 'fails', len([x for x in f if x[1] != 'recursion']))
