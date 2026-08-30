"""_y8485_fire.py : the 40037 check for law 8485 -- make EACH rule fire at EACH chain product.

A rule whose precondition constrains only `a1 v` (or only `u`), with `v` pinned solely by a
recomputation guard, can fire at a DIFFERENT product of the chain than the one it was extracted for.
No sweep finds those instances; they must be CONSTRUCTED from the rule's own precondition.

Constructors (v built so that rule k fires on the pair (u,v)):
  k=0 R1 [free]     v = J w (J (J (J zz w) u) u)                       -> w
  k=1 R2 [zP@x22]   v = J w c,  tg w = 2, tg (a2 w) = 2,
                    c = op(op(op(a2(a2 w), w), u), u)                  -> w
  k=2 R3 [zP@u22]   needs tg u = 2, tg (a2 u) = 2, tg (a2 (a2 u)) = 2;
                    v = J w c, c = op(op(op(a1(a2(a2 u)), w), u), u)   -> w
  k=3 R4 [zP@u221]  as k=2 with one more level: z at a1 (a1 (a2 (a2 u)))

Then, for each product of the law's chain, we build assignments that force that product's pair to
match each constructor, and check the law.

Usage: python -u gen/_y8485_fire.py
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
RULES = m.VARIANTS['f']
TAGS = ['R1free', 'R2:zP@x22', 'R3:zP@u22', 'R4:zP@u221']


def J(a, b):
    return ('J', a, b)


def a1(t):
    return t[1] if t[0] == 'J' else None


def a2(t):
    return t[2] if t[0] == 'J' else None


def show(t):
    return ('g%d' % t[1]) if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def which(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i
    return -1


def mk(C, k, u, w, zz):
    """a v on which rule k should fire with payload w; None if the shape is unavailable"""
    if k == 0:
        return J(w, J(J(J(zz, w), u), u))
    if k == 1:
        if w[0] != 'J' or a2(w)[0] != 'J':
            return None
        c = C.op(C.op(C.op(a2(a2(w)), w), u), u)
        return J(w, c)
    if k in (2, 3):
        if u[0] != 'J' or a2(u)[0] != 'J' or a2(a2(u))[0] != 'J':
            return None
        zt = a1(a2(a2(u)))
        if k == 3:
            if zt[0] != 'J':
                return None
            zt = a1(zt)
        c = C.op(C.op(C.op(zt, w), u), u)
        return J(w, c)
    return None


def chain_cells(C, x, y, z):
    P = C.op(z, x); Q = C.op(P, y); R = C.op(Q, y); S = C.op(x, R); T = C.op(y, S)
    return (which(C, z, x), which(C, P, y), which(C, Q, y), which(C, x, R), which(C, y, S)), T


def work():
    sys.setrecursionlimit(20000)
    g = [('g', 0), ('g', 1), ('g', 2)]
    seeds = g + [J(g[0], g[1]), J(J(g[0], g[1]), g[2]), J(g[0], J(g[1], g[2])),
                 J(J(g[0], g[0]), J(g[1], g[1])),
                 J(g[0], J(g[1], J(g[0], g[1]))),
                 J(J(g[0], g[1]), J(g[2], J(g[0], g[1]))),
                 J(g[1], J(J(g[0], g[1]), J(g[2], g[0])))]
    census = collections.Counter()
    fails = []
    tried = collections.Counter()
    C = cf.Closed(law, RULES)
    n = 0
    for k in range(4):
        for w in seeds:
            for zz in seeds:
                for other in seeds:
                    for z in seeds:
                        # (P) force rule k on the pair (z, x): x := mk(k, z, w, zz)
                        v = mk(C, k, z, w, zz)
                        if v is not None:
                            x, y = v, other
                            tried['P<-%s' % TAGS[k]] += 1
                            cells, T = chain_cells(C, x, y, z)
                            census[cells] += 1; n += 1
                            if T != x and len(fails) < 8:
                                fails.append(('P', k, x, y, z, cells, T))
                        # (Q) force rule k on (P, y): y := mk(k, P, w, zz) with P from a free x
                        x = other
                        P = C.op(z, x)
                        v = mk(C, k, P, w, zz)
                        if v is not None:
                            y = v
                            tried['Q<-%s' % TAGS[k]] += 1
                            cells, T = chain_cells(C, x, y, z)
                            census[cells] += 1; n += 1
                            if T != x and len(fails) < 8:
                                fails.append(('Q', k, x, y, z, cells, T))
                        # (R) force rule k on (Q, y): y := mk(k, Q, w, zz) with Q from that same y
                        #     (fixpoint attempt: use Q computed from a provisional y)
                        y0 = mk(C, 0, C.op(z, other), w, zz)
                        Q0 = C.op(C.op(z, other), y0)
                        v = mk(C, k, Q0, w, zz)
                        if v is not None:
                            x, y = other, v
                            tried['R<-%s' % TAGS[k]] += 1
                            cells, T = chain_cells(C, x, y, z)
                            census[cells] += 1; n += 1
                            if T != x and len(fails) < 8:
                                fails.append(('R', k, x, y, z, cells, T))
                        # (S) force rule k on (x, R): choose y so R matches mk(k, x, w, zz)?
                        #     R is determined by y, so instead sweep y over enc-shapes on x
                        y = mk(C, 0, x, w, zz) if x is not None else None
                        if y is not None:
                            tried['S-probe'] += 1
                            cells, T = chain_cells(C, other, y, z)
                            census[cells] += 1; n += 1
                            if T != other and len(fails) < 8:
                                fails.append(('S', k, other, y, z, cells, T))
    print('constructed %d assignments' % n, flush=True)
    print('attempts per target:', dict(tried), flush=True)
    print('\nREACHABLE CELLS (P,Q,R,S,top):', flush=True)
    for cells, c in census.most_common():
        print('  %-24s %7d   %s' % (str(cells), c,
                                    ' '.join(('free' if i < 0 else TAGS[i]) for i in cells)), flush=True)
    print('\nFAILURES: %d' % len(fails), flush=True)
    for tgt, k, x, y, z, cells, T in fails:
        print('  target=%s rule=%s cells=%s' % (tgt, TAGS[k], cells), flush=True)
        print('    x=%s' % show(x), flush=True)
        print('    y=%s' % show(y), flush=True)
        print('    z=%s  got=%s' % (show(z), show(T)), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
