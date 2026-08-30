"""_xt_prunecheck.py <eq,eq,...> [--n 4000]

Differential proof-by-testing that closedform2.prune's SUBSUMPTION step is behaviour-preserving: extract
the rule list with dedup only, and with dedup+subsumption, then compare Closed.op on
  (a) every pair of free-magma terms of size <= 7 over 2 generators,
  (b) the rule-shaped fuzz pairs of the FULL set (the pairs that actually exercise the guards),
  (c) random law instances.
Any difference is a bug in the subsumption argument.  Prints one JSON line per law.
"""
import sys, os, json, random, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import closedform2 as cf2
import fuzz as fz
from freemodel import normalise, catalog, size, rand_term, pvars
from laws import parse_eq

_real_prune = cf2.prune


def dedup_only(rules):
    seen = set(); uniq = []
    for r in rules:
        key = (frozenset(r[0]), r[1])
        if key in seen: continue
        seen.add(key); uniq.append(r)
    return uniq


def terms_upto(maxsize, gens):
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, maxsize + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for s in by[a]:
                    for t in by[b]:
                        by[n].append(('J', s, t))
    out = []
    for n in sorted(by): out += by[n]
    return out


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dz = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    return ('x', leangen.dual_pat(orig[1])) if dz else orig


def main():
    eqs = [int(x) for x in sys.argv[1].split(',')]
    N = int(sys.argv[sys.argv.index('--n') + 1]) if '--n' in sys.argv else 4000
    for eq in eqs:
        law = get_law(eq)
        cf2.prune = dedup_only
        full = cf2.Extractor(law).rules()
        cf2.prune = _real_prune
        pruned = cf2.Extractor(law).rules()
        Cf = cf2.Closed(law, full); Cp = cf2.Closed(law, pruned)
        pairs = []
        pool = terms_upto(7, 2)
        pairs += [(u, v) for u in pool for v in pool]
        random.seed(eq)
        # rule-shaped pairs from the FULL set (the ones that exercise every guard)
        p2 = [('g', i) for i in range(3)]
        for d in range(3):
            for u, v in fz.instances(full, p2, 4, d, Cf):
                pairs.append((u, v))
                for t in (u, v):
                    if size(t) <= 60 and t not in p2: p2.append(t)
        random.shuffle(pairs)
        pairs = pairs[:N]
        bad = 0; tested = 0
        for u, v in pairs:
            try:
                a = Cf.op(u, v)
            except RecursionError:
                continue
            try:
                b = Cp.op(u, v)
            except RecursionError:
                b = 'rec'
            tested += 1
            if a != b: bad += 1
        print(json.dumps(dict(eq=eq, full=len(full), pruned=len(pruned), tested=tested, differences=bad)), flush=True)


if __name__ == '__main__':
    main()
