"""Exhaustive validation of the LEAN semantics of gen/nf27859.lean (law 27859).

Carrier M ::= g n | K | J a b.  op is transcribed verbatim from the Lean skeleton,
gates and `else u` fallbacks included.
Law: op (op (op y (op y x)) x) (op z z) = x.   (op z z = K always, so z drops out.)
"""
import sys

sys.setrecursionlimit(100000)

K = ('K',)


def G(n):
    return ('g', n)


def J(a, b):
    return ('J', a, b)


_sz = {}


def sz(t):
    r = _sz.get(t)
    if r is None:
        r = 1 if t[0] != 'J' else sz(t[1]) + sz(t[2]) + 1
        _sz[t] = r
    return r


def tg(t):
    return {'g': 0, 'K': 1, 'J': 2}[t[0]]


def a1(t):
    return t[1] if t[0] == 'J' else t


def a2(t):
    return t[2] if t[0] == 'J' else t


_memo = {}


def op(u, v):
    key = (u, v)
    r = _memo.get(key)
    if r is not None:
        return r
    a = a1(a1(u))
    b = a2(a1(u))
    q = a2(u)
    r1 = op(a, q) if sz(a) + sz(q) < sz(u) + sz(v) else u
    r2 = op(a, b) if sz(a) + sz(b) < sz(u) + sz(v) else u
    if u == v:
        r = K
    elif v == K and tg(u) == 2 and tg(a1(u)) == 2 and r1 == b and r2 == J(a, b):
        r = q
    elif v == K and tg(u) == 2 and tg(q) == 2 and a2(q) == a1(u):
        r = q
    else:
        r = J(u, v)
    _memo[key] = r
    return r


def law(x, y, z):
    return op(op(op(y, op(y, x)), x), op(z, z))


def terms(maxsz, ngen=1):
    """all carrier terms of size <= maxsz over ngen generators plus K"""
    by = {1: [G(i) for i in range(ngen)] + [K]}
    for n in range(2, maxsz + 1):
        cur = []
        for i in range(1, n):
            j = n - 1 - i
            if j < 1:
                continue
            for a in by.get(i, ()):
                for b in by.get(j, ()):
                    cur.append(J(a, b))
        by[n] = cur
    out = []
    for n in range(1, maxsz + 1):
        out.extend(by[n])
    return out


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 9
    NG = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    ZN = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ts = terms(N, NG)
    zs = terms(ZN, NG)
    print('terms', len(ts), 'z-pool', len(zs))
    bad = 0
    tot = 0
    for x in ts:
        for y in ts:
            for z in zs:
                tot += 1
                if law(x, y, z) != x:
                    bad += 1
                    if bad <= 5:
                        print('FAIL x=', x, 'y=', y, 'z=', z, 'got=', law(x, y, z))
    print('assignments', tot, 'failures', bad)
