"""23357 gap hunter: force a chosen rule to fire at a chosen CHAIN product and test the law.

fuzz.instances builds concrete (p, q) pairs shaped like each rule (EQ conditions imposed by copying, OPEQ
guards satisfied by computing).  For the law's chain  a = op y x ; u = op a y ; b = op y z ; v = op x b
each product can be driven directly:

    b := op y z   ->  y := p, z := q, x free
    a := op y x   ->  y := p, x := q, z free
    v := op x b   ->  x := p and b := q, realised by y := a1 q, z := a2 q (b free), q a J-node
    u := op a y   ->  y := q and a := p, realised by x := a2 p when p = J q _ (a free)

Reports every (rule, slot) whose instances break the law, with the smallest witness.

usage: python gen/_x23357_hunt.py [rules-module]        (default: gen/_x23357_rep.py)
"""
import sys, os, random, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, trace as tr, fuzz as fz
from freemodel import size, rand_term
import importlib.util

MODPATH = sys.argv[1] if len(sys.argv) > 1 else \
    'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py'
spec = importlib.util.spec_from_file_location('_rulesmod', MODPATH)
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law, rules = mod.law, mod.rules
show = tr.show
J = lambda a, b: ('J', a, b)


def build_pool(C, n=8):
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
    return pool


def hunt(nper=14, seed=11, maxsize=90):
    random.seed(seed)
    C = cf.Closed(law, rules)
    pool = build_pool(C)
    fillers = [t for t in pool if size(t) <= 9][:40] or [('g', 0)]

    def fill(p, q):
        """candidate values for the law variable the driven product leaves free: small fillers, but also
        parts of the very pair that is decoding (that is what makes a SECOND product decode too)."""
        out = [random.choice(fillers), random.choice(pool)]
        for t in (p, q):
            out.append(t)
            if t[0] == 'J':
                out += [t[1], t[2]]
                if t[1][0] == 'J':
                    out += [t[1][1], t[1][2]]
        return out
    bad = collections.defaultdict(list)
    ntest = 0
    for d in (0, 1, 2):
        pairs_by_rule = []
        for k in range(len(rules)):
            ps = fz.instances([rules[k]], pool, nper, d, C)
            pairs_by_rule.append(ps)
        for k, ps in enumerate(pairs_by_rule):
            for (p, q) in ps:
                cands = []
                fl = fill(p, q)
                cands.append(('b', [(f, p, q) for f in fl]))                   # x, y, z
                cands.append(('a', [(q, p, f) for f in fl]))
                if q[0] == 'J':
                    cands.append(('v', [(p, q[1], q[2])]))
                if p[0] == 'J' and p[1] == q:
                    cands.append(('u', [(p[2], q, f) for f in fl]))
                for slot, triples in cands:
                    for (x, y, z) in triples:
                        if max(size(t) for t in (x, y, z)) > maxsize:
                            continue
                        s = {'x': x, 'y': y, 'z': z}
                        try:
                            got = C.op(C.evp(law[1][0], s), C.evp(law[1][1], s))
                        except RecursionError:
                            continue
                        ntest += 1
                        if got != x:
                            bad[(k + 1, rules[k][2], slot)].append((x, y, z))
    return ntest, bad


if __name__ == '__main__':
    import collections as _c
    nper = int(os.environ.get('NPER', '14'))
    seeds = [int(q) for q in os.environ.get('SEEDS', '11').split(',')]
    ntest = 0; bad = _c.defaultdict(list)
    for sd in seeds:
        n, b = hunt(nper, sd)
        ntest += n
        for k, v in b.items():
            bad[k] += v
        print('  seed %d: tested %d, broken %d' % (sd, n, len(b)), flush=True)
    print('tested', ntest, 'broken families', len(bad))
    for key in sorted(bad, key=lambda k: (k[0], k[2])):
        ws = sorted(bad[key], key=lambda t: sum(size(q) for q in t))
        x, y, z = ws[0]
        print('R%d %-18s slot=%s  n=%d   smallest: x=%s  y=%s  z=%s'
              % (key[0], key[1], key[2], len(ws), show(x), show(y), show(z)))
