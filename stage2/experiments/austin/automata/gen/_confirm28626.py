import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from closedform import Extractor
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
A, B = law[1]
X = Extractor(law)
rules = X.rules(exist=False)
C = cf.Closed(law, rules)

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

# minimal instance
w = ('g', 0)
y = ('J', ('J', ('J', w, ('g',1)), w), w)
x = ('J', ('J', ('g',1), y), y)
z = x
s = {'x': x, 'y': y, 'z': z}
lhs = C.op(C.evp(A,s), C.evp(B,s))
print('minimal instance:', 'OK' if lhs==x else 'FAIL')

# original seed-21 instance
y0 = ('J', ('J', ('J', ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))), ('g', 1)), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1)))), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))))
x0 = ('J', ('J', ('g', 1), ('J', ('J', ('J', ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))), ('g', 1)), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1)))), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))))), ('J', ('J', ('J', ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1))), ('g', 1)), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1)))), ('J', ('J', ('J', ('g', 1), ('g', 1)), ('g', 0)), ('J', ('g', 1), ('g', 1)))))
z0 = x0
s0 = {'x': x0, 'y': y0, 'z': z0}
C2 = cf.Closed(law, rules)
lhs0 = C2.op(C2.evp(A,s0), C2.evp(B,s0))
print('original seed21 instance:', 'OK' if lhs0==x0 else 'FAIL')
