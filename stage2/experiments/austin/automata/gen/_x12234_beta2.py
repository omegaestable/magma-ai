"""Direct construction of a beta counterexample to Dfree for law 12234.

Dfree is FALSE as soon as there are A, y, s with
    op A y = J A y            (B free)
    op s (J A y) = y          (y decodes out of B with y-slot s)
because then x := J (J t s) (J A y) makes rule R2 fire at (B, C=J x y) with result s.

Recipe for `op s B = y`:  take q with op y q = y  (q := enc(y,y,z1), an instance of the law with x:=y),
put A := J (J w y) q, s := a2 A = q; then R2 at (q, B) has guard  a2 B = y = op (a2 (a1 (a1 B))) q
= op y q = y.
"""
import sys, random
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.setrecursionlimit(30000)
from freemodel import size
import _x12234_leanval as LV

LeanModel, J, isJ, a1, a2, oc, msr = LV.LeanModel, LV.J, LV.isJ, LV.a1, LV.a2, LV.oc, LV.msr
M = LeanModel()


def g(n): return ('g', n)
def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
def enc(w, u, q):
    return M.op(M.op(M.op(q, w), u), M.op(w, u))


def rnd(d, k=3):
    if d <= 0 or random.random() < 0.4: return g(random.randrange(k))
    return J(rnd(d - 1, k), rnd(d - 1, k))


def try_one(y, z1, w, t):
    q = enc(y, y, z1)
    if M.op(y, q) != y: return 'no-selfdec', None
    A = J(J(w, y), q)
    B = M.op(A, y)
    if B != J(A, y): return 'B-not-free', None
    s = a2(A)
    if M.op(s, B) != y: return 'ops_B-ne-y', None
    x = J(J(t, s), B)
    C = M.op(x, y)
    if C != J(x, y): return 'C-not-free', None
    D = M.op(B, C)
    if D != J(B, C):
        # Dfree violated; does the law still hold for this (x, y, z)?  z is free: any z with op z x = A
        return 'DFREE-VIOLATED', (y, z1, w, t, q, A, B, x, C, D, s)
    return 'D-free', (y, z1, w, t, q, A, B, x, C, D, s)


def main():
    random.seed(11)
    kinds = {}
    hits = []
    pool = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(g(0), g(0)), J(g(0), J(g(1), g(2)))]
    for it in range(6000):
        y = random.choice(pool); z1 = random.choice(pool)
        w = random.choice(pool); t = random.choice(pool)
        k, dat = try_one(y, z1, w, t)
        kinds[k] = kinds.get(k, 0) + 1
        if k == 'DFREE-VIOLATED' and len(hits) < 3:
            hits.append(dat)
    print('outcomes', kinds)
    for dat in hits:
        y, z1, w, t, q, A, B, x, C, D, s = dat
        print('--- Dfree VIOLATED')
        print('   y', size(y), show(y))
        print('   q', size(q), show(q) if size(q) < 80 else '<big>')
        print('   A', size(A), '  B', size(B), '  x', size(x), '  C', size(C))
        print('   op B C =', size(D), show(D) if size(D) < 80 else '<big>')
        print('   D == s ?', D == s)
        # is the law still true for some z with op z x = A ?
        for z in pool + [rnd(2) for _ in range(30)]:
            A2 = M.op(z, x)
            if A2 == A:
                Bp = M.op(A2, y); Cp = M.op(x, y); Dp = M.op(Bp, Cp)
                print('   found z with op z x = A; law op y D =', show(M.op(y, Dp))[:60],
                      ' expected x; holds?', M.op(y, Dp) == x)
                break
        else:
            print('   no z found with op z x = A among the probes'
                  ' (Dfree is stated for all x,y,z, so this still refutes Dfree)')


if __name__ == '__main__':
    main()
