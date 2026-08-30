"""_xt_ship.py <eq> [--decocc0]

Validate a `closedform2`-extracted rule set to the FULL standard of DEEP_SESSION_6_AUSTIN_HANDOVER.md
("Testing protocol", item 1) and, if it passes, emit the package into gen/xrep<eq>/ so a proof agent can
pick it up.  Never writes into gen/ itself (the generated skeletons stay where they are).

  1. rv.run_tests(law, rules, [3,4,5], 3000, 12000)  == 0 value fails
  2. cf.deep_tests(..., 20000, 300, seed) == 0 fails on two further seeds
  3. leangen.emit(eq, gen/xrep<eq>, rules_override=rules); `refuted` must be non-empty
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import closedform2 as cf
import revalidate as rv
from freemodel import normalise, catalog, size
from laws import parse_eq


def main():
    eq = int(sys.argv[1])
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dz = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', leangen.dual_pat(orig[1])) if dz else orig
    X = cf.Extractor(law)
    rules, info = cf.extract(law, decocc=('--decocc0' not in sys.argv))
    print('LAW %d %s %s %s decpaths=%s' % (eq, cat[eq], '(dualized)' if dz else '', json.dumps(info), X.decpaths), flush=True)
    t0 = time.time()
    fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
    real = [f for f in fails if f[1] != 'recursion']
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    print(json.dumps(dict(step='run_tests', eq=eq, nrules=len(rules), fails=len(fails), value_fails=len(real),
                          kinds=kinds, secs=round(time.time() - t0, 1))), flush=True)
    if real:
        for s, r, kind, sd in real[:3]:
            print('  FAIL', kind, sd, {k: size(v) for k, v in s.items()}, flush=True)
        return
    for sd in (77771, 88881):
        t1 = time.time()
        C = cf.Closed(law, rules)
        tested, f = cf.deep_tests(C, law, 20000, 300, sd)
        f = [z for z in f if z[1] != 'recursion']
        print(json.dumps(dict(step='deep20k', seed=sd, tested=tested, fails=len(f), secs=round(time.time() - t1, 1))), flush=True)
        if f: return
    out = os.path.join(HERE, 'gen', 'xrep%d' % eq)
    res = leangen.emit(eq, out, rules_override=rules)
    print(json.dumps(dict(step='emit', out=out, **res)), flush=True)


if __name__ == '__main__':
    main()
