"""_x8485_probe.py : trace the shipped 4-rule set and the semantic free model on the failing
instances of law 8485 (x = y * (x * (((z * x) * y) * y))), and classify each failure.
Usage: python gen/_x8485_probe.py [nfails]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']


def sh(t):
    if t[0] == 'g':
        return 'g%d' % t[1]
    return '(%s*%s)' % (sh(t[1]), sh(t[2]))


def which(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d[%s]' % (i + 1, tag)
    return 'free'


def chain(M, s, C=None, R=None):
    x, y, z = s['x'], s['y'], s['z']
    P = M.op(z, x); Q = M.op(P, y); Rr = M.op(Q, y); S = M.op(x, Rr); T = M.op(y, S)
    steps = [('P=z*x', z, x, P), ('Q=P*y', P, y, Q), ('R=Q*y', Q, y, Rr), ('S=x*R', x, Rr, S), ('T=y*S', y, S, T)]
    out = []
    for n, a, b, r in steps:
        if C is not None:
            tag = which(C, R, a, b)
        else:
            tag = 'free' if r == ('J', a, b) else 'DEC'
        out.append('%s:%s sz%d' % (n, tag, size(r)))
    return ' | '.join(out), T == x, [st[3] for st in steps]


def report(s, verbose=True):
    C = cf.Closed(law, rules)
    F = fm.Free(law)
    cl, okc, vc = chain(C, s, C, rules)
    fr, okf, vf = chain(F, s)
    print('  x=%s' % sh(s['x']))
    print('  y=%s' % sh(s['y']))
    print('  z=%s' % sh(s['z']))
    print('   closed: %s  => %s' % (cl, okc))
    print('   free  : %s  => %s' % (fr, okf))
    if verbose:
        for nm, t in zip(['P', 'Q', 'R', 'S', 'T'], vf):
            print('     free %s = %s' % (nm, sh(t)))
    return okc, okf


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    fails = rv.run_tests(law, rules, [3], 3000, 12000)
    fails = [f for f in fails if f[2] != 'recursion']
    fails.sort(key=lambda f: sum(size(v) for v in f[0].values()))
    print('total fails', len(fails))
    nfree = 0
    for f in fails[:n]:
        print('== %s seed %s' % (f[2], f[3]))
        okc, okf = report(f[0])
        if not okf:
            nfree += 1
    print('free-model also fails on %d of the %d shown' % (nfree, min(n, len(fails))))
