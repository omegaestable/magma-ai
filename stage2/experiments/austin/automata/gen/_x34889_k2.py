"""Law 34889 -- tagged carrier, clause engine + exhaustive law check.

Modelled (dual, L-form) law:      x = z * ((x * (z * x)) * (y * y))
Carrier:  g n | J a b | K a.
op(u,u) = K u  (or u when u is already a K-node)  -- forced: the law derives (g*g)*(g*g) = g*g.
Because every square is a K-node, the  y*y  slot of the encoding is a tagged constructor no free
product can imitate, so  R = P * Q  is always free when P is a J-node.
"""
import sys, itertools, collections

sys.setrecursionlimit(100000)
CL = 'C0,Ca,Cb,Cc,Cd'


def isK(t):
    return t[0] == 'K'


def mkop(clauses):
    cs = set(clauses.split(','))

    def op(u, v):
        if 'C0' in cs and u == v:
            return u if isK(u) else ('K', u)
        if v[0] == 'J' and isK(v[2]):
            p = v[1]
            if p[0] == 'J':
                p1, p2 = p[1], p[2]
                if 'Ca' in cs and p2 == ('J', u, p1):
                    return p1
                if 'Cb' in cs and p1 == u and p2 == ('K', u):
                    return u
                if 'Cd' in cs and p2 == u and isK(u):
                    return p1
            if 'Cc' in cs and p == u and isK(u):
                return u
        return ('J', u, v)
    return op


def terms(maxsize, gens):
    by = collections.defaultdict(list)
    by[1] = [('g', i) for i in range(gens)]
    for n in range(2, maxsize + 1):
        out = [('K', t) for t in by[n - 1]]
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
        return 'K%s' % show(t[1])
    return '(%s*%s)' % (show(t[1]), show(t[2]))


def check(op, pool, limit=25, verbose=True, tag=''):
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
            fails.append((z, x, y, got, W, P, Q, R))
            if len(fails) >= limit:
                break
    if verbose:
        print('%s tested %d, fails %d' % (tag, n, len(fails)))
        for z, x, y, got, W, P, Q, R in fails[:6]:
            print('   z=%s x=%s y=%s' % (show(z), show(x), show(y)))
            print('      W=%s P=%s Q=%s R=%s got=%s' % (show(W), show(P), show(Q), show(R), show(got)))
    return fails


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    cl = sys.argv[3] if len(sys.argv) > 3 else CL
    pool = terms(ms, gens)
    print('clauses=%s pool=%d (size<=%d, %d gens)' % (cl, len(pool), ms, gens))
    check(mkop(cl), pool)
