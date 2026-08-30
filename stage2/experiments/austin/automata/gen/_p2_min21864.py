"""Rule-firing census + validated removal for 21864's 13-rule t8 set.

usage: python gen/_p2_min21864.py census
       python gen/_p2_min21864.py drop <csv of 0-based indices>
"""
import sys, os, time, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog
from laws import parse_eq
import _x21864_rules as RR

T8 = RR.GEN[:5] + [RR.R4c, RR.R5c, RR.RA, RR.R6d, RR.R6e, RR.RB, RR.RB2, RR.RD]
law = normalise(parse_eq(catalog()[21864]))


def census(rules):
    """run the full validator's own load on ONE Closed per stage and union the fired sets."""
    tot = collections.Counter()
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        sc.exhaustive(C, law, ms, g, limit=25)
        tot.update({k: v for k, v in C.fired.items()})
    for sd in (3, 4, 5):
        C = cf.Closed(law, rules); cf.deep_tests(C, law, 3000, 240, sd); tot.update(C.fired)
        C = cf.Closed(law, rules); fz.fuzz(C, law, rules, 12000, seed=sd + 100); tot.update(C.fired)
        C = cf.Closed(law, rules); fz.closure_fuzz(C, law, 12000, seed=sd + 200); tot.update(C.fired)
        C = cf.Closed(law, rules); fz.critical_fuzz(C, law, 12000, seed=sd + 300); tot.update(C.fired)
    return tot


def validate(rules, tag):
    t0 = time.time()
    f = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    vf = [q for q in f if q[1] != 'recursion']
    print('  %-30s rules=%-3d FAILS total %d value %d  (%.1fs)'
          % (tag, len(rules), len(f), len(vf), time.time() - t0), flush=True)
    return len(vf) == 0 and len(f) == 0


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'census'
    if mode == 'census':
        t0 = time.time()
        c = census(T8)
        print('firing census (%.1fs):' % (time.time() - t0))
        for i, r in enumerate(T8):
            print('  R%-2d %-22s fired %d' % (i + 1, r[2], c.get(i, 0)))
        never = [i for i in range(len(T8)) if c.get(i, 0) == 0]
        print('never fired (0-based):', never, [T8[i][2] for i in never])
    else:
        drop = set(int(t) for t in sys.argv[2].split(',')) if len(sys.argv) > 2 and sys.argv[2] else set()
        rules = [r for i, r in enumerate(T8) if i not in drop]
        print('drop', sorted(drop))
        validate(rules, 'candidate')
