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

random.seed(9)
found = None
for i in range(300000):
    y = rand_term(3); x = rand_term(3)
    Cx = cf.Closed(law, rules)
    r = Cx.op(y, x)
    if Cx.fired:
        found = (y, x)
        break
print('found y,x with u1 nonfree:', show(found[0]), show(found[1]) if found else None)
y, x = found
C = cf.Closed(law, rules)
u1 = C.op(y, x)
print('u1 =', show(u1), 'fired', C.fired)
u2 = C.op(u1, y)
print('u2 =', show(u2), 'fired', C.fired)
u3 = C.op(u2, y)
print('u3 =', show(u3), 'fired', C.fired)
z = rand_term(2)
v = C.op(x, z)
print('v =', show(v), 'fired', C.fired)
final = C.op(u3, v)
print('final =', show(final), 'expect x=', show(x), 'match', final == x, 'fired', C.fired)
