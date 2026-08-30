"""Lab for law 9663 (x = y * ((z*y) * (x*(x*y)))). Not a shared file."""
import sys, os, json, time, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, fuzz as fz, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 9663
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
LAW = ('x', leangen.dual_pat(orig[1])) if dualized else orig


def gen_rules():
    src = open(os.path.join(HERE, 'gen/chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def validate(rules, seeds=(3, 4, 5), N=3000, NF=12000, label=''):
    t0 = time.time()
    fails = rv.run_tests(LAW, rules, list(seeds), N, NF)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    print('%-14s nrules=%d run_tests fails=%d (value=%d) %s  %.1fs' %
          (label, len(rules), len(fails), len(real), json.dumps(kinds), time.time() - t0), flush=True)
    return real


def deep2(rules, seeds=(9001, 9002), N=20000, secs=600):
    for sd in seeds:
        C = cf.Closed(LAW, rules)
        t, f = cf.deep_tests(C, LAW, N, secs, sd)
        real = [x for x in f if x[1] != 'recursion']
        print('   deep seed %d: tested %d fails %d (value %d)' % (sd, t, len(f), len(real)), flush=True)
        if real:
            return real
    return []


def show(rules):
    for i, r in enumerate(rules):
        print('R%d %s' % (i + 1, cf.show_rule(r)))


if __name__ == '__main__':
    rules = gen_rules()
    print('generated rules:', len(rules))
    if 'show' in sys.argv:
        show(rules)
    if 'val' in sys.argv:
        real = validate(rules, label='GENERATED')
        for s, r, kind, sd in real[:5]:
            print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()})
            print('   ', json.dumps({k: leangen.show_term(v) if hasattr(leangen, 'show_term') else str(v) for k, v in s.items()})[:1500])
