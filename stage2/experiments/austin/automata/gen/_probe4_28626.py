import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from closedform import Extractor, show_rule
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
X = Extractor(law)
rules = X.rules(exist=False)

random.seed(5)
C = cf.Closed(law, rules)
N = 200000
which_counts = {}
for i in range(N):
    y = rand_term(3); x = rand_term(3)
    C.op(y, x)
    for k in list(C.fired):
        pass
# use a fresh Closed per test to isolate which rule fires for op(y,x) specifically
whichc = {}
for i in range(N):
    y = rand_term(3); x = rand_term(3)
    Cx = cf.Closed(law, rules)
    r = Cx.op(y, x)
    if r[0] == 'J' and not Cx.fired:
        continue
    if Cx.fired:
        k = list(Cx.fired.keys())[0]
        whichc[k] = whichc.get(k, 0) + 1
print('u1=op(y,x) rule-fire distribution over', N, ':', whichc)

# same for v=op(x,z)
whichv = {}
for i in range(N):
    x = rand_term(3); z = rand_term(3)
    Cx = cf.Closed(law, rules)
    r = Cx.op(x, z)
    if Cx.fired:
        k = list(Cx.fired.keys())[0]
        whichv[k] = whichv.get(k, 0) + 1
print('v=op(x,z) rule-fire distribution over', N, ':', whichv)
