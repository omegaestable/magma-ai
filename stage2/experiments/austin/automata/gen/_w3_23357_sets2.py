"""23357: second round of candidate rule sets.

The min6 refutation (gen/_w3_23357_wit.py) is case "A,U,B free, V L-decoded": u = J (J y x) y with x itself
U-shaped and v = a2 (a1 x).  The purely STRUCTURAL rule for that cell is

    LD : Ushape u & Ushape x & v = a2 (a1 x) -> x            (x = a2 (a1 u))

which subsumes the generated Bs / Bs|ex:Qb / Bs|ex:Qc variants of the same cell.  Its R-decode twin is

    RD : Ushape u & tg x = 2 & op (a2 x) v = a1 x -> x

Together with the generated A0s family (v free, A decoded) these should cover the whole chain:
  1a-i  A,B,V free                -> P1  (free)
  1a-ii A free, B decoded, V free -> P2/P3 (B1s) or P11 (A0s,B1s|rd:A0) or P12 (As)
  1b    A free, V decoded         -> LD / RD
  2a    A decoded, V free         -> P9/P10/P11/P12
  2b    A and V both decoded      -> conjecturally impossible (23354's ONESIDE)
"""
import sys, time, collections
D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D)
import closedform as cf, revalidate as rv
import importlib.util
G = D + '/gen/'
spec = importlib.util.spec_from_file_location('_x23357_rep', G + '_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law = mod.law
TAG = {r[2]: r for r in mod.rules}

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e)
EQ_ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)
OP = lambda a, b: ('OP', a, b)
u1 = A1(U); u11 = A1(u1); u12 = A2(u1); u2 = A2(U)
TOP = [TG(U), TG(u1), EQ_(u11, u2)]
X = u12; Y = u11

LD = (TOP + [TG(X), TG(A1(X)), EQ_(A1(A1(X)), A2(X)), EQ_(V, A2(A1(X)))], X, 'LD')
RD = (TOP + [TG(X), OPEQ(OP(A2(X), V), A1(X))], X, 'RD')

def S(*tags):
    out = []
    for t in tags:
        out.append(LD if t == 'LD' else RD if t == 'RD' else TAG[t])
    return out

SETS = {
    # L-type rules first, then R-type (see gen/_x23357_rep.py: shared result makes the Lean proof cheap)
    'a7': S('free', 'LD', 'RD', 'A0s', 'A0s,B1s', 'A0s,B1s|rd:A0', 'As'),
    'a5': S('free', 'LD', 'RD', 'A0s,B1s|rd:A0', 'As'),
    'a4': S('free', 'LD', 'RD', 'As'),
    'a6': S('free', 'LD', 'RD', 'A0s', 'A0s,B1s|rd:A0', 'As'),
    'b6': S('free', 'B1s', 'LD', 'RD', 'A0s,B1s|rd:A0', 'As'),
    'c8': S('free', 'B1s', 'B1s|rd:A0', 'LD', 'RD', 'A0s', 'A0s,B1s|rd:A0', 'As'),
    'd7': S('free', 'Bs|rd:A0', 'LD', 'RD', 'A0s,B1s|rd:A0', 'As', 'A0s'),
    'e7': S('free', 'LD', 'RD', 'Bs|rd:A0', 'A0s', 'A0s,B1s|rd:A0', 'As'),
    # the validated-removal survivor of a5: LD is droppable (RD covers its cell)
    'f4': S('free', 'RD', 'A0s,B1s|rd:A0', 'As'),
    'f3': S('free', 'RD', 'As'),

}

if __name__ == '__main__':
    for name in (sys.argv[1:] or sorted(SETS)):
        rules = SETS[name]
        t0 = time.time()
        f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
        k = collections.Counter(q[2] for q in f)
        print('%-5s %d rules  run_tests fails %d %s (%.0fs)' % (name, len(rules), len(f), dict(k), time.time() - t0), flush=True)
        if f:
            print('    first:', {a: b for a, b in f[0][0].items()}, flush=True)
