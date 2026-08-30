"""Characterise the EXCEPTION CELL: decoded (u,v) whose guard product op u C is itself decoded,
i.e. a1 (a1 v) != u.  These are exactly the residues left in SFa/SFb.  Dump their full structure
and test candidate invariants that would refute SFa's residue."""
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
def enc(a, b, c): return J(J(b, J(J(a, c), c)), c)
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
    for w in G:
        SELF.append(enc(q, q, w))
for q in G + E1[:4]:
    for w in G[:2]:
        e = enc(q, q, w)
        SELF += [enc(e, e, w), enc(e, q, w), enc(q, e, w)]
for x in G + E1 + SELF[:20]:
    for y in G + E1 + E2 + SELF:
        for z in G + E1[:6]:
            try:
                P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); C.op(z, S)
            except RecursionError:
                pass

dec = [(u, v) for (u, v), w in C.memo.items() if not free(w, u, v)]
print('decoded pairs:', len(dec))
exc = [(u, v) for (u, v) in dec if not (isJ(v) and isJ(a1(v)) and a1(a1(v)) == u)]
print('exception cells (a1(a1 v) != u):', len(exc))

inv = collections.Counter()
for (u, v) in dec:
    r = C.memo[(u, v)]; w = a2(v)
    # the uniform guard: a1 v = op u (op (op r w) w)
    try:
        Cg = C.op(C.op(r, w), w); gp = C.op(u, Cg)
    except RecursionError:
        inv['guard recursion'] += 1; continue
    inv['guard matches a1 v' if gp == a1(v) else '**guard MISMATCH**'] += 1
    inv['guard free' if free(gp, u, Cg) else 'guard DECODED'] += 1
    if a1(a1(v)) == u: inv['I1 a1a1v=u'] += 1
    else: inv['**I1 fails**'] += 1
    if sz(a1(a1(v))) <= sz(u): inv['I3 sz(a1a1v)<=sz u'] += 1
    else: inv['**I3 fails**'] += 1
    if sz(u) <= sz(a1(a1(v))): inv['I2 sz u<=sz(a1a1v)'] += 1
    else: inv['**I2 fails**'] += 1
    if sz(u) < sz(a1(v)): inv['I7 sz u<sz(a1 v)'] += 1
    else: inv['**I7 fails**'] += 1
    if sz(r) < sz(a1(v)): inv['I8 sz(op u v)<sz(a1 v)'] += 1
    else: inv['**I8 fails**'] += 1
for k in sorted(inv): print('   %-26s %d' % (k, inv[k]))

for i, (u, v) in enumerate(exc[:4]):
    r = C.memo[(u, v)]; w = a2(v)
    Cg = C.op(C.op(r, w), w); gp = C.op(u, Cg)
    print('\n=== EXCEPTION %d ===' % i)
    print(' sz u=%d sz v=%d sz(a1 v)=%d sz(a1a1 v)=%d sz(op u v)=%d sz w=%d sz C=%d' %
          (sz(u), sz(v), sz(a1(v)), sz(a1(a1(v))), sz(r), sz(w), sz(Cg)))
    print(' u        = %s' % sh(u)[:160])
    print(' a1(a1 v) = %s' % sh(a1(a1(v)))[:160])
    print(' op u v   = %s' % sh(r)[:160])
    print(' a2(a1a1v)= %s' % sh(a2(a1(a1(v))))[:160])
    print(' guard op u C == a1 v : %s   free: %s' % (gp == a1(v), free(gp, u, Cg)))
    print(' C = op (op r w) w ; op r w free: %s ; C free: %s' %
          (free(C.op(r, w), r, w), free(Cg, C.op(r, w), w)))
    # SFa residue test at this cell: is a1(a1 v) = J z (op (op x v) v) possible with x=?; here u plays P
    print(' is a1(a1 v) a J with a2 = op u v ?  %s' % (isJ(a1(a1(v))) and a2(a1(a1(v))) == r))
