"""_pb_repro9667.py -- playbook reproduction: run the documented repair procedure end to end on law 9667.

Step 1  load the GENERATED rule set (gen/chk9667_gen0.py) and show rv.run_tests refutes it.
Step 2  trace the smallest failing instance (which product decoded unexpectedly).
Step 3  apply the repair (relocate the decoder to a provably free occurrence) and show 0 fails.

Usage: python gen/_pb_repro9667.py [step1|step2|step3|all]
"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import closedform as cf
import revalidate as rv
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 9667
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig


def load(fname):
    src = open(os.path.join(HERE, fname), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def report(name, rules, seeds=(3, 4, 5)):
    t0 = time.time()
    fails = rv.run_tests(law, rules, list(seeds), 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    print('%-14s nrules=%d  run_tests fails=%d (value fails=%d) %s  %.1fs'
          % (name, len(rules), len(fails), len(real), json.dumps(kinds), time.time() - t0), flush=True)
    real.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    for s, r, kind, sd in real[:2]:
        print('   FAIL[%s seed %s]' % (kind, sd), {k: show(v) for k, v in s.items()},
              '-> got', show(r) if isinstance(r, tuple) and size(r) < 60 else str(r)[:40], flush=True)
    return real


mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
gen0 = load('chk9667_gen0.py')
rep = load('chk9667.py')
print('law %d: %s   dualized=%s' % (EQ, cat[EQ], dualized))
print('GENERATED R2 :', cf.show_rule(gen0[1]))
print('REPAIRED  R2 :', cf.show_rule(rep[1]))
print()

if mode in ('all', 'step1'):
    bad = report('GENERATED', gen0)

if mode in ('all', 'step2'):
    # the hand instance of gen/hole9667.py, re-derived: op(z, u) fired the RECURSIVE rule, so u.1 is not free
    C = cf.Closed(law, gen0)
    g = lambda n: ('g', n)
    J = lambda a, b: ('J', a, b)
    c, q, d = g(1), g(2), g(0)
    z = J(J(c, q), J(d, J(q, q)))
    y = J(d, J(J(z, z), J(z, z)))
    x = g(1)
    s = {'x': x, 'y': y, 'z': z}
    P = C.op(z, y)
    print('step2: op(z,y) =', show(P), ' (decoded, so y.1 = op(q,z) is NOT of the free J-shape)')
    print('step2: law under GENERATED rules holds?', C.evp(law[1], s) == s['x'])
    print('step2: law under REPAIRED  rules holds?', cf.Closed(law, rep).evp(law[1], s) == s['x'])

if mode in ('all', 'step3'):
    ok = report('REPAIRED', rep)
    t0 = time.time()
    C = cf.Closed(law, rep)
    tested, f2 = cf.deep_tests(C, law, 20000, 900, 987)
    print('REPAIRED  cf.deep_tests %d tested, %d fails, %.1fs' % (tested, len(f2), time.time() - t0), flush=True)
