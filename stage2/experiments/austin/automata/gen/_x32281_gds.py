"""Probe the GUARD-DECODED cells: what is C = op (op r w) w there?  Is C = r?  sz C vs sz r?
Also re-test GDS in the strict form and the sub-facts a proof would need."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf, fuzz as fz
from freemodel import size as sz

RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(p, u, w): return J(J(u, J(J(p, w), w)), w)
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def free(r, u, v): return r[0] == 'J' and r[1] == u and r[2] == v

C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202, 555, 909):
    cf.deep_tests(C, LAW, 5000, 300, sd)
    fz.critical_fuzz(C, LAW, 8000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 8000, seed=sd + 200)
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
SELF = []
for q in G + E1[:9]:
    for w in G: SELF.append(enc(q, q, w))
for q in G + E1[:4]:
    for w in G[:2]:
        e = enc(q, q, w); SELF += [enc(e, e, w), enc(e, q, w), enc(q, e, w)]
for x in G + E1 + SELF[:20]:
    for y in G + E1 + E2 + SELF:
        for z in G + E1[:6]:
            try:
                P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); C.op(z, S)
            except RecursionError: pass

dec = [(u, v) for (u, v), w in C.memo.items() if not free(w, u, v)]
cnt = collections.Counter()
for (u, v) in dec:
    r = C.memo[(u, v)]; w = a2(v)
    try:
        B = C.op(r, w); Cg = C.op(B, w); D = C.op(u, Cg)
    except RecursionError:
        cnt['recursion'] += 1; continue
    if free(D, u, Cg):
        cnt['guard free'] += 1; continue
    cnt['guard DECODED'] += 1
    cnt['  C == r' if Cg == r else '  C != r'] += 1
    cnt['  sz C <= sz r' if sz(Cg) <= sz(r) else '  **sz C > sz r**'] += 1
    cnt['  D == a1 v' if D == a1(v) else '  **D != a1 v**'] += 1
    cnt['  sz(a1 v) < sz r' if sz(a1(v)) < sz(r) else '  sz(a1 v) >= sz r'] += 1
    cnt['  B free' if free(B, r, w) else '  B DECODED'] += 1
    cnt['  C free' if free(Cg, B, w) else '  C DECODED'] += 1
    cnt['  a1(a1 v)==u' if a1(a1(v)) == u else '  **a1a1v != u**'] += 1
print('decoded pairs:', len(dec))
for k in sorted(cnt): print('   %-24s %d' % (k, cnt[k]))
