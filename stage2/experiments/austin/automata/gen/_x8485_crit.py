"""_x8485_crit.py : the fast discriminating tests only (critical fuzz + rule fuzz + closure fuzz),
which is what killed variant 'h' in 0.5 s while the deep tests are minutes.
Usage: python -u gen/_x8485_crit.py <variant> [N]
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
import closedform as cf, fuzz as fz, smallcheck as sc
from freemodel import size

sys.setrecursionlimit(20000)
law = m.law
VAR = sys.argv[1] if len(sys.argv) > 1 else 'f'
N = int(sys.argv[2]) if len(sys.argv) > 2 else 6000
R = m.VARIANTS[VAR]


def work():
    sys.setrecursionlimit(20000)
    print('variant %s : %d rules' % (VAR, len(R)), flush=True)
    tot = 0
    for sd in (3, 4, 5, 6):
        for kind, fn in (('crit', lambda C: fz.critical_fuzz(C, law, N, seed=sd + 300)),
                         ('fuzz', lambda C: fz.fuzz(C, law, R, N, seed=sd + 100)),
                         ('clos', lambda C: fz.closure_fuzz(C, law, N, seed=sd + 200))):
            t0 = time.time()
            t, f = fn(cf.Closed(law, R))
            real = [q for q in f if q[1] != 'recursion']
            tot += len(real)
            print('%s %d tested %d fails %d (rec %d)  %.1fs'
                  % (kind, sd, t, len(real), len(f) - len(real), time.time() - t0), flush=True)
            for s, r in real[:2]:
                print('    FAIL', {k: str(v) for k, v in s.items()}, flush=True)
    print('TOTAL %d' % tot, flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
