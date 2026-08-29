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

random.seed(2)
C = cf.Closed(law, rules)
N = 100000
c1 = c2 = c3 = cv = 0
for i in range(N):
    y = rand_term(3); x = rand_term(3); z = rand_term(3)
    u1 = C.op(y, x)
    if u1[0] != 'J': c1 += 1
    u2 = C.op(u1, y)
    if u2[0] != 'J': c2 += 1
    u3 = C.op(u2, y)
    if u3[0] != 'J': c3 += 1
    v = C.op(x, z)
    if v[0] != 'J': cv += 1

print('N', N, 'u1 nonfree', c1, 'u2 nonfree', c2, 'u3 nonfree', c3, 'v nonfree', cv)
