"""Compare candidate rule sets for 12087 on the strict standard."""
import sys, os, time, json
sys.path.insert(0, r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen, fuzz as fz
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12087
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig

def loadrules(path):
    src = open(path, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}; exec(src, ns); return ns['rules']

X = cf.Extractor(law)
full = X.rules(exist=False)
sets = {
    'min3': loadrules('gen/_x12087out/chk12087.py'),
    'rep4': loadrules('gen/rep12087/chk12087.py') if os.path.exists('gen/rep12087/chk12087.py') else None,
    'full': full,
}
for name, rules in sets.items():
    if rules is None: continue
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    tot = len(real)
    kinds = {}
    for s, r, kind, sd in real:
        kinds[kind] = kinds.get(kind, 0) + 1
    deep = 0
    for sd in (101, 202, 303):
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, 20000, 300, sd)
        deep += len([q for q in f if q[1] != 'recursion'])
    print(name, 'nrules', len(rules), 'run_tests real', tot, kinds, 'deep20k x3 real', deep, 'secs', round(time.time() - t0, 1), flush=True)
    print('   tags:', [r[2] for r in rules], flush=True)
