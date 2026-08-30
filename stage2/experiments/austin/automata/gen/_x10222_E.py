"""10222 -- the E-carrier model (encoding constructor that forgets z).

10222 derives  (a*a)*((a*a)*a) = (a*a)*((b*a)*a)  (gen/_x10222_identity.py), i.e. B(a,a,z) must not
depend on z.  So instead of leaving the encoding as the free product J P R we make `op` PRODUCE a tag:

    M ::= g n | J u v | E u v          -- E y x = "the encoding of x by y"

    op (J x y) (J (J z y) y)  =  E y x        (encode: z is forgotten)
    op u (E u x)              =  x            (decode)
    otherwise                 =  J u v

Then B(x,y,z) = E y x for every z, and op y (E y x) = x, which is the law.  The remaining rules below
patch the cases where a chain product itself encodes/decodes.

`op` uses NO recursive calls -- it is a plain pattern match -- so in Lean it is a structural `match`
with no termination measure, no msr gate and no `op_cases` packing.

python gen/_x10222_E.py [maxsize] [gens]
"""
import sys, os, itertools, time

def G(n): return ('g', n)
def J(a, b): return ('J', a, b)
def E(y, x): return ('E', y, x)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    if t[0] == 'E': return 'E[%s|%s]' % (show(t[1]), show(t[2]))
    return '(%s*%s)' % (show(t[1]), show(t[2]))

def size(t):
    if t[0] == 'g': return 1
    return size(t[1]) + size(t[2]) + 1

RULES_ON = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None

def op(u, v):
    # A: decode   op u (E u x) = x
    if v[0] == 'E' and v[1] == u:
        return v[2]
    # B: encode   op (J x y) (J (J z y) y) = E y x
    if (u[0] == 'J' and v[0] == 'J' and v[2] == u[2]
            and v[1][0] == 'J' and v[1][2] == u[2]):
        return E(u[2], u[1])
    # C: P decoded by A   u = E x p , v = J p (J (J z u) u)  ->  x
    if (u[0] == 'E' and v[0] == 'J' and v[1] == u[2]
            and v[2][0] == 'J' and v[2][2] == u and v[2][1][0] == 'J' and v[2][1][2] == u):
        return u[1]
    # D: u is an E and the chain is free   u = E _ _ , v = J (J x u) (J q u)  ->  x
    if (u[0] == 'E' and v[0] == 'J' and v[1][0] == 'J' and v[1][2] == u
            and v[2][0] == 'J' and v[2][2] == u):
        return v[1][1]
    return J(u, v)

def B(x, y, z):
    return op(op(x, y), op(op(z, y), y))

def law(x, y, z):
    return op(y, B(x, y, z))

def terms_upto(maxsize, gens):
    by = {1: [G(i) for i in range(gens)]}
    out = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        for a in range(1, n):
            b = n - 1 - a
            if b >= 1 and a in by and b in by:
                for s in by[a]:
                    for t in by[b]:
                        cur.append(J(s, t)); cur.append(E(s, t))
        by[n] = cur
        out += cur
    return out

def check(maxsize, gens, limit=20):
    pool = terms_upto(maxsize, gens)
    fails = []; n = 0
    for x, y, z in itertools.product(pool, repeat=3):
        n += 1
        if law(x, y, z) != x:
            fails.append((x, y, z, law(x, y, z)))
            if len(fails) >= limit: break
    return n, fails, len(pool)

if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    for m in range(2, ms + 1):
        t0 = time.time()
        n, f, np_ = check(m, gens)
        print('maxsize=%d gens=%d pool=%d tested=%d fails=%d (%.1fs)' % (m, gens, np_, n, len(f), time.time() - t0), flush=True)
        for x, y, z, r in f[:5]:
            print('   FAIL x=%s y=%s z=%s -> %s' % (show(x), show(y), show(z), show(r)), flush=True)
        if f: break
