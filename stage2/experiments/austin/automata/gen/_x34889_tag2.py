"""Law 34889 -- TAG AUTOMATON v2 (non-recursive op).

Modelled (dual, L-form) law:      x = z * ((x * (z * x)) * (y * y))
Carrier:  M ::= g n | J a b | K a | B a b | E a b

Phases:   W = z*x  (anything, but z must be readable from (x,W))
          P = x*W  = B(x, z)
          Q = y*y  = K y            (always a K-node -- forced: the law derives (g*g)*(g*g)=g*g)
          R = P*Q  = E(x, z)
          FINAL = z*R = x           (E(a,b) with b = u  ->  a)
"""
import sys, itertools, collections

sys.setrecursionlimit(100000)
ORDER = 'P5,D,X,T,Tp,S,P1,P2,P4a,P4b,P4c,P3'


def mkop(order=ORDER):
    ors = [s.strip() for s in order.split(',') if s.strip()]

    def op(u, v):
        for r in ors:
            if r == 'P5':
                if u[0] == 'E' and v == u[1]:
                    return ('B', u, u[2])
            elif r == 'D':
                if v[0] == 'E' and v[2] == u:
                    return v[1]
            elif r == 'X':
                if u[0] == 'E' and v[0] == 'K':
                    return ('E', ('B', u[1], u[2]), ('B', u[1], u[2]))
            elif r == 'T':
                if u[0] == 'B' and v[0] == 'K':
                    return ('E', u[1], u[2])
            elif r == 'Tp':
                if u[0] == 'K' and v[0] == 'K':
                    return ('E', u, u)
            elif r == 'S':
                if u == v:
                    return u if u[0] == 'K' else ('K', u)
            elif r == 'P1':
                if v[0] == 'J' and v[2] == u:
                    return ('B', u, v[1])
            elif r == 'P2':
                if v[0] == 'B':
                    return ('B', u, v[1])
            elif r == 'P4a':
                if v[0] == 'E' and v[1] == v[2] and v[1][0] == 'K':
                    return ('B', u, v[1])
            elif r == 'P4b':
                if v[0] == 'E' and v[1] == v[2] and v[1][0] == 'B':
                    return ('B', u, ('E', v[1][1], v[1][2]))
            elif r == 'P4c':
                if v[0] == 'E':
                    return ('B', u, ('B', v[1], v[2]))
            elif r == 'P3':
                if v[0] == 'K' and v[1] == u:
                    return ('B', u, u)
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
