# -*- coding: utf-8 -*-
"""GENERAL image-differential harness (session 9).

Answers, for any lab module of the 9663 shape (module-level `op`, `chain`, `G`, `sz`, `show`):

  Q1  exact  Im_n = { ev(w) : w a free-magma term with <= n leaves }   (BFS, no heuristic membership)
  Q2  exhaustive law sweep over Im_n^3      -- the anchored carrier's own obligation
  Q3  for every free-carrier failure, is each of x,y,z in Im_N?        -- the SHARP TEST
  Q4  |Im_N| as a fraction of the term algebra of the same size        -- how big the restriction is

Q3 is what decides a law: op-built witness => the image is VOID for it; forged => the image deletes it.

usage:  python _anch_img.py <labmodule> [wsize] [ngens] [termsize]
"""
import sys, collections, importlib, itertools

sys.path.insert(0, '.')
sys.setrecursionlimit(100000)

MOD = sys.argv[1] if len(sys.argv) > 1 else '_x9663_lab4'
WS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
NG = int(sys.argv[3]) if len(sys.argv) > 3 else 2
TS = int(sys.argv[4]) if len(sys.argv) > 4 else 5

L = importlib.import_module(MOD)
op, chain, sz, show, G = L.op, L.chain, L.sz, L.show, L.G
prof = getattr(L, 'prof', None)


def build_image(ngens, wsize):
    """Exact: Im_n by BFS over free-magma terms with <= n leaves.  Returns (by_level, set)."""
    by = {1: [G(i) for i in range(ngens)]}
    seen = set(by[1])
    for s in range(2, wsize + 1):
        out = []
        for i in range(1, s):
            for a in by.get(i, []):
                for b in by.get(s - i, []):
                    try:
                        r = op(a, b)
                    except RecursionError:
                        continue
                    if r not in seen:
                        seen.add(r)
                        out.append(r)
        by[s] = out
    return by, seen


def law_ok(x, y, z):
    try:
        return chain(x, y, z)[-1] == x
    except RecursionError:
        return None


def main():
    by, IMG = build_image(NG, WS)
    pool = [t for s in sorted(by) for t in by[s]]
    print('MODULE %s   gens=%d  W-size<=%d' % (MOD, NG, WS))
    print('Q1  image by W-size %s   total %d'
          % ({s: len(by[s]) for s in sorted(by)}, len(pool)))
    print('    head constructors: %s'
          % dict(collections.Counter(t[0] for t in pool)))

    # ---- Q4: fraction of the term algebra
    allt = L.terms(TS, NG)
    inimg = [t for t in allt if t in IMG]
    print('Q4  term algebra size<=%d over %d gens: %d terms; %d of them are in Im_%d (%.2f%%)'
          % (TS, NG, len(allt), len(inimg), WS, 100.0 * len(inimg) / max(1, len(allt))))
    print('    NOTE this is a LOWER bound on the image: Im_%d only, larger W-terms add more.' % WS)

    # ---- Q2: exhaustive sweep on the image
    fails = []
    tot = 0
    for x in pool:
        for y in pool:
            for z in pool:
                r = law_ok(x, y, z)
                if r is None:
                    continue
                tot += 1
                if not r:
                    fails.append((x, y, z))
    print('Q2  EXHAUSTIVE image sweep: %d chains, %d FAIL' % (tot, len(fails)))
    if fails:
        fails.sort(key=lambda t: sum(sz(q) for q in t))
        for (x, y, z) in fails[:3]:
            p = ','.join(prof(x, y, z)) if prof else '?'
            print('    FAIL prof=%s' % p)
            for nm, t in (('x', x), ('y', y), ('z', z)):
                print('      %s (sz %d) = %s' % (nm, sz(t), show(t)[:150]))

    # ---- Q3: free-carrier failures, and whether their witnesses are op-built
    ft = L.terms(TS, NG)
    ffails = []
    ftot = 0
    for x in ft:
        for y in ft:
            for z in ft:
                r = law_ok(x, y, z)
                if r is None:
                    continue
                ftot += 1
                if not r:
                    ffails.append((x, y, z))
    nb = collections.Counter()
    for (x, y, z) in ffails:
        k = tuple(sorted(nm for nm, t in (('x', x), ('y', y), ('z', z)) if t not in IMG))
        nb[k] += 1
    print('Q3  FREE-carrier sweep (term algebra size<=%d): %d chains, %d FAIL' % (TS, ftot, len(ffails)))
    print('    failures by which components are FORGED (not in Im_%d):' % WS)
    for k, n in sorted(nb.items(), key=lambda kv: -kv[1]):
        lab = 'ALL OP-BUILT' if not k else 'forged: ' + ','.join(k)
        print('      %-22s %6d' % (lab, n))
    opb = nb.get((), 0)
    print('    => %d of %d free-carrier failures survive the image restriction (%.1f%%)'
          % (opb, len(ffails), 100.0 * opb / max(1, len(ffails))))
    print('    VERDICT: %s'
          % ('the image is VOID for this law (op-built witnesses remain)' if opb
             else 'the image DELETES every failure at this size -- widen W and re-run'))


if __name__ == '__main__':
    main()
