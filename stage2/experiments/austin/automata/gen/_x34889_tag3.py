"""Law 34889 -- TAG AUTOMATON v3: the encoding tag is VERIFIED by a recursive guard.

Modelled (dual, L-form) law:      x = z * ((x * (z * x)) * (y * y))
Carrier:  M ::= g n | K a | B a b | E a b        (B is the free product; K is the square tag)

    W = z*x   (whatever it is)
    P = x*W   = B(x, W)          -- the DEFAULT product
    Q = y*y   = K y              -- forced: the law derives (g*g)*(g*g) = g*g, so op(Ka,Ka) = Ka
    R = P*Q   = E(x, W)          -- u a B-node, v a K-node
    FINAL     = z * E(x,W) = x   -- guarded by  op(z,x) == W , which holds BY DEFINITION

Only recursion:  op u (v.1)  and  op u (v.1.1) , so `sizeOf v` decreases -- a one-line termination.
"""
import sys, itertools, collections

sys.setrecursionlimit(200000)
ORDER = 'R1,R1c,R3,Rtp,R0,R2'


def mkop(order=ORDER):
    ors = [s.strip() for s in order.split(',') if s.strip()]
    memo = {}

    def op(u, v):
        k = (u, v)
        r = memo.get(k)
        if r is None:
            r = _op(u, v)
            memo[k] = r
        return r

    def _op(u, v):
        for r in ors:
            if r == 'R1':
                if v[0] == 'E' and op(u, v[1]) == v[2]:
                    return v[1]
            elif r == 'Re':
                if v[0] == 'E' and v[1] == v[2]:
                    return v[1]
            elif r == 'Reg':
                if v[0] == 'E' and v[1] == v[2] and op(u, v[1]) == v:
                    return v[1]
            elif r == 'R1c':
                if v[0] == 'B' and v[2] == ('K', v[1]) and v[1][0] == 'B' and op(u, v[1][1]) == v[1][2]:
                    return v[1][1]
            elif r == 'R3':
                if u == v:
                    return u if u[0] == 'K' else ('K', u)
            elif r == 'Rtp':
                if u[0] == 'K' and v[0] == 'K':
                    return ('E', u, u)
            elif r == 'R0':
                if v[0] == 'K' and v[1] == u:
                    return ('B', u, v)
            elif r == 'R2':
                if u[0] == 'B' and v[0] == 'K':
                    return ('E', u[1], u[2])
            elif r == 'L2':
                if (u[0] == 'B' and u[2][0] == 'B' and u[2][2] == u[1]
                        and v[0] == 'B' and v[1] == u[1] and v[2][0] == 'K'):
                    return u[2][1]
            elif r == 'R2g':
                if u[0] == 'B' and v[0] == 'K' and op(u[1], u[2]) == u:
                    return ('E', u[1], u[2])
        return ('B', u, v)
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
                    out.append(('B', s, t))
                    out.append(('E', s, t))
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
    return '%s(%s,%s)' % (t[0], show(t[1]), show(t[2]))


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
        for z, x, y, got, W, P, Q, R in fails[:8]:
            print('   z=%s x=%s y=%s' % (show(z), show(x), show(y)))
            print('      W=%s P=%s Q=%s R=%s got=%s' % (show(W), show(P), show(Q), show(R), show(got)))
    return fails


if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    order = sys.argv[3] if len(sys.argv) > 3 else ORDER
    pool = terms(ms, gens)
    print('order=%s pool=%d (size<=%d, %d gens)' % (order, len(pool), ms, gens))
    check(mkop(order), pool)
