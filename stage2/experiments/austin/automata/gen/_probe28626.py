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

random.seed(1)
C = cf.Closed(law, rules)
# Test: is op(op(W,y),y) ALWAYS free for random W,y?  (the outer "*y)*y" chain)
nonfree_outer = 0
nonfree_inner1 = 0  # op(y,x)
nonfree_v = 0  # op(x,z)
N = 30000
for i in range(N):
    W = rand_term(3)
    y = rand_term(3)
    x = rand_term(3)
    z = rand_term(3)
    u1 = C.op(y, x)
    if u1[0] != 'J' or C.fired:
        pass
    r1 = C.op(W, y)
    r2 = C.op(r1, y)
    if r2[0] != 'J' or C.check(rules[0][0], r1, y) or any(C.check(rl[0], r1, y) for rl in rules):
        nonfree_outer += 1
    if any(C.check(rl[0], y, x) for rl in rules):
        nonfree_inner1 += 1
    if any(C.check(rl[0], x, z) for rl in rules):
        nonfree_v += 1

print('N', N, 'nonfree_outer(op(op(W,y),y) matches a rule)', nonfree_outer,
      'nonfree_inner1(op(y,x) matches a rule)', nonfree_inner1,
      'nonfree_v(op(x,z) matches a rule)', nonfree_v)
