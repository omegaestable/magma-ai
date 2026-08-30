"""Validate the generated 24-rule package for law 12294 to the §7 standard."""
import sys, os, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 12294
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized', dualized, 'law', law, flush=True)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}
exec(src, ns)
rules = ns['rules']
print('nrules', len(rules), flush=True)

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
val = [f for f in fails if f[2] != 'recursion']
print('run_tests fails %d (value %d) in %.1fs' % (len(fails), len(val), time.time() - t0), flush=True)
kinds = {}
for f in fails:
    kinds[f[2]] = kinds.get(f[2], 0) + 1
print('kinds', kinds, flush=True)
for f in val[:5]:
    print('FAIL', f[2], f[3], {k: cf.show(v) if hasattr(cf, 'show') else str(v) for k, v in f[0].items()}, flush=True)

if not val:
    C = cf.Closed(law, rules)
    for seed in (911, 2027):
        t0 = time.time()
        tested, df = cf.deep_tests(C, law, 20000, 300, seed)
        dv = [f for f in df if f[2] != 'recursion'] if df and len(df[0]) > 2 else df
        print('deep20k seed %d: tested %d fails %d (%.1fs)' % (seed, tested, len(df), time.time() - t0), flush=True)
        for f in df[:3]:
            print('  ', f, flush=True)
print('DONE', flush=True)
