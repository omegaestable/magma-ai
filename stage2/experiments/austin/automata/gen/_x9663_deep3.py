# -*- coding: utf-8 -*-
"""LEVEL-k DESCENT + LARGE JUNK for the 9663 models (the sixth oracle, LEMMA_LIBRARY).

enc(u,w,j) = the code of w w.r.t. u = J A (J w (op w u)), with A in im(R_u) in one of two flavours:
   'free'    A = J j u
   'dec'     A = a1 (a2 u)      (needs u = J _ (J A _); this is inimg's second disjunct)

Descent of depth k: p_k base, p_{i} = enc(x, p_{i+1}, j), y = enc(x, p_1, j).
Then op(x,y) = p_1, op(x,p_1) = p_2, ... all decode -- the SAME rule at k successive depths of the
same argument.  Large junk: j drawn from a pool of deliberately big terms (17286's refutation shape).
"""
import sys, os, random, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _idc_lib import G, J, sz, show
M = __import__(sys.argv[1] if len(sys.argv) > 1 else 'q9663c')
op, inimg = M.op, M.inimg

def rand_term(rng, n, gens=3):
    if n <= 1: return G(rng.randrange(gens))
    a = rng.randint(1, n - 1)
    return J(rand_term(rng, a, gens), rand_term(rng, n - a, gens))

def enc(u, w, j, flavour):
    P = op(w, u)
    if flavour == 'free':
        A = J(j, u)
    else:
        if not (u[0] == 'J' and u[2][0] == 'J'): return None
        A = u[2][1]
    if not inimg(A, u): return None
    return J(A, J(w, P))

def run(seed, depth, bigjunk, flavour, N):
    rng = random.Random(seed)
    small = [rand_term(rng, rng.randint(1, 4), 2) for _ in range(120)]
    big = [rand_term(rng, rng.randint(9, 17), 3) for _ in range(120)]
    junk = big if bigjunk else small
    hits = bad = 0; cells = collections.Counter(); worst = None
    for _ in range(N):
        x = rng.choice(small)
        p = rng.choice(small)
        ok = True
        for _ in range(depth):
            p = enc(x, p, rng.choice(junk), flavour)
            if p is None: ok = False; break
        if not ok: continue
        y = enc(x, p, rng.choice(junk), flavour)
        if y is None: continue
        if op(x, y) != p: continue                       # the first decode must really fire
        z = rng.choice(small + junk)
        P = op(x, y); Q = op(x, P); A = op(z, y); Cc = op(A, Q); R = op(y, Cc)
        hits += 1
        cells[(P != J(x, y), Q != J(x, P), A != J(z, y), Cc != J(A, Q))] += 1
        if R != x:
            bad += 1
            t = sz(x) + sz(y) + sz(z)
            if worst is None or t < worst[0]: worst = (t, x, y, z, R)
    print('  seed=%d depth=%d bigjunk=%-5s A=%-4s hits=%-5d BAD=%d' % (seed, depth, bigjunk, flavour, hits, bad), flush=True)
    for k, n in cells.most_common(4):
        print('       cell P%d Q%d A%d C%d : %d' % (k[0], k[1], k[2], k[3], n), flush=True)
    if worst:
        t, x, y, z, R = worst
        print('   SMALLEST BAD total=%d  x=%d y=%d z=%d' % (t, sz(x), sz(y), sz(z)), flush=True)
        print('     x =', show(x)[:220], flush=True)
        print('     y =', show(y)[:220], flush=True)
        print('     z =', show(z)[:120], flush=True)
        print('     -> ', show(R)[:220], flush=True)
    return bad

tot = 0
for fl in ('free', 'dec'):
    for depth in (0, 1, 2, 3):
        for bj in (False, True):
            for sd in (5, 19):
                tot += run(sd, depth, bj, fl, 400)
print('%s TOTAL BAD %d' % (sys.argv[1] if len(sys.argv) > 1 else 'q9663c', tot), flush=True)
