"""Law 34889 -- tagged carrier prototype.

Modelled (dual, L-form) law:      x = z * ((x * (z * x)) * (y * y))
The law DERIVES  (g*g)*(g*g) = g*g  (see _x34889_ident.py), so the free magma is not a model.
Carrier here:  g n | J a b | K a      with  op(u,u) = K u   (K u already a K-node -> u).
Every square is a K-node, so the `y*y` slot of the encoding is a *tagged* constructor that a free
product can never imitate.  That kills the whole (P,Q) derailment family of the free model.
"""
import sys, itertools, collections

sys.setrecursionlimit(100000)


def sq(u):
    return u if u[0] == 'K' else ('K', u)


def mkop(rules):
    def op(u, v):
        if u == v:
            return sq(u)
        if v[0] == 'J' and v[2][0] == 'K':
            p = v[1]
            if 'a' in rules and p[0] == 'J' and p[2] == ('J', u, p[1]):
                return p[1]
            if 'b' in rules and p[0] == 'J' and p[1] == u and p[2] == ('K', u):
                return u
            if 'c' in rules and p == u and u[0] == 'K':
                return u
        return ('J', u, v)
    return op


def terms(maxsize, gens, withK=True):
    by = collections.defaultdict(list)
    by[1] = [('g', i) for i in range(gens)]
    for n in range(2, maxsize + 1):
        out = []
        if withK and n - 1 in by:
            out += [('K', t) for t in by[n - 1]]
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by[a]:
                for t in by[b]:
                    out.append(('J', s, t))
        by[n] = out
    res = []
    for n in sorted(by):
        res += by[n]
    return res


def show(t):
    if t[0] == 'g':
        return 'g%d' % t[1]
    if t[0] == 'K':
        return 'K(%s)' % show(t[1])
    return '(%s*%s)' % (show(t[1]), show(t[2]))


def check(op, pool, limit=12, verbose=True):
    fails = []
    n = 0
    for z, x, y in itertools.product(pool, repeat=3):
        n += 1
        W = op(z, x)
        P = op(x, W)
        Q = op(y, y)
        R = op(P, Q)
        got = op(z, R)
        if got != x:
            fails.append((z, x, y, got))
            if len(fails) >= limit:
                break
    if verbose:
        print('  tested %d, fails %d' % (n, len(fails)))
        for z, x, y, got in fails[:8]:
            print('    z=%s x=%s y=%s -> %s' % (show(z), show(x), show(y), show(got)))
    return fails


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    for rs in ('a', 'ab', 'abc'):
        pool = terms(ms, gens)
        print('rules=%s pool=%d' % (rs, len(pool)))
        check(mkop(rs), pool)
