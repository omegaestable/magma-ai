"""Which RULE fires at each product of the law's chain, for r13?  (P,Q,A,S,top)"""
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

def which(C, u, v):
    """'F' if free, else '1'/'2' for the rule index that fires"""
    r = C.op(u, v)
    if r[0] == 'J' and r[1] == u and r[2] == v:
        # could still be rule-produced; check by re-running the rule tests
        pass
    for i, (conds, xe, tag) in enumerate(RULES):
        if C.check(conds, u, v):
            e = C.ev(xe, u, v)
            if e is not None:
                return str(i + 1), r
    return 'F', r

def chain(C, x, y, z):
    out = []
    P = C.op(x, y); out.append(which(C, x, y)[0])
    Q = C.op(P, y); out.append(which(C, P, y)[0])
    A = C.op(z, Q); out.append(which(C, z, Q)[0])
    S = C.op(A, y); out.append(which(C, A, y)[0])
    top = C.op(z, S); out.append(which(C, z, S)[0])
    return ''.join(out), top == x, (P, Q, A, S, top)

# pool: chained encodings + adversarial decoded pairs
C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202):
    cf.deep_tests(C, LAW, 4000, 200, sd)
    fz.critical_fuzz(C, LAW, 6000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 6000, seed=sd + 200)
pairs = [(u, v) for (u, v), w in C.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)]
pairs.sort(key=lambda p: size(p[0]) + size(p[1]))
gens = [g(0), g(1), g(2)]
cnt = collections.Counter(); ex = {}
C2 = cf.Closed(LAW, RULES)
for (x, Z) in pairs[:6000]:
    for Y in gens:
        try:
            pat, ok, vals = chain(C2, x, Z, Y)
        except RecursionError:
            cnt['recursion'] += 1; continue
        cnt[pat + ('' if ok else ' **FAIL**')] += 1
        ex.setdefault(pat, (x, Z, Y, vals))
G = gens
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
for x in G + E1:
    for y in G + E1 + E2:
        for z in G + E1[:6]:
            try:
                pat, ok, vals = chain(C2, x, y, z)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            ex.setdefault(pat, (x, y, z, vals))
print('chain rule-census (P,Q,A,S,top):')
for k in sorted(cnt): print('   %-14s %d' % (k, cnt[k]))
for k in sorted(ex):
    x, y, z, vals = ex[k]
    print('%-8s x=%s' % (k, sh(x)[:120]))
    print('         y=%s' % sh(y)[:120])
    print('         Q=%s  A=%s  S=%s' % (sh(vals[1])[:60], sh(vals[2])[:60], sh(vals[3])[:60]))
