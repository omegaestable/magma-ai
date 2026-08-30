# -*- coding: utf-8 -*-
"""LEVEL-K DESCENT oracle for 21864, adapted from gen/_w3_12087_deep3.py.

Law 21864:  x = (y * (z * x)) * (x * (x * y))
   decoder side  AT(y,z,t) = op(y, op(z,t))        encoding side  BT(t,y) = op(t, op(t,y))
   the law is exactly   op( AT(y,z,t), BT(t,y) ) = t          -- one matched PAIR per payload

R2 [B1s] fires when the ENCODING's inner product op(t,y) is itself decoded, which needs (t,y) to be
a decoding pair of the level below.  So the descent is built by ITERATING THE PAIR:

    (t_0, y_0) = (small, small)
    (t_{k+1}, y_{k+1}) = ( AT(y_k, junk, t_k),  BT(t_k, y_k) )        so op(t_{k+1}, y_{k+1}) = t_k

and y_{k+1}'s own inner product op(t_k, y_k) is again a decode, k levels deep.  Feeding
x := t_L, y := y_L into the law forces the same rule at L successive depths of one argument.

usage: python gen/_p2_deep321864.py [N] [--selftest]
"""
import sys, os, random, collections, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
import _x21864_rules as RR

law = normalise(parse_eq(catalog()[21864]))
T8 = RR.GEN[:5] + [RR.R4c, RR.R5c, RR.RA, RR.R6d, RR.R6e, RR.RB, RR.RB2, RR.RD]
SETS = {'ship11': [r for i, r in enumerate(T8) if i not in {2, 8}], 't8_13': T8, 'gen9': RR.GEN}
J = lambda a, b: ('J', a, b)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


VARIANT = 'B'


def run(name, rules, seed, bigjunk, levels, N, verbose=False):
    C = cf.Closed(law, rules)
    random.seed(seed)
    small = [rand_term(random.randint(1, 3), 2) for _ in range(80)]
    big = [rand_term(random.randint(5, 8), 3) for _ in range(80)]
    junk = big if bigjunk else small

    def AT(y, z, t):
        return C.op(y, C.op(z, t))

    def BT(t, y):
        return C.op(t, C.op(t, y))

    def dec(a, b):
        return C.op(a, b) != J(a, b)

    bad = hits = ndec = 0
    cells = collections.Counter()
    worst = None
    for i in range(N):
        try:
            t = random.choice(small)
            y = random.choice(small)
            depth = 0
            for _ in range(levels):
                t, y = AT(y, random.choice(junk), t), BT(t, y)
                depth += 1
            # variant A: x is the deep decoder, y its matched encoding  -> Q = op(x,y) descends
            # variant B: x is the deep ENCODING and z the matched decoder -> P = op(z,x) descends
            if VARIANT == 'A':
                x, yy, zz = t, y, random.choice(junk)
            else:
                x, yy, zz = y, random.choice(small), t
            P = C.op(zz, x); u = C.op(yy, P); Q = C.op(x, yy); v = C.op(x, Q); top = C.op(u, v)
        except RecursionError:
            continue
        hits += 1
        cell = tuple('D' if d else 'F' for d in (dec(zz, x), dec(yy, P), dec(x, yy), dec(x, Q)))
        cells[cell] += 1
        if 'D' in cell:
            ndec += 1
        if top != x:
            bad += 1
            tot = size(x) + size(yy) + size(zz)
            if worst is None or tot < worst[0]:
                worst = (tot, x, yy, zz, top)
    print('%-8s var=%s seed=%-3d bigjunk=%-5s levels=%d hits=%-5d decoding=%-5d BAD=%d  cycles=%d'
          % (name, VARIANT, seed, bigjunk, levels, hits, ndec, bad, C.cycles), flush=True)
    for k, n in cells.most_common(4):
        print('      %-26s %d' % (str(k), n), flush=True)
    if worst:
        tot, x, yy, zz, top = worst
        print('   SMALLEST BAD total=%d  x=%d y=%d z=%d' % (tot, size(x), size(yy), size(zz)), flush=True)
        print('     x =', show(x)[:240], flush=True)
        print('     y =', show(yy)[:240], flush=True)
        print('     z =', show(zz)[:240], flush=True)
        print('     got =', show(top)[:240], flush=True)
        json.dump({'x': x, 'y': yy, 'z': zz, 'set': name, 'levels': levels},
                  open(os.path.join(HERE, '_p2_deep321864_bad.json'), 'w'))
    return bad, ndec


if __name__ == '__main__':
    N = int(sys.argv[1]) if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else 300
    for va in ('A', 'B'):
        VARIANT = va
        for nm in ('gen9', 'ship11', 't8_13'):
            tot = totd = 0
            for lv in (1, 2, 3, 4):
                for bj in (False, True):
                    for sd in (5, 19, 77, 101):
                        b, d = run(nm, SETS[nm], sd, bj, lv, N)
                        tot += b
                        totd += d
            print('>>> %s var=%s TOTAL BAD %d  (instances with >=1 decode: %d)'
                  % (nm, va, tot, totd), flush=True)
