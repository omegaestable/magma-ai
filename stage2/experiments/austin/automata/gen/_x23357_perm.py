"""23357: PERMISSIVE rule sets.

The model only has to satisfy the law; a rule does not have to characterise readings exactly.  The
generated rules split every mode into a separate rule because the extractor certifies "(u,v) IS a
reading".  Dropping the conditions that only serve that certification collapses whole families:

  QF  u = J (J y x) y  and  v = J x _                            (rules 1,2,3 of the 12-rule set)
  QL  u = J (J y x) y  and  x = J (J p q) p  and  v = q          (rules 4,6,7,8)
  QM  u = J (J y x) y,  tg x = 2,  v = y,  op (a2 x) v = a1 x    (rule 5)
  QR  tg u = 2, tg v = 2, op (a2 u) (a1 v) = a1 u                (rules 9,10,11)
  QA  tg v = 2, tg (a2 v) = 2, op (op (a1 (a2 v)) (a1 v)) (a1 (a2 v)) = u   (rule 12)

L-type first (QF, QL, QM), then R-type (QR, QA) -- see gen/_x23357_rep.py for why the order matters.
"""
import sys, os, time, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog
from laws import parse_eq

EQ = 23357
law = normalise(parse_eq(catalog()[EQ]))

U = ('U',); V = ('V',)
A1 = lambda e: ('A1', e)
A2 = lambda e: ('A2', e)
TG = lambda e: ('TG', e)
EQ_ = lambda a, b: ('EQ', a, b)
OPEQ = lambda a, b: ('OPEQ', a, b)
OP = lambda a, b: ('OP', a, b)

u1 = A1(U); u11 = A1(u1); u12 = A2(u1); u2 = A2(U)
TOP = [TG(U), TG(u1), EQ_(u11, u2)]
X = u12          # x = a2 (a1 u)
Y = u11          # y = a1 (a1 u)

QF = (TOP + [TG(V), EQ_(X, A1(V))], X, 'QF')
QL = (TOP + [TG(X), TG(A1(X)), EQ_(V, A2(A1(X))), EQ_(A1(A1(X)), A2(X))], X, 'QL')
QM = (TOP + [TG(X), EQ_(Y, V), OPEQ(OP(A2(X), V), A1(X))], X, 'QM')
QR = ([TG(U), TG(V), OPEQ(OP(u2, A1(V)), u1)], A1(V), 'QR')
QA = ([TG(V), TG(A2(V)), OPEQ(OP(OP(A1(A2(V)), A1(V)), A1(A2(V))), U)], A1(V), 'QA')

SETS = {
    'perm5': [QF, QL, QM, QR, QA],
    'perm4': [QF, QL, QR, QA],
    'perm3': [QF, QL, QR],
}

if __name__ == '__main__':
    import importlib.util
    D = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
    hspec = importlib.util.spec_from_file_location('_x23357_hunt', D + '_x23357_hunt.py')
    for name in (sys.argv[1:] or list(SETS)):
        rules = SETS[name]
        t0 = time.time()
        for r in rules:
            print('   ', cf.show_rule(r))
        f = [q for q in rv.run_tests(law, rules, [3, 4, 5], 3000, 12000) if q[1] != 'recursion']
        k = collections.Counter(q[2] for q in f)
        print('%-7s %d rules  run_tests fails %d %s (%.0fs)' % (name, len(rules), len(f), dict(k), time.time() - t0), flush=True)
        if f:
            print('    first:', {a: b for a, b in f[0][0].items()})
            continue
        hm = importlib.util.module_from_spec(hspec); hspec.loader.exec_module(hm)
        hm.rules = rules; hm.law = law
        tot = 0; bad = 0
        for sd in (41, 42, 43):
            n, b = hm.hunt(20, sd)
            tot += n; bad += len(b)
        print('%-7s hunt tested %d broken %d (%.0fs)' % (name, tot, bad, time.time() - t0), flush=True)
        if bad == 0:
            for sd in (901, 902):
                C = cf.Closed(law, rules)
                t, ff = cf.deep_tests(C, law, 20000, 300, sd)
                ff = [q for q in ff if q[1] != 'recursion']
                print('%-7s deep20k seed %d fails %d' % (name, sd, len(ff)), flush=True)
