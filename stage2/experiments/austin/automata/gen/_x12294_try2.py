"""12294: generated 24 rules + a permissive fallback R0 appended LAST.

R0 = the generated R1 with the `s1 = J z u` guard (which recovers z) dropped.  It can only fire
where every generated rule already failed, so it adds firings exactly in the hole.
"""
import sys, time, json
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 12294
law = normalise(parse_eq(catalog()[EQ]))

U = ('U',); V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)

src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chk%d.py' % EQ,
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); GEN = ns['rules']

R0 = ([TG(V), TG(A1(V)), TG(A2(V)),
       EQ_(A2(A1(V)), A1(A2(V))), EQ_(U, A2(A2(V)))],
      A2(A1(V)), 'R0')

def report(name, rules, seeds=(3, 4, 5), N=3000, NF=12000):
    t0 = time.time()
    fails = rv.run_tests(law, rules, list(seeds), N, NF)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    val = [f for f in fails if f[1] != 'recursion']
    print('%-14s nrules=%d fails=%d (value %d) %s  %.1fs' % (name, len(rules), len(fails), len(val), json.dumps(kinds), time.time() - t0), flush=True)
    for s, r, kind, sd in val[:4]:
        print('   FAIL', kind, sd, {k: size(v) for k, v in s.items()}, '->', size(r) if r != 'recursion' else r, flush=True)
    return val

if __name__ == '__main__':
    report('gen24+R0', GEN + [R0])
