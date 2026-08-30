"""Take the ONE exceptional decoded pair (R2 fires, outer gate product decoded, u != a1(a1 v))
and run the LAW on it: x := u, y := v, z over generators and small terms."""
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
exc = [(u, v) for (u, v) in dec if not (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u)]
print('exceptional pairs:', len(exc))
ZS = G + E1[:9] + [J(g(0), g(1)), J(g(2), g(2))]
tot = 0; fails = 0
for (u, v) in exc:
    print('  u size', size(u), 'v size', size(v))
    print('  u =', sh(u)[:200])
    for z in ZS:
        try:
            P = C.op(u, v); Q = C.op(P, v); A = C.op(z, Q); S = C.op(A, v); top = C.op(z, S)
        except RecursionError:
            print('   z size %d: RECURSION' % size(z)); continue
        tot += 1
        def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
        pat = ''.join('F' if fr(*t) else 'D' for t in ((P, u, v), (Q, P, v), (A, z, Q), (S, A, v), (top, z, S)))
        ok = top == u
        if not ok: fails += 1
        print('   z size %-3d pat=%s  %s' % (size(z), pat, 'OK' if ok else '*** LAW FAILS ***'))
        if not ok:
            print('      x = %s' % sh(u))
            print('      y = %s' % sh(v))
            print('      z = %s' % sh(z))
            print('      got = %s' % sh(top)[:400])
            break
print('total', tot, 'fails', fails)
