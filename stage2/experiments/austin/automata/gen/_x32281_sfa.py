"""Is SFa TRUE?  SFa: tg y = 2 -> a1 (a1 y) = J z (op (op x y) y) -> False.
For a given (x,y) this is falsifiable iff tg (a1 (a1 y)) = 2 and a2 (a1 (a1 y)) = op (op x y) y
(then z := a1 (a1 (a1 y)) is a witness).  Also censuses the residues SFa's proof leaves open."""
import sys, os, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf, fuzz as fz
from freemodel import size

RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def isJ(t): return t[0] == 'J'
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v

C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202, 555, 909):
    cf.deep_tests(C, LAW, 4000, 300, sd)
    fz.critical_fuzz(C, LAW, 6000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 6000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
E3 = ([enc(a, b, c) for a in E2[:8] for b in G[:2] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in E2[:8] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in G[:2] for c in E2[:8]])

rnd = random.Random(20260830)
def rt(d):
    if d <= 0 or rnd.random() < 0.3: return g(rnd.randrange(10))
    return J(rt(d - 1), rt(d - 1))
RND = [rt(rnd.randrange(1, 6)) for _ in range(400)]

cnt = collections.Counter(); bad = []
def check(x, y):
    cnt['n'] += 1
    if not isJ(y): return
    A11 = a1(a1(y))
    if not isJ(A11): return
    P = C.op(x, y); Q = C.op(P, y)
    if a2(A11) == Q:
        cnt['**SFa FAILS**'] += 1
        if len(bad) < 3: bad.append((x, y, a1(A11)))
    else:
        cnt['sfa ok (a1a1y is J)'] += 1

pool_y = G + E1 + E2 + E3 + RND
pool_x = G + E1 + E2[:20] + RND[:80]
for x in pool_x:
    for y in pool_y:
        try: check(x, y)
        except RecursionError: cnt['recursion'] += 1

# also: every decoded pair the model built, reused as (x,y)
dec = [(u, v) for (u, v), w in C.memo.items() if not free(w, u, v)]
print('decoded pairs in memo:', len(dec))
for (x, y) in dec:
    try: check(x, y)
    except RecursionError: cnt['recursion'] += 1
# and every memo pair at all (free ones too)
for (x, y) in list(C.memo.keys()):
    try: check(x, y)
    except RecursionError: cnt['recursion'] += 1

for k in sorted(cnt): print('   %-24s %d' % (k, cnt[k]))
for x, y, z in bad:
    print('SFa FAIL:\n  x=%s\n  y=%s\n  z=%s' % (sh(x)[:300], sh(y)[:300], sh(z)[:300]))
