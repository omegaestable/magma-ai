"""Full wave-3 validation of a named rule set from _v11081_rs.py.
usage: python gen/_v11081_val2.py <setname>"""
import sys, time, collections, random
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import closedform as cf, revalidate as rv, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
from _v11081_rs import SETS

law = normalise(parse_eq(catalog()[11081]))
A, B = law[1]
NAME = sys.argv[1]
rules = SETS[NAME]
print('rule set', NAME, flush=True)
for r in rules:
    print('  ', cf.show_rule(r), flush=True)
t0 = time.time()
f = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [q for q in f if q[1] != 'recursion']
print('STAGE1 run_tests: %d fails (%d real)  %.0fs' % (len(f), len(real), time.time() - t0), flush=True)
for q in real[:5]:
    print('   FAIL', q[2], q[3], {k: size(v) for k, v in q[0].items()}, flush=True)
for sd in (7, 11, 13, 17, 23):
    C = cf.Closed(law, rules)
    t, fl = cf.deep_tests(C, law, 20000, 600, sd)
    r2 = [q for q in fl if q[1] != 'recursion']
    print('STAGE2 deep20000 seed %d: tested %d fails %d (real %d)  %.0fs'
          % (sd, t, len(fl), len(r2), time.time() - t0), flush=True)


def branch(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i + 1
    return 0


byb = collections.defaultdict(list)
PER = 400
for name, mk in (('exh9', lambda C: sc.exhaustive(C, law, 9, 1, limit=25)),
                 ('exh5', lambda C: sc.exhaustive(C, law, 5, 2, limit=25)),
                 ('deep3', lambda C: cf.deep_tests(C, law, 4000, 300, 3)),
                 ('fuzz3', lambda C: fz.fuzz(C, law, rules, 15000, seed=103)),
                 ('clos3', lambda C: fz.closure_fuzz(C, law, 15000, seed=203)),
                 ('crit3', lambda C: fz.critical_fuzz(C, law, 15000, seed=303)),
                 ('fuzz4', lambda C: fz.fuzz(C, law, rules, 15000, seed=104)),
                 ('clos4', lambda C: fz.closure_fuzz(C, law, 15000, seed=204)),
                 ('crit4', lambda C: fz.critical_fuzz(C, law, 15000, seed=304)),
                 ('fuzz5', lambda C: fz.fuzz(C, law, rules, 15000, seed=105)),
                 ('clos5', lambda C: fz.closure_fuzz(C, law, 15000, seed=205)),
                 ('crit5', lambda C: fz.critical_fuzz(C, law, 15000, seed=305))):
    C = cf.Closed(law, rules)
    mk(C)
    for (u, v) in list(C.memo.keys()):
        b = branch(C, u, v)
        if b and len(byb[b]) < PER:
            byb[b].append((u, v))
print('STAGE3 firing pairs per branch:', {k: len(v) for k, v in sorted(byb.items())},
      '%.0fs' % (time.time() - t0), flush=True)
random.seed(11)
pool = [('g', 0), ('g', 1), ('g', 2), ('J', ('g', 0), ('g', 1)),
        ('J', ('g', 0), ('J', ('g', 1), ('g', 0)))] + [rand_term(3) for _ in range(10)]
fails = collections.Counter(); tests = 0; shown = 0
for b, prs in sorted(byb.items()):
    for (u, v) in prs:
        for slot in ('zy', 'yx', 'xy'):
            for t in pool:
                C = cf.Closed(law, rules)
                s = ({'x': t, 'y': v, 'z': u} if slot == 'zy' else
                     {'x': v, 'y': u, 'z': t} if slot == 'yx' else {'x': u, 'y': v, 'z': t})
                try:
                    got = C.op(C.evp(A, s), C.evp(B, s))
                except RecursionError:
                    continue
                tests += 1
                if got != s['x']:
                    fails[(b, slot)] += 1; shown += 1
                    if shown <= 3:
                        print('   LAW FAILS b=%d slot=%s |x|=%d |y|=%d |z|=%d'
                              % (b, slot, size(s['x']), size(s['y']), size(s['z'])), flush=True)
print('STAGE3 producer-fuzz tests %d  failures %s  TOTAL %d  %.0fs'
      % (tests, dict(fails), sum(fails.values()), time.time() - t0))
