"""Wave-3 FULL validation of the 2-rule set r13 = [R1(free), R3(dec3)] for law 32281."""
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
import closedform as cf, fuzz as fz
from freemodel import size

RULES = [R1, R3]
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)
def enc(xv, zv, yv): return J(J(zv, J(J(xv, yv), yv)), yv)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

# 1. run_tests on fresh seeds
for seeds in ((7, 8, 9), (77, 78, 79)):
    report(LAW, RULES, seeds=seeds, N=3000, NF=12000, tag='r13 %s' % (seeds,))

# 2. deep 20k on 5 fresh seeds
for sd in (111, 222, 333, 444, 555):
    C = cf.Closed(LAW, RULES)
    t, f = cf.deep_tests(C, LAW, 20000, 400, sd)
    print('deep20k seed %d: tested %d fails %d cycles %d fired %s' % (
        sd, t, len(f), len(f), C.cycles, ), flush=True)
    print('    fired', {('R%d' % (i + 1)): c for i, c in sorted(C.fired.items())}, flush=True)

# 3. hierarchy attack: every pair the model DECODES re-used as (x, y)
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
print('attack: decoded pairs collected:', len(fired), flush=True)
gens = [('g', i) for i in range(3)]
cur = sorted(fired, key=lambda p: size(p[0]) + size(p[1]))
for rnd in range(3):
    fails = []; cnt = collections.Counter()
    C2 = cf.Closed(LAW, RULES)
    for (x, Z) in cur[:4000]:
        for Y in gens:
            try:
                pat, ok = law_ok(C2, x, Y, Z)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            if not ok: fails.append((x, Y, Z))
    print('attack round %d over %d pairs: %s' % (rnd, min(len(cur), 4000), dict(cnt)), flush=True)
    if fails:
        x, Y, Z = fails[0]
        print('   FIRST FAIL x=%s\n     Y=%s\n     Z=%s' % (sh(x)[:200], sh(Y)[:200], sh(Z)[:200]))
        break
    nxt = [(u, v) for (u, v), w in C2.memo.items() if not (w[0] == 'J' and w[1] == u and w[2] == v)]
    nxt = [p for p in nxt if p not in set(cur)]
    nxt.sort(key=lambda p: size(p[0]) + size(p[1]))
    print('   new decoded pairs:', len(nxt), flush=True)
    if not nxt: break
    cur = nxt

# 4. deep case tree, 3 levels of chained encoding
G = [g(0), g(1), g(2)]
E1 = [enc(a, b, c) for a in G for b in G for c in G]
E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
      [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
      [enc(a, b, c) for a in G for b in G for c in E1[:9]])
E3 = ([enc(a, b, c) for a in E2[:8] for b in G[:2] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in E2[:8] for c in G[:2]] +
      [enc(a, b, c) for a in G[:2] for b in G[:2] for c in E2[:8]])
cnt = collections.Counter(); bad = []
C = cf.Closed(LAW, RULES)
t0 = time.time()
for x in G + E1 + E2[:12]:
    for y in G + E1 + E2 + E3:
        for z in G + E1[:6]:
            try:
                pat, ok = law_ok(C, x, z, y)   # law_ok(C, x, Y=z, Z=y)
            except RecursionError:
                cnt['recursion'] += 1; continue
            cnt[pat + ('' if ok else ' **FAIL**')] += 1
            if not ok and len(bad) < 5: bad.append((x, y, z, pat))
print('case tree (%.1fs):' % (time.time() - t0))
for k in sorted(cnt): print('   %-14s %d' % (k, cnt[k]))
print('   fired:', {('R%d' % (i + 1)): c for i, c in sorted(C.fired.items())})
for x, y, z, pat in bad:
    print('FAIL pat=%s\n   x=%s\n   y=%s\n   z=%s' % (pat, sh(x)[:200], sh(y)[:200], sh(z)[:200]))
print('DONE')
