"""_x38565_cand.py -- validate candidate rule sets for law 38565.
usage: python gen/_x38565_cand.py <name>
Sets are indices into the extractor's full rule list (see gen/_x38565_rules.py output).
"""
import sys, os, time, pickle
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))

with open(os.path.join(HERE, '_x38565_full.pkl'), 'rb') as f:
    full = pickle.load(f)

SETS = {
    'A': [0, 1, 6],
    'B': [0, 1, 6, 29],
    'C': [0, 1, 29],
    'D': [0, 1, 6, 22, 23],
    'E': list(range(30)),
    'F': [0, 1, 6, 23],
}

g = lambda n: ('g', n)
J = lambda a, b: ('J', a, b)
z0 = J(g(1), J(g(1), g(1)))
x0 = J(J(g(1), g(0)), J(g(1), J(g(1), g(0))))
y0 = J(J(z0, J(x0, z0)), g(1))
HAND = [{'x': x0, 'y': y0, 'z': z0}]


def ev(o, p, s):
    if isinstance(p, str):
        return s[p]
    return o.op(ev(o, p[0], s), ev(o, p[1], s))


def check(name):
    idx = SETS[name]
    rules = [full[i] for i in idx]
    print('SET', name, 'rules', [full[i][2] for i in idx])
    C = cf.Closed(law, rules)
    ok = True
    for s in HAND:
        got = ev(C, law[1], s)
        good = got == s['x']
        ok = ok and good
        print('  hand instance:', 'OK' if good else 'FAIL got sz %d' % size(got))
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    fails = [f for f in fails if f[1] != 'recursion']
    print('  run_tests fails %d (%.1fs)' % (len(fails), time.time() - t0))
    for f in fails[:3]:
        print('   ', {k: size(v) for k, v in f[0].items()}, f[2] if len(f) > 2 else '')
    C2 = cf.Closed(law, rules)
    tot = 0
    for seed in (777, 991, 20260829, 13, 4242):
        t0 = time.time()
        tested, fl = cf.deep_tests(C2, law, 20000, 300, seed)
        fl = [f for f in fl if f[1] != 'recursion']
        tot += len(fl)
        print('  deep seed %-9d tested %5d fails %d (%.1fs)' % (seed, tested, len(fl), time.time() - t0))
    print('  TOTAL deep fails', tot, 'run_tests fails', len(fails))
    return ok and not fails and not tot


if __name__ == '__main__':
    for nm in sys.argv[1:]:
        check(nm)
