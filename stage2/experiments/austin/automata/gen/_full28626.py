import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf
from closedform import Extractor, Closed, show_rule
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 28626
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = orig
A, B = law[1]

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

w = ('g', 0)
y = ('J', ('J', ('J', w, ('g',1)), w), w)
x = ('J', ('J', ('g',1), y), y)
z = x
s = {'x': x, 'y': y, 'z': z}

t0 = time.time()
X = Extractor(law)
full_rules = X.rules(exist=False)
print('exist=False rules:', len(full_rules), 'secs', round(time.time()-t0,1))
C = Closed(law, full_rules)
lhs = C.op(C.evp(A,s), C.evp(B,s))
print('full(exist=False) result:', 'OK' if lhs==x else 'FAIL got %s' % (show(lhs) if size(lhs)<150 else '<size %d>'%size(lhs)))
if lhs == x:
    # which rule fired at the top?
    print('fired counts:', C.fired)

t0 = time.time()
X2 = Extractor(law)
full_rules2 = X2.rules(exist=True)
print('exist=True rules:', len(full_rules2), 'secs', round(time.time()-t0,1))
C2 = Closed(law, full_rules2)
lhs2 = C2.op(C2.evp(A,s), C2.evp(B,s))
print('full(exist=True) result:', 'OK' if lhs2==x else 'FAIL got %s' % (show(lhs2) if size(lhs2)<150 else '<size %d>'%size(lhs2)))

print("--- all exist=False rules ---")
for i, r in enumerate(full_rules):
    print(i, show_rule(r))
