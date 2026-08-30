"""Candidate-invariant hunt over every decoded pair the model builds (corrected pool).
The residues left in SFa/SFb are exactly the GUARD-DECODED cells; find the invariant that kills them."""
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
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t
def isJ(t): return t[0] == 'J'
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
cnt = collections.Counter(); bad = collections.defaultdict(list)
def note(k, ok, u, v):
    cnt[k if ok else '**' + k + ' FAILS**'] += 1
    if not ok and len(bad[k]) < 2: bad[k].append((u, v))
for (u, v) in dec:
    r = C.memo[(u, v)]; A11 = a1(a1(v))
    note('L1 op u v != u', r != u, u, v)
    note('L2 a1(a1 v) != op u v', A11 != r, u, v)
    note('L2t tg(a1 v)=2 -> a1(a1 v) != op u v', not (isJ(a1(v)) and A11 == r), u, v)
    note('L3 GDS: a1a1v=u or sz(a1 v)<=sz r', A11 == u or sz(a1(v)) <= sz(r), u, v)
    note('L4 a1 v != op u v', a1(v) != r, u, v)
    note('L5 sz(a1a1 v) <= sz r or a1a1v=u', A11 == u or sz(A11) <= sz(r), u, v)
    note('L6 a1a1v=u or tg(a1 v)!=2', A11 == u or not isJ(a1(v)), u, v)
print('decoded pairs:', len(dec))
for k in sorted(cnt): print('   %-42s %d' % (k, cnt[k]))
for k, lst in bad.items():
    for (u, v) in lst:
        r = C.memo[(u, v)]
        print('\n%s counterexample: sz u=%d sz v=%d sz(a1 v)=%d sz(a1a1v)=%d sz r=%d' %
              (k, sz(u), sz(v), sz(a1(v)), sz(a1(a1(v))), sz(r)))
        print('  u =%s\n  a1(a1 v)=%s\n  r =%s' % (sh(u)[:140], sh(a1(a1(v)))[:140], sh(r)[:140]))
