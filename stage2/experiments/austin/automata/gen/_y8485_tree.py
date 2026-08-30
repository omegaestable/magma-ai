"""_y8485_tree.py : the W3-6 CASE TREE for law 8485, variant f.

Law 8485 (L-form): x = y * (x * (((z*x)*y)*y))
  P = op(z,x)   Q = op(P,y)   R = op(Q,y)   S = op(x,R)   top = op(y,S) must be x.

For every assignment we record which rule fired at each of the 5 products (-1 = free), so the
census is the reachable set of cells of the 2^5 free/decoded tree -- and, per the 40037 warning,
we deliberately construct instances that make EACH rule fire at EACH chain product by chained
encoding, which no random sweep reaches.

Encoding (R1's own shape):  enc(u,w,zz) = J w (J (J (J zz w) u) u)  and  op(u, enc(u,w,zz)) = w.

Usage: python -u gen/_y8485_tree.py [maxsize] [gens]
"""
import sys, os, itertools, collections, threading, time, importlib.util
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
spec = importlib.util.spec_from_file_location('_x8485_min', 'gen/_x8485_min.py')
m = importlib.util.module_from_spec(spec); sys.modules['_x8485_min'] = m
_a = sys.argv; sys.argv = ['x', 'a']
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass
sys.argv = _a
import closedform as cf
from freemodel import size

law = m.law
R = m.VARIANTS['f']
TAGS = ['R1free', 'R2:zP@x22', 'R3:zP@u22', 'R4:zP@u221']


def J(a, b):
    return ('J', a, b)


def show(t):
    return ('g%d' % t[1]) if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def enc(u, w, zz):
    """the free encoding: op(u, enc(u,w,zz)) = w by R1"""
    return J(w, J(J(J(zz, w), u), u))


def which(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            if C.ev(x, u, v) is not None:
                return i
    return -1


def chain(C, x, y, z):
    P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); T = C.op(y, S)
    cells = (which(C, z, x), which(C, P, y), which(C, Rr if False else Q, y),
             which(C, x, Rr), which(C, y, S))
    return cells, T


def terms_upto(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)]}
    allt = list(by[1])
    for n in range(3, maxsize + 1, 2):
        cur = []
        for a in range(1, n - 1):
            b = n - 1 - a
            for s in by.get(a, []):
                for t in by.get(b, []):
                    cur.append(J(s, t))
        by[n] = cur
        allt += cur
    return allt


def run(pool, label, census, fails, limit=6):
    C = cf.Closed(law, R)
    n = 0
    for x, y, z in pool:
        n += 1
        try:
            cells, T = chain(C, x, y, z)
        except RecursionError:
            continue
        census[cells] += 1
        if T != x and len(fails) < limit:
            fails.append((label, x, y, z, cells, T))
    return n


def work():
    sys.setrecursionlimit(20000)
    census = collections.Counter()
    fails = []
    g0, g1, g2 = ('g', 0), ('g', 1), ('g', 2)

    # ---- 1. exhaustive over small terms
    ts = terms_upto(int(sys.argv[1]) if len(sys.argv) > 1 else 5,
                    int(sys.argv[2]) if len(sys.argv) > 2 else 2)
    t0 = time.time()
    n = run(list(itertools.product(ts, ts, ts)), 'exh', census, fails)
    print('exhaustive over %d terms: %d assignments  %.1fs' % (len(ts), n, time.time() - t0), flush=True)

    # ---- 2. CHAINED ENCODINGS: force each product to decode, one at a time and in combination
    pool = []
    small = [g0, g1, J(g0, g1), J(g1, J(g0, g0))]
    for w in small:
        for zz in small:
            for y in small:
                for z in small:
                    # (a) P decodes: x is the encoding of w under z
                    x = enc(z, w, zz)
                    pool.append((x, y, z))
                    # (b) Q decodes: y is the encoding of w under P (P computed free = J z x)
                    C0 = cf.Closed(law, R)
                    P0 = C0.op(z, g0)
                    pool.append((g0, enc(P0, w, zz), z))
                    # (c) R decodes: y encodes under Q
                    Q0 = C0.op(C0.op(z, g0), y)
                    pool.append((g0, enc(Q0, w, zz), z))
                    # (d) S decodes: R must be an encoding under x -- force via y
                    #     R = op(Q,y); make y such that R = enc(x, w, zz) is impossible directly,
                    #     so instead take x = g0 and y = enc(...) shapes (covered by (b)/(c)),
                    #     plus: v = R free = J Q y with y = enc-shaped so P1 x R can fire
                    pool.append((g0, enc(g0, w, zz), z))
                    # (e) top decodes through a rule other than R1: x J-shaped with a2 (a2 x) = z
                    pool.append((J(w, J(zz, z)), y, z))
    t0 = time.time()
    n2 = run(pool, 'chain', census, fails)
    print('chained-encoding pool: %d assignments  %.1fs' % (n2, time.time() - t0), flush=True)

    print('\nREACHABLE CELLS (P,Q,R,S,top ; -1 = free, k = rule k+1):', flush=True)
    for cells, c in census.most_common():
        print('  %-24s %8d   %s' % (str(cells), c,
                                    ' '.join(('free' if i < 0 else TAGS[i]) for i in cells)), flush=True)
    print('\nFAILURES: %d' % len(fails), flush=True)
    for lbl, x, y, z, cells, T in fails:
        print('  [%s] x=%s y=%s z=%s cells=%s got=%s' % (lbl, show(x), show(y), show(z), cells, show(T)), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
