"""_x38565_rules.py -- dump the extractor's full rule set for 38565 with tags."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 38565
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
X = cf.Extractor(law)
rules = X.rules()
print('full nrules', len(rules))
import pickle
for i, r in enumerate(rules):
    print('%3d %-28s %s' % (i, r[2], cf.show_rule(r)))
with open(os.path.join(HERE, '_x38565_full.pkl'), 'wb') as f:
    pickle.dump(rules, f)
