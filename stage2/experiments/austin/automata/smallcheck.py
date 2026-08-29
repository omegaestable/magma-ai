"""smallcheck.py <eq_id> [maxsize=5] [gens=2] [--closed] [--values]

Exhaustive check of the law on ALL assignments of its variables to terms of size <= maxsize over `gens`
generators, in the semantic free model (`freemodel.Free`) or, with --closed, in the closed-form package of
gen/chk<eq>.py.  Random tests miss derived identities (6912, 12073): the failing instances are specific
small terms.  R-form laws are checked through the dual L-form model with the operation flipped (as served).
Prints the failures (smallest first) and a JSON summary line.
"""
import sys, os, json, itertools, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import freemodel as fm
from freemodel import normalise, catalog, pvars, size
from laws import parse_eq

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

def exhaustive(C, law, maxsize, gens, limit=None):
    """all assignments of the (L-form) law's variables to terms of size <= maxsize over `gens` generators,
    evaluated in the closed form C; returns (n, fails)"""
    vs = pvars(law[1]); pool = terms_upto(maxsize, gens)
    def ev(p, s):
        if isinstance(p, str): return s[p]
        return C.op(ev(p[0], s), ev(p[1], s))
    fails = []; n = 0
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals)); n += 1
        try:
            r = ev(law[1], s)
        except RecursionError:
            fails.append((s, 'recursion')); continue
        if r != s['x']: fails.append((s, r))
        if limit and len(fails) >= limit: break
    return n, fails

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

def main():
    eq = int(sys.argv[1])
    maxsize = int(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 5
    gens = int(sys.argv[3]) if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else 2
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', dual_pat(orig[1])) if dualized else orig
    if '--closed' in sys.argv:
        import importlib.util
        spec = importlib.util.spec_from_file_location('chk', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gen', 'chk%d.py' % eq))
        src = open(spec.origin, encoding='utf-8').read().split('C = cf.Closed')[0]
        ns = {}; exec(src, ns)
        import closedform as cf
        M = cf.Closed(law, ns['rules']); opf = M.op
    else:
        M = fm.Free(law); opf = M.op
    def ev(p, s):
        if isinstance(p, str): return s[p]
        a, b = ev(p[0], s), ev(p[1], s)
        return opf(b, a) if dualized else opf(a, b)
    vs = pvars(orig[1])
    pool = terms_upto(maxsize, gens)
    if '--values' in sys.argv:
        # keep only VALUE terms: every J-node is the free product of its children under the model's op
        def is_value(t):
            if t[0] == 'g': return True
            return is_value(t[1]) and is_value(t[2]) and opf(t[1], t[2]) == t
        pool = [t for t in pool if is_value(t)]
        print('value pool', len(pool))
    t0 = time.time(); fails = []; n = 0
    for vals in itertools.product(pool, repeat=len(vs)):
        s = dict(zip(vs, vals)); n += 1
        try:
            r = ev(orig[1], s)
        except RecursionError:
            fails.append((s, 'recursion')); continue
        if r != s[orig[0]]: fails.append((s, r))
    fails.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    def show(t):
        if t == 'recursion': return 'recursion'
        return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))
    for s, r in fails[:6]:
        print('FAIL', {k: show(v) for k, v in s.items()}, '->', show(r))
    conf = len(getattr(M, 'conflicts', []))
    print(json.dumps(dict(eq=eq, dualized=dualized, maxsize=maxsize, gens=gens, assignments=n, fails=len(fails), conflicts=conf, secs=round(time.time() - t0, 1))))

if __name__ == '__main__':
    main()
