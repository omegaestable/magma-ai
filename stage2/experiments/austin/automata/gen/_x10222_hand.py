"""10222 -- hand-built rule set.

Law (L-form):  x = y * ((x*y) * ((z*y)*y))     u = y (decoder), v = encoding.
Chain:  P = op(x,u), Q = op(z,u), R = op(Q,u), v = op(P,R), and op(u,v) must be x.

The generated rule sets are FALSE because their lazy/struct rules decode with a *weaker* shape than the
all-free reading, which makes op(.,u) non-injective (measured: op(z7,s2) = op(x2,s2) = g0 for
s2 = g0*g0, z7 = (g0*g0)*((g0*g0)*g0), x2 = (g0*g0)*(((g1*g0)*g0)) ...).  Here we keep ONLY the strict
all-free reading R0 and add one rule per way a chain product can decode, all keyed on

    u = J (J p w) (J (J q w) w)          w := u.1.2 = u.2.1.2 = u.2.2

which is the only shape at which op(.,u) decodes at all under R0.

python gen/_x10222_hand.py [quick|full]
"""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import closedform as cf, smallcheck as sc, revalidate as rv, fuzz as fz
from freemodel import normalise, catalog
from laws import parse_eq

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def TG(e): return ('TG', e)
def EQ(a, b): return ('EQ', a, b)
def OP(a, b): return ('OP', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

law = normalise(parse_eq(catalog()[10222]))

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

# --- accessor shorthands -------------------------------------------------
P_ = A1(A1(U))            # p  = u.1.1
W_ = A2(A1(U))            # w  = u.1.2
USHAPE = [TG(U), TG(A1(U)), TG(A2(U)), TG(A1(A2(U))),
          EQ(W_, A2(A1(A2(U)))), EQ(W_, A2(A2(U)))]
OPW = OP(W_, U)           # op(w, u)

R0 = ([TG(V), TG(A1(V)), EQ(U, A2(A1(V))),
       TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), EQ(U, A2(A2(V)))],
      A1(A1(V)), 'free')

B1 = (USHAPE + [TG(V), EQ(A1(V), P_),
                TG(A2(V)), TG(A1(A2(V))), EQ(U, A2(A1(A2(V)))), EQ(U, A2(A2(V))),
                OPEQ(OPW, A1(V))],
      W_, 'B1_Pdec')

B2 = (USHAPE + [TG(V), TG(A1(V)), EQ(U, A2(A1(V))),
                TG(A2(V)), EQ(A1(A2(V)), P_), EQ(U, A2(A2(V))),
                OPEQ(OPW, A1(A2(V)))],
      A1(A1(V)), 'B2_Qdec')

B3 = (USHAPE + [TG(V), EQ(A1(V), P_),
                TG(A2(V)), EQ(A1(A2(V)), P_), EQ(U, A2(A2(V))),
                OPEQ(OPW, A1(V))],
      W_, 'B3_PQdec')

B4a = (USHAPE + [EQ(P_, W_), TG(V), TG(A1(V)), EQ(U, A2(A1(V))), EQ(A2(V), W_),
                 OPEQ(OPW, W_)],
       A1(A1(V)), 'B4a')

B4b = (USHAPE + [EQ(P_, W_), TG(V), EQ(A1(V), W_), EQ(A2(V), W_),
                 OPEQ(OPW, W_)],
       W_, 'B4b')

RULES = [R0, B1, B2, B3, B4a, B4b]

SETS = {
    'R0':      [R0],
    'R0B1':    [R0, B1],
    'hand6':   RULES,
}

# --- catch-all rules for a chain product whose decoder is NOT recoverable ----------------
# C1: Q = op(z,u) decoded to an arbitrary value (z occurs only inside that node, so it is
#     unconstrained); v = J (J x u) (J Q u).   Placed AFTER R0, which covers Q = J z u.
C1 = ([TG(V), TG(A1(V)), EQ(U, A2(A1(V))), TG(A2(V)), EQ(U, A2(A2(V)))], A1(A1(V)), 'C1_Qany')

# C2: same, but P is the decoded one as well: v = J p (J Q u) with p = u.1.1 (needs USHAPE on u)
C2 = (USHAPE + [TG(V), EQ(A1(V), P_), TG(A2(V)), EQ(U, A2(A2(V))), OPEQ(OPW, A1(V))], W_, 'C2_PQany')

RULES2 = [R0, B1, B2, B3, B4a, B4b, C1]
RULES3 = [R0, B1, B2, B3, B4a, B4b, C2, C1]
SETS['hand7'] = RULES2
SETS['hand8'] = RULES3

def report(name, rules, full=False):
    print('%-8s nrules=%d' % (name, len(rules)), flush=True)
    for r in rules:
        print('    ', cf.show_rule(r), flush=True)
    tot = 0
    for ms, g in ((9, 1), (5, 2)):
        C = cf.Closed(law, rules)
        t0 = time.time()
        n, f = sc.exhaustive(C, law, ms, g, limit=200)
        rec = [x for x in f if x[1] == 'recursion']
        val = [x for x in f if x[1] != 'recursion']
        tot += len(val)
        print('   exh%d/%d tested=%d rec=%d val=%d (%.1fs)' % (ms, g, n, len(rec), len(val), time.time() - t0), flush=True)
        for s, r in val[:3]:
            print('     VALFAIL', {k: show(v) for k, v in s.items()}, '->', show(r), flush=True)
        for s, r in rec[:2]:
            print('     RECFAIL', {k: show(v) for k, v in s.items()}, flush=True)
    if full and tot == 0:
        t0 = time.time()
        fails = rv.run_tests(law, rules, [3, 4, 5], 3000, 12000)
        real = [x for x in fails if x[1] != 'recursion']
        kinds = {}
        for s, r, kind, sd in real:
            kinds[kind] = kinds.get(kind, 0) + 1
        print('   run_tests fails=%d real=%d %s (%.1fs)' % (len(fails), len(real), kinds, time.time() - t0), flush=True)
        for s, r, kind, sd in real[:5]:
            print('     FAIL', kind, {k: str(v)[:90] for k, v in s.items()}, flush=True)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quick'
    sel = sys.argv[2:] or ['hand6']
    for name in sel:
        report(name, SETS[name], full=(mode == 'full'))
