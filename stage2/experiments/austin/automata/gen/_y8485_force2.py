# -*- coding: utf-8 -*-
"""_y8485_force2.py : CORRECTED forcing suite for law 8485 (the 10218 lesson).

A forcing run proves nothing unless the census says the rule ACTUALLY FIRED.  Rules beyond the first
differ from R1 only in that a product inside their guard is DECODED rather than free; build that
product free and R1's precondition holds too, R1 is checked first, and the "forced" firing never
happens.  So: to force rule k, construct the product inside rule k's OWN guard as an encoding.

Law 8485 (L-form):  x = y * (x * (((z*x)*y)*y))
  P = op(z,x)   Q = op(P,y)   R = op(Q,y)   S = op(x,R)   top = op(y,S)  must be x.

  R1 [free]    reads the whole chain structurally out of v      -> needs P,Q,R free
  R2 [zP@x22]  z at a2(a2(a1 v))   fires when *P is decoded*    -> force with  x := enc(z, w, j)
  R3 [zP@u22]  z at a1(a2(a2 u))   fires when *Q is decoded*    -> force with  y := enc(P, w, j)
  R4 [zP@u221] z at a1(a1(a2(a2 u))) fires when *R is decoded*  -> force with  y := enc(Q, w, j)  (fixpoint)

  H3           y := enc(j, w, x)   -- y a genuine encoding BY x

Every construction is also evaluated under the FULL 83-rule extraction, so that a failure can be
classified as a real model failure or a MINIMISATION ARTIFACT (10218's shape).

Usage: python -u gen/_y8485_force2.py [N]
"""
import sys, os, random, collections, threading, time, importlib.util
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
VF = m.VARIANTS['f']
FULL = cf.Extractor(law).rules(exist=False)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 200


class CT(cf.Closed):
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


def chain(C, x, y, z):
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R); T = C.op(y, S)
    cells = (C.ruleof.get((z, x), -1), C.ruleof.get((P, y), -1), C.ruleof.get((Q, y), -1),
             C.ruleof.get((x, R), -1), C.ruleof.get((y, S), -1))
    return cells, T


def build(C, kind, small, junk, rnd):
    """returns (x, y, z) or None"""
    def enc(u, w, j):
        return C.op(w, C.op(C.op(C.op(j, w), u), u))
    z = rnd.choice(small); y = rnd.choice(small)
    if kind == 'A-generic':
        return rnd.choice(small), y, z
    if kind == 'B-R2 (P decoded: x = enc(z,w,j))':
        x = enc(z, rnd.choice(small), rnd.choice(junk))
        return x, y, z
    if kind == 'C-R3 (Q decoded: y = enc(P,w,j))':
        x = rnd.choice(small); P = C.op(z, x)
        return x, enc(P, rnd.choice(small), rnd.choice(junk)), z
    if kind == 'D-R4 (R decoded: y = enc(Q,w,j), fixpoint)':
        x = rnd.choice(small); P = C.op(z, x); y0 = rnd.choice(small)
        for _ in range(3):
            Q = C.op(P, y0)
            y0 = enc(Q, rnd.choice(small), rnd.choice(junk))
        return x, y0, z
    if kind == 'E-H3 (y = enc(j,w,x): y an encoding BY x)':
        x = rnd.choice(small)
        return x, enc(rnd.choice(junk), rnd.choice(small), x), z
    if kind == 'F-B+C (P and Q both decoded)':
        x = enc(z, rnd.choice(small), rnd.choice(junk)); P = C.op(z, x)
        return x, enc(P, rnd.choice(small), rnd.choice(junk)), z
    if kind == 'G-B+E':
        x = enc(z, rnd.choice(small), rnd.choice(junk))
        return x, enc(rnd.choice(junk), rnd.choice(small), x), z
    return None


KINDS = ['A-generic', 'B-R2 (P decoded: x = enc(z,w,j))', 'C-R3 (Q decoded: y = enc(P,w,j))',
         'D-R4 (R decoded: y = enc(Q,w,j), fixpoint)', 'E-H3 (y = enc(j,w,x): y an encoding BY x)',
         'F-B+C (P and Q both decoded)', 'G-B+E']
WANT = {'A-generic': 0, 'B-R2 (P decoded: x = enc(z,w,j))': 1,
        'C-R3 (Q decoded: y = enc(P,w,j))': 2, 'D-R4 (R decoded: y = enc(Q,w,j), fixpoint)': 3}


def work():
    sys.setrecursionlimit(20000)
    print('variant f: %d rules;  FULL extraction: %d rules' % (len(VF), len(FULL)), flush=True)
    grand = 0
    sel = os.environ.get('KINDS')
    for kind in ([k for k in KINDS if k[0] in sel] if sel else KINDS):
        for bigjunk in (False, True):
            for seed in (7, 23):
                rnd = random.Random(seed)
                C = CT(law, VF)
                small = [rand_term(rnd.randint(1, 3), 2) for _ in range(120)]
                junk = [rand_term(rnd.randint(5, 8), 3) for _ in range(120)] if bigjunk else small
                cells = collections.Counter(); fails = []; n = 0; firedtop = collections.Counter()
                for _ in range(N):
                    try:
                        t = build(C, kind, small, junk, rnd)
                        if t is None:
                            continue
                        x, y, z = t
                        cl, T = chain(C, x, y, z)
                    except RecursionError:
                        continue
                    n += 1
                    cells[cl] += 1
                    firedtop[cl[4]] += 1
                    if T != x:
                        fails.append((x, y, z, cl, T))
                w = WANT.get(kind)
                ok = firedtop.get(w, 0) if w is not None else None
                grand += len(fails)
                print('%-46s junk=%-5s seed=%-3d n=%-4d BAD=%-3d  top-rule census=%s%s'
                      % (kind, bigjunk, seed, n, len(fails), dict(firedtop),
                         ('   *** rule %d fired %d/%d ***' % (w, ok, n)) if w is not None else ''),
                      flush=True)
                if fails:
                    CFULL = CT(law, FULL)
                    for x, y, z, cl, T in fails[:2]:
                        P = CFULL.op(z, x); Q = CFULL.op(P, y); R = CFULL.op(Q, y)
                        S = CFULL.op(x, R); TF = CFULL.op(y, S)
                        print('    FAIL cells=%s' % (cl,), flush=True)
                        print('      x=%s' % show(x)[:200], flush=True)
                        print('      y=%s' % show(y)[:200], flush=True)
                        print('      z=%s' % show(z)[:200], flush=True)
                        print('      variant-f got %s ; FULL-83 got %s -> %s'
                              % (show(T)[:120], show(TF)[:120],
                                 'MINIMISATION ARTIFACT' if TF == x else 'REAL MODEL FAILURE'), flush=True)
    print('GRAND TOTAL BAD %d' % grand, flush=True)


threading.stack_size(96 * 1024 * 1024)
th = threading.Thread(target=work); th.start(); th.join()
