"""_x8485_alt.py : alternative rule sets for 8485 that never have to LOCATE z.

Law  x = y * (x * (((z*x)*y)*y)).  Write P = op z x, and Ch(P,u) = op (op P u) u, so the encoding
is  v = J x (Ch(P,u))  with u = y.  P is either the free product J z x  or the decoded value a1 x.
So a rule only has to try the two candidate P's that are READABLE FROM v ITSELF:

  P = a1 (a1 v)          -- the decoded case (op z x = a1 x, x = a1 v)
  P = a1 (a1 (a2 v))     -- the free case    (Ch(P,u) = J (J P u) u, so P = v.2.1.1)

and verify  op (op P u) u = a2 v  by computation.  No accessor path to z is needed anywhere, which
is what the generated rule set needed three separate rules for (and what the Lean proof of the
generated set would have to justify).
Usage: python -u gen/_x8485_alt.py <set> [full]
"""
import sys, os, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
import fuzz as fz, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq
from collections import Counter

EQ = 8485
cat = catalog(); law = normalise(parse_eq(cat[EQ]))
src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); rules = ns['rules']
R1 = rules[0]

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
OP = lambda a, b: ('OP', a, b)
TG = lambda e: ('TG', e)
EQc = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)

X = A1(V)                       # the payload
Pdec = A1(A1(V))                # candidate P in the decoded case:  a1 x
Pfree = A1(A1(A2(V)))           # candidate P in the free case:     v.2.1.1
CH = lambda P: OP(OP(P, U), U)

# decoded-P rule: x = a1 v must be a J (a decoding returns a1 of a J)
D1 = ([TG(V), TG(X), OPEQ(CH(Pdec), A2(V))], X, 'Pdec')
# free-P rule: v.2.1.1 must be J(z, x)
F1 = ([TG(V), TG(A2(V)), TG(A1(A2(V))), TG(Pfree), EQc(X, A2(Pfree)),
       OPEQ(CH(Pfree), A2(V))], X, 'Pfree')
# free-P rule with the freeness of op(z,x) itself verified
F2 = ([TG(V), TG(A2(V)), TG(A1(A2(V))), TG(Pfree), EQc(X, A2(Pfree)),
       OPEQ(OP(A1(Pfree), X), Pfree), OPEQ(CH(Pfree), A2(V))], X, 'Pfree+')

SETS = {
    's1': [R1, D1],
    's2': [F1, D1],
    's3': [F2, D1],
    's4': [R1, F1, D1],
    's5': [D1, F1],
    's6': [R1, D1, F1],
}


def run(name, R, full=False):
    print('set %s : %d rules' % (name, len(R)), flush=True)
    for r in R:
        print('   ', cf.show_rule(r))
    bad = 0
    for ms, gg in ((9, 1), (5, 2)):
        t0 = time.time()
        n, f = sc.exhaustive(cf.Closed(law, R), law, ms, gg, limit=25)
        bad += len(f)
        print('  exh%d/%d tested %d fails %d  %.1fs' % (ms, gg, n, len(f), time.time() - t0), flush=True)
    if bad:
        return bad
    for sd in (3, 4):
        t0 = time.time()
        t, f = cf.deep_tests(cf.Closed(law, R), law, 800, 120, sd)
        nf = len([q for q in f if q[1] != 'recursion'])
        bad += nf
        print('  deep %d tested %d fails %d  %.1fs' % (sd, t, nf, time.time() - t0), flush=True)
        t0 = time.time()
        t, f = fz.critical_fuzz(cf.Closed(law, R), law, 4000, seed=sd + 300)
        nf = len([q for q in f if q[1] != 'recursion'])
        bad += nf
        print('  crit %d tested %d fails %d  %.1fs' % (sd, t, nf, time.time() - t0), flush=True)
        t0 = time.time()
        t, f = fz.closure_fuzz(cf.Closed(law, R), law, 4000, seed=sd + 200)
        nf = len([q for q in f if q[1] != 'recursion'])
        bad += nf
        print('  clos %d tested %d fails %d  %.1fs' % (sd, t, nf, time.time() - t0), flush=True)
        t0 = time.time()
        t, f = fz.fuzz(cf.Closed(law, R), law, R, 4000, seed=sd + 100)
        nf = len([q for q in f if q[1] != 'recursion'])
        bad += nf
        print('  fuzz %d tested %d fails %d  %.1fs' % (sd, t, nf, time.time() - t0), flush=True)
    if full and not bad:
        t0 = time.time()
        fails = rv.run_tests(law, R, [3, 4, 5], 3000, 12000)
        real = [f for f in fails if f[1] != 'recursion']
        print('  run_tests fails %d (value %d) %s  %.1fs'
              % (len(fails), len(real),
                 dict(Counter((('rec' if f[1] == 'recursion' else 'val') + ':' + f[2]) for f in fails)),
                 time.time() - t0), flush=True)
        bad += len(real)
    print('  TOTAL BAD %d' % bad, flush=True)
    return bad


if __name__ == '__main__':
    which = sys.argv[1] if len(sys.argv) > 1 else 'all'
    full = 'full' in sys.argv
    for name, R in SETS.items():
        if which != 'all' and name != which:
            continue
        run(name, R, full)
