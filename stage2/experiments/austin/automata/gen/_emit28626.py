import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import leangen
from closedform import Extractor
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = Extractor(law)
rules = X.rules(exist=False)
print('nrules', len(rules))
res = leangen.emit(EQ, os.path.dirname(os.path.abspath(__file__)), rules_override=rules)
print(json.dumps(res))
