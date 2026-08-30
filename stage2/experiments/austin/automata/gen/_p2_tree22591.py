"""Full wave-3 validation of 22591's model (gen/_p2_q22591.py):
   (1) the CASE TREE  -- explicit construction of every (P,S,v) free/decoded cell
   (2) qmod.run_tests (exhaustive + deep + closure + critical) must be EMPTY
   (3) deep at 20,000 on >= 3 seeds
   (4) identity_probe (qz_lib's, adapted to this carrier)

`u = op(y, op(y,x))` is proved never to decode (see gen/P2_MECHANISM.md), so the tree is 2^3.

usage: python gen/_p2_tree22591.py <MODE> [stage]     stage in {tree,tests,deep,probe,all}
"""
import sys, os, random, itertools, collections, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
_ARGV = list(sys.argv)
sys.argv = [sys.argv[0], _ARGV[1] if len(_ARGV) > 1 else '6']
import qmod
qmod.UNARY = []
from qmod import sz, terms_upto
import _p2_q22591 as Q

MODE = int(sys.argv[1])
STAGE = _ARGV[2] if len(_ARGV) > 2 else 'all'
J = Q.J
g = lambda n: ('g', n)


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else ('E' if t[0] == 'E' else '(%s*%s)' % (show(t[1]), show(t[2])))


def chain(M, x, y, z):
    P = M.op(y, x); u = M.op(y, P); S = M.op(x, x); v = M.op(S, z); top = M.op(u, v)
    return (P != J(y, x), u != J(y, P), S != J(x, x), v != J(S, z)), top


def invsq(M, s):
    T = M.op(s, s)
    return J(T, J(T, s))


# --------------------------------------------------------------------- (1) the case tree
def case_tree(M):
    """one constructed instance per (P,S,v) cell, built by chained encoding."""
    cases = []
    ws = [g(0), J(g(0), g(1)), J(J(g(0), g(1)), g(2)), J(g(0), J(g(1), g(2)))]
    for w in ws:
        T = M.op(w, w)
        Iw = invsq(M, w)               # op(Iw,Iw) = w
        IIw = invsq(M, Iw)             # op(IIw,IIw) = Iw
        zdec = J(M.op(w, w), g(7))     # a1 z = op(w,w)  makes op(Iw, z) decode to w
        # FFF : nothing decodes
        cases.append(('FFF', g(0), g(1), g(2)))
        # FTF : S dec (x = invsq w), P free (y an atom), v free
        cases.append(('FTF', Iw, g(1), g(2)))
        # TTF : P dec and S dec, v free   <- the recorded R3 refutation family
        cases.append(('TTF', Iw, J(g(3), J(g(3), w)), g(2)))
        # FTT : S dec and v dec, P free.  x = invsq(invsq(v)), z decodes op(S,z)
        cases.append(('FTT', IIw, g(1), J(M.op(w, w), g(7))))
        cases.append(('FTT', IIw, g(1), zdec))
        # TTT : P dec, S dec, v dec.  y = J p (J p Iw) with op(Iw,Iw) = w = a1 x
        cases.append(('TTT', IIw, J(g(3), J(g(3), Iw)), zdec))
        cases.append(('TTT', IIw, J(w, J(w, Iw)), zdec))
        # TFF : P dec, S free, v free.  a1 x = op(P,P) with P := w  ->  x = J (op(w,w)) t
        cases.append(('TFF', J(T, g(4)), J(g(3), J(g(3), w)), g(2)))
        # FFT / TFT : S free and v dec -- claimed impossible; construct the attempt anyway
        cases.append(('FFT?', J(g(0), g(1)), g(1), J(J(w, w), g(7))))
        cases.append(('TFT?', J(T, g(4)), J(g(3), J(g(3), w)), J(J(w, w), g(7))))
        # one more level of nesting: x = invsq^3
        IIIw = invsq(M, IIw)
        cases.append(('TTT-3', IIIw, J(g(3), J(g(3), IIw)), J(M.op(Iw, Iw), g(7))))
        cases.append(('FTT-3', IIIw, g(1), J(M.op(Iw, Iw), g(7))))
    return cases


