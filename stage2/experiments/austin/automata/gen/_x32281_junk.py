"""JUNK-VARIABLE CHECK for AF / SF / hk (the 17286 warning).

32281's reading pins u = z structurally and reads x, y out of v, so no variable is formally 'junk' --
but my earlier AF/SF pool drew x, y, z from STRUCTURED terms only (generators + chained encodings +
first components of decoded pairs, all small).  Here every slot is filled with a LARGE RANDOM term over
FRESH generators in turn, and combined with structure only where a decode actually needs it.
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
from freemodel import size
RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v

def rnd(rg, n, gens):
    """random term of about n nodes over the given generator indices"""
    if n <= 1 or rg.random() < 0.25: return g(rg.choice(gens))
    k = rg.randrange(1, max(2, n - 1))
    return J(rnd(rg, k, gens), rnd(rg, n - 1 - k, gens))

C = cf.Closed(LAW, RULES)
cnt = collections.Counter(); bad = {}
def check(x, y, z, tag):
    try:
        P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); top = C.op(z, S)
    except RecursionError:
        cnt['recursion'] += 1; return
    cnt['n'] += 1
    if not free(A, z, Q): cnt['**AF FAILS** ' + tag] += 1; bad.setdefault('AF ' + tag, (x, y, z))
    if not free(S, A, y): cnt['**SF FAILS** ' + tag] += 1; bad.setdefault('SF ' + tag, (x, y, z))
    if not free(P, x, y):
        ok = (y[0] == 'J' and y[1][0] == 'J' and y[1][1] == x)
        cnt[('hk ok ' if ok else '**hk FAILS** ') + tag] += 1
        if not ok: bad.setdefault('hk ' + tag, (x, y, z))
    if top != x: cnt['**LAW FAILS** ' + tag] += 1; bad.setdefault('LAW ' + tag, (x, y, z))

rg = random.Random(20260829)
G = [g(0), g(1), g(2)]
JG = [7, 8, 9]                       # fresh generators, appear nowhere in the structured pool
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])

# 1. pure random deep triples (all three slots junk)
for i in range(4000):
    check(rnd(rg, rg.choice([5, 11, 21, 41, 61]), [0, 1, 2] + JG),
          rnd(rg, rg.choice([5, 11, 21, 41, 61]), [0, 1, 2] + JG),
          rnd(rg, rg.choice([1, 5, 11, 31]), [0, 1, 2] + JG), 'rand')

# 2. structured y (so decodes really happen) x LARGE JUNK x, z
YS = E1 + E2
for i in range(6000):
    y = rg.choice(YS)
    check(rnd(rg, rg.choice([11, 31, 61, 91]), JG), y, rg.choice(G), 'junkX')
    check(rg.choice(G + E1), y, rnd(rg, rg.choice([11, 31, 61, 91]), JG), 'junkZ')

# 3. junk *inside* the encoding: y = enc(payload, decoder, JUNK PARAMETER) and enc(JUNK, x, w)
for i in range(4000):
    big = rnd(rg, rg.choice([11, 31, 61]), JG)
    x = rg.choice(G + E1)
    check(x, enc(rg.choice(G), x, big), rg.choice(G), 'junkParam')
    check(x, enc(big, x, rg.choice(G)), rg.choice(G), 'junkPayload')
    check(big, enc(rg.choice(G), big, rg.choice(G)), rg.choice(G), 'junkDec')

# 4. two-level encodings with junk at the bottom
for i in range(2000):
    big = rnd(rg, rg.choice([11, 31]), JG)
    x = rg.choice(G)
    inner = enc(rg.choice(G), x, big)
    check(x, enc(rg.choice(G), x, inner), rg.choice(G), 'junk2lvl')
    check(x, inner, rg.choice(G + E1), 'junk2b')

for k in sorted(cnt): print('   %-24s %d' % (k, cnt[k]))
for k, (x, y, z) in bad.items():
    print('%s FAIL:\n  x=%s\n  y=%s\n  z=%s' % (k, sh(x)[:220], sh(y)[:220], sh(z)[:220]))
