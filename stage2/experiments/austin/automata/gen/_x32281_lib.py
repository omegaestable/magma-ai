"""Shared helpers for law 32281 (dualised L-form: x = y * ((y * ((x*z)*z)) * z))."""
import sys, os
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE)
import closedform as cf, revalidate as rv, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 32281
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
LAW = ('x', leangen.dual_pat(orig[1])) if dualized else orig

U = ('U',)
V = ('V',)
def A1(e): return ('A1', e)
def A2(e): return ('A2', e)
def OP(a, b): return ('OP', a, b)
def JJ(a, b): return ('J', a, b)
def TG(e): return ('TG', e)
def EQ_(a, b): return ('EQ', a, b)
def OPEQ(a, b): return ('OPEQ', a, b)

def gen_rules():
    src = open(os.path.join(HERE, 'gen', 'chk%d.py' % EQ), encoding='utf-8').read().split('C = cf.Closed')[0]
    ns = {}
    exec(src, ns)
    return ns['rules']

def report(law, rules, seeds=(3, 4, 5), N=3000, NF=12000, tag=''):
    import time
    t0 = time.time()
    fails = rv.run_tests(law, rules, list(seeds), N, NF)
    kinds = {}
    for s, r, kind, sd in fails:
        k = ('recursion' if r == 'recursion' else 'value') + ':' + kind
        kinds[k] = kinds.get(k, 0) + 1
    real = [f for f in fails if f[1] != 'recursion']
    print('%s nrules=%d fails=%d real=%d %s  %.1fs' % (tag, len(rules), len(fails), len(real), kinds, time.time() - t0), flush=True)
    return fails, real