def run_tree():
    M = Q.Mod(MODE)
    cases = case_tree(M)
    cells = collections.Counter()
    bad = 0
    for lab, x, y, z in cases:
        try:
            cell, top = chain(M, x, y, z)
        except RecursionError:
            print('  RECURSION %s' % lab); bad += 1; continue
        key = (cell[0], cell[2], cell[3])
        cells[('T' if key[0] else 'F') + ('T' if key[1] else 'F') + ('T' if key[2] else 'F')] += 1
        if cell[1]:
            print('  !! u DECODED (contradicts the freeness lemma) at %s' % lab)
        if top != x:
            bad += 1
            print('  **FAIL** %-7s cell(P,S,v)=%s x=%s y=%s z=%s -> %s'
                  % (lab, key, show(x)[:44], show(y)[:34], show(z)[:24], show(top)[:44]))
    print('case tree: %d instances, %d fails; cells realised %s'
          % (len(cases), bad, dict(cells)))
    return bad


# --------------------------------------------------------------------- (4) identity probe
def identity_probe(seeds=(1, 2, 3, 4, 5, 6), rounds=800, depth=3):
    M = Q.Mod(MODE)
    subs = []

    def walk(p):
        if isinstance(p, str):
            return
        subs.append(p); walk(p[0]); walk(p[1])
    walk(Q.LAW[1])
    vs = ['x', 'y', 'z']
    n = 0
    fails = []
    for sd in seeds:
        rng = random.Random(sd)
        pool = [g(i) for i in range(3)] + [qmod.rand_term(depth, 3, 0.0) for _ in range(24)]
        for t in [g(0), g(1), J(g(0), g(1))]:
            a = invsq(M, t); pool += [a, invsq(M, a)]
        for _ in range(rounds):
            base = {v: rng.choice(pool) for v in vs}
            if rng.random() < 0.5:
                a, b = rng.sample(vs, 2)
                base[a] = base[b]
            cur = dict(base)
            for _lvl in range(3):
                p = rng.choice(subs)
                try:
                    val = M.ev(p, cur)
                except RecursionError:
                    break
                if sz(val) > 4000:
                    break
                s = dict(base)
                s[rng.choice(vs)] = val
                if rng.random() < 0.5:
                    s['x'] = val
                n += 1
                try:
                    got = M.ev(Q.LAW[1], s)
                except RecursionError:
                    fails.append((s, 'recursion')); break
                if got != s['x']:
                    fails.append((dict(s), got))
                    if len(fails) >= 5:
                        return n, fails
                cur = s
    return n, fails


if __name__ == '__main__':
    print('=== 22591 MODE %d  stage=%s ===' % (MODE, STAGE))
    if STAGE in ('tree', 'all'):
        t0 = time.time(); run_tree(); print('  (%.1fs)' % (time.time() - t0))
    if STAGE in ('tests', 'all'):
        t0 = time.time()
        f = qmod.run_tests(lambda: Q.Mod(MODE), Q.LAW, (3, 4, 5), 3000, 12000,
                           small=((7, 1), (5, 2)))
        print('run_tests(3,4,5 / 3000 / 12000): %d fails  (%.1fs)' % (len(f), time.time() - t0))
        for s, r, k, sd in f[:4]:
            print('  FAIL[%s] %s -> %s' % (k, {a: show(b) for a, b in s.items()},
                                           show(r) if r != 'recursion' else r))
    if STAGE in ('deep', 'all'):
        for sd in (77, 78, 91):
            t0 = time.time()
            n, f = qmod.deep(Q.Mod(MODE), Q.LAW, 20000, sd)
            print('deep20k seed %d: tested %d fails %d  (%.1fs)' % (sd, n, len(f), time.time() - t0))
            for s, r in f[:2]:
                print('  FAIL %s -> %s' % ({a: show(b) for a, b in s.items()},
                                           show(r) if r != 'recursion' else r))
    if STAGE in ('probe', 'all'):
        t0 = time.time()
        n, f = identity_probe()
        print('identity_probe n=%d fails=%d  (%.1fs)' % (n, len(f), time.time() - t0))
        for s, r in f[:3]:
            print('  FAIL', {k: show(v)[:70] for k, v in s.items()}, '->',
                  show(r)[:70] if r != 'recursion' else r)
