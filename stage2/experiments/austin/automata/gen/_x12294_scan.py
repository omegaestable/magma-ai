"""12294: screen prefixes / hand sets of rules quickly (exhaustive + a small deep/fuzz)."""
import sys, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12294
law = normalise(parse_eq(catalog()[EQ]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); GEN = ns['rules']


def quick(name, rules, seeds=(3,), N=400, NF=1500):
    t0 = time.time()
    fails = rv.run_tests(law, rules, list(seeds), N, NF)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('rec' if r == 'recursion' else 'val') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    val = [f for f in fails if f[1] != 'recursion']
    print('%-12s n=%2d fails=%3d val=%3d %-70s %.1fs' % (name, len(rules), len(fails), len(val), json.dumps(kinds), time.time() - t0), flush=True)
    return val


if __name__ == '__main__':
    for k in (1, 2, 3, 4, 6, 8, 12, 16, 20, 24):
        quick('prefix%d' % k, GEN[:k])
