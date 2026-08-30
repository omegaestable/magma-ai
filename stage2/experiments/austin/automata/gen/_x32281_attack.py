"""Generic hierarchy attack: take every pair the model DECODES and re-use it as (x, Z).
Iterate: the survivors of round k feed round k+1.  Usage: python _x32281_attack.py <ruleset>
   ruleset in {r13, r134, r135}
"""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
import closedform as cf, fuzz as fz
from freemodel import size

from _x32281_try1 import R1, R2
from _x32281_try2 import R3
from _x32281_try4 import R4
from _x32281_try5 import R5

SETS = {'r12': [R1, R2], 'r13': [R1, R3], 'r134': [R1, R3, R4], 'r135': [R1, R3, R5],
        'r1345': [R1, R3, R4, R5]}
name = sys.argv[1] if len(sys.argv) > 1 else 'r13'
RULES = SETS[name]

def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(' + sh(t[1]) + '*' + sh(t[2]) + ')'

def law_ok(C, x, Y, Z):
    P = C.op(x, Z); Q = C.op(P, Z); R = C.op(Y, Q); S = C.op(R, Z); top = C.op(Y, S)
    def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
    pat = ''.join('F' if fr(r, a, b) else 'D' for r, a, b in
                  ((P, x, Z), (Q, P, Z), (R, Y, Q), (S, R, Z)))
    return pat, top == x

# collect decoded pairs from adversarial workloads
C = cf.Closed(LAW, RULES)
for sd in (3, 4, 202):
    cf.deep_tests(C, LAW, 6000, 200, sd)
    fz.critical_fuzz(C, LAW, 8000, seed=sd + 300)
    fz.closure_fuzz(C, LAW, 8000, seed=sd + 200)
fired = [(u, v) for (u, v), w in C.memo.items()
         if not (w[0] == 'J' and w[1] == u and w[2] == v)]
print(name, 'decoded pairs collected:', len(fired))

gens = [('g', i) for i in range(3)]
rounds = []
cur = sorted(fired, key=lambda p: size(p[0]) + size(p[1]))
for rnd in range(3):
    fails = []
    cnt = collections.Counter()
    C2 = cf.Closed(LAW, RULES)
    for (x, Z) in cur[:4000]:
        for Y in gens:
            try:
                pat, ok = law_ok(C2, x, Y, Z)
            except RecursionError:
                cnt['recursion'] += 1
                continue
            cnt[pat + ('' if ok else ' FAIL')] += 1
            if not ok:
                fails.append((x, Y, Z))
    print('round %d over %d pairs: %s' % (rnd, min(len(cur), 4000), dict(cnt)), flush=True)
    if fails:
        x, Y, Z = fails[0]
        print('   FIRST FAIL sizes x=%d Y=%d Z=%d' % (size(x), size(Y), size(Z)))
        print('   x =', sh(x)[:150])
        break
    # next round: pairs decoded during this round
    nxt = [(u, v) for (u, v), w in C2.memo.items()
           if not (w[0] == 'J' and w[1] == u and w[2] == v)]
    nxt = [p for p in nxt if p not in set(cur)]
    nxt.sort(key=lambda p: size(p[0]) + size(p[1]))
    print('   new decoded pairs for next round:', len(nxt), flush=True)
    if not nxt:
        break
    cur = nxt
