"""xtrans.py -- cross-transplant screen.

Every model we already have is a magma.  A model M built for law L also settles an
OPEN row (eq1, eq2) whenever  M |= eq1  and  M |/= eq2 -- regardless of which law M
was built for.  This is free coverage nobody has checked: it costs seconds and each
hit is a whole row (its Lean cert is a copy of M's with a new `rhs`).

Usage: python xtrans.py [screenN] [deepN]
"""
import sys, os, json, glob, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as cf
from freemodel import normalise, catalog
from laws import parse_eq, load_rows


def load_chk(path):
    src = open(path, encoding='utf-8').read()
    i = src.find('C = cf.Closed')
    if i < 0:
        return None
    ns = {'__name__': '_chk'}
    try:
        exec(compile(src[:i], path, 'exec'), ns)
    except Exception:
        return None
    if 'law' not in ns or 'rules' not in ns:
        return None
    return ns['law'], ns['rules']


class Opp:
    """the opposite magma of C"""
    def __init__(self, C):
        self.C = C
    def op(self, u, v):
        return self.C.op(v, u)
    def evp(self, p, s):
        if isinstance(p, str):
            return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))


def test_pair(args):
    modpath, eq, N, secs = args
    got = load_chk(modpath)
    if got is None:
        return None
    mlaw, rules = got
    cat = catalog()
    law = normalise(parse_eq(cat[eq]))
    out = []
    for tag, C in (('', cf.Closed(mlaw, rules)), ('^op', Opp(cf.Closed(mlaw, rules)))):
        try:
            tested, fails = cf.deep_tests(C, law, N, secs, 7)
        except Exception:
            continue
        if tested and not fails:
            out.append((os.path.basename(modpath), tag, eq, tested))
    return out or None


def main():
    N = int(sys.argv[1]) if len(sys.argv) > 1 else 250
    secs = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    rows = load_rows()
    shipped = set(os.path.basename(p)[:-5] for p in glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'certs', '*.lean')))
    open_eqs = sorted({int(r['eq1_id']) for r in rows if r['id'] not in shipped})
    mods = sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen', 'chk*.py')))
    tasks = [(m, e, N, secs) for m in mods for e in open_eqs]
    print('models', len(mods), 'open laws', len(open_eqs), 'tasks', len(tasks), flush=True)
    import multiprocessing as mp
    t0 = time.time()
    hits = []
    with mp.Pool(24) as pool:
        for i, r in enumerate(pool.imap_unordered(test_pair, tasks, chunksize=4)):
            if r:
                hits.extend(r)
                for h in r:
                    print('HIT', h, flush=True)
            if i % 200 == 0:
                print('..', i, round(time.time() - t0), 's', flush=True)
    print('hits', len(hits))
    json.dump(hits, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'xtrans_hits.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
