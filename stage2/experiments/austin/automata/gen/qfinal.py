"""Final validation of the three quotient/free models (12073, 27859, 22591), 6 seeds."""
import sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
import qcheck
import q12073e, q27859, q22591b

SEEDS = (3, 4, 5, 7, 11, 13)

JOBS = [
    ('12073', q12073e.M, q12073e.LAW, ['x', 'y'], ['z'], ((9, 1), (5, 2), (5, 3)), (11, 1, 5)),
    ('27859', q27859.M, q27859.LAW, ['x', 'y'], ['z'], ((9, 1), (5, 2), (5, 3)), (11, 1, 5)),
    ('22591', q22591b.M, q22591b.LAW, ['x', 'y', 'z'], [], ((7, 1), (5, 2)), (9, 1, 3)),
]

if __name__ == '__main__':
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for name, Mf, law, ess, irr, sizes, big in JOBS:
        if only and only != name:
            continue
        print('=' * 70)
        print('LAW', name, flush=True)
        t0 = time.time()
        ok = qcheck.check(Mf, law, ess, irr, sizes=sizes, big=big,
                          deepN=20000, seeds=SEEDS, fuzzN=12000)
        print('LAW %s -> %s   (%.0f s)' % (name, 'VALIDATED' if ok else 'FAILED', time.time() - t0), flush=True)
