# -*- coding: utf-8 -*-
"""sepfind -- THE PAIR DIFF, automated.  (session 9)

The five open laws all say some version of "the root and the inner position are indistinguishable,
so `op` cannot tell them apart, so I need a different carrier".  That is a CHECKABLE claim and this
tool checks it.

For a law + model, over a sweep:
  GOOD = the set of (u,v) pairs where the target rule fires and the chain SUCCEEDS
  BAD  = the set of (u,v) pairs where the target rule fires and the chain FAILS

  * GOOD & BAD  non-empty  =>  HARD COLLISION.  The same pair must behave two ways.  `op` is a
    function, so NO carrier restriction, NO well-formedness invariant and NO extra guard can help;
    only changing `op` upstream (so the pair stops arising) can.  This is a proof.
  * GOOD & BAD  empty      =>  GUARD GAP.  A separating predicate exists trivially; the tool then
    searches a DSL vocabulary for a GENERALISABLE one -- true on every GOOD pair, false on every
    BAD pair -- and prints it.  That predicate is the fix.

usage:  python sepfind.py <labmodule> [nsweep] [gens]
The lab module must expose  op(u,v), chain(x,y,z), prof(x,y,z), G, tg, a1, a2, sz, show, terms.
"""
import sys, random, collections, importlib, itertools

sys.path.insert(0, '.')
sys.setrecursionlimit(100000)


def predicates(tg, a1, a2, sz, op):
    """The DSL vocabulary.  Each entry is (name, fn(u,v) -> bool | None)."""
    P = []

    def safe(f):
        def g(u, v):
            try:
                return bool(f(u, v))
            except (RecursionError, KeyError, IndexError, TypeError):
                return None
        return g

    for t in range(1, 7):
        P.append(('tg u == %d' % t, safe(lambda u, v, t=t: tg(u) == t)))
        P.append(('tg v == %d' % t, safe(lambda u, v, t=t: tg(v) == t)))
        P.append(('tg (a1 v) == %d' % t, safe(lambda u, v, t=t: tg(a1(v)) == t)))
        P.append(('tg (a2 v) == %d' % t, safe(lambda u, v, t=t: tg(a2(v)) == t)))
        P.append(('tg (a1 u) == %d' % t, safe(lambda u, v, t=t: tg(a1(u)) == t)))
        P.append(('tg (a2 u) == %d' % t, safe(lambda u, v, t=t: tg(a2(u)) == t)))
    acc = {'u': lambda u, v: u, 'v': lambda u, v: v,
           'a1 u': lambda u, v: a1(u), 'a2 u': lambda u, v: a2(u),
           'a1 v': lambda u, v: a1(v), 'a2 v': lambda u, v: a2(v),
           'a1(a1 v)': lambda u, v: a1(a1(v)), 'a2(a1 v)': lambda u, v: a2(a1(v)),
           'a1(a2 v)': lambda u, v: a1(a2(v)), 'a2(a2 v)': lambda u, v: a2(a2(v)),
           'a1(a1 u)': lambda u, v: a1(a1(u)), 'a2(a2 u)': lambda u, v: a2(a2(u))}
    names = list(acc)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            n1, n2 = names[i], names[j]
            f1, f2 = acc[n1], acc[n2]
            P.append(('%s == %s' % (n1, n2), safe(lambda u, v, f1=f1, f2=f2: f1(u, v) == f2(u, v))))
    # recomputation guards: op of two accessors equals a third
    reco = [('op u (a1 v) == a2 v', lambda u, v: op(u, a1(v)) == a2(v)),
            ('op (a1 v) u == a2 v', lambda u, v: op(a1(v), u) == a2(v)),
            ('op u (a2 v) == v', lambda u, v: op(u, a2(v)) == v),
            ('op (a1 v) (a2 v) == v', lambda u, v: op(a1(v), a2(v)) == v),
            ('op u (a1(a2 v)) == a2(a2 v)', lambda u, v: op(u, a1(a2(v))) == a2(a2(v))),
            ('op (a1(a2 v)) u == a2(a2 v)', lambda u, v: op(a1(a2(v)), u) == a2(a2(v))),
            ('op (a1 u) (a2 u) == u', lambda u, v: op(a1(u), a2(u)) == u),
            ('op u u == a1 v', lambda u, v: op(u, u) == a1(v))]
    for nm, f in reco:
        P.append((nm, safe(f)))
    for nm, f in [('sz u < sz v', lambda u, v: sz(u) < sz(v)),
                  ('sz u == sz v', lambda u, v: sz(u) == sz(v)),
                  ('sz (a1 v) < sz u', lambda u, v: sz(a1(v)) < sz(u)),
                  ('sz (a2 v) < sz u', lambda u, v: sz(a2(v)) < sz(u))]:
        P.append((nm, safe(f)))
    return P


