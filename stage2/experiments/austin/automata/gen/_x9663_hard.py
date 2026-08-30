"""Harder validation of the 9663 `pay` model: bigger pools, 2 generators, deep random."""
import sys, os, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show, terms, check, ev
import q9663 as M

LAW = M.LAW_RHS

def deep_terms(op, gens, depth, n, rng):
    """random terms built with op itself (so codes and decoded values appear)."""
    pool = [G(i) for i in range(gens)]
    out = []
    for _ in range(n):
        t = rng.choice(pool)
        for _ in range(depth):
            s = rng.choice(pool + out[-30:] if out else pool)
            t = op(t, s) if rng.random() < .5 else op(s, t)
        out.append(t)
    return out

if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'exh':
        ms, gens, zs = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        pool = terms(ms, gens); zp = terms(zs, gens)
        t0 = time.time()
        n, f = check(M.op, LAW, pool, pools={'x': pool, 'y': pool, 'z': zp}, limit=3)
        print('exh size<=%d gens=%d zsize<=%d: pool=%d zpool=%d tested=%d FAILS=%d (%.1fs)'
              % (ms, gens, zs, len(pool), len(zp), n, len(f), time.time()-t0))
        for s, r in f[:3]:
            print('   x=%s y=%s z=%s -> %s' % (show(s['x']), show(s['y']), show(s['z']),
                                               show(r) if r != 'RECURSION' else r))
    elif mode == 'deep':
        seeds = [int(a) for a in sys.argv[2].split(',')]
        n = int(sys.argv[3]); depth = int(sys.argv[4]); gens = int(sys.argv[5])
        for sd in seeds:
            rng = random.Random(sd)
            ts = deep_terms(M.op, gens, depth, 260, rng)
            bad = 0; t0 = time.time()
            for _ in range(n):
                s = {v: rng.choice(ts) for v in 'xyz'}
                try:
                    r = ev(M.op, LAW, s)
                except RecursionError:
                    r = None
                if r != s['x']:
                    bad += 1
                    if bad <= 2:
                        print('   FAIL x=%s y=%s z=%s' % (show(s['x'])[:90], show(s['y'])[:90], show(s['z'])[:90]))
            print('deep seed=%d n=%d depth=%d gens=%d: FAILS=%d (%.1fs)' % (sd, n, depth, gens, bad, time.time()-t0), flush=True)
