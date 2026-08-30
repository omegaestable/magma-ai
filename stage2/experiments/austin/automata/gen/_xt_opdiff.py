"""_xt_opdiff.py <eq> [--maxsize 9] [--gens 1] [--mod closedform2] [--rules <chk file>] [--extract]

The sharp extractor measurement: enumerate every pair (u, v) of free-magma terms up to `maxsize` over
`gens` generators and compare the SEMANTIC free model's op with the EXTRACTED rule system's op.
The smallest disagreement names the missing mode directly (no law-failure indirection).

Prints, for each disagreement (smallest first): u, v, free's answer, closed's answer, and which rule (if any)
fired in the closed form.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

MOD = 'closedform'
if '--mod' in sys.argv:
    MOD = sys.argv[sys.argv.index('--mod') + 1]
cf = __import__(MOD)


def show(t):
    if t is None: return 'None'
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


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


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', leangen.dual_pat(orig[1])) if dualized else orig
    return law, dualized, cat[eq]


def load_rules(eq, path=None):
    p = path or os.path.join(HERE, 'gen', 'chk%d.py' % eq)
    src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']


def which_rule(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None:
                return i, tag
    return None, 'free'


def diffs(law, rules, maxsize, gens, limit=12, quiet=False):
    C = cf.Closed(law, rules)
    F = fm.Free(law)
    pool = terms_upto(maxsize, gens)
    pool.sort(key=size)
    out = []
    pairs = [(u, v) for u in pool for v in pool]
    pairs.sort(key=lambda p: (size(p[0]) + size(p[1]), size(p[0])))
    for u, v in pairs:
        try:
            fr = F.op(u, v)
        except Exception:
            continue
        try:
            cr = C.op(u, v)
        except RecursionError:
            cr = 'recursion'
        if fr != cr:
            i, tag = which_rule(C, u, v)
            out.append((u, v, fr, cr, i, tag))
            if not quiet:
                print('DIFF  u=%s  v=%s' % (show(u), show(v)))
                print('      free   = %s' % (show(fr) if size(fr) < 60 else '<size %d>' % size(fr)))
                print('      closed = %s   [%s]' % (show(cr) if cr == 'recursion' or size(cr) < 60 else '<size %d>' % size(cr),
                                                    'free' if i is None else 'R%d %s' % (i + 1, tag)))
            if len(out) >= limit: break
    return out, C, F


def main():
    eq = int(sys.argv[1])
    ms = int(sys.argv[sys.argv.index('--maxsize') + 1]) if '--maxsize' in sys.argv else 9
    gens = int(sys.argv[sys.argv.index('--gens') + 1]) if '--gens' in sys.argv else 1
    law, dualized, txt = get_law(eq)
    if '--extract' in sys.argv:
        t0 = time.time(); rules = cf.Extractor(law).rules(); print('extracted %d rules in %.1fs' % (len(rules), time.time() - t0))
    else:
        rules = load_rules(eq, sys.argv[sys.argv.index('--rules') + 1] if '--rules' in sys.argv else None)
    print('LAW %d  %s  %s  nrules=%d' % (eq, txt, '(dualized)' if dualized else '', len(rules)))
    t0 = time.time()
    out, C, F = diffs(law, rules, ms, gens)
    print(json.dumps(dict(eq=eq, maxsize=ms, gens=gens, ndiffs=len(out), secs=round(time.time() - t0, 1),
                          free_conflicts=len(F.conflicts))))


if __name__ == '__main__':
    main()
