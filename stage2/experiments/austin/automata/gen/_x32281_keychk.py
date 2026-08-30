"""In the r13 model: (a) does R2 ever fire with the outer gate product NON-free?
   (b) does 'op u v decoded  ->  u = a1 (a1 v)' hold on every decoded pair?"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf, fuzz as fz
from freemodel import size
RULES = [R1, R3]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t

C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202, 555):
    cf.deep_tests(C, LAW, 8000, 300, sd)
    fz.critical_fuzz(C, LAW, 12000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 12000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
for x in G + E1:
    for y in G + E1 + E2:
        for z in G + E1[:6]:
            try:
                P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); C.op(z, S)
            except RecursionError:
                pass
dec = [(u, v) for (u, v), w in C.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)]
print('decoded pairs:', len(dec))
cnt = collections.Counter(); bad1 = []; bad2 = []
for (u, v) in dec:
    r = C.memo[(u, v)]
    r1 = C.check(R1[0], u, v) and C.ev(R1[1], u, v) is not None
    tag = 'R1' if r1 else 'R2'
    cnt[tag] += 1
    # (b) u = a1 (a1 v)?
    ok = (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u)
    cnt[tag + (' u=a1a1v' if ok else ' **u!=a1a1v**')] += 1
    if not ok and len(bad2) < 3: bad2.append((u, v, tag))
    if tag == 'R2':
        w = a2(v); X2 = a1(a1(w))
        try:
            T1 = C.op(X2, w); T2 = C.op(T1, w); T3 = C.op(u, T2)
        except RecursionError:
            cnt['R2 recursion'] += 1; continue
        fr = (T3[0] == 'J' and T3[1] == u and T3[2] == T2)
        cnt['R2 outer-free' if fr else 'R2 **outer-DECODED**'] += 1
        if not fr and len(bad1) < 3: bad1.append((u, v))
for k in sorted(cnt): print('   %-24s %d' % (k, cnt[k]))
for u, v in bad1:
    print('R2 outer decoded:\n   u=%s\n   v=%s' % (sh(u)[:200], sh(v)[:200]))
for u, v, tag in bad2:
    print('%s u != a1(a1 v):\n   u=%s\n   v=%s' % (tag, sh(u)[:200], sh(v)[:200]))
