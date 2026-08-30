import sys, os, time, threading
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
os.chdir('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen, smallcheck as sc
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 10218


def main():
    cat = catalog(); law = normalise(parse_eq(cat[EQ]))
    src = open('gen/chk%d.py' % EQ, encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    rules = ns['rules']
    print('nrules', len(rules), flush=True)

    t = time.time()
    C = cf.Closed(law, rules)
    n, f = cf.deep_tests(C, law, 3000, 300, 991)
    print('deep 3000: tested', n, 'fails', len(f), '%.1fs' % (time.time() - t), flush=True)
    for s, r in f[:3]:
        print('  FAIL', {k: size(v) for k, v in s.items()}, 'got', 'recursion' if r == 'recursion' else size(r), flush=True)

    t = time.time()
    n, f = sc.exhaustive(cf.Closed(law, rules), law, 9, 1, limit=25)
    print('exh9/1: tested', n, 'fails', len(f), '%.1fs' % (time.time() - t), flush=True)
    for s, r in f[:3]:
        print('  FAIL', s, 'got', r, flush=True)

    t = time.time()
    n, f = sc.exhaustive(cf.Closed(law, rules), law, 5, 2, limit=25)
    print('exh5/2: tested', n, 'fails', len(f), '%.1fs' % (time.time() - t), flush=True)
    for s, r in f[:3]:
        print('  FAIL', s, 'got', r, flush=True)


threading.stack_size(64 * 1024 * 1024)
th = threading.Thread(target=main)
th.start()
th.join()
