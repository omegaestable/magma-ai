"""_x8485_emitfail.py : reproduce leangen.emit's own 'fails_kept: 1' for the variant-a 8485 rules
and print the failing instance with the rule fired at each product."""
import sys, os, importlib.util
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
spec = importlib.util.spec_from_file_location('_x8485_min', 'gen/_x8485_min.py')
m = importlib.util.module_from_spec(spec); sys.modules['_x8485_min'] = m
_a = sys.argv; sys.argv = ['x', 'a']
try:
    spec.loader.exec_module(m)
except SystemExit:
    pass
sys.argv = _a
import closedform as cf, fuzz as fz
import freemodel as fm
from freemodel import size

law = m.law
R = m.VARIANTS['a']
EQ = 8485


def sh(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))


def which(C, u, v):
    for i, (conds, e, tag) in enumerate(R):
        if C.check(conds, u, v) and C.ev(e, u, v) is not None:
            return 'R%d[%s]' % (i + 1, tag)
    return 'free'


def chain(M, s, C=None):
    x, y, z = s['x'], s['y'], s['z']
    P = M.op(z, x); Q = M.op(P, y); Rr = M.op(Q, y); S = M.op(x, Rr); T = M.op(y, S)
    names = ['P=z*x', 'Q=P*y', 'R=Q*y', 'S=x*R', 'T=y*S']
    args = [(z, x, P), (P, y, Q), (Q, y, Rr), (x, Rr, S), (y, S, T)]
    out = []
    for n, (a, b, r) in zip(names, args):
        tag = which(C, a, b) if C is not None else ('free' if r == ('J', a, b) else 'DEC')
        out.append('%s:%s sz%d' % (n, tag, size(r)))
    return ' | '.join(out), T == x


C2 = cf.Closed(law, R)
t2, f2 = cf.deep_tests(C2, law, 3000, 200, EQ * 5 + 7)
print('deep seed %d: tested %d fails %d' % (EQ * 5 + 7, t2, len(f2)), flush=True)
ft, ff = fz.fuzz(cf.Closed(law, R), law, R, 12000, seed=EQ)
print('fuzz seed %d: tested %d fails %d' % (EQ, ft, len(ff)), flush=True)
for s, r in (f2 + ff)[:6]:
    if r == 'recursion':
        print('  recursion (not a counterexample)', {k: size(v) for k, v in s.items()})
        continue
    print('  x=%s' % sh(s['x']))
    print('  y=%s' % sh(s['y']))
    print('  z=%s' % sh(s['z']))
    print('   closed:', chain(cf.Closed(law, R), s, cf.Closed(law, R)))
    print('   free  :', chain(fm.Free(law), s))
