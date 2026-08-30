"""_x8485_val.py : full validation of an 8485 rule set, run inside a big-stack thread.

freemodel.py raises the recursion limit to 100,000, which on Windows makes a deep
`Closed.op` chain overflow the C stack and kill the process with NO traceback (that is what
silently killed two earlier validation runs).  Here the work runs in a thread with a 512 MB
stack and the limit is put back to 20,000.
Usage: python -u gen/_x8485_val.py <variant> [deep N] [fuzz N]
"""
import sys, os, threading, time, importlib.util
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
import closedform as cf, revalidate as rv
import fuzz as fz, smallcheck as sc
from freemodel import size
from collections import Counter

sys.setrecursionlimit(20000)
law = m.law
name = sys.argv[1] if len(sys.argv) > 1 else 'a'
DEEP = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
FZ = int(sys.argv[3]) if len(sys.argv) > 3 else 12000
R = m.VARIANTS[name]


def work():
    sys.setrecursionlimit(20000)
    print('variant %s : %d rules' % (name, len(R)), flush=True)
    for r in R:
        print('   ', cf.show_rule(r))
    allf = []
    for ms, gg in ((9, 1), (5, 2)):
        t0 = time.time()
        n, f = sc.exhaustive(cf.Closed(law, R), law, ms, gg, limit=25)
        allf += [(s, r, 'exh%d/%d' % (ms, gg), 0) for s, r in f]
        print('exh%d/%d tested %d fails %d  %.1fs' % (ms, gg, n, len(f), time.time() - t0), flush=True)
    for sd in (3, 4, 5):
        for kind, fn in (('deep', lambda C: cf.deep_tests(C, law, DEEP, 240, sd)),
                         ('fuzz', lambda C: fz.fuzz(C, law, R, FZ, seed=sd + 100)),
                         ('clos', lambda C: fz.closure_fuzz(C, law, FZ, seed=sd + 200)),
                         ('crit', lambda C: fz.critical_fuzz(C, law, FZ, seed=sd + 300))):
            t0 = time.time()
            t, f = fn(cf.Closed(law, R))
            real = [q for q in f if q[1] != 'recursion']
            allf += [(s, r, kind, sd) for s, r in real]
            print('%s %d tested %d fails %d (rec %d)  %.1fs'
                  % (kind, sd, t, len(real), len(f) - len(real), time.time() - t0), flush=True)
    print('TOTAL value fails %d' % len(allf), flush=True)
    for s, r, kind, sd in allf[:6]:
        print('  FAIL %s seed %s sizes %s' % (kind, sd, {k: size(v) for k, v in s.items()}), flush=True)
        print('    ', {k: str(v) for k, v in s.items()}, flush=True)
    # two extra deep seeds at 20,000 (the handover's standard)
    if not allf:
        for sd in (777, 991):
            t0 = time.time()
            t, f = cf.deep_tests(cf.Closed(law, R), law, 20000, 900, sd)
            real = [q for q in f if q[1] != 'recursion']
            print('deep20k %d tested %d fails %d (rec %d)  %.1fs'
                  % (sd, t, len(real), len(f) - len(real), time.time() - t0), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start()
th.join()
