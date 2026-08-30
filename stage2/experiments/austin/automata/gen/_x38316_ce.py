"""Verify the recorded 38316 counterexample in the SEMANTIC free model and in rule sets."""
import sys, os
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
print('L-form law:', law)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))

z = g(2)
y = J(g(0), J(J(g(2), J(g(1), g(0))), g(2)))
x = J(J(y, J(g(3), g(2))), y)
print('x =', sh(x)); print('y =', sh(y)); print('z =', sh(z))

def run(opf, tag):
    try:
        a = opf(z, x); b = opf(y, a); c = opf(b, y); d = opf(x, c); top = opf(y, d)
    except RecursionError:
        print(tag, 'RECURSION'); return
    print('%-14s a=%-4d b=%-4d c=%-4d d=%-4d top=%-4d ok=%s' % (tag, size(a), size(b), size(c), size(d), size(top), top == x))
    if top != x:
        print('   b =', sh(b) if size(b) < 60 else '<big %d>' % size(b))
        print('   c =', sh(c) if size(c) < 60 else '<big %d>' % size(c))
        print('   top=', sh(top) if size(top) < 90 else '<big %d>' % size(top))

M = fm.Free(law)
run(M.op, 'SEMANTIC')

GEN = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/'
src = open(GEN + 'chkrep38316.py', encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
run(cf.Closed(law, ALL).op, 'REP10')
run(cf.Closed(law, [r for r in ALL if r[2].startswith('V0')]).op, 'V0-5')
