"""Large exhaustive sweeps for the three validated models."""
import sys, os, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qmod
qmod.UNARY = []
from qmod import terms_upto, show
import qcheck
import q12073e, q27859, q22591b


def run(name, Mf, law, ess, fixed, pools, tag):
    M = Mf()
    t0 = time.time()
    n, f = qcheck.exh_pairs(M, law, ess, fixed, pools)
    print('%-8s %-26s n=%-12d fails=%d  %.0fs' % (name, tag, n, len(f), time.time() - t0), flush=True)
    for s, r in f[:4]:
        print('    FAIL ' + '  '.join('%s=%s' % (a, show(b)) for a, b in sorted(s.items())),
              '->', show(r) if r != 'recursion' else r, flush=True)
    return len(f)


if __name__ == '__main__':
    p11 = terms_upto(11, 1)
    p7 = terms_upto(7, 1)
    p9 = terms_upto(9, 1)
    p52 = terms_upto(5, 2)
    print('pools: <=11/1gen %d   <=9/1gen %d   <=7/1gen %d   <=5/2gen %d'
          % (len(p11), len(p9), len(p7), len(p52)), flush=True)
    bad = 0
    bad += run('12073', q12073e.M, q12073e.LAW, ['x', 'y'], {'z': ('g', 0)}, [p11, p11], 'x,y <= 11 (1 gen)')
    bad += run('27859', q27859.M, q27859.LAW, ['x', 'y'], {'z': ('g', 0)}, [p11, p11], 'x,y <= 11 (1 gen)')
    bad += run('12073', q12073e.M, q12073e.LAW, ['x', 'y'], {'z': ('g', 0)}, [p52, p52], 'x,y <= 5 (2 gen) full')
    bad += run('22591', q22591b.M, q22591b.LAW, ['x', 'y', 'z'], {}, [p9, p7, p7], 'x<=9, y,z<=7 (1 gen)')
    bad += run('22591', q22591b.M, q22591b.LAW, ['x', 'y', 'z'], {}, [p7, p9, p7], 'y<=9, x,z<=7 (1 gen)')
    bad += run('22591', q22591b.M, q22591b.LAW, ['x', 'y', 'z'], {}, [p7, p7, p9], 'z<=9, x,y<=7 (1 gen)')
    bad += run('22591', q22591b.M, q22591b.LAW, ['x', 'y', 'z'], {}, [p52, p52, p52], 'x,y,z <= 5 (2 gen) full')
    print('TOTAL FAILS', bad, flush=True)
