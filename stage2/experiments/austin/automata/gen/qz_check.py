"""qz_check.py <module> [N] [seeds...] -- deep/closure/critical random validation + goal refutation."""
import sys, os, importlib, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qz_lib as L
from laws import parse_eq, load_rows
from freemodel import catalog, normalise


def run(mod, N=20000, seeds=(1, 2), gens=3, depth=3, quiet=False):
    eq = mod.EQ
    law, txt = L.law_of(eq)
    op = mod.op
    CT = mod.CT
    L.UN = list(getattr(mod, 'UN', ()))
    L.CONST = list(getattr(mod, 'CONST', ()))
    tot = {}
    allf = []
    for sd in seeds:
        for name, fn, n in (('deep', L.deep_tests, N), ('closure', L.closure_tests, N // 2),
                            ('critical', L.critical_tests, N // 2)):
            t0 = time.time()
            k, f = fn(op, law, n, sd, gens=gens, ctors=CT, depth=depth)
            tot['%s/%d' % (name, sd)] = (k, len(f), round(time.time() - t0, 1))
            allf += [(name, sd, s, r) for s, r in f]
    t0 = time.time()
    k, f = L.identity_probe(op, law, gens=gens, ctors=CT, depth=depth, seeds=tuple(seeds))
    tot['identity'] = (k, len(f), round(time.time() - t0, 1))
    allf += [('identity', 0, s, r) for s, r in f]
    if not quiet:
        print(json.dumps(dict(eq=eq, law=txt, tests=tot)))
        for name, sd, s, r in allf[:4]:
            print('FAIL', name, sd, {k: L.show(v) for k, v in s.items()}, '-> got', L.show(r))
    return allf


def goals(mod, gens=3, depth=2):
    eq = mod.EQ
    op = mod.op
    CT = mod.CT
    L.UN = list(getattr(mod, 'UN', ()))
    L.CONST = list(getattr(mod, 'CONST', ()))
    cat = catalog()
    out = []
    for r in load_rows():
        if int(r['eq1_id']) != eq:
            continue
        g = parse_eq(cat[int(r['eq2_id'])])
        res = L.refute_goal(op, g, gens=gens, ctors=CT, tries=20000, seed=7, depth=depth)
        out.append((r['id'], r['eq2_id'], r['equation2'],
                    None if res is None else ({k: L.show(v) for k, v in res[0].items()},
                                              L.show(res[1]), L.show(res[2]))))
    return out


if __name__ == '__main__':
    mod = importlib.import_module(sys.argv[1])
    N = int(sys.argv[2]) if len(sys.argv) > 2 else 20000
    seeds = [int(a) for a in sys.argv[3:]] or [1, 2]
    run(mod, N, seeds)
    for rid, gid, gtxt, res in goals(mod):
        print('GOAL', rid, gid, gtxt, '->', 'REFUTED' if res else 'NOT REFUTED', res if res else '')
