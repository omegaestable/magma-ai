"""10222 quotient (tag) model -- standalone.

10222 (x = y*((x*y)*((z*y)*y))) derives  (a*a)*((a*a)*a) = (a*a)*((b*a)*a)  (see _x10222_identity.py),
so the free magma on g/J is NOT a model.  Carrier here:

    M ::= g n | J u v | K u

`K a` is the single element the derived identity forces:  K a = (a*a)*((b*a)*a) for every b, and it is
the unique W with a*W = a.

`op` is an ordered rule list; the first matching rule wins, else the free product J u v.
Rules are pure pattern matches on the two arguments (no recursive op calls at all), so termination
in Lean would be structural, not by a measure.

python gen/_x10222_quot.py [maxsize] [gens]
"""
import sys, os, itertools, time

# ---------- terms ----------
def G(n): return ('g', n)
def J(a, b): return ('J', a, b)
def K(a): return ('K', a)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    if t[0] == 'K': return 'K(%s)' % show(t[1])
    return '(%s*%s)' % (show(t[1]), show(t[2]))

def size(t):
    if t[0] == 'g': return 1
    if t[0] == 'K': return size(t[1]) + 1
    return size(t[1]) + size(t[2]) + 1

# ---------- op ----------
def op(u, v):
    # R1  op(a, K a) = a
    if v[0] == 'K' and v[1] == u:
        return u
    # R2  op(K a, a*a) = a
    if u[0] == 'K' and v[0] == 'J' and v[1] == u[1] and v[2] == u[1]:
        return u[1]
    # R3  op(a*a, (b*a)*a) = K a          [the identified family]
    if (u[0] == 'J' and u[1] == u[2] and v[0] == 'J' and v[2] == u[1]
            and v[1][0] == 'J' and v[1][2] == u[1]):
        return K(u[1])
    # R4  op(u, (x*u)*((z*u)*u)) = x      [the all-free reading]
    if (v[0] == 'J' and v[1][0] == 'J' and v[1][2] == u
            and v[2][0] == 'J' and v[2][2] == u
            and v[2][1][0] == 'J' and v[2][1][2] == u):
        return v[1][1]
    # R5  op(K a, a*(q*(K a))) = a        [P decoded by R1, then the top]
    if (u[0] == 'K' and v[0] == 'J' and v[1] == u[1]
            and v[2][0] == 'J' and v[2][2] == u):
        return u[1]
    return J(u, v)

def B(x, y, z):
    return op(op(x, y), op(op(z, y), y))

def law(x, y, z):
    return op(y, B(x, y, z))

# ---------- exhaustive check ----------
def terms_upto(maxsize, gens, withK=True):
    by = {1: [G(i) for i in range(gens)]}
    out = list(by[1])
    for n in range(2, maxsize + 1):
        cur = []
        for a in range(1, n):
            b = n - 1 - a
            if b >= 1 and a in by and b in by:
                for s in by[a]:
                    for t in by[b]:
                        cur.append(J(s, t))
        if withK and (n - 1) in by:
            for s in by[n - 1]:
                cur.append(K(s))
        by[n] = cur
        out += cur
    return out

def check(maxsize, gens, limit=20, withK=True):
    pool = terms_upto(maxsize, gens, withK)
    fails = []
    n = 0
    for x, y, z in itertools.product(pool, repeat=3):
        n += 1
        r = law(x, y, z)
        if r != x:
            fails.append((x, y, z, r))
            if len(fails) >= limit: break
    return n, fails, len(pool)

if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    for m in range(2, ms + 1):
        t0 = time.time()
        n, f, np_ = check(m, gens)
        print('maxsize=%d gens=%d pool=%d tested=%d fails=%d (%.1fs)' % (m, gens, np_, n, len(f), time.time() - t0), flush=True)
        for x, y, z, r in f[:4]:
            print('   FAIL x=%s y=%s z=%s -> %s' % (show(x), show(y), show(z), show(r)), flush=True)
        if f: break
