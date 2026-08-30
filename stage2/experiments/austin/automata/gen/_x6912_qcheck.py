"""Check law 6912 in the QUOTIENT free model (carrier = free magma with a square constructor K,
K idempotent), exhaustively on small terms and on biased random terms."""
import sys, os, json, itertools, random, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
import _x6912_fm as fm
from _x6912_fm import normalise, catalog, pvars, size, default, K
from laws import parse_eq

EQ = 6912
law = normalise(parse_eq(catalog()[EQ]))
print('law', law)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    if t[0] == 'K': return 'K(%s)' % show(t[1])
    return '(%s*%s)' % (show(t[1]), show(t[2]))

def terms_upto(maxsize, gens):
    """all carrier normal forms of size <= maxsize: g n, K u (u not a K), J u v (u != v)"""
    by = {1: [('g', i) for i in range(gens)]}
    allt = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        # K u : size = size u + 1
        for u in by.get(n - 1, []):
            if u[0] != 'K': cur.append(('K', u))
        # J u v : size = size u + size v + 1
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    if s != t: cur.append(('J', s, t))
        by[n] = cur
        allt += cur
    return allt

def run_exhaustive(maxsize, gens, limit=25):
    F = fm.Free(law)
    A, B = law[1]
    vs = pvars(law[1])
    ts = terms_upto(maxsize, gens)
    fails = []
    n = 0
    def ev(p, s):
        if isinstance(p, str): return s[p]
        return F.op(ev(p[0], s), ev(p[1], s))
    for combo in itertools.product(ts, repeat=len(vs)):
        s = dict(zip(vs, combo))
        n += 1
        try:
            r = F.op(ev(A, s), ev(B, s))
        except RecursionError:
            continue
        if r != s['x']:
            fails.append((s, r))
            if len(fails) >= limit: break
    return n, fails, F

if __name__ == '__main__':
    maxsize = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    t0 = time.time()
    n, fails, F = run_exhaustive(maxsize, gens)
    print('exhaustive size<=%d gens=%d : %d assignments, %d fails, conflicts %d, cycles %d, bail %d, %.1fs'
          % (maxsize, gens, n, len(fails), len(F.conflicts), F.cycles, F.bail, time.time() - t0))
    for s, r in fails[:6]:
        print('  FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if size(r) < 60 else '<%d>' % size(r))
    for u, v, xs in F.conflicts[:4]:
        print('  CONFLICT op(%s, %s) = %s' % (show(u), show(v), [show(x) for x in xs]))
