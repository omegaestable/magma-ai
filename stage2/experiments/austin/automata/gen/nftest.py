"""nftest.py <module> <eq> -- validate a normal-form model against its law and refute its goals.

  python nftest.py nf12073 12073 [--big N] [--deep 20000]

Runs, in order:
  (a) exhaustive over ALL carrier terms (g, S, E, J) of size <= k, 1 and 2 generators;
  (b) exhaustive over the *pair* (y,x) at a much larger size with the remaining variables drawn
      from a fixed small set (the law's value is z-independent, so this is the real content);
  (c) exhaustive over the classic validator pools: one-generator J-terms of size <= 9 and
      two-generator J-terms of size <= 5;
  (d) deep random on two seeds, closure fuzz and critical-pair fuzz (nfcore);
  (e) a refuting assignment for every goal equation of every row of that law.
"""
import sys, os, json, time, itertools, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import nfcore as nf
from nfcore import S, show, sz
from freemodel import catalog, pvars, normalise
from laws import parse_eq, load_rows

def main():
    mod = importlib.import_module(sys.argv[1])
    eq = int(sys.argv[2])
    op = mod.op
    useE = getattr(mod, 'USE_E', True)
    nf.ALLOW_E = useE
    law = nf.get_law(eq)
    big = int(sys.argv[sys.argv.index('--big') + 1]) if '--big' in sys.argv else 8
    deepn = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 20000
    small = int(sys.argv[sys.argv.index('--small') + 1]) if '--small' in sys.argv else 6
    out = dict(eq=eq, law=catalog()[eq], module=sys.argv[1])
    ev = nf.evaluator(op)
    vs = pvars(law[1])
    print('law', eq, catalog()[eq], '->', law, flush=True)

    # (a) full carrier exhaustive
    for ms, g in ((small, 1), (small - 1, 2), (4, 3)):
        t0 = time.time(); pool = nf.carrier_upto(ms, g, use_E=useE)
        n, f = nf.exhaustive(op, law, pool, limit=3)
        out['exh_carrier_%d_%d' % (ms, g)] = dict(pool=len(pool), n=n, fails=len(f))
        print('(a) carrier<=%d g%d: pool %d, %d assignments, %d fails  [%.1fs]'
              % (ms, g, len(pool), n, len(f), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('    FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r)

    # (b) exhaustive over (y,x) at a big size, other variables from a fixed set
    others = [v for v in vs if v not in ('x', 'y')]
    fill = [('g', 0), ('g', 1), S, ('J', ('g', 0), ('g', 1)), ('J', S, ('g', 0))] + ([('E', ('g', 0)), ('E', ('J', S, ('g', 0)))] if useE else [('J', ('g',0), S)])
    for ms, g in ((big, 1), (big - 2, 2)):
        t0 = time.time(); pool = nf.carrier_upto(ms, g, use_E=useE)
        fails = []; n = 0
        for yv in pool:
            for xv in pool:
                for ov in itertools.product(fill, repeat=len(others)):
                    s = {'y': yv, 'x': xv}
                    s.update(dict(zip(others, ov)))
                    n += 1
                    try: r = ev(law[1], s)
                    except RecursionError:
                        fails.append((dict(s), 'recursion')); continue
                    if r != s['x']: fails.append((dict(s), r))
                if len(fails) >= 3: break
            if len(fails) >= 3: break
        out['exh_pair_%d_%d' % (ms, g)] = dict(pool=len(pool), n=n, fails=len(fails))
        print('(b) (y,x) over carrier<=%d g%d: pool %d, %d assignments, %d fails  [%.1fs]'
              % (ms, g, len(pool), n, len(fails), time.time() - t0), flush=True)
        for s, r in fails[:3]:
            print('    FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r)

    # (c) the classic validator pools
    for ms, g, tag in ((9, 1, 'jterm9_1'), (5, 2, 'jterm5_2')):
        t0 = time.time(); pool = nf.jterms_upto(ms, g)
        n, f = nf.exhaustive(op, law, pool, limit=3)
        out['exh_' + tag] = dict(pool=len(pool), n=n, fails=len(f))
        print('(c) J-terms<=%d g%d: pool %d, %d assignments, %d fails  [%.1fs]'
              % (ms, g, len(pool), n, len(f), time.time() - t0), flush=True)
        for s, r in f[:3]:
            print('    FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r)

    # (d) deep / closure / critical fuzz
    for seed in (eq * 7 + 3, eq * 13 + 101):
        t0 = time.time()
        n1, f1 = nf.deep_random(op, law, deepn, seed)
        n2, f2 = nf.closure_random(op, law, deepn // 2, seed + 7)
        n3, f3 = nf.critical_random(op, law, deepn // 2, seed + 19)
        out['fuzz_%d' % seed] = dict(deep=(n1, len(f1)), closure=(n2, len(f2)), critical=(n3, len(f3)))
        print('(d) seed %d: deep %d/%d fails, closure %d/%d, critical %d/%d  [%.1fs]'
              % (seed, len(f1), n1, len(f2), n2, len(f3), n3, time.time() - t0), flush=True)
        for s, r in (f1 + f2 + f3)[:3]:
            print('    FAIL', {k: show(v) for k, v in s.items()}, '->', show(r) if r != 'recursion' else r)

    # (e) goal refutation
    cat = catalog()
    out['goals'] = {}
    for row in load_rows():
        if int(row['eq1_id']) != eq: continue
        g = parse_eq(cat[int(row['eq2_id'])])
        res = nf.refute_goal(op, g)
        if res is None:
            print('(e) %s goal %s  NOT REFUTED' % (row['id'], row['eq2_id']), flush=True)
            out['goals'][row['id']] = None
        else:
            s, a, b = res
            print('(e) %s goal %s (%s): %s  ->  LHS %s  !=  RHS %s'
                  % (row['id'], row['eq2_id'], row['equation2'],
                     {k: show(v) for k, v in s.items()}, show(a), show(b)), flush=True)
            out['goals'][row['id']] = dict(eq2=row['eq2_id'], eq2_text=row['equation2'],
                                           assign={k: show(v) for k, v in s.items()},
                                           lhs=show(a), rhs=show(b))
    print(json.dumps(out))

if __name__ == '__main__':
    main()
