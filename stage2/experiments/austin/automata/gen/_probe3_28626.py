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

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

random.seed(3)
C = cf.Closed(law, rules)
N = 50000
c1=c2=c3=cv=0
for i in range(N):
    y = rand_term(3)
    x = y  # x = y forced
    z = rand_term(3)
    u1 = C.op(y, x)
    if u1[0] != 'J': c1 += 1
    u2 = C.op(u1, y)
    if u2[0] != 'J': c2 += 1; print('u2 nonfire with x=y', show(y))
    u3 = C.op(u2, y)
    if u3[0] != 'J': c3 += 1
print('x=y test: N', N, 'u1 nonfree', c1, 'u2 nonfree', c2, 'u3 nonfree', c3)

# also test whole law with x=y forced (does law still hold, via full C.evp)
C2 = cf.Closed(law, rules)
A, B = law[1]
fails = 0
for i in range(20000):
    y = rand_term(3); x = y; z = rand_term(3)
    s = {'x': x, 'y': y, 'z': z}
    lhs = C2.op(C2.evp(A, s), C2.evp(B, s))
    if lhs != x: fails += 1
print('x=y forced, law check over 20000: fails', fails)