def run(modname, nsweep, gens, target_branch, positions):
    L = importlib.import_module(modname)
    op, chain, prof = L.op, L.chain, L.prof
    tg, a1, a2, sz, show, G = L.tg, L.a1, L.a2, L.sz, L.show, L.G
    ctors = getattr(L, 'CTORS', ('J', 'E', 'F'))

    def rt(rng, dd):
        if dd <= 0 or rng.random() < 0.3:
            return G(rng.randrange(gens))
        return (rng.choice(ctors), rt(rng, dd - 1), rt(rng, dd - 1))

    rng = random.Random(11)
    GOODP, BADP = set(), set()
    goodinst, badinst = [], []
    seen = 0
    pool = L.terms(5, gens)
    src = list(pool)
    while seen < nsweep:
        seen += 1
        if seen % 3 == 0:
            x, y, z = rng.choice(src), rng.choice(src), rng.choice(src)
        else:
            x, y, z = rt(rng, 4), rt(rng, 4), rt(rng, 4)
        try:
            pr = prof(x, y, z)
            r = chain(x, y, z)[-1]
        except RecursionError:
            continue
        ok = (r == x)
        pairs = L.pairs(x, y, z)
        for idx, (u, v) in enumerate(pairs):
            if positions and idx not in positions:
                continue
            if str(pr[idx]) != str(target_branch):
                continue
            if ok:
                GOODP.add((u, v))
                if len(goodinst) < 4000:
                    goodinst.append((idx, u, v))
            else:
                BADP.add((u, v))
                if len(badinst) < 4000:
                    badinst.append((idx, u, v))

    print('sweep %d instances; target branch %r at positions %s' % (seen, target_branch, positions or 'all'))
    analyze(GOODP, BADP, tg, a1, a2, sz, op, show)


def rootfunc(rootmap, show):
    """THE ROOT FUNCTIONALITY TEST -- the only rigorous collision criterion.

    Every law instance imposes  op(u_root, v_root) = x  as a HARD requirement.  If two instances
    present the SAME root pair with DIFFERENT x, the model is refuted and **no change to the root
    rule's guard can repair it**: `op` is a function, so the repair must change the chain-building
    rules upstream so that the two pairs separate.  This is a proof about the model, and it is the
    honest version of "the root and the inner position are indistinguishable".
    """
    coll = {k: v for k, v in rootmap.items() if len(v) > 1}
    print('  root pairs seen %d;  root pairs demanding TWO different values: %d'
          % (len(rootmap), len(coll)))
    if coll:
        print('  ==> ROOT COLLISION (proof): no root-rule guard can repair this model.')
        for k, vals in list(coll.items())[:2]:
            u, v = k
            print('      u = %s' % show(u)[:150])
            print('      v = %s' % show(v)[:150])
            for w in list(vals)[:3]:
                print('        required = %s' % show(w)[:120])
    else:
        print('  ==> root map is a FUNCTION: no root collision. A root rule computing it EXISTS;')
        print('      the only question is whether a DSL predicate expresses its domain.')
    return coll


def analyze(GOODP, BADP, tg, a1, a2, sz, op, show, rootmap=None):
    """The pair diff.  GOODP/BADP are sets of (u,v) at which the target rule fired.

    NOTE on semantics: GOOD & BAD non-empty means the pair occurs in both a succeeding and a
    failing chain.  That is NOT by itself a contradiction -- the failing chain may fail elsewhere.
    The rigorous criterion is `rootfunc` above.  Overlap here means only: no predicate on (u,v)
    can separate these two occurrences, so if this rule's firing IS the cause, the fix is upstream.
    """
    if rootmap is not None:
        rootfunc(rootmap, show)
    print('  GOOD pairs %d   BAD pairs %d' % (len(GOODP), len(BADP)))
    inter = GOODP & BADP
    print('  GOOD & BAD = %d  (pairs occurring in both a succeeding and a failing chain)' % len(inter))
    if inter:
        print('  ==> NO PREDICATE ON (u,v) SEPARATES THESE OCCURRENCES.')
        print('      If this branch firing is the cause of the failure, the fix must be upstream,')
        print('      not a guard and not a carrier restriction (a submagma keeps both occurrences).')
        for (u, v) in list(inter)[:2]:
            print('      u = %s' % show(u)[:140])
            print('      v = %s' % show(v)[:140])
        return
    if not BADP:
        print('  ==> no failing firings of this branch in the sweep; nothing to separate.')
        return
    print('  ==> GUARD GAP: the pairs are disjoint, so a separator EXISTS. Searching the DSL...')
    P = predicates(tg, a1, a2, sz, op)
    hits = []
    for nm, f in P:
        gv = set()
        for (u, v) in GOODP:
            gv.add(f(u, v))
            if len(gv) > 1:
                break
        if len(gv) != 1 or None in gv:
            continue
        want = gv.pop()
        bv = set()
        okp = True
        for (u, v) in BADP:
            r = f(u, v)
            if r is None or r == want:
                okp = False
                break
        if okp:
            hits.append((nm, want))
    if hits:
        print('  SEPARATORS FOUND (%d): require the predicate to hold as shown' % len(hits))
        for nm, want in hits[:25]:
            print('     %-34s must be %s' % (nm, want))
    else:
        print('  no SINGLE predicate in the vocabulary separates them; trying pairs...')
        cand = []
        for nm, f in P:
            gv = set(f(u, v) for (u, v) in list(GOODP)[:400])
            if len(gv) == 1 and None not in gv:
                cand.append((nm, f, gv.pop()))
        found = 0
        for i in range(len(cand)):
            for j in range(i + 1, len(cand)):
                n1, f1, w1 = cand[i]
                n2, f2, w2 = cand[j]
                if all((f1(u, v) != w1) or (f2(u, v) != w2) for (u, v) in BADP):
                    print('     (%s must be %s) AND (%s must be %s)' % (n1, w1, n2, w2))
                    found += 1
                    if found >= 10:
                        return
        if not found:
            print('     none at arity 2 either -- the vocabulary is exhausted for this cell.')


if __name__ == '__main__':
    mod = sys.argv[1] if len(sys.argv) > 1 else '_x9663_lab4'
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 40000
    gn = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    br = sys.argv[4] if len(sys.argv) > 4 else 'D'
    pos = tuple(int(c) for c in sys.argv[5]) if len(sys.argv) > 5 else ()
    run(mod, n, gn, br, pos)
