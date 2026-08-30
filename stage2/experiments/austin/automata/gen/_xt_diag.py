"""_xt_diag.py <eq> [--mod closedform2] [--rules gen/chk<eq>.py]

EXTRACTOR-agent diagnostic. Runs the full validator on the generated (or given) rule set for a law and
prints the failure kinds plus the smallest failing instance, then compares the closed form against the
SEMANTIC free model on the products of that instance's evaluation chain, so the first product where the
two disagree is named.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import freemodel as fm
from freemodel import normalise, catalog, pvars, size
from laws import parse_eq

MOD = 'closedform'
if '--mod' in sys.argv:
    MOD = sys.argv[sys.argv.index('--mod') + 1]
cf = __import__(MOD)
import revalidate as rv
rv.cf = cf
import fuzz as fz


def show(t):
    if t is None: return 'None'
    if t == 'recursion': return 'recursion'
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


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


def extract(eq, **kw):
    law, dualized, txt = get_law(eq)
    X = cf.Extractor(law)
    t0 = time.time()
    rules = X.rules(**kw)
    return law, rules, time.time() - t0


def run(eq, rules=None, seeds=None, N=3000, NF=12000):
    law, dualized, txt = get_law(eq)
    if rules is None:
        rules = load_rules(eq)
    seeds = seeds or [eq * 7 + 3 + 11 * i for i in range(3)]
    t0 = time.time()
    fails = rv.run_tests(law, rules, seeds, N, NF)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    real = [f for f in fails if f[1] != 'recursion']
    return dict(eq=eq, nrules=len(rules), fails=len(fails), real=len(real), kinds=kinds,
                secs=round(time.time() - t0, 1)), real, law, rules


def chain_compare(law, rules, s):
    """evaluate the law pattern under assignment s in both models; report the first product that differs"""
    C = cf.Closed(law, rules)
    F = fm.Free(law)
    out = []
    def go(p):
        if isinstance(p, str):
            return s[p], s[p]
        ca, fa = go(p[0]); cb, fb = go(p[1])
        cr = C.op(ca, cb)
        try:
            fr = F.op(fa, fb)
        except Exception as e:
            fr = ('ERR', str(e))
        out.append((p, ca, cb, cr, fa, fb, fr))
        return cr, fr
    A, B = law[1]
    ua, uf = go(A); va, vf = go(B)
    cr = C.op(ua, va)
    try:
        fr = F.op(uf, vf)
    except Exception as e:
        fr = ('ERR', str(e))
    out.append((('ROOT',), ua, va, cr, uf, vf, fr))
    return out, C, F


def main():
    eq = int(sys.argv[1])
    rpath = sys.argv[sys.argv.index('--rules') + 1] if '--rules' in sys.argv else None
    rules = load_rules(eq, rpath)
    rep, real, law, rules = run(eq, rules)
    print(json.dumps(rep))
    if not real:
        print('no value failures')
        return
    real.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    s, got, kind, sd = real[0]
    print('SMALLEST FAIL', kind, sd, {k: show(v) for k, v in s.items()}, '-> got', show(got) if got != 'recursion' else 'recursion')
    ch, C, F = chain_compare(law, rules, s)
    for p, ca, cb, cr, fa, fb, fr in ch:
        agree = (cr == fr)
        print('  %-30s closed=%s  free=%s  %s' % (str(p)[:30],
              show(cr) if cr is None or cr == 'recursion' or size(cr) < 40 else '<size %d>' % size(cr),
              show(fr) if not isinstance(fr, tuple) or fr[0] != 'ERR' else fr[1][:40],
              'OK' if agree else '<<< DISAGREE'))


if __name__ == '__main__':
    main()
