"""_x8485_u2.py : measure the dichotomy that the Lean proof of 8485 needs.

Lemma U2 (candidate):  op u v != J u v  ->  tg v = 2 AND
     (A)  tg (a2 v) = 2 AND u = a2 (a2 v)          -- last chain step free / rule 1
  or (B)  tg u = 2 AND a2 v = a1 u                 -- last chain step decoded

(A) is what the top-level rule needs (z = a2 (a2 (a1 v)) at the top).  (B) is the hole.
This script counts, over decoding pairs reached from random law instances, how many are (A), how
many are (B) only, and prints (B)-only examples.
Usage: python -u gen/_x8485_u2.py <variant> [N]
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
VAR = sys.argv[1] if len(sys.argv) > 1 else 'f'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
R = m.VARIANTS[VAR]


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


def classify(C, u, v):
    if C.op(u, v) == ('J', u, v):
        return None
    a = v[0] == 'J' and v[2][0] == 'J' and u == v[2][2]
    b = u[0] == 'J' and v[0] == 'J' and v[2] == u[1]
    return (a, b)


def work():
    sys.setrecursionlimit(20000)
    C = cf.Closed(law, R)
    cnt = Counter(); ex = {}
    pairs = set()

    def note(u, v):
        if (u, v) in pairs:
            return
        pairs.add((u, v))
        c = classify(C, u, v)
        if c is None:
            return
        cnt[c] += 1
        if not c[0]:
            ex.setdefault(c, (u, v))

    terms = enum_terms(9, 1) + enum_terms(5, 2)
    for x in terms:
        for y in terms:
            for z in terms:
                if size(x) + size(y) + size(z) > 14:
                    continue
                try:
                    P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); C.op(y, S)
                except RecursionError:
                    continue
                for a, b in ((z, x), (P, y), (Q, y), (x, Rr), (y, S)):
                    note(a, b)
    print('after exhaustive:', dict(cnt), flush=True)
    random.seed(7)
    pool = [('g', i) for i in range(3)]
    for it in range(N):
        s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
        try:
            t = C.evp(B, s)
            if size(t) <= 60:
                pool.append(t)
            if len(pool) > 300:
                pool.pop(random.randrange(3, len(pool)))
            x, y, z = s['x'], s['y'], s['z']
            P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); C.op(y, S)
        except RecursionError:
            continue
        for a, b in ((z, x), (P, y), (Q, y), (x, Rr), (y, S)):
            note(a, b)
        if (it + 1) % 4000 == 0:
            print('  ... %d, distinct pairs %d, classes %s' % (it + 1, len(pairs), dict(cnt)), flush=True)
    print('(A = u = a2 (a2 v), B = a2 v = a1 u)  counts:', flush=True)
    for c, k in cnt.most_common():
        print('   A=%s B=%s : %d' % (c[0], c[1], k), flush=True)
    for c, (u, v) in ex.items():
        print('   NOT-A example A=%s B=%s u=%s v=%s' % (c[0], c[1], u, v), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
