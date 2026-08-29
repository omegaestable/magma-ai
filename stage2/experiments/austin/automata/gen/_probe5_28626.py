import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from closedform import Extractor
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = Extractor(law)
rules = X.rules(exist=False)

random.seed(6)
N = 60000
whichv = {}
for i in range(N):
    x = rand_term(3); z = rand_term(3)
    Cx = cf.Closed(law, rules)
    r = Cx.op(x, z)
    if Cx.fired:
        k = list(Cx.fired.keys())[0]
        whichv[k] = whichv.get(k, 0) + 1
print('v=op(x,z) rule-fire distribution over', N, ':', whichv)
