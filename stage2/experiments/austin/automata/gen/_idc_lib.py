"""Tiny standalone harness: free-term carrier + exhaustive law check. No shared-file edits."""
import sys, os, itertools, time, random
sys.setrecursionlimit(100000)

def G(n): return ('g', n)
def J(a, b): return ('J', a, b)
def E(): return ('E',)
def K(a): return ('K', a)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    if t[0] == 'E': return 'E'
    if t[0] == 'K': return 'K[%s]' % show(t[1])
    return '(%s*%s)' % (show(t[1]), show(t[2]))

_SZ = {}
def sz(t):
    r = _SZ.get(t)
    if r is None:
        if t[0] == 'J': r = 1 + sz(t[1]) + sz(t[2])
        elif t[0] == 'K': r = 1 + sz(t[1])
        else: r = 1
        _SZ[t] = r
    return r

def terms(maxsize, gens, ctors=('J',)):
    """all carrier terms of size <= maxsize (odd sizes for J-only)."""
    by = {1: [G(i) for i in range(gens)] + ([E()] if 'E' in ctors else [])}
    out = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        for a in range(1, n):
            b = n - 1 - a
            if b >= 1 and a in by and b in by:
                for s in by[a]:
                    for t in by[b]: cur.append(J(s, t))
        if 'K' in ctors and (n - 1) in by:
            for s in by[n - 1]: cur.append(K(s))
        by[n] = cur; out += cur
    return out

def ev(op, pat, s):
    if isinstance(pat, str): return s[pat]
    return op(ev(op, pat[0], s), ev(op, pat[1], s))

def check(op, RHS, pool, vs=('x', 'y', 'z'), limit=6, pools=None):
    n = 0; fails = []
    ps = pools or {v: pool for v in vs}
    for combo in itertools.product(*[ps[v] for v in vs]):
        s = dict(zip(vs, combo))
        n += 1
        try:
            r = ev(op, RHS, s)
        except RecursionError:
            fails.append((s, 'RECURSION')); 
            if len(fails) >= limit: break
            continue
        if r != s['x']:
            fails.append((s, r))
            if len(fails) >= limit: break
    return n, fails

def report(name, op, RHS, maxsize, gens, ctors=('J',), zsizes=None, limit=4):
    pool = terms(maxsize, gens, ctors)
    zp = terms(zsizes, gens, ctors) if zsizes else pool
    t0 = time.time()
    n, f = check(op, RHS, pool, pools={'x': pool, 'y': pool, 'z': zp})
    print('%s: pool=%d zpool=%d tested=%d FAILS=%d (%.1fs)' % (name, len(pool), len(zp), n, len(f), time.time()-t0), flush=True)
    for s, r in f[:limit]:
        print('   FAIL %s -> %s' % ({k: show(v) for k, v in s.items()},
                                    show(r) if r != 'RECURSION' else r), flush=True)
    return n, f
