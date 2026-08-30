"""_xt_cost.py <eq> [<eq> ...] [--mod closedform2] [--cap2 A,B,C] [--profile]

Extraction-cost measurement for the Extractor: prints, per law, the shape (lform/rform/both, #nodes,
#encnodes, #rnodes), then times X.rules(...) at several cap2 values and reports rule counts and seconds.
"""
import sys, os, json, time, itertools, cProfile, pstats, io
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
from freemodel import normalise, catalog, pvars
from laws import parse_eq

MOD = 'closedform'
if '--mod' in sys.argv:
    MOD = sys.argv[sys.argv.index('--mod') + 1]
cf = __import__(MOD)


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
    return law, dualized, cat[eq]


def shape(eq):
    law, dualized, txt = get_law(eq)
    X = cf.Extractor(law)
    nodes = [('A',) + p for p, _ in cf.positions(X.A)] + [('B',) + p for p, _ in cf.positions(X.B)]
    encpat = X.B if X.lform else X.A
    encnodes = [p for p, _ in cf.positions(encpat)] if not isinstance(encpat, str) else []
    rnodes = [('A',) + p for p, _ in cf.positions(X.A) if p] + [('B',) + p for p, _ in cf.positions(X.B) if p]
    nmodes = 4 if (X.lform or X.rform) else 2
    return dict(eq=eq, law=txt, dualized=dualized, lform=X.lform, rform=X.rform,
                nodes=len(nodes), encnodes=len(encnodes), rnodes=len(rnodes),
                modevecs=nmodes ** len(nodes), rdsets=1 + len(rnodes) + len(rnodes) * (len(rnodes) - 1) // 2,
                subs=2 ** len(encnodes))


def main():
    eqs = [int(a) for a in sys.argv[1:] if a.isdigit()]
    caps = [int(c) for c in sys.argv[sys.argv.index('--cap2') + 1].split(',')] if '--cap2' in sys.argv else [64]
    for eq in eqs:
        print(json.dumps(shape(eq)), flush=True)
        law, dualized, txt = get_law(eq)
        for cap in caps:
            X = cf.Extractor(law)
            t0 = time.time()
            if '--profile' in sys.argv:
                pr = cProfile.Profile(); pr.enable()
                rules = X.rules(cap2=cap)
                pr.disable()
                s = io.StringIO(); pstats.Stats(pr, stream=s).sort_stats('cumulative').print_stats(18)
                print(s.getvalue()[:4000], flush=True)
            else:
                rules = X.rules(cap2=cap)
            print('  cap2=%-6d nrules=%-5d secs=%.1f' % (cap, len(rules), time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
