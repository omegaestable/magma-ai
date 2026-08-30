"""_y8485_emit.py : emit the Lean skeleton for law 8485 from VALIDATED variant 'f'.

variant f = [R1(free), N4(zP@x22), N1(zP@u22), N2(zP@u221)]  -- gen/_x8485_min.py
Full validation on record in gen/_x8485_val_f.out: exh9/1 0, exh5/2 0,
deep/fuzz/clos/crit on seeds 3,4,5 all 0  ->  TOTAL value fails 0.

Runs in a 64 MB-stack thread (freemodel raises the recursion limit to 100,000, which overflows the
C stack on Windows and kills the process with no traceback).
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
import leangen, closedform as cf

VAR = sys.argv[1] if len(sys.argv) > 1 else 'f'
R = m.VARIANTS[VAR]
OUT = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/rep8485_%s' % VAR


def work():
    sys.setrecursionlimit(20000)
    print('variant %s : %d rules' % (VAR, len(R)), flush=True)
    for r in R:
        print('   ', cf.show_rule(r), flush=True)
    t0 = time.time()
    info = leangen.emit(8485, OUT, rules_override=R)
    print('emit %.1fs ->' % (time.time() - t0), info, flush=True)
    print('files', os.listdir(OUT), flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=work)
th.start(); th.join()
