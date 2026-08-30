"""_x8485_cases2.py : census of the (inner rule, top rule) cells for the variant-a 8485 rules,
in a big-stack thread and with incremental printing.

Cell = (rule at (z,x), (P,y), (Q,y), (x,R), (y,S)), 'F' = free product.
Usage: python -u gen/_x8485_cases2.py [Nrandom]
"""
import sys, os, random, threading, importlib.util
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
from collections import Counter

sys.setrecursionlimit(20000)
law = m.law
A, B = law[1]
R = m.VARIANTS[sys.argv[2] if len(sys.argv) > 2 else 'a']
TAGS = [str(i + 1) for i in range(12)]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000


def which(C, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return TAGS[i]
    return 'F'


def enum_terms(maxsize, gens):
    bysz = {1: [('g', i) for i in range(gens)]}
    for s in range(2, maxsize + 1):
        out = []
        for a in range(1, s):
            b = s - 1 - a
            if b < 1:
                continue
            for t1 in bysz.get(a, []):
                for t2 in bysz.get(b, []):
                    out.append(('J', t1, t2))
        bysz[s] = out
    return [t for s in sorted(bysz) for t in bysz[s]]


def cell(C, x, y, z):
    P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); T = C.op(y, S)
    return (which(C, z, x), which(C, P, y), which(C, Q, y), which(C, x, Rr), which(C, y, S)), T == x


def work():
    sys.setrecursionlimit(20000)
    C = cf.Closed(law, R)
    cnt = Counter(); bad = Counter(); badex = {}
    terms = enum_terms(9, 1) + enum_terms(5, 2)
    n = 0
    for x in terms:
        for y in terms:
            for z in terms:
                if size(x) + size(y) + size(z) > 15:
                    continue
                n += 1
                try:
                    c, ok = cell(C, x, y, z)
                except RecursionError:
                    continue
                cnt[c] += 1
                if not ok:
                    bad[c] += 1; badex.setdefault(c, (x, y, z))
    print('exhaustive triples', n, flush=True)
    for c, k in cnt.most_common():
        print('  %s  %8d %s' % (''.join(c), k, ('BAD %d' % bad[c]) if bad[c] else ''), flush=True)
    random.seed(1)
    pool = [('g', i) for i in range(3)]
    for it in range(N):
        s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
        try:
            t = C.evp(B, s)
            if size(t) <= 60:
                pool.append(t)
            if len(pool) > 300:
                pool.pop(random.randrange(3, len(pool)))
            c, ok = cell(C, s['x'], s['y'], s['z'])
        except RecursionError:
            continue
        cnt[c] += 1
        if not ok:
            bad[c] += 1; badex.setdefault(c, (s['x'], s['y'], s['z']))
        if (it + 1) % 2000 == 0:
            print('  ... %d random done, cells %d, bad %d' % (it + 1, len(cnt), sum(bad.values())), flush=True)
    print('ALL cells (zx,Py,Qy,xR,yS) count [bad]', flush=True)
    for c, k in cnt.most_common():
        print('  %s  %8d %s' % (''.join(c), k, ('BAD %d' % bad[c]) if bad[c] else ''), flush=True)
    print('total bad', sum(bad.values()), flush=True)
    for c, ex in badex.items():
        print('  BAD example', ''.join(c), [str(t) for t in ex], flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
