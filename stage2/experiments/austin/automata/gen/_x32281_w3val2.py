"""(a) does the 2-rule set r13 = [R1,R3(dec3)] validate?   (b) which rules actually fire?"""
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
from freemodel import size

J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

SETS = {'r13': [R1, R3], 'r135': [R1, R3, R5]}

def cell(C, x, y, z):
    P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); top = C.op(z, S)
    def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
    pat = ''.join('F' if fr(*t) else 'D' for t in ((P, x, y), (Q, P, y), (A, z, Q), (S, A, y), (top, z, S)))
    return pat, top == x

for name in ('r13', 'r135'):
    RULES = SETS[name]
    t0 = time.time()
    fails, real = report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag='%-5s FULL' % name)
    for s, r, kind, sd in real[:3]:
        print('   REAL FAIL', kind, {k: sh(v)[:90] for k, v in s.items()})
    # firing census over the deep tests
    C = cf.Closed(LAW, RULES)
    cf.deep_tests(C, LAW, 8000, 300, 555)
    print('   fired over deep8k:', {('R%d' % (i + 1)): c for i, c in sorted(C.fired.items())}, flush=True)

# case-tree with rule census, r135
RULES = SETS['r135']
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
E3 = [enc(a, b, c) for a in E2[:6] for b in G[:2] for c in G[:2]] + \
     [enc(a, b, c) for a in G[:2] for b in E2[:6] for c in G[:2]] + \
     [enc(a, b, c) for a in G[:2] for b in G[:2] for c in E2[:6]]
cnt = collections.Counter(); bad = []
C = cf.Closed(LAW, RULES)
t0 = time.time()
for x in G + E1 + E2[:12]:
    for y in G + E1 + E2 + E3:
        for z in G + E1[:6]:
            try:
                pat, ok = cell(C, x, y, z)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            if not ok and len(bad) < 5: bad.append((x, y, z, pat))
print('deep case tree (%.1fs):' % (time.time() - t0))
for k in sorted(cnt): print('   %-14s %d' % (k, cnt[k]))
print('   fired:', {('R%d' % (i + 1)): c for i, c in sorted(C.fired.items())})
for x, y, z, pat in bad:
    print('FAIL pat=%s\n   x=%s\n   y=%s\n   z=%s' % (pat, sh(x)[:200], sh(y)[:200], sh(z)[:200]))
