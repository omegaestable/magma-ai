"""Are AF ('A = op z (op (op x y) y) is always free') and SF ('op (J z Q) y is free') TRUE for r135?
And how often does hk ('op x y decoded -> tg y = 2 & tg (a1 y) = 2 & a1 (a1 y) = x') fail?"""
import sys, os, collections
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
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v

C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202, 555, 909):
    cf.deep_tests(C, LAW, 6000, 300, sd)
    fz.critical_fuzz(C, LAW, 9000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 9000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
E3 = ([enc(a, b, c) for a in E2[:6] for b in G[:2] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in E2[:6] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in G[:2] for c in E2[:6]])
pairs = sorted([(u, v) for (u, v), w in C.memo.items() if not free(w, u, v)],
               key=lambda p: size(p[0]) + size(p[1]))

cnt = collections.Counter(); bad = {}
def check(x, y, z):
    P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); top = C.op(z, S)
    cnt['n'] += 1
    if not free(A, z, Q):
        cnt['**AF FAILS**'] += 1; bad.setdefault('AF', (x, y, z))
    if not free(S, A, y):
        cnt['**SF FAILS**'] += 1; bad.setdefault('SF', (x, y, z))
    if not free(P, x, y):
        ok = (y[0] == 'J' and y[1][0] == 'J' and y[1][1] == x)
        cnt['hk ok' if ok else '**hk FAILS**'] += 1
        if not ok: bad.setdefault('hk', (x, y, z))
    if top != x:
        cnt['**LAW FAILS**'] += 1; bad.setdefault('LAW', (x, y, z))

# (i) chained-encoding triples
for x in G + E1 + E2[:12]:
    for y in G + E1 + E2 + E3:
        for z in G + E1[:6]:
            try: check(x, y, z)
            except RecursionError: cnt['recursion'] += 1
# (ii) every decoded pair reused as (x,y), z over generators AND over decoded first components
zs = G + [p[0] for p in pairs[:40]]
for (x, y) in pairs[:5000]:
    for z in zs[:8]:
        try: check(x, y, z)
        except RecursionError: cnt['recursion'] += 1
for k in sorted(cnt): print('   %-16s %d' % (k, cnt[k]))
for k, (x, y, z) in bad.items():
    print('%s FAIL:\n  x=%s\n  y=%s\n  z=%s' % (k, sh(x)[:200], sh(y)[:200], sh(z)[:200]))
