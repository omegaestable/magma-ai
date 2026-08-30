"""_y6912_e.py : the E-quotient carrier for law 6912 -- candidate `op`, exhaustively tested.

Law 6912 (L-form):  x = y * (y * ((z*z) * (x*y)))
Carrier  M ::= g n | E | J a b     with  op(u,u) = E  for every u, so  z*z = E  and z drops out.
LE :  x = op(y, op(y, op(E, op(x,y))))

Chain: A = op(x,y), B = op(E,A), C = op(y,B), top = op(y,C) = x.

Every rule here is PURELY STRUCTURAL -- no nested `op` call, hence no recursion and no gates.
Usage: python -u gen/_y6912_e.py <variant> [maxsize] [gens]
"""
import sys, os, itertools, collections, random, time

E = ('E',)


def J(a, b):
    return ('J', a, b)


def isJ(t):
    return t[0] == 'J'


def sz(t):
    if t[0] in ('g', 'E'):
        return 1
    return 1 + sz(t[1]) + sz(t[2])


def show(t):
    if t[0] == 'E':
        return 'E'
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(%s*%s)' % (show(t[1]), show(t[2]))


def terms_upto(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)] + [E]}
    allt = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    cur.append(('J', s, t))
        by[n] = cur
        allt += cur
    return allt


# --------------------------------------------------------------------------- variants of op

def op_v1(u, v):
    """R1 SQ, R2 SELF (v = u*E), R3 DEC, R5 EE (v = E*(E*u)), R4 DEC2"""
    if u == v:
        return E                                     # R1
    if isJ(v) and v[1] == u and v[2] == E and u != E:
        return u                                     # R2
    if isJ(v) and v[1] == u and isJ(v[2]) and v[2][1] == E:
        w = v[2][2]
        if isJ(w) and w[2] == u and w[1] != E:
            return w[1]                              # R3
    if isJ(v) and v[1] == E and isJ(v[2]) and v[2][1] == E and v[2][2] == u and u != E:
        return u                                     # R5
    if isJ(v) and v[1] == u and isJ(v[2]) and v[2][1] == E:
        w = v[2][2]
        if u == J(w, E) and w != E:
            return w                                 # R4
    return J(u, v)


VARIANTS = {'v1': op_v1}


def law_holds(op, x, y, z=None):
    A = op(x, y)
    B = op(E, A)
    C = op(y, B)
    return op(y, C), A, B, C


def exhaustive(op, pool, limit=25):
    fails = []
    n = 0
    for x in pool:
        for y in pool:
            n += 1
            r, A, B, C = law_holds(op, x, y)
            if r != x:
                fails.append((x, y, r, A, B, C))
                if len(fails) >= limit:
                    return n, fails
    return n, fails


def zcheck(op, pool):
    """op(z,z) = E for every z -- the reason z drops out of the law."""
    bad = [t for t in pool if op(t, t) != E]
    return bad


def edefcheck(op, pool):
    """op(a,b) = E  =>  a = b   (the invariant the collisions violated)."""
    bad = []
    for a in pool:
        for b in pool:
            if a != b and op(a, b) == E:
                bad.append((a, b))
                if len(bad) > 8:
                    return bad
    return bad


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'v1'
    ms = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    gens = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    op = VARIANTS[name]
    pool = terms_upto(ms, gens)
    print('variant %s   pool %d terms (size<=%d, %d gens)' % (name, len(pool), ms, gens), flush=True)
    t0 = time.time()
    n, fails = exhaustive(op, pool)
    print('exhaustive %d assignments, %d fails, %.1fs' % (n, len(fails), time.time() - t0), flush=True)
    for x, y, r, A, B, C in fails[:8]:
        print('  FAIL x=%s y=%s  -> %s' % (show(x), show(y), show(r)))
        print('       A=op(x,y)=%s  B=op(E,A)=%s  C=op(y,B)=%s' % (show(A), show(B), show(C)))
    b = zcheck(op, pool)
    print('op(z,z)=E fails: %d' % len(b))
    b2 = edefcheck(op, pool[:200])
    print('op(a,b)=E with a!=b (first 200 terms): %d %s'
          % (len(b2), [(show(a), show(c)) for a, c in b2[:4]]))
