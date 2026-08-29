import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chk28626.py')
src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns)
rules = ns['rules']
A, B = law[1]

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def test(c, y, verbose=False):
    C = cf.Closed(law, rules)
    x = ('J', ('J', c, y), y)
    z = x
    s = {'x': x, 'y': y, 'z': z}
    lhs = C.op(C.evp(A, s), C.evp(B, s))
    ok = (lhs == x)
    if verbose or not ok:
        print('c=', show(c), 'y=', show(y), 'OK' if ok else 'FAIL got=%s' % (show(lhs) if size(lhs) < 120 else '<size %d>' % size(lhs)))
    return ok

w = ('g', 0)
y = ('J', ('J', ('J', w, ('g',1)), w), w)
for c in [('g',0), ('g',1), ('g',2), ('J',('g',0),('g',1)), ('J',('g',2),('g',1)), y]:
    test(c, y)

print('--- vary y shape: does y need the exact self-embed structure? ---')
for y2 in [('g',0), ('J',('g',0),('g',1)), ('J',('J',('g',0),('g',1)),('g',2)), ('J',('g',0),('J',('g',1),('g',2)))]:
    test(('g',1), y2)
