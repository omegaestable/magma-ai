"""Targeted hunt for a GENUINE Dfree violation for law 12234, i.e. x,y,z with
    op (op (op z x) y) (op x y)  !=  J (op (op z x) y) (op x y).

The paper analysis says a violation needs (case beta)  a2 x = J A y = op A y  with A = op z x
decoded, plus  op (a2 A) (J A y) = y.  Both halves are separately realisable (gen/_x12234_beta2.py
builds the second).  This builds x as an encoding of A by y --- so that op y x = A by the law ---
with A of the self-decoding shape, and tries every z.
"""
import sys, random, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.setrecursionlimit(40000)
from freemodel import size
import smallcheck as sc
import _x12234_leanval as LV

LeanModel, J, isJ, a1, a2, oc, msr = LV.LeanModel, LV.J, LV.isJ, LV.a1, LV.a2, LV.oc, LV.msr
M = LeanModel()


def g(n): return ('g', n)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def enc(w, u, q):
    return M.op(M.op(M.op(q, w), u), M.op(w, u))
def dfree(x, y, z):
    A = M.op(z, x); B = M.op(A, y); C = M.op(x, y)
    return M.op(B, C) == J(B, C), A, B, C


def rnd(d, k=3):
    if d <= 0 or random.random() < 0.4: return g(random.randrange(k))
    return J(rnd(d - 1, k), rnd(d - 1, k))


def report(tag, x, y, z, A, B, C):
    print('*** DFREE VIOLATION (%s)' % tag)
    print('   x', size(x), '  y', size(y), '  z', size(z))
    print('   A = op z x', size(A), ' free', A == J(z, x))
    print('   B = op A y', size(B), ' free', B == J(A, y))
    print('   C = op x y', size(C), ' free', C == J(x, y))
    print('   D = op B C', size(M.op(B, C)))
    print('   law op y D == x ?', M.op(y, M.op(B, C)) == x)


def main():
    random.seed(2026)
    found = 0
    tested = 0

    # ---- generator 1: x an encoding of A by y, A a self-decoder shape (the beta recipe) ----
    small = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(g(0), g(0)),
             J(g(0), J(g(1), g(2))), J(J(g(0), g(1)), g(2))]
    for it in range(20000):
        y = random.choice(small)
        z1 = random.choice(small)
        w = random.choice(small)
        q = enc(y, y, z1)                      # op y q = y
        if M.op(y, q) != y: continue
        A = J(J(w, y), q)                      # a2 A = q, op q (J A y) = y (beta2 recipe)
        B = M.op(A, y)
        if B != J(A, y): continue
        if M.op(a2(A), B) != y: continue       # the beta side condition
        for z2 in small:
            x = enc(A, y, z2)                  # op y x = A by the law
            if size(x) > 400: continue
            tested += 1
            ok, A2, B2, C2 = dfree(x, y, y)    # z := y is the main beta branch
            if not ok:
                report('gen1 z=y', x, y, y, A2, B2, C2); found += 1
            for z in small + [a2(x), a1(x), oc(x)]:
                tested += 1
                ok, A2, B2, C2 = dfree(x, y, z)
                if not ok:
                    report('gen1', x, y, z, A2, B2, C2); found += 1
            if found > 2: break
        if found > 2: break
    print('generator 1: tested', tested, 'violations', found)

    # ---- generator 2: closure sweep -- pool closed under enc and the law's subproducts ----
    random.seed(99)
    pool = [g(0), g(1), g(2)]
    tested2 = 0
    for rnd_i in range(700):
        a, b, c = (random.choice(pool) for _ in range(3))
        for t in (enc(a, b, c), M.op(a, b), M.op(M.op(c, a), b)):
            if 1 <= size(t) <= 90 and len(pool) < 900:
                pool.append(t)
        for _ in range(60):
            x, y, z = (random.choice(pool) for _ in range(3))
            if size(x) + size(y) + size(z) > 220: continue
            tested2 += 1
            ok, A2, B2, C2 = dfree(x, y, z)
            if not ok:
                report('gen2', x, y, z, A2, B2, C2); found += 1
                break
        if found > 2: break
    print('generator 2: tested', tested2, 'violations', found)


if __name__ == '__main__':
    main()
