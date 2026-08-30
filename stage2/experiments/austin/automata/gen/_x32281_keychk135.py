"""r135: does 'op u v decoded -> u = a1 (a1 v)' hold on every decoded pair?  (the r13 census found 1 exception)"""
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
def P(s):
    s = s.strip()
    if s.startswith('g'): return ('g', int(s[1:]))
    d = 0
    for i, ch in enumerate(s[1:-1], 1):
        if ch == '(': d += 1
        elif ch == ')': d -= 1
        elif ch == '*' and d == 0: return ('J', P(s[1:i]), P(s[i+1:-1]))
    raise ValueError(s)

C = cf.Closed(LAW, RULES)
# the r13 exceptional pair, replayed in r135
XU = P('(g2*g2)')
XV = P('((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(((((g2*g2)*(((((g2*g2)*((g2*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2))*(g2*g2))*(g2*g2)))*(g2*g2)))')
r = C.op(XU, XV)
print('r13-exceptional pair under r135: decoded=%s  u==a1(a1 v)=%s  result=%s' % (
    not (r[0] == 'J' and r[1] == XU and r[2] == XV), XV[1][1] == XU, sh(r)[:80]))

for sd in (3, 4, 202, 555, 909):
    cf.deep_tests(C, LAW, 6000, 300, sd)
    fz.critical_fuzz(C, LAW, 9000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 9000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
for x in G + E1:
    for y in G + E1 + E2:
        for z in G + E1[:6]:
            try:
                p = C.op(x, y); q = C.op(p, y); a = C.op(z, q); s = C.op(a, y); C.op(z, s)
            except RecursionError:
                pass
dec = [(u, v) for (u, v), w in C.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)]
cnt = collections.Counter(); bad = []
for (u, v) in dec:
    ok = (v[0] == 'J' and v[1][0] == 'J' and v[1][1] == u)
    cnt['ok' if ok else '**u != a1(a1 v)**'] += 1
    if not ok and len(bad) < 3: bad.append((u, v))
print('decoded pairs:', len(dec))
for k in sorted(cnt): print('   %-22s %d' % (k, cnt[k]))
for u, v in bad:
    print('EXC:\n  u=%s\n  v=%s\n  result=%s' % (sh(u)[:200], sh(v)[:200], sh(C.memo[(u, v)])[:200]))
