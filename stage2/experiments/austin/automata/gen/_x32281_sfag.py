"""Is the GENERALISED SFa true?   tg y = 2 -> a1 (a1 y) = op z (op (op x y) y) -> False.
Pool corrected per the AF refutation: encodings whose payload slot and decoder slot hold the SAME
non-generator term, nested self-encodings, plus the old structured/random pools.
Also censuses the generalised SFb hypothesis and the exception cells."""
import sys, os, collections, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf, fuzz as fz
from freemodel import size as sz

RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(p, u, w): return J(J(u, J(J(p, w), w)), w)   # payload p, decoder u, filler w
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def isJ(t): return t[0] == 'J'
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v

C = cf.Closed(LAW, RULES)
G = [g(i) for i in range(5)]
E1 = [enc(a, b, c) for a in G[:3] for b in G[:3] for c in G[:3]]
# --- the corrected pool: payload == decoder, and nested self-encodings ---
SELF = []
for q in G[:4] + E1[:9]:
    for w in G[:4]:
        SELF.append(enc(q, q, w))                    # payload slot == decoder slot
for q in G[:3] + E1[:6]:
    for w in G[:3]:
        e = enc(q, q, w)
        SELF.append(enc(e, e, w))                    # nested self-encoding
        SELF.append(enc(e, q, w)); SELF.append(enc(q, e, w))
E2 = ([enc(a, b, c) for a in E1[:9] for b in G[:3] for c in G[:3]] +
      [enc(a, b, c) for a in G[:3] for b in E1[:9] for c in G[:3]] +
      [enc(a, b, c) for a in G[:3] for b in G[:3] for c in E1[:9]])
rnd = random.Random(20260830)
def rt(d):
    if d <= 0 or rnd.random() < 0.3: return g(rnd.randrange(6))
    return J(rt(d - 1), rt(d - 1))
RND = [rt(rnd.randrange(1, 6)) for _ in range(300)]

cnt = collections.Counter(); bad = []
def check(x, y, z):
    cnt['n'] += 1
    if not isJ(y): return
    A11 = a1(a1(y))
    P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q)
    if A11 == A:
        cnt['**SFag FAILS**'] += 1
        if len(bad) < 5: bad.append((x, y, z))
    if not free(A, z, Q): cnt['A decoded (old AF fails)'] += 1

pool_y = G + E1 + SELF + E2[:60] + RND[:120]
pool_x = G[:3] + E1[:9] + SELF[:40] + RND[:40]
pool_z = G[:3] + E1[:4] + SELF[:12]
for x in pool_x:
    for y in pool_y:
        for z in pool_z:
            try: check(x, y, z)
            except RecursionError: cnt['recursion'] += 1

# every memo pair reused as (x,y) with a spread of z
zs = G[:3] + E1[:3] + SELF[:6]
keys = list(C.memo.keys())
print('memo pairs after pool sweep:', len(keys))
for (x, y) in keys[:6000]:
    for z in zs:
        try: check(x, y, z)
        except RecursionError: cnt['recursion'] += 1

for k in sorted(cnt): print('   %-26s %d' % (k, cnt[k]))
for x, y, z in bad:
    print('SFag FAIL:\n  x=%s\n  y=%s\n  z=%s' % (sh(x)[:300], sh(y)[:300], sh(z)[:300]))
