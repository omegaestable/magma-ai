# -*- coding: utf-8 -*-
"""_y8485_deep3.py : the LEVEL-k DESCENT oracle for law 8485 (the 12087 construction, adapted).

Law 8485 (L-form):  x = y * (x * (((z*x)*y)*y))
Chain:  P = op(z,x)   Q = op(P,y)   R = op(Q,y)   S = op(x,R)   op(y,S) must be x.

The decoder reads the payload out of the RIGHT argument, so "descending in the same argument"
means: x is an encoding whose payload is an encoding whose payload is an encoding, all under the
SAME left element `u0`, and then z := u0 so that the chain's first product op(z,x) decodes, its
result decodes again, and so on.

    enc(u,w,j) = op(w, op(op(op(j,w),u),u))          -- semantic, built with C.op, so inner decodes fire
    op(u, enc(u,w,j)) = w                            -- the law itself

    p_0 = small ; p_{i+1} = enc(u0, p_i, junk) ; x = p_levels ; z = u0
    => op(z,x), op(z, op(z,x)), op(z, op(z, op(z,x))) all decode  (levels successive depths)

Also (a) LARGE JUNK: the junk slot `j` no rule constrains, drawn from big terms.
Usage: python -u gen/_y8485_deep3.py [N]
"""
import sys, os, random, collections, json, threading, importlib.util
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
os.chdir(D)
spec = importlib.util.spec_from_file_location('_x8485_min', 'gen/_x8485_min.py')
m = importlib.util.module_from_spec(spec); sys.modules['_x8485_min'] = m
_a = sys.argv; sys.argv = ['x', 'a']
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass
sys.argv = _a
import closedform as cf
from freemodel import size, rand_term

law = m.law
RULES = m.VARIANTS['f']
TAGS = ['R1', 'R2', 'R3', 'R4']
N = int(sys.argv[1]) if len(sys.argv) > 1 else 300


class C2(cf.Closed):
    def __init__(self, law, rules):
        super().__init__(law, rules); self.ruleof = {}

    def op(self, u, v):
        key = (u, v)
        mm = self.memo.get(key)
        if mm is not None:
            return mm
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None; ri = None
        for i, (conds, xx, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(xx, u, v)
                if r is not None:
                    res = r; ri = i; break
        self.inprog.discard(key)
        if res is None:
            res = ('J', u, v)
        else:
            self.ruleof[key] = ri
        self.memo[key] = res
        return res


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def run(seed, bigjunk, levels, N):
    C = C2(law, RULES); random.seed(seed)
    small = [rand_term(random.randint(1, 3), 2) for _ in range(120)]
    big = [rand_term(random.randint(5, 8), 3) for _ in range(120)]
    junk = big if bigjunk else small

    def enc(u, w, j):
        return C.op(w, C.op(C.op(C.op(j, w), u), u))

    def dec(u, v):
        return C.op(u, v) != ('J', u, v)

    bad = 0; hits = 0; depth_ok = 0
    cells = collections.Counter(); worst = None
    for _ in range(N):
        try:
            u0 = random.choice(small)
            p = random.choice(small)
            for _ in range(levels):
                p = enc(u0, p, random.choice(junk))
            x = enc(u0, p, random.choice(junk))
            z = u0
            y = random.choice(small)
            if not dec(z, x):
                continue
            # how many successive decodes in the SAME argument
            d = 0; cur = x
            while d < 5 and dec(z, cur):
                cur = C.op(z, cur); d += 1
            P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y)
            S = C.op(x, Rr); T = C.op(y, S)
        except RecursionError:
            continue
        hits += 1
        if d >= 3:
            depth_ok += 1
        cells[(C.ruleof.get((z, x), -1), C.ruleof.get((P, y), -1), C.ruleof.get((Q, y), -1),
               C.ruleof.get((x, Rr), -1), C.ruleof.get((y, S), -1), 'depth%d' % d)] += 1
        if T != x:
            bad += 1
            t = size(x) + size(y) + size(z)
            if worst is None or t < worst[0]:
                worst = (t, y, x, z, T)
    print('seed=%-3d bigjunk=%-5s levels=%d  hits=%-4d depth>=3: %-4d cycles=%d  BAD=%d'
          % (seed, bigjunk, levels, hits, depth_ok, C.cycles, bad), flush=True)
    for k, n in cells.most_common(4):
        print('      %-46s %d' % (str(k), n), flush=True)
    if worst:
        t, y, x, z, T = worst
        print('   SMALLEST BAD total=%d  y=%d x=%d z=%d' % (t, size(y), size(x), size(z)), flush=True)
        print('     y =', show(y)[:220], flush=True)
        print('     x =', show(x)[:220], flush=True)
        print('     z =', show(z)[:220], flush=True)
        print('     got =', show(T)[:220], flush=True)
        json.dump({'y': y, 'x': x, 'z': z}, open('gen/_y8485_deep3_bad.json', 'w'))
    return bad


def work():
    sys.setrecursionlimit(20000)
    tot = 0
    for lv in (0, 1, 2, 3):
        for bj in (False, True):
            for sd in (5, 19):
                tot += run(sd, bj, lv, N)
    print('TOTAL BAD %d' % tot, flush=True)


threading.stack_size(96 * 1024 * 1024)
th = threading.Thread(target=work); th.start(); th.join()
