"""Full validation of the 10-rule set that rec28626.lean was emitted from.

Law 28626: x = (((y*x)*y)*y)*(x*z)  -- both-compound, dualized == False.
Rules: Extractor(law).rules(exist=False)  (10 rules; NOT minimised -- rail: never minimise
both-compound sets by firing counts).
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, revalidate as rv, leangen
from closedform import Extractor, show_rule
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
print('law', cat[EQ], 'dualized', dualized)

X = Extractor(law)
rules = X.rules(exist=False)
print('nrules', len(rules))
for i, r in enumerate(rules):
    print(' R%d' % (i + 1), show_rule(r))

t0 = time.time()
fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
real = [f for f in fails if f[1] != 'recursion']
print('run_tests fails', len(fails), 'real', len(real), 'secs', round(time.time() - t0, 1))
for f in fails[:6]:
    print('  FAIL', f[2], 'seed', f[3])

for sd in (21, 77, 78):
    t0 = time.time()
    C = cf.Closed(law, rules)
    t, f = cf.deep_tests(C, law, 20000, 600, sd)
    fr = [q for q in f if q[1] != 'recursion']
    print('deep_tests seed', sd, 'tested', t, 'fails', len(f), 'real', len(fr), 'secs', round(time.time() - t0, 1))
