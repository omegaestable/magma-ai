"""Probe the key lemma Dfree for law 12234:  op (op (op z x) y) (op x y) = J (op (op z x) y) (op x y).

Also probes the two hard sub-cases of the size digest:
  alpha : B = op A y decoded, C = op x y free
  beta  : B free, C free, A = op z x decoded
and collects, for any violating instance, the rule that fired.
"""
import sys, os, time, random, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen')
sys.setrecursionlimit(20000)
from freemodel import size
import smallcheck as sc
import _x12234_leanval as LV

LeanModel, J, isJ, a1, a2, oc, msr = LV.LeanModel, LV.J, LV.isJ, LV.a1, LV.a2, LV.oc, LV.msr


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def rulefired(M, u, v):
    """which rule index fires on (u,v) in the Lean op (0 = free)"""
    before = dict(M.fired)
    M.memo.pop((u, v), None)
    M.op(u, v)
    after = M.fired
    for k in range(1, 7):
        if after.get(k, 0) != before.get(k, 0):
            return k
    return 0


def probe(M, x, y, z, bad, stats):
    A = M.op(z, x)
    B = M.op(A, y)
    C = M.op(x, y)
    D = M.op(B, C)
    Bfree = (B == J(A, y))
    Cfree = (C == J(x, y))
    Afree = (A == J(z, x))
    stats[(Afree, Bfree, Cfree)] = stats.get((Afree, Bfree, Cfree), 0) + 1
    if D != J(B, C):
        bad.append(('Dfree', x, y, z, A, B, C, D, Afree, Bfree, Cfree))
        return
    # the two hard case shapes: record whether they occur at all
    if (not Bfree) and Cfree:
        stats['alpha'] = stats.get('alpha', 0) + 1
    if Bfree and Cfree and (not Afree):
        stats['beta'] = stats.get('beta', 0) + 1


def main():
    pool9 = sc.terms_upto(9, 1)
    pool5 = sc.terms_upto(5, 2)
    bad = []; stats = {}
    M = LeanModel()
    t0 = time.time()
    for pool in (pool9, pool5):
        for x, y, z in itertools.product(pool, repeat=3):
            probe(M, x, y, z, bad, stats)
    print('exhaustive done', round(time.time() - t0, 1), 's  violations', len(bad))

    # random deep terms built from the model's own encodings (coincidence-targeted)
    def rnd(d):
        if d <= 0 or random.random() < 0.35: return ('g', random.randrange(3))
        return J(rnd(d - 1), rnd(d - 1))

    def enc(w, u, q):
        return M.op(M.op(M.op(q, w), u), M.op(w, u))

    random.seed(20260829)
    pool = [('g', i) for i in range(3)]
    n = 0
    for it in range(60000):
        mode = random.randrange(4)
        if mode == 0:
            x, y, z = rnd(3), rnd(3), rnd(3)
        elif mode == 1:
            w, u, q = random.choice(pool), random.choice(pool), random.choice(pool)
            x = enc(w, u, q); y = random.choice(pool); z = random.choice(pool)
        elif mode == 2:
            w, u, q = random.choice(pool), random.choice(pool), random.choice(pool)
            y = enc(w, u, q); x = random.choice(pool); z = random.choice(pool)
        else:
            w, u, q = random.choice(pool), random.choice(pool), random.choice(pool)
            z = enc(w, u, q); x = random.choice(pool); y = random.choice(pool)
        if max(size(x), size(y), size(z)) > 130: continue
        n += 1
        probe(M, x, y, z, bad, stats)
        for t in (x, y, z, M.op(x, y), M.op(z, x)):
            if size(t) <= 45 and len(pool) < 500: pool.append(t)
        if len(bad) > 4: break
    print('random targeted', n, 'violations', len(bad))
    print('shape stats (Afree,Bfree,Cfree):',
          {str(k): v for k, v in sorted(stats.items(), key=lambda kv: str(kv[0]))})
    for b in bad[:4]:
        print('VIOLATION', b[0])
        print('   x =', show(b[1])); print('   y =', show(b[2])); print('   z =', show(b[3]))
        print('   A =', show(b[4]), 'free', b[8]); print('   B =', show(b[5]), 'free', b[9])
        print('   C =', show(b[6]), 'free', b[10]); print('   D =', show(b[7]))
        print('   rule fired on (B,C):', rulefired(M, b[5], b[6]))


if __name__ == '__main__':
    main()
