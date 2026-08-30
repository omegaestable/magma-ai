"""_x8485_paths.py : for every failing top pair (u,v) of an 8485 rule set, find EVERY accessor path
p in u or v whose value w satisfies the reading guard  op (op (op w (a1 v)) u) u = a2 v  with all
three recursion gates passing.  That is the set of rules that would close the hole; the path that
works on every failure is the one to add.

Usage: python -u gen/_x8485_paths.py [variant] [Nrandom]
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
VAR = sys.argv[1] if len(sys.argv) > 1 else 'a'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 12000
R = m.VARIANTS[VAR]


def paths_of(t, maxdepth=6):
    """all accessor paths (as strings of 1/2) into t, with their values"""
    out = [('', t)]
    frontier = [('', t)]
    for _ in range(maxdepth):
        nxt = []
        for p, s in frontier:
            if s[0] == 'J':
                nxt.append((p + '1', s[1])); nxt.append((p + '2', s[2]))
        out += nxt; frontier = nxt
    return out


def guard_ok(C, w, u, v):
    """op (op (op w (a1 v)) u) u = a2 v with the gates, exactly as closedform would evaluate it"""
    if v[0] != 'J':
        return False
    x = v[1]
    try:
        if not cf.gate_ok(w, x, u, v):
            return False
        p1 = C.op(w, x)
        if not cf.gate_ok(p1, u, u, v):
            return False
        p2 = C.op(p1, u)
        if not cf.gate_ok(p2, u, u, v):
            return False
        p3 = C.op(p2, u)
    except RecursionError:
        return False
    return p3 == v[2]


def work():
    sys.setrecursionlimit(20000)
    C = cf.Closed(law, R)
    random.seed(1)
    pool = [('g', i) for i in range(3)]
    hits = Counter(); nfail = 0; shown = 0
    for it in range(N):
        s = {v: random.choice(pool) for v in ('x', 'y', 'z')}
        try:
            t = C.evp(B, s)
            if size(t) <= 60:
                pool.append(t)
            if len(pool) > 300:
                pool.pop(random.randrange(3, len(pool)))
            x, y, z = s['x'], s['y'], s['z']
            P = C.op(z, x); Q = C.op(P, y); Rr = C.op(Q, y); S = C.op(x, Rr); T = C.op(y, S)
        except RecursionError:
            continue
        if T == x:
            continue
        nfail += 1
        u, v = y, S
        cand = set()
        if v[0] == 'J':
            for p, w in paths_of(u):
                if guard_ok(C, w, u, v):
                    cand.add('u.' + p if p else 'u')
            for p, w in paths_of(v):
                if guard_ok(C, w, u, v):
                    cand.add('v.' + p if p else 'v')
        for c in cand:
            hits[c] += 1
        hits['__ANY' if cand else '__NONE'] += 1
        if shown < 4:
            shown += 1
            print('FAIL %d: sizes x=%d y=%d z=%d ; S free? %s ; paths: %s'
                  % (nfail, size(x), size(y), size(z), S == ('J', x, Rr), sorted(cand)), flush=True)
        if (it + 1) % 2000 == 0:
            print('  ... %d done, %d fails' % (it + 1, nfail), flush=True)
    print('failures', nfail, flush=True)
    for p, k in hits.most_common(40):
        print('  %-12s %d' % (p, k), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
