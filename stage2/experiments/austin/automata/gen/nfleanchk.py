"""nfleanchk.py -- re-implement the LEAN form of `op` (total accessors + `sz`-gated recursive
calls, exactly as gen/nf12073.lean and gen/nf27859.lean define it) and check it agrees with the
validated pattern-matching model on every pair of carrier terms up to a size bound, and that the
law still holds for the Lean form.
"""
import sys, os, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nfcore as nf
from nfcore import S as K, sz, show
import nf12073, nf27859

def J(a, b): return ('J', a, b)
def E(t): return ('E', t)

def tg(t): return {'g': 0, 'S': 1, 'E': 2, 'J': 3}[t[0]]
def d(t): return t[1] if t[0] == 'E' else t
def a1(t): return t[1] if t[0] == 'J' else t
def a2(t): return t[2] if t[0] == 'J' else t

_m1 = {}
def lean12073(u, v):
    k = (u, v)
    r = _m1.get(k)
    if r is not None: return r
    w = d(v); p = a1(w); q = a2(w); e = a2(d(u))
    r1 = lean12073(u, q) if sz(q) < sz(v) else v
    r2 = lean12073(p, q) if sz(q) < sz(v) else v
    r3 = lean12073(K, w) if sz(w) < sz(v) else v
    r4 = lean12073(u, w) if sz(w) < sz(v) else v
    r5 = lean12073(K, e) if sz(e) < sz(v) else v
    if u == v: r = K
    elif tg(v) == 1: r = E(u)
    elif tg(v) == 2 and u != K and tg(w) == 2 and d(w) == E(u): r = K
    elif tg(v) == 2 and tg(w) == 3 and q != K and r1 == p and r2 == J(p, q): r = q
    elif tg(v) == 2 and w != K and u == E(J(r3, w)): r = u
    elif tg(v) == 2 and w == u and tg(u) == 2 and tg(d(u)) == 3 and e != K and r5 == a1(d(u)): r = E(e)
    elif tg(v) == 2 and w != K and r4 == K and r3 == J(K, w): r = E(J(K, w))
    else: r = J(u, v)
    _m1[k] = r
    return r

def tg2(t): return {'g': 0, 'S': 1, 'J': 2}[t[0]]

_m2 = {}
def lean27859(u, v):
    k = (u, v)
    r = _m2.get(k)
    if r is not None: return r
    a = a1(a1(u)); b = a2(a1(u)); q = a2(u)
    r1 = lean27859(a, q) if sz(a) + sz(q) < sz(u) + sz(v) else u
    r2 = lean27859(a, b) if sz(a) + sz(b) < sz(u) + sz(v) else u
    if u == v: r = K
    elif v == K and tg2(u) == 2 and tg2(a1(u)) == 2 and r1 == b and r2 == J(a, b): r = q
    elif v == K and tg2(u) == 2 and tg2(q) == 2 and a2(q) == a1(u): r = q
    else: r = J(u, v)
    _m2[k] = r
    return r

if __name__ == '__main__':
    for name, leanop, pyop, eq, useE, ms in (('12073', lean12073, nf12073.op, 12073, True, 5),
                                             ('27859', lean27859, nf27859.op, 27859, False, 7)):
        nf.ALLOW_E = useE
        pool = nf.carrier_upto(ms, 2, use_E=useE)
        t0 = time.time(); diff = 0; n = 0
        for u in pool:
            for v in pool:
                n += 1
                if leanop(u, v) != pyop(u, v):
                    diff += 1
                    if diff <= 3: print('  DIFF', show(u), show(v), show(leanop(u, v)), show(pyop(u, v)))
        print('%s: %d pairs from a pool of %d (size<=%d, 2 generators), %d disagreements  [%.1fs]'
              % (name, n, len(pool), ms, diff, time.time() - t0), flush=True)
        law = nf.get_law(eq)
        for g, s in ((1, ms), (2, ms - 2)):
            p2 = nf.carrier_upto(s, g, use_E=useE)
            nn, f = nf.exhaustive(leanop, law, p2, limit=3)
            print('   LEAN-form law check carrier<=%d g%d: %d assignments, %d fails' % (s, g, nn, len(f)))
            for a, r in f[:3]: print('     FAIL', {kk: show(vv) for kk, vv in a.items()}, '->', show(r) if r != 'recursion' else r)
        for seed in (31337, 900001):
            nn, f = nf.deep_random(leanop, law, 20000, seed)
            n2, f2 = nf.critical_random(leanop, law, 10000, seed + 3)
            print('   LEAN-form fuzz seed %d: deep %d/%d, critical %d/%d' % (seed, len(f), nn, len(f2), n2), flush=True)
