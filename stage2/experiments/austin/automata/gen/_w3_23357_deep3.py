"""23357 LEVEL-k DESCENT + LARGE JUNK (W3-6's two newest oracles), adapted from gen/_w3_12087_deep3.py.

Law   x = ((y*x)*y)*(x*(y*z)),  chain  A = op y x ; U = op A y ; B = op y z ; V = op x B ; top = op U V.
Encodings that make a product decode:
    encU(X,Y)   = op (op Y X) Y          -- the u-side of a top pair for payload X
    encV(X,Y,Z) = op X (op Y Z)          -- the v-side
and  op (encU(X,Y)) (encV(X,Y,Z)) = X  is exactly the law.

LEVEL k, on the z side: B = op y z decodes to a payload that is ITSELF an encV whose decode is an encV ...
so op x B decodes, and its result decodes, forcing the reader to descend k levels through one argument.
    T_0 = base ;  T_{i+1} = encV(T_i, Y, junk)      (a tower of v-encodings)
    y := encU(T_{k-1}, Y) ... etc.
LEVEL k, on the u side: A = op y x decodes and the result is again a u-encoding, so op A y decodes ...

The junk variable of this law is z (it occurs nowhere else), and every encoding carries its own junk slot;
`bigjunk` fills all of them from a pool of large fresh-generator terms (the 17286 lesson).

usage:  python gen/_w3_23357_deep3.py [rules-module] [N]
"""
import sys, os, random, collections, json, time
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, D + '/gen')
import closedform as cf
from freemodel import normalise, catalog, size, rand_term
from laws import parse_eq
import importlib.util

EQ = 23357
law = normalise(parse_eq(catalog()[EQ]))
MODPATH = sys.argv[1] if len(sys.argv) > 1 else D + '/gen/_x23357_rep.py'
spec = importlib.util.spec_from_file_location('_rulesmod', MODPATH)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
RULES = mod.rules
N = int(sys.argv[2]) if len(sys.argv) > 2 else 400


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s.%s)' % (show(t[1]), show(t[2]))


def run(name, rules, seed, bigjunk, levels, N, side):
    C = cf.Closed(law, rules)
    random.seed(seed)
    small = [rand_term(random.randint(1, 3), 2) for _ in range(120)]
    big = [rand_term(random.randint(5, 9), 3) for _ in range(120)]
    junk = big if bigjunk else small
    JJ = lambda: random.choice(junk)
    encU = lambda X, Y: C.op(C.op(Y, X), Y)
    encV = lambda X, Y, Z: C.op(X, C.op(Y, Z))
    dec = lambda u, v: C.op(u, v) != ('J', u, v)
    bad = 0; hits = 0; cells = collections.Counter(); worst = None
    for _ in range(N):
        try:
            Y = random.choice(small)
            if side == 'z':
                # tower of v-encodings so the z-side decode chain descends `levels` times
                T = random.choice(small)
                for _ in range(levels):
                    T = encV(T, Y, JJ())
                y = encU(T, Y)                 # op y z decodes to T when z is an encV for (T,Y)
                z = encV(T, Y, JJ())
                x = encU(T, Y) if levels else random.choice(small)
                if levels:
                    x = encU(C.op(y, z), Y)    # make op x B decode too
            else:
                # tower on the u side: op y x decodes, and its result is again a u-encoding
                T = random.choice(small)
                x = encV(T, Y, JJ())
                for _ in range(levels):
                    T = encU(T, Y)
                    x = encV(T, Y, JJ())
                y = encU(T, Y)
                z = random.choice(junk)
            if max(size(t) for t in (x, y, z)) > 400:
                continue
            A = C.op(y, x); U = C.op(A, y); B = C.op(y, z); V = C.op(x, B)
            got = C.op(U, V)
        except (RecursionError, KeyError):
            continue
        hits += 1
        cells[('A' + ('D' if A != ('J', y, x) else 'F'),
               'U' + ('D' if U != ('J', A, y) else 'F'),
               'B' + ('D' if B != ('J', y, z) else 'F'),
               'V' + ('D' if V != ('J', x, B) else 'F'))] += 1
        if got != x:
            bad += 1
            t = size(x) + size(y) + size(z)
            if worst is None or t < worst[0]:
                worst = (t, x, y, z, got)
    print('%-8s side=%s seed=%d bigjunk=%-5s levels=%d hits=%-5d BAD=%d'
          % (name, side, seed, bigjunk, levels, hits, bad), flush=True)
    for k, n in cells.most_common(5):
        print('      %-34s %d' % (str(k), n), flush=True)
    if worst:
        t, x, y, z, got = worst
        print('   SMALLEST BAD total=%d  x=%d y=%d z=%d' % (t, size(x), size(y), size(z)), flush=True)
        print('     x =', show(x)[:400], flush=True)
        print('     y =', show(y)[:400], flush=True)
        print('     z =', show(z)[:400], flush=True)
        json.dump({'x': x, 'y': y, 'z': z}, open(D + '/gen/_w3_23357_deep3_bad.json', 'w'))
    return bad


if __name__ == '__main__':
    tot = 0
    for side in ('z', 'u'):
        for lv in (0, 1, 2, 3):
            for bj in (False, True):
                for sd in (5, 19):
                    tot += run('R%d' % len(RULES), RULES, sd, bj, lv, N, side)
    print('TOTAL BAD', tot, flush=True)
