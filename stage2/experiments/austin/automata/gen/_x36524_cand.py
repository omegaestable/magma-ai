"""Candidate rule sets for law 36524 (dual L-form: x = y o ((z o y) o (y o (x o y)))).

Usage: python gen/_x36524_cand.py <name> [--quick]
"""
import sys, os, time, json
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 36524
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
LAW = ('x', leangen.dual_pat(orig[1]))

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

# --- the chain, all free:  v = J( P , J(u, J(x,u)) ),  P = op(z,u)
# x sits at v.2.2.1 ; alternative locations of x inside u: u.1.2 (=a2 a1 u) and u.2.1 (=a1 a2 u)
X1 = A2(A1(U))          # x located at u.1.2
X2 = A1(A2(U))          # x located at u.2.1
TG1 = [TG(U), TG(A1(U))]
TG2 = [TG(U), TG(A2(U))]

# A : v.2 = J(u, J(x,u)) ; v.1 unconstrained (the existential z is not checked)
A = ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V))), TG(A2(A2(V))), EQ_(U, A2(A2(A2(V))))],
     A1(A2(A2(V))), 'free')
# A0 : the strict version (v.1 = J(_,u), i.e. op(z,u) free)  -- the generated R1
A0 = ([TG(V), TG(A1(V)), EQ_(U, A2(A1(V))), TG(A2(V)), EQ_(U, A1(A2(V))),
       TG(A2(A2(V))), EQ_(U, A2(A2(A2(V))))], A1(A2(A2(V))), 'free')

def Bk(X, tgs, tag):      # T = op(x,u) decoded:  v.2 = J(u, t), op(x,u) == t
    return ([TG(V), TG(A2(V)), EQ_(U, A1(A2(V)))] + tgs + [OPEQ(OP(X, U), A2(A2(V)))], X, tag)

def Ck(X, tgs, tag):      # Q = op(u, op(x,u)) decoded: op(u, op(x,u)) == v.2
    return ([TG(V)] + tgs + [OPEQ(OP(U, OP(X, U)), A2(V))], X, tag)

def Dk(X, tgs, tag):      # v itself decoded: v == op(op(x,u), op(u,op(x,u)))   (witness z := x)
    return (tgs + [OPEQ(OP(OP(X, U), OP(U, OP(X, U))), V)], X, tag)

B1 = Bk(X1, TG1, 'B1'); B2 = Bk(X2, TG2, 'B2')
C1 = Ck(X1, TG1, 'C1'); C2 = Ck(X2, TG2, 'C2')
D1 = Dk(X1, TG1, 'D1'); D2 = Dk(X2, TG2, 'D2')

SETS = {
    'S1': [A],
    'S1s': [A0],
    'S2': [A, B1, B2, C1, C2, D1, D2],
    'S2r': [B1, B2, C1, C2, D1, D2, A],
    'S3': [A, B1, C1, D1],
    'S4': [A, C1, C2, D1, D2],
    'S5': [A, B1, B2, C1, C2],
}

def load_gen():
    src = open(os.path.join(HERE, 'gen', 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}; exec(src, ns); return ns['rules']
SETS['GEN'] = load_gen()

def report(name, rules, quick=False):
    t0 = time.time()
    if quick:
        fails = rv.run_tests(LAW, rules, [3], 1500, 6000)
    else:
        fails = rv.run_tests(LAW, rules, [3, 4, 5], 3000, 12000)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    real = [f for f in fails if f[1] != 'recursion']
    print('%-6s nrules=%2d  fails=%3d real=%3d %s  %.1fs' % (name, len(rules), len(fails), len(real), kinds, time.time() - t0), flush=True)
    for s, r, kind, sd in real[:3]:
        print('    FAIL', kind, 'seed', sd, {k: size(v) for k, v in s.items()}, 'got', size(r) if r != 'recursion' else 'rec', flush=True)
    return real

if __name__ == '__main__':
    quick = '--quick' in sys.argv
    names = [a for a in sys.argv[1:] if not a.startswith('--')] or ['S1', 'S3', 'S2']
    for n in names:
        real = report(n, SETS[n], quick)
        if not real and not quick:
            for sd in (777, 778):
                C = cf.Closed(LAW, SETS[n]); t, f = cf.deep_tests(C, LAW, 20000, 300, sd)
                rf = [x for x in f if x[1] != 'recursion']
                print('    deep20k seed %d: tested %d real fails %d' % (sd, t, len(rf)), flush=True)
