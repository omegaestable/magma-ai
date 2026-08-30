"""_y8485_p2.py : is there a pair (u,v) on which op decodes via a rule OTHER than R1?

Every Lean case of law 8485 that I can close uses R1's own conjunct `u = a2 (a2 v)` as the locator.
If op(u,v) can decode with P1 u v FALSE, the law's P-decoded cell splits and needs a second argument.
Search: constructed encodings + exhaustive small terms + the R2/R3/R4 constructors.
"""
import sys, os, itertools, collections, threading, importlib.util
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
law = m.law; RULES = m.VARIANTS['f']
TAGS = ['R1free', 'R2:zP@x22', 'R3:zP@u22', 'R4:zP@u221']
J = lambda a, b: ('J', a, b)
show = lambda t: ('g%d' % t[1]) if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def which(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(x, u, v) is not None:
            return i
    return -1


def terms(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)]}
    allt = list(by[1])
    for n in range(3, maxsize + 1, 2):
        cur = []
        for a in range(1, n - 1):
            for s in by.get(a, []):
                for t in by.get(n - 1 - a, []):
                    cur.append(J(s, t))
        by[n] = cur; allt += cur
    return allt


def work():
    sys.setrecursionlimit(20000)
    C = cf.Closed(law, RULES)
    g = [('g', 0), ('g', 1), ('g', 2)]
    pool = terms(7, 2)
    seeds = g + [J(g[0], g[1]), J(J(g[0], g[1]), g[2]), J(g[0], J(g[1], g[2])),
                 J(g[0], J(g[1], J(g[0], g[1])))]
    hits = collections.Counter(); ex = {}
    n = 0
    # (a) exhaustive small pairs
    for u in pool:
        for v in pool:
            n += 1
            k = which(C, u, v)
            if k > 0:
                hits[k] += 1; ex.setdefault(k, (u, v))
    print('exhaustive %d pairs over %d terms' % (n, len(pool)), flush=True)
    # (b) the R2 constructor: v = J w c, c = op(op(op(a2(a2 w), w), u), u)
    n2 = 0
    for u in seeds:
        for w in seeds:
            if w[0] != 'J' or w[2][0] != 'J':
                continue
            c = C.op(C.op(C.op(w[2][2], w), u), u)
            v = J(w, c); n2 += 1
            k = which(C, u, v)
            if k > 0:
                hits[k] += 1; ex.setdefault(k, (u, v))
    # (c) the R3/R4 constructors
    for u in seeds:
        if u[0] != 'J' or u[2][0] != 'J' or u[2][2][0] != 'J':
            continue
        for w in seeds:
            for kk, zt in ((2, u[2][2][1]), (3, u[2][2][1][1] if u[2][2][1][0] == 'J' else None)):
                if zt is None:
                    continue
                c = C.op(C.op(C.op(zt, w), u), u)
                v = J(w, c); n2 += 1
                k = which(C, u, v)
                if k > 0:
                    hits[k] += 1; ex.setdefault(k, (u, v))
    print('constructed %d extra pairs' % n2, flush=True)
    print('\ndecodes via a rule OTHER than R1:', dict(hits), flush=True)
    for k, (u, v) in ex.items():
        print('  %s :  u=%s\n              v=%s\n              -> %s' % (TAGS[k], show(u), show(v), show(C.op(u, v))), flush=True)
    if not hits:
        print('  NONE FOUND -- every decode in this population is R1', flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work); th.start(); th.join()
