import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
import fuzz as fz
from closedform import Extractor, show_rule
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = Extractor(law)
rules = X.rules(exist=False)
C = cf.Closed(law, rules)
cf.deep_tests(C, law, 20000, 200, 21)
cf.deep_tests(C, law, 20000, 200, 3)
fz.fuzz(C, law, rules, 20000, seed=11)
fz.closure_fuzz(C, law, 20000, seed=13)
fz.critical_fuzz(C, law, 20000, seed=17)
print('fired:', C.fired)
for i, r in enumerate(rules):
    print(i, 'fired', C.fired.get(i,0), show_rule(r))
