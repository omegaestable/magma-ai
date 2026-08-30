"""23357: try rule ORDERINGS / SUBSETS that make the Lean proof tractable.

All rules split into two families by their result:
  L-type  (P1,P2,P3,P4,P5,P10,P11,P12)  precondition  tg u = 2 & tg (a1 u) = 2 & a1 (a1 u) = a2 u,
                                        result  a2 (a1 u)
  R-type  (P6,P7,P8,P9)                 precondition  tg v = 2,   result  a1 v

With every L-type rule BEFORE every R-type rule, "some L-branch holds" already implies
op u v = a2 (a1 u) (all earlier branches return the same value), which removes the whole
"refute the other eleven branches" burden from the Lean proof.
"""
import sys, os, time, collections
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
import importlib.util
spec = importlib.util.spec_from_file_location(
    '_x23357_rep', 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/_x23357_rep.py')
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
law = mod.law
R = mod.rules                       # R[0..11] = R1..R12 in generated order

L_IDX = [0, 1, 2, 3, 4, 9, 10, 11]  # R1 R2 R3 R4 R5 R10 R11 R12
RT_IDX = [5, 6, 7, 8]               # R6 R7 R8 R9

VARIANTS = {
    'orig12': list(range(12)),
    'Lfirst': L_IDX + RT_IDX,
    'Lonly': L_IDX,
}


def test(name, idx, seeds=(3, 4, 5)):
    rules = [R[i] for i in idx]
    t0 = time.time()
    fails = [q for q in rv.run_tests(law, rules, list(seeds), 3000, 12000) if q[1] != 'recursion']
    kinds = collections.Counter(q[2] for q in fails)
    print('%-8s %2d rules  run_tests fails %3d %s  (%.0fs)' % (name, len(rules), len(fails), dict(kinds), time.time() - t0), flush=True)
    return rules, fails


if __name__ == '__main__':
    which = sys.argv[1:] or list(VARIANTS)
    for name in which:
        test(name, VARIANTS[name])
