"""_x8485_alt2.py : show the exhaustive failures of the alt sets of gen/_x8485_alt.py."""
import sys, os, time, importlib.util
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
spec = importlib.util.spec_from_file_location('_x8485_alt', 'gen/_x8485_alt.py')
m = importlib.util.module_from_spec(spec); sys.modules['_x8485_alt'] = m
_argv = sys.argv; sys.argv = ['x', 'none']
spec.loader.exec_module(m)
sys.argv = _argv
import closedform as cf, smallcheck as sc
from freemodel import size
import freemodel as fm

law = m.law


def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))


def which(C, R, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d[%s]' % (i + 1, tag)
    return 'free'


def chain(M, s, C=None, R=None):
    x, y, z = s['x'], s['y'], s['z']
    P = M.op(z, x); Q = M.op(P, y); Rr = M.op(Q, y); S = M.op(x, Rr); T = M.op(y, S)
    names = ['P=z*x', 'Q=P*y', 'R=Q*y', 'S=x*R', 'T=y*S']
    args = [(z, x, P), (P, y, Q), (Q, y, Rr), (x, Rr, S), (y, S, T)]
    out = []
    for n, (a, b, r) in zip(names, args):
        tag = which(C, R, a, b) if C is not None else ('free' if r == ('J', a, b) else 'DEC')
        out.append('%s:%s=%s' % (n, tag, sh(r) if size(r) < 20 else '<%d>' % size(r)))
    return ' | '.join(out), T == x


name = sys.argv[1] if len(sys.argv) > 1 else 's1'
R = m.SETS[name]
print('set', name)
n, f = sc.exhaustive(cf.Closed(law, R), law, 9, 1, limit=25)
print('exh9/1 fails', len(f))
for s, r in f[:8]:
    C = cf.Closed(law, R); F = fm.Free(law)
    print('  x=%s y=%s z=%s' % (sh(s['x']), sh(s['y']), sh(s['z'])))
    print('    closed:', chain(C, s, C, R))
    print('    free  :', chain(F, s))
