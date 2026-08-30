"""Does the level-0 decoder location hold?   op u v != J u v  ->  a1 (a1 v) = u ?
Also probe the two size digests SZU / SZR, and which rule fires."""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf
from freemodel import size

RULES = [R1, R3]
C = cf.Closed(LAW, RULES)

def a1(t): return t[1] if t[0] == 'J' else None
def a2(t): return t[2] if t[0] == 'J' else None
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

def enc(Y, x, Z):
    return ('J', ('J', Y, ('J', ('J', x, Z), Z)), Z)

random.seed(7)
pool = [('g', i) for i in range(4)]
stats = collections.Counter()
bad = []
for it in range(60000):
    r = random.random()
    if r < 0.35 and len(pool) < 4000:
        a, b, c = (random.choice(pool) for _ in range(3))
        t = enc(a, b, c)
        if size(t) <= 200:
            pool.append(t)
    u = random.choice(pool); v = random.choice(pool)
    try:
        w = C.op(u, v)
    except RecursionError:
        continue
    free = (w[0] == 'J' and w[1] == u and w[2] == v)
    if free:
        stats['free'] += 1
        continue
    stats['fired'] += 1
    # SZR
    if not size(w) < size(v): stats['!SZR'] += 1; bad.append(('SZR', u, v))
    # SZU
    if not size(u) < size(v): stats['!SZU'] += 1; bad.append(('SZU', u, v))
    # KEY : a1 (a1 v) = u
    b = a1(a1(v)) if (v[0] == 'J' and v[1][0] == 'J') else None
    if b != u:
        stats['!KEY'] += 1
        # KEY' : op (a1 (a1 v)) v = op u v
        try:
            ok = (b is not None and C.op(b, v) == w)
        except RecursionError:
            ok = None
        stats["KEY'ok" if ok else "!KEY'"] += 1
        if len(bad) < 6: bad.append(('KEY', u, v, w, b))
    # also: which rule?  (recompute by structural check on R1)
print(stats)
for e in bad[:6]:
    print(e[0], 'u=', sh(e[1])[:120], ' v=', sh(e[2])[:200])
    if e[0] == 'KEY':
        print('   op u v =', sh(e[3])[:120], ' a1(a1 v)=', (sh(e[4])[:120] if e[4] else None))
print('pool', len(pool))
