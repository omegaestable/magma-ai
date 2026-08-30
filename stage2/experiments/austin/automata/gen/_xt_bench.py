"""_xt_bench.py <eq,eq,...> [--mods closedform,closedform2] [--deep 3000] [--fuzz 12000] [--seeds 3]
                            [--kw '{"cap2":64}'] [--out gen/_xt_bench.jsonl]

Before/after table for the extractor: for each law and each module, EXTRACT the rule set fresh and run the
full validator (`revalidate.run_tests`: exhaustive size<=9/1gen and <=5/2gen, deep, fuzz, closure, critical).
Prints one JSON line per (law, module): nrules, extraction seconds, validation seconds, value fails, kinds.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
from freemodel import normalise, catalog, size
from laws import parse_eq
import revalidate as rv


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
    return law, dualized, cat[eq]


def bench(eq, modname, seeds, N, NF, kw):
    sound = modname.endswith('+sound')
    base = modname[:-len('+sound')] if sound else modname
    cf = __import__(base)
    rv.cf = cf
    law, dualized, txt = get_law(eq)
    t0 = time.time()
    info = {}
    try:
        if sound:
            rules, info = cf.extract(law, **kw)
        else:
            rules = cf.Extractor(law).rules(**kw)
    except Exception as e:
        return dict(eq=eq, mod=modname, error='extract:%s' % e)
    tex = time.time() - t0
    t1 = time.time()
    fails = rv.run_tests(law, rules, seeds, N, NF)
    tv = time.time() - t1
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    real = [f for f in fails if f[1] != 'recursion']
    return dict(eq=eq, mod=modname, dualized=dualized, nrules=len(rules), extract_s=round(tex, 2),
                validate_s=round(tv, 1), fails=len(fails), value_fails=len(real), kinds=kinds,
                dropped=info.get('dropped'))


def main():
    eqs = [int(x) for x in sys.argv[1].split(',')]
    mods = sys.argv[sys.argv.index('--mods') + 1].split(',') if '--mods' in sys.argv else ['closedform', 'closedform2']
    N = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 3000
    NF = int(sys.argv[sys.argv.index('--fuzz') + 1]) if '--fuzz' in sys.argv else 12000
    ns = int(sys.argv[sys.argv.index('--seeds') + 1]) if '--seeds' in sys.argv else 3
    kw = json.loads(sys.argv[sys.argv.index('--kw') + 1]) if '--kw' in sys.argv else {}
    outp = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    fh = open(outp, 'a', encoding='utf-8') if outp else None
    for eq in eqs:
        seeds = [eq * 7 + 3 + 11 * i for i in range(ns)]
        for m in mods:
            r = bench(eq, m, seeds, N, NF, kw)
            line = json.dumps(r)
            print(line, flush=True)
            if fh: fh.write(line + '\n'); fh.flush()


if __name__ == '__main__':
    main()
