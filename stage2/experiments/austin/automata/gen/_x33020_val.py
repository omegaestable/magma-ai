"""_x33020_val.py : FULL validation standard for the repaired 33020/12883 rule set.

rv.run_tests(law, rules, [3,4,5], 3000, 12000) == []   plus cf.deep_tests 20000 on two more seeds.
Law is R-form (33020 = x = A * y), so the modelled law is the dualised one = 12883 (L-form).
Rules are taken from gen/repair33020/chk33020.py (the emitted package), literal only.
Run: python gen/_x33020_val.py [which]
"""
import sys, os, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 33020
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('dualized =', dualized)
print('law modelled =', law)
print('12883 normalised =', normalise(parse_eq(cat[12883])))
assert law == normalise(parse_eq(cat[12883])), 'the dualised 33020 should be 12883'

src = open(os.path.join(HERE, 'repair33020', 'chk33020.py'), encoding='utf-8').read()
ns = {}
exec(src[src.index('rules = '):src.index('C = cf.Closed')], {'cf': cf}, ns)
rules = ns['rules']
print('nrules =', len(rules))
for r in rules:
    print('  ', cf.show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
val = [f for f in fails if f[1] != 'recursion' and (len(f) < 3 or not str(f[2]).startswith('recursion'))]
print('\nrun_tests: %d fails (%.1fs)' % (len(fails), time.time() - t0))
kinds = {}
for f in fails:
    k = f[2] if len(f) > 2 else '?'
    kinds[k] = kinds.get(k, 0) + 1
print('  kinds:', kinds)
for f in fails[:5]:
    print('  ', f)

for seed in (101, 202, 303):
    C = cf.Closed(law, rules)
    t0 = time.time()
    tested, df = cf.deep_tests(C, law, 20000, 300, seed)
    nv = [d for d in df if d[1] != 'recursion']
    print('deep 20000 seed %d: tested %d fails %d (non-recursion %d) %.1fs' % (seed, tested, len(df), len(nv), time.time() - t0))
    for d in nv[:2]:
        print('   ', {k: size(t) for k, t in d[0].items()})
