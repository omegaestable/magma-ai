"""revalidate.py <eq_id> [--out gen] [--seeds 3] [--deep 3000] [--fuzz 12000] [--noexist]

Validate-then-minimise a closed-form package properly.

Why: `closedform.best_rules` keeps the rules that *fired* on one seed and re-tests once; on 11 laws the
kept set fails a second seed while the full set passes (24200: 0/3000 all rules, 21/3000 kept).  Here:
  1. extract the full rule set (without `exist`, then with it if needed);
  2. validate on several seeds of deep tests plus the structured fuzz, keeping every failing instance
     as a regression pool;
  3. greedy minimisation by *validated removal*: drop one rule at a time (least-fired first) and keep
     the drop only if the regression pool, a fresh deep test and a fresh fuzz all still pass;
  4. emit the package (`leangen.emit` with the validated rules).
Failures are reported with their kind (`recursion` = evaluator depth, not a counterexample).
"""
import sys, os, json, time, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as cf
import fuzz as fz
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

def run_tests(law, rules, seeds, N, NF, secs=240, exhaustive=True):
    import smallcheck as sc
    fails = []
    if exhaustive:
        for ms, g in ((9, 1), (5, 2)):
            n, f = sc.exhaustive(cf.Closed(law, rules), law, ms, g, limit=25)
            fails += [(s, r, 'exh%d/%d' % (ms, g), 0) for s, r in f]
    for sd in seeds:
        C = cf.Closed(law, rules)
        t, f = cf.deep_tests(C, law, N, secs, sd)
        fails += [(s, r, 'deep', sd) for s, r in f]
        t2, f2 = fz.fuzz(cf.Closed(law, rules), law, rules, NF, seed=sd + 100)
        fails += [(s, r, 'fuzz', sd) for s, r in f2]
        t3, f3 = fz.closure_fuzz(cf.Closed(law, rules), law, NF, seed=sd + 200)
        fails += [(s, r, 'closure', sd) for s, r in f3]
        t4, f4 = fz.critical_fuzz(cf.Closed(law, rules), law, NF, seed=sd + 300)
        fails += [(s, r, 'critical', sd) for s, r in f4]
    return fails

def check_pool(law, rules, pool):
    C = cf.Closed(law, rules)
    A, B = law[1]
    bad = 0
    for s, r, kind, sd in pool:
        try:
            lhs = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            bad += 1; continue
        if lhs != s['x']: bad += 1
    return bad

def main():
    eq = int(sys.argv[1])
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen')
    nseeds = int(sys.argv[sys.argv.index('--seeds') + 1]) if '--seeds' in sys.argv else 3
    N = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 3000
    NF = int(sys.argv[sys.argv.index('--fuzz') + 1]) if '--fuzz' in sys.argv else 12000
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
    X = cf.Extractor(law)
    t0 = time.time()
    seeds = [eq * 7 + 3 + 11 * i for i in range(nseeds)]
    report = dict(eq=eq, dualized=dualized, law=cat[eq])
    chosen = None
    for exist in ([False, True] if '--noexist' not in sys.argv else [False]):
        rules = X.rules(exist=exist)
        fails = run_tests(law, rules, seeds, N, NF)
        kinds = {}
        for s, r, kind, sd in fails:
            k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
            kinds[k] = kinds.get(k, 0) + 1
        report['full_%s' % ('exist' if exist else 'noexist')] = dict(nrules=len(rules), fails=len(fails), kinds=kinds)
        print(json.dumps(dict(eq=eq, exist=exist, nrules=len(rules), fails=len(fails), kinds=kinds, secs=round(time.time() - t0, 1))), flush=True)
        for s, r, kind, sd in fails[:3]:
            print('  FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()}, 'got', 'recursion' if r == 'recursion' else size(r), flush=True)
        real = [f for f in fails if f[1] != 'recursion']
        if not real:
            chosen = (rules, fails); break
    if chosen is None:
        # emit anyway: the full (noexist) rule set is the proof agent's starting point for a repair
        report['status'] = 'FAIL'
        rules = X.rules(exist=False)
        res = leangen.emit(eq, out, rules_override=rules)
        report['emit'] = res
        print(json.dumps(report), flush=True)
        return
    rules, pool = chosen
    # firing counts over the pool tests
    C = cf.Closed(law, rules)
    cf.deep_tests(C, law, min(N, 1500), 120, seeds[0] + 999)
    fz.fuzz(C, law, rules, min(NF, 6000), seed=seeds[0] + 998)
    order = sorted(range(len(rules)), key=lambda i: C.fired.get(i, 0))
    keep = list(rules)
    removed = []
    for i in order:
        r = rules[i]
        if r[2] == 'free': continue
        trial = [q for q in keep if q is not r]
        if check_pool(law, trial, pool): continue
        f = run_tests(law, trial, [seeds[0] + 501], min(N, 1500), min(NF, 6000), secs=90)
        real = [x for x in f if x[1] != 'recursion']
        if real:
            pool += real
            continue
        keep = trial; removed.append(r[2])
        print('  dropped', r[2], 'fired', C.fired.get(i, 0), '->', len(keep), 'rules', flush=True)
    # final validation of the minimised set on fresh seeds
    ffails = run_tests(law, keep, [seeds[0] + 777, seeds[0] + 778], N, NF)
    real = [x for x in ffails if x[1] != 'recursion']
    if real:
        print('  minimised set FAILS fresh seeds (%d); falling back to the full set' % len(real), flush=True)
        keep = rules
    report.update(status='OK', nrules_full=len(rules), nrules=len(keep), removed=removed, secs=round(time.time() - t0, 1))
    res = leangen.emit(eq, out, rules_override=keep)
    report['emit'] = res
    print(json.dumps(report), flush=True)

if __name__ == '__main__':
    main()
