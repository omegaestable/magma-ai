"""qz_iter.py <module> [maxsize] [gens] -- run the checks on gen/<module>.op and trace the smallest failures."""
import sys, os, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qz_lib as L


def trace(op, law, s):
    out = []

    def ev(p):
        if isinstance(p, str):
            return s[p]
        a, b = ev(p[0]), ev(p[1])
        r = op(a, b)
        out.append('  op(%s , %s) = %s' % (L.show(a), L.show(b), L.show(r)))
        return r
    r = ev(law[1])
    return r, out


def main():
    mod = importlib.import_module(sys.argv[1])
    eq = getattr(mod, 'EQ')
    maxsize = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    gens = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    law, txt = L.law_of(eq)
    op = mod.op
    CT = mod.CT
    UN = getattr(mod, 'UN', ())
    L.UN = list(UN)
    L.CONST = list(getattr(mod, 'CONST', ()))
    print('law', eq, txt)
    n, pool, fails = L.exhaustive(op, law, maxsize, gens, CT, limit=400, un=UN)
    print('exh %d/%d  assignments=%d pool=%d FAILS=%d' % (maxsize, gens, n, len(pool), len(fails)))
    fails.sort(key=lambda f: (sum(L.size(t) for t in f[0].values()), str(f[0])))
    for s, r in fails[:int(os.environ.get('NF', '3'))]:
        print('FAIL', {k: L.show(v) for k, v in s.items()}, '-> got', L.show(r))
        _, tr = trace(op, law, s)
        for t in tr:
            print(t)
    return fails


if __name__ == '__main__':
    main()
