"""9663 validation driver. usage: _x9663_val.py <ruleset-name> [seeds...]
ruleset-name: gen (the 49 generated), or a name registered in _x9663_rules.py
Writes gen/_x9663_val_<name>.log
"""
import sys, os, json, time
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import closedform as cf, revalidate as rv, fuzz as fz, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 9663
cat = catalog()
LAW = normalise(parse_eq(cat[EQ]))   # L-form, not dualized


def show(t):
    if not isinstance(t, tuple):
        return str(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def gen_rules():
    src = open(os.path.join(HERE, 'gen/chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def get(name):
    if name == 'gen':
        return gen_rules()
    import _x9663_rules as R
    return R.SETS[name]


def main():
    name = sys.argv[1]
    seeds = [int(a) for a in sys.argv[2:] if a.isdigit()] or [3, 4, 5]
    rules = get(name)
    log = open(os.path.join(HERE, 'gen/_x9663_val_%s.log' % name), 'w', encoding='utf-8')

    def p(*a):
        s = ' '.join(str(x) for x in a)
        print(s, flush=True)
        log.write(s + '\n')
        log.flush()

    p('ruleset', name, 'nrules', len(rules), 'seeds', seeds)
    for i, r in enumerate(rules):
        p('  R%d %s' % (i + 1, cf.show_rule(r)))
    t0 = time.time()
    fails = rv.run_tests(LAW, rules, seeds, 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    p('run_tests fails=%d value=%d %s  %.1fs' % (len(fails), len(real), json.dumps(kinds), time.time() - t0))
    for s, r, kind, sd in real[:6]:
        p('  FAIL[%s seed %s] sizes %s' % (kind, sd, {k: size(v) for k, v in s.items()}))
        p('     ' + json.dumps({k: show(v) for k, v in s.items()}))
        p('     got ' + show(r))
    if not real:
        for sd in (90001, 90002):
            C = cf.Closed(LAW, rules)
            t, f = cf.deep_tests(C, LAW, 20000, 900, sd)
            rf = [x for x in f if x[1] != 'recursion']
            p('  deep20k seed %d tested %d fails %d (value %d)' % (sd, t, len(f), len(rf)))
            for s, r in rf[:3]:
                p('     ' + json.dumps({k: show(v) for k, v in s.items()})[:900])
    p('DONE %s  value-fails %d  %.1fs' % (name, len(real), time.time() - t0))
    log.close()


if __name__ == '__main__':
    main()
