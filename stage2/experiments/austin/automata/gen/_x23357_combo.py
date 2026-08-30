"""23357: histogram of (rule fired at a, u, b, v, top) over the law's chain, for the repaired 11-rule set.

a = op y x ; u = op a y ; b = op y z ; v = op x b ; top = op u v.
Tells the Lean proof which mode combinations actually occur (and which are empirically unreachable).
'-' = free.  Also flags any instance where the top does not return x.
"""
import sys, os, random, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size, rand_term
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law, rules = mod.law, mod.rules

T = tr.Tracing(law, rules)


def fired(a, b):
    T.trace_on = True; T.log = []
    r = T.op(a, b)
    T.trace_on = False
    # find the log entry for exactly this pair (memoised calls log nothing)
    w = None
    for (uu, vv, wi, rr) in T.log:
        if uu == a and vv == b:
            w = wi
    if not T.log:
        # memoised: recompute which rule matches
        for i, (conds, x, tag) in enumerate(rules):
            if T.check(conds, a, b) and T.ev(x, a, b) is not None:
                w = i; break
    return r, ('-' if w is None else 'R%d' % (w + 1))


def run(pool, N, seed):
    random.seed(seed)
    hist = collections.Counter(); bad = []
    for _ in range(N):
        x, y, z = (random.choice(pool) for _ in range(3))
        if random.random() < 0.35:
            x = random.choice(pool)
            y, z = random.choice(pool), random.choice(pool)
        try:
            a, ra = fired(y, x)
            u, ru = fired(a, y)
            b, rb = fired(y, z)
            v, rv = fired(x, b)
            t, rt = fired(u, v)
        except RecursionError:
            continue
        hist[(ra, ru, rb, rv, rt)] += 1
        if t != x:
            bad.append((x, y, z, ra, ru, rb, rv, rt))
    return hist, bad


if __name__ == '__main__':
    C = cf.Closed(law, rules)
    # build a rich pool the way fuzz does
    pool = [('g', i) for i in range(3)]
    for d in range(3):
        for u, v in fz.instances(rules, pool, 8, d, C):
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
    pool = [t for t in pool if size(t) <= 40][:2500]
    print('pool', len(pool), flush=True)
    tot = collections.Counter(); allbad = []
    for sd in (1, 2, 3):
        h, bad = run(pool, int(sys.argv[1]) if len(sys.argv) > 1 else 4000, sd)
        tot += h; allbad += bad
    print('LAW FAILURES:', len(allbad))
    for q in allbad[:5]:
        print('   ', q[3:])
    print('%-6s %-6s %-6s %-6s %-6s  %s' % ('a', 'u', 'b', 'v', 'top', 'count'))
    for k, n in tot.most_common():
        print('%-6s %-6s %-6s %-6s %-6s  %d' % (k + (n,)))
