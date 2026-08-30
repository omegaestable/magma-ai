"""Try to CONSTRUCT the residual `beta` configuration of Dfree for law 12234.

beta:  B = op A y is free, C = op x y is free, and op B C decodes.
Paper derivation forces:  a2 x = B = J A y, r = op B C = a2 A, y = op r B, y = op y r,
a2 r = J y y, A = op z x decoded, z = y (main branch).
Build all of that bottom-up out of law instances and see whether op B C really decodes.
"""
import sys, os, random, itertools
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
    """the encoding of w by u with z-slot q:  ((q*w)*u)*(w*u);  op u (enc w u q) = w by the law"""
    return M.op(M.op(M.op(q, w), u), M.op(w, u))


def rnd(d, k=3):
    if d <= 0 or random.random() < 0.4: return g(random.randrange(k))
    return J(rnd(d - 1, k), rnd(d - 1, k))


def attempt(y, z1, A1, z2, verbose=False):
    r = enc(y, y, z1)                       # op y r = y  (law with x := y)
    if M.op(y, r) != y: return ('selfdec-failed', None)
    A = J(A1, r)                            # a2 A = r  by construction
    B = M.op(A, y)
    if B != J(A, y): return ('B-not-free', None)
    V = M.op(M.op(z2, A), y)
    x = M.op(V, B)                          # x = enc(A, y, z2), so op y x = A by the law
    if x != J(V, B): return ('x-not-free', None)
    if M.op(y, x) != A: return ('opyx-ne-A', None)
    if a2(x) != B: return ('a2x-ne-B', None)
    C = M.op(x, y)
    if C != J(x, y): return ('C-not-free', None)
    if M.op(r, B) != y: return ('oprB-ne-y', None)
    if oc(B) != r: return ('ocB-ne-r', None)
    if oc(C) != B: return ('ocC-ne-B', None)
    D = M.op(B, C)
    if D != J(B, C):
        return ('DFREE-VIOLATED', (y, z1, A1, z2, A, B, C, D, r, V, x))
    return ('D-free-ok', (y, z1, A1, z2, A, B, C, D, r, V, x))


def main():
    random.seed(7)
    kinds = {}
    hit = None
    pool = [g(0), g(1), g(2), J(g(0), g(1)), J(g(1), g(0)), J(g(0), g(0))]
    trials = 0
    for it in range(40000):
        y = random.choice(pool) if random.random() < 0.6 else rnd(2)
        z1 = random.choice(pool) if random.random() < 0.6 else rnd(2)
        A1 = random.choice(pool) if random.random() < 0.6 else rnd(2)
        z2 = random.choice(pool) if random.random() < 0.6 else rnd(2)
        if max(size(y), size(z1), size(A1), size(z2)) > 12: continue
        trials += 1
        k, dat = attempt(y, z1, A1, z2)
        kinds[k] = kinds.get(k, 0) + 1
        if k == 'DFREE-VIOLATED' and hit is None:
            hit = dat
    print('trials', trials)
    print('outcomes', kinds)
    if hit:
        y, z1, A1, z2, A, B, C, D, r, V, x = hit
        for nm, t in (('y', y), ('r', r), ('A', A), ('B', B), ('x', x), ('C', C), ('D', D)):
            print(' ', nm, 'size', size(t), show(t) if size(t) < 60 else '<big>')

    # which check kills it most often -- print one full example of the commonest non-ok outcome
    for want in ('D-free-ok', 'C-not-free', 'x-not-free', 'B-not-free', 'opyx-ne-A', 'oprB-ne-y'):
        if kinds.get(want):
            random.seed(7)
            for it in range(40000):
                y = random.choice(pool) if random.random() < 0.6 else rnd(2)
                z1 = random.choice(pool) if random.random() < 0.6 else rnd(2)
                A1 = random.choice(pool) if random.random() < 0.6 else rnd(2)
                z2 = random.choice(pool) if random.random() < 0.6 else rnd(2)
                if max(size(y), size(z1), size(A1), size(z2)) > 12: continue
                k, dat = attempt(y, z1, A1, z2)
                if k == want and dat:
                    y, z1, A1, z2, A, B, C, D, r, V, x = dat
                    print('--- example of', want)
                    print('   y', size(y), show(y), ' r', size(r), ' A', size(A), ' B', size(B),
                          ' x', size(x), ' C', size(C))
                    print('   D == J B C ?', D == J(B, C), ' size D', size(D))
                    break
            break


if __name__ == '__main__':
    main()
