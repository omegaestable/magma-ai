"""Wave-3 validation of the r135 (R1,R3,R5) rule set for law 32281.

 1. rv.run_tests(LAW, rules, [3,4,5], 3000, 12000)      -- must be EMPTY of value fails
 2. cf.deep_tests 20000 on 3 fresh seeds
 3. THE CASE TREE: pool of chained free encodings; every triple (x,y,z) drawn from it, classified by
    the free/decoded pattern of the four chain products P,Q,A,S, law checked in each cell.
"""
import sys, os, time, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _x32281_lib import *
from _x32281_try1 import R1
from _x32281_try2 import R3
from _x32281_try5 import R5
import closedform as cf
from freemodel import size

RULES = [R1, R3, R5]
J = lambda a, b: ('J', a, b)
g = lambda n: ('g', n)

def enc(xv, zv, yv):
    """free encoding: the value of  z*((z*((x*y)*y))*y)  with every product free -> reads back xv"""
    return J(J(zv, J(J(xv, yv), yv)), yv)

def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

def cell(C, x, y, z):
    P = C.op(x, y); Q = C.op(P, y); A = C.op(z, Q); S = C.op(A, y); top = C.op(z, S)
    def fr(r, a, b): return r[0] == 'J' and r[1] == a and r[2] == b
    pat = ''.join('F' if fr(*t) else 'D' for t in ((P, x, y), (Q, P, y), (A, z, Q), (S, A, y)))
    pat += 'F' if fr(top, z, S) else 'D'
    return pat, top == x, (P, Q, A, S, top)

def main():
    what = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if what in ('all', 'full'):
        t0 = time.time()
        fails, real = report(LAW, RULES, seeds=(3, 4, 5), N=3000, NF=12000, tag='r135 FULL [3,4,5]')
        if real:
            for s, r, kind, sd in real[:5]:
                print('   REAL FAIL', kind, {k: sh(v) for k, v in s.items()})
            return
    if what in ('all', 'deep'):
        for sd in (777, 888, 999):
            C = cf.Closed(LAW, RULES)
            t, f = cf.deep_tests(C, LAW, 20000, 400, sd)
            print('deep20k seed %d: tested %d fails %d cycles %d' % (sd, t, len(f), C.cycles), flush=True)
    if what in ('all', 'tree'):
        G = [g(0), g(1), g(2)]
        E1 = [enc(a, b, c) for a in G for b in G for c in G]
        E2 = ([enc(a, b, c) for a in E1[:9] for b in G for c in G] +
              [enc(a, b, c) for a in G for b in E1[:9] for c in G] +
              [enc(a, b, c) for a in G for b in G for c in E1[:9]])
        XS = G + E1
        YS = G + E1 + E2
        ZS = G + E1[:9]
        print('pool: x=%d y=%d z=%d -> %d triples' % (len(XS), len(YS), len(ZS), len(XS) * len(YS) * len(ZS)), flush=True)
        C = cf.Closed(LAW, RULES)
        cnt = collections.Counter(); bad = []
        t0 = time.time()
        for x in XS:
            for y in YS:
                for z in ZS:
                    try:
                        pat, ok, vals = cell(C, x, y, z)
                    except RecursionError:
                        cnt['recursion'] += 1; continue
                    cnt[pat + ('' if ok else ' **FAIL**')] += 1
                    if not ok and len(bad) < 5:
                        bad.append((x, y, z, pat, vals))
        print('case-tree cells (%.1fs):' % (time.time() - t0))
        for k in sorted(cnt): print('   %-14s %d' % (k, cnt[k]))
        for x, y, z, pat, vals in bad:
            print('FAIL pat=%s' % pat)
            print('   x =', sh(x)[:200]); print('   y =', sh(y)[:200]); print('   z =', sh(z)[:200])
            print('   top =', sh(vals[4])[:200])

main()
