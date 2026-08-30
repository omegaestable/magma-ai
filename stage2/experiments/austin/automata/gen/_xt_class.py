"""_xt_class.py <eq> [--mod closedform2] [--deep 1500] [--fuzz 5000] [--seeds 1] [--rules <chk file>]

Classify a rule set's validator failures into
  SEMANTIC   - the semantic free model fails on the same instance (no rule set can fix it: quotient law)
  HOLE       - the semantic model finds the reading and the closed form does not (an extractor hole)
and, for the smallest HOLE, print the evaluation chain of both models side by side and the rules whose
STRUCTURAL conditions hold at the disagreeing product.
"""
import sys, os, json, time
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'gen'))
import leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

MOD = sys.argv[sys.argv.index('--mod') + 1] if '--mod' in sys.argv else 'closedform2'
cf = __import__(MOD)
import revalidate as rv
rv.cf = cf
import trace as tr


def show(t):
    if t is None or t == 'recursion': return str(t)
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


def brief(t):
    return show(t) if (t is None or t == 'recursion' or size(t) < 45) else '<size %d>' % size(t)


def get_law(eq):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    dz = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    return (('x', leangen.dual_pat(orig[1])) if dz else orig), dz, cat[eq]


def sem_ok(law, s):
    F = fm.Free(law)
    def ev(p, a):
        if isinstance(p, str): return a[p]
        return F.op(ev(p[0], a), ev(p[1], a))
    try:
        return ev(law[1], s) == s['x']
    except Exception:
        return None


def main():
    eq = int(sys.argv[1])
    N = int(sys.argv[sys.argv.index('--deep') + 1]) if '--deep' in sys.argv else 1500
    NF = int(sys.argv[sys.argv.index('--fuzz') + 1]) if '--fuzz' in sys.argv else 5000
    ns = int(sys.argv[sys.argv.index('--seeds') + 1]) if '--seeds' in sys.argv else 1
    law, dz, txt = get_law(eq)
    if '--rules' in sys.argv:
        p = sys.argv[sys.argv.index('--rules') + 1]
        src = open(p, encoding='utf-8').read().split('C = cf.Closed')[0]
        nsx = {}; exec(src, nsx); rules = nsx['rules']
    else:
        rules = cf.Extractor(law).rules()
    print('LAW %d %s %s  nrules=%d  pattern=%s' % (eq, txt, '(dualized)' if dz else '', len(rules), law[1]))
    seeds = [eq * 7 + 3 + 11 * i for i in range(ns)]
    t0 = time.time()
    fails = rv.run_tests(law, rules, seeds, N, NF)
    real = [f for f in fails if f[1] != 'recursion']
    real.sort(key=lambda f: sum(size(t) for t in f[0].values()))
    sem = 0; hole = []
    for s, r, kind, sd in real[:40]:
        if sem_ok(law, s):
            hole.append((s, r, kind, sd))
        else:
            sem += 1
    print(json.dumps(dict(eq=eq, nrules=len(rules), value_fails=len(real), sampled=min(40, len(real)),
                          semantic_also_fails=sem, extractor_holes=len(hole), secs=round(time.time() - t0, 1))))
    if not hole:
        print('no extractor hole in the sample')
        return
    s, r, kind, sd = hole[0]
    print('SMALLEST HOLE', kind, {k: show(v) for k, v in s.items()})
    C = cf.Closed(law, rules); F = fm.Free(law)
    def go(p):
        if isinstance(p, str): return s[p], s[p]
        ca, fa = go(p[0]); cb, fb = go(p[1])
        cr = C.op(ca, cb); fr = F.op(fa, fb)
        print('  %-34s closed=%-22s free=%-22s %s' % (str(p)[:34], brief(cr), brief(fr), '' if cr == fr else '<<< DISAGREE'))
        return cr, fr
    A, B = law[1]
    ua, uf = go(A); va, vf = go(B)
    cr = C.op(ua, va); fr = F.op(uf, vf)
    print('  %-34s closed=%-22s free=%-22s %s' % ('ROOT', brief(cr), brief(fr), '' if cr == fr else '<<< DISAGREE'))
    print('  u = %s' % brief(ua))
    print('  v = %s' % brief(va))
    okr = [i + 1 for i in range(len(rules)) if tr.struct_ok(C, rules[i][0], ua, va)]
    print('  rules whose structural conditions hold at the final pair:', okr, [rules[i - 1][2] for i in okr])


if __name__ == '__main__':
    main()
