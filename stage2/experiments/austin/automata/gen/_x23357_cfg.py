"""23357: which DIGEST configurations of the chain actually occur, and which top rule fires.

Each of  A = op y x, U = op A y, B = op y z, V = op x B  is classified F (free) / L (result a2 (a1 .))
/ R (result a1 .) exactly as the Lean digest TR does.  The sample is the coincidence-rich pool the gap
hunter uses, driven so that each rule fires at each chain slot.
"""
import sys, os, random, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law, rules = mod.law, mod.rules
show = tr.show
NL = 8            # rules 1..8 are L-type, 9..12 R-type

C = cf.Closed(law, rules)


def fire(a, b):
    """(value, rule index or None)"""
    for i, (conds, x, tag) in enumerate(rules):
        if C.check(conds, a, b):
            r = C.ev(x, a, b)
            if r is not None:
                return r, i
    return ('J', a, b), None


def cls(a, b):
    r, i = fire(a, b)
    if i is None:
        return r, 'F', None
    return r, ('L' if i < NL else 'R'), i + 1


def classify(x, y, z):
    A, cA, _ = cls(y, x)
    U, cU, _ = cls(A, y)
    B, cB, _ = cls(y, z)
    V, cV, _ = cls(x, B)
    T, cT, kT = cls(U, V)
    return (cA, cU, cB, cV), (kT if kT else 0), (T == x)


def build_pool(n=10):
    pool = [('g', i) for i in range(3)]
    for d in range(3):
        for u, v in fz.instances(rules, pool, n, d, C):
            for t in (u, v):
                if size(t) <= 60 and t not in pool:
                    pool.append(t)
            try:
                r = C.op(u, v)
                if size(r) <= 60 and r not in pool:
                    pool.append(r)
            except RecursionError:
                pass
    for t in list(pool):
        if t[0] == 'J':
            for s in (t[1], t[2]):
                if s not in pool:
                    pool.append(s)
    return [t for t in pool if size(t) <= 45]


if __name__ == '__main__':
    random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 5)
    pool = build_pool()
    print('pool', len(pool), flush=True)
    hist = collections.Counter(); bad = []
    # (a) random triples from the pool
    for _ in range(6000):
        x, y, z = (random.choice(pool) for _ in range(3))
        try:
            cfg, k, ok = classify(x, y, z)
        except RecursionError:
            continue
        hist[(cfg, k)] += 1
        if not ok:
            bad.append((x, y, z))
    # (b) rule-driven: force rule k to fire at each chain slot
    for k in range(len(rules)):
        for d in (0, 1, 2):
            for (p, q) in fz.instances([rules[k]], pool, 12, d, C):
                trip = [(random.choice(pool), p, q), (q, p, random.choice(pool))]
                if q[0] == 'J':
                    trip.append((p, q[1], q[2]))
                if p[0] == 'J' and p[1] == q:
                    trip.append((p[2], q, random.choice(pool)))
                for (x, y, z) in trip:
                    if max(size(t) for t in (x, y, z)) > 90:
                        continue
                    try:
                        cfg, kk, ok = classify(x, y, z)
                    except RecursionError:
                        continue
                    hist[(cfg, kk)] += 1
                    if not ok:
                        bad.append((x, y, z))
    print('law failures', len(bad))
    for q in bad[:3]:
        print('   x=%s y=%s z=%s' % tuple(show(t) for t in q))
    print('%-16s %-6s %s' % ('(A,U,B,V)', 'top', 'count'))
    for (cfg, k), n in sorted(hist.items(), key=lambda kv: (-kv[1],)):
        print('%-16s R%-5s %d' % (''.join(cfg), k if k else 'free', n))
