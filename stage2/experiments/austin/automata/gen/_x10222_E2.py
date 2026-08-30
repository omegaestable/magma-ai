"""10222 -- the E-carrier model, iteration 2.

M ::= g n | J u v | E u v      (E y x = "the encoding of x by y"; z is forgotten)

`op` is a plain ordered pattern match, NO recursive calls.  Rules, in order:

  A  op u (E u x)                        = x                     decode
  B  op (J x y) (J (J z y) y)            = E y x                 encode
  C  op (E p q) (J q (J (J z (E p q)) (E p q)))       = p        P decoded, Q/R free
  D  op u (J (J x u) (J q u))            = x                     Q decoded to anything
  E1 op (E p p) (J p p)                  = p                     x=z=p, p=q
  E1b op (E p p) (E b a)  [p = J a b]    = p                     ditto, op(q,q) encoded
  E2 op (E p q) (J q (J q (E p q)))      = p                     x=z=p, p<>q
  E3 op (E p p) (J (J x (E p p)) p)      = x                     x<>p, z=p, p=q
  F  op u (J (E c x') (J q u))  [u = J _ c] = J x' c             P encoded (u B-shaped)

python gen/_x10222_E2.py [maxsize] [gens]
"""
import sys, os, itertools, time

def G(n): return ('g', n)
def J(a, b): return ('J', a, b)
def E(y, x): return ('E', y, x)

def show(t):
    if t[0] == 'g': return 'g%d' % t[1]
    if t[0] == 'E': return 'E[%s|%s]' % (show(t[1]), show(t[2]))
    return '(%s*%s)' % (show(t[1]), show(t[2]))

TRACE = False

def op(u, v):
    r = _op(u, v)
    if TRACE: print('      op %s  %s  = %s [%s]' % (show(u), show(v), show(r[0]), r[1]))
    return r[0] if TRACE else r[0]

def _op(u, v):
    # A decode
    if v[0] == 'E' and v[1] == u:
        return v[2], 'A'
    # B encode
    if (u[0] == 'J' and v[0] == 'J' and v[2] == u[2]
            and v[1][0] == 'J' and v[1][2] == u[2]):
        return E(u[2], u[1]), 'B'
    # C  u = E p q ; v = J q (J (J z u) u)
    if (u[0] == 'E' and v[0] == 'J' and v[1] == u[2]
            and v[2][0] == 'J' and v[2][2] == u and v[2][1][0] == 'J' and v[2][1][2] == u):
        return u[1], 'C'
    # E2 u = E p q ; v = J q (J q u)
    if (u[0] == 'E' and v[0] == 'J' and v[1] == u[2]
            and v[2][0] == 'J' and v[2][1] == u[2] and v[2][2] == u):
        return u[1], 'E2'
    # E1 u = E p p ; v = J p p
    if (u[0] == 'E' and u[1] == u[2] and v[0] == 'J' and v[1] == u[1] and v[2] == u[1]):
        return u[1], 'E1'
    # E1b u = E p p, p = J a b ; v = E b a
    if (u[0] == 'E' and u[1] == u[2] and u[1][0] == 'J'
            and v[0] == 'E' and v[1] == u[1][2] and v[2] == u[1][1]):
        return u[1], 'E1b'
    # E3 u = E p p ; v = J (J x u) p
    if (u[0] == 'E' and u[1] == u[2] and v[0] == 'J'
            and v[1][0] == 'J' and v[1][2] == u and v[2] == u[1]):
        return v[1][1], 'E3'
    # F  u = J _ c ; v = J (E c x') (J q u)
    if (u[0] == 'J' and v[0] == 'J' and v[1][0] == 'E' and v[1][1] == u[2]
            and v[2][0] == 'J' and v[2][2] == u):
        return J(v[1][2], u[2]), 'F'
    # D  v = J (J x u) (J q u)
    if (v[0] == 'J' and v[1][0] == 'J' and v[1][2] == u
            and v[2][0] == 'J' and v[2][2] == u):
        return v[1][1], 'D'
    return J(u, v), 'free'

def B_(x, y, z):
    return op(op(x, y), op(op(z, y), y))

def law(x, y, z):
    return op(y, B_(x, y, z))

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
        by[n] = cur; out += cur
    return out

def check(maxsize, gens, limit=20):
    pool = terms_upto(maxsize, gens)
    fails = []; n = 0
    for x, y, z in itertools.product(pool, repeat=3):
        n += 1
        r = law(x, y, z)
        if r != x:
            fails.append((x, y, z, r))
            if len(fails) >= limit: break
    return n, fails, len(pool)

def trace(x, y, z):
    print('x=%s y=%s z=%s' % (show(x), show(y), show(z)))
    P = _op(x, y); print('  P = op(x,y) = %s [%s]' % (show(P[0]), P[1]))
    Q = _op(z, y); print('  Q = op(z,y) = %s [%s]' % (show(Q[0]), Q[1]))
    R = _op(Q[0], y); print('  R = op(Q,y) = %s [%s]' % (show(R[0]), R[1]))
    V = _op(P[0], R[0]); print('  v = op(P,R) = %s [%s]' % (show(V[0]), V[1]))
    T = _op(y, V[0]); print('  top        = %s [%s]   expected %s' % (show(T[0]), T[1], show(x)))

if __name__ == '__main__':
    ms = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    gens = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    for m in range(2, ms + 1):
        t0 = time.time()
        n, f, np_ = check(m, gens)
        print('maxsize=%d gens=%d pool=%d tested=%d fails=%d (%.1fs)' % (m, gens, np_, n, len(f), time.time() - t0), flush=True)
        for x, y, z, r in f[:4]:
            trace(x, y, z)
        if f: break
