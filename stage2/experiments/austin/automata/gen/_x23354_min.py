"""Validated removal on the 4-rule 23354 set: try every subset that keeps R1('free')."""
import sys, time, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23354
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']

for keepset in ([0,1,2,3],[0,1,2],[0,1,3],[0,2,3],[0,1],[0,2],[0,3]):
    trial = [rules[i] for i in keepset]
    t0 = time.time()
    f = rv.run_tests(law, trial, [3, 4, 5], 3000, 12000)
    real = [x for x in f if x[1] != 'recursion']
    extra = 0
    if not real:
        for sd in (911, 912, 913):
            C = cf.Closed(law, trial)
            t, ff = cf.deep_tests(C, law, 20000, 300, sd)
            extra += len([x for x in ff if x[1] != 'recursion'])
    print(keepset, 'run_tests real fails', len(real), 'deep20kx3 fails', extra, 'secs', round(time.time()-t0,1), flush=True)
