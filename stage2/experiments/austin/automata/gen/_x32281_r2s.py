"""32281: strengthen R3(dec3) to its STRUCTURAL form R2s -- require the outer product of the
gate to be the FREE product  v.1 = J(u, T2)  instead of  op(u,T2) = v.1.
If [R1,R2s] still validates, the Lean proof gets the invariant  'P decoded -> x = a1(a1 y)'  for free."""
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf, fuzz as fz
from freemodel import size

ZZ = A2(V)                 # w = a2 v
X2 = A1(A1(ZZ))            # a1 (a1 w)
T2 = OP(OP(X2, ZZ), ZZ)

# structural: v.1 = J u T2   <=>   tg (a1 v) = 2  &  u = a1 (a1 v)  &  a2 (a1 v) = T2
R2s = ([TG(V), TG(ZZ), TG(A1(ZZ)), TG(A1(V)), EQ_(U, A1(A1(V))), OPEQ(T2, A2(A1(V)))], X2, 'dec3s')

RULES = [R1, R2s]
J = lambda a, b: ('J', a, b); g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

for r in RULES: print(cf.show_rule(r))
for seeds in ((3, 4, 5), (7, 8, 9)):
    report(LAW, RULES, seeds=seeds, N=3000, NF=12000, tag='r1+r2s %s' % (seeds,))
for sd in (111, 222, 333):
    C = cf.Closed(LAW, RULES)
    t, f = cf.deep_tests(C, LAW, 20000, 400, sd)
    print('deep20k seed %d: tested %d fails %d fired %s' % (sd, t, len(f), {('R%d' % (i+1)): c for i, c in sorted(C.fired.items())}), flush=True)

def law_ok(C, x, Y, Z):
    P = C.op(x, Z); Q = C.op(P, Z); A = C.op(Y, Q); S = C.op(A, Z); top = C.op(Y, S)
    def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
    pat = ''.join('F' if fr(*t) else 'D' for t in ((P, x, Z), (Q, P, Z), (A, Y, Q), (S, A, Z), (top, Y, S)))
    return pat, top == x

C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202):
    cf.deep_tests(C, LAW, 6000, 200, sd)
    fz.critical_fuzz(C, LAW, 8000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 8000, seed=sd + 200)
fired = [(u, v) for (u, v), w in C.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)]
print('attack: decoded pairs', len(fired), flush=True)
gens = [g(0), g(1), g(2)]
cur = sorted(fired, key=lambda p: size(p[0]) + size(p[1]))
for rnd in range(3):
    fails = []; cnt = collections.Counter(); C2 = cf.Closed(LAW, RULES)
    for (x, Z) in cur[:4000]:
        for Y in gens:
            try:
                pat, ok = law_ok(C2, x, Y, Z)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            if not ok: fails.append((x, Y, Z))
    print('attack round %d: %s' % (rnd, dict(cnt)), flush=True)
    if fails:
        x, Y, Z = fails[0]
        print('  FIRST FAIL\n   x=%s\n   Y=%s\n   Z=%s' % (sh(x)[:200], sh(Y)[:200], sh(Z)[:200])); break
    nxt = [p for p in [(u, v) for (u, v), w in C2.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)] if p not in set(cur)]
    nxt.sort(key=lambda p: size(p[0]) + size(p[1]))
    print('   new pairs', len(nxt), flush=True)
    if not nxt: break
    cur = nxt

G = gens
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
E3 = ([enc(a, b, c) for a in E2[:8] for b in G[:2] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in E2[:8] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in G[:2] for c in E2[:8]])
cnt = collections.Counter(); bad = []
C = cf.Closed(LAW, RULES)
for x in G + E1 + E2[:12]:
    for y in G + E1 + E2 + E3:
        for z in G + E1[:6]:
            try:
                pat, ok = law_ok(C, x, z, y)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            if not ok and len(bad) < 3: bad.append((x, y, z, pat))
print('case tree:')
for k in sorted(cnt): print('   %-14s %d' % (k, cnt[k]))
print('   fired:', {('R%d' % (i + 1)): c for i, c in sorted(C.fired.items())})
for x, y, z, pat in bad:
    print('FAIL pat=%s\n  x=%s\n  y=%s\n  z=%s' % (pat, sh(x)[:200], sh(y)[:200], sh(z)[:200]))
print('DONE')
