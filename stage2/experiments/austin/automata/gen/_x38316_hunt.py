"""Hunt for instances of law 38316 where the chain product c = op(b,y) (or d = op(x,c)) DECODES.

Derived necessary conditions (from the I2 invariant a2 (a2 v) = u on every decoding pair):
  c = op(b,y) decodes  =>  a2 (a2 y) = b  and (since b = op(y,a) must then be smaller than y) b decodes,
                           so b = a1 a and a2 (a2 a) = y.
Construction:  z, y1, W3, A1 free; W2 = J W3 y1 ; w = J z W2 ; y = J y1 (J w z) ;
               A = J A1 z ; q = J y A ; x = J q y.
"""
import sys, os, itertools
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import closedform as cf, leangen
from freemodel import normalise, catalog, size
from laws import parse_eq

EQ = 38316
cat = catalog(); orig = normalise(parse_eq(cat[EQ]))
law = ('x', leangen.dual_pat(orig[1]))
src = open('c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/gen/chkrep38316.py',
           encoding='utf-8').read().split('C = cf.Closed')[0]
ns = {}; exec(src, ns); ALL = ns['rules']
sel = sys.argv[1] if len(sys.argv) > 1 else 'V0-W1-q0,V0-W1-q1,V0-W2,V0-W3-q0,V0-W3-q1'
RULES = ALL if sel == 'all' else [r for r in ALL if r[2] in sel.split(',')]
TAGS = [r[2] for r in RULES]
C = cf.Closed(law, RULES)
print('rules', TAGS)

def J(a, b): return ('J', a, b)
def g(n): return ('g', n)
def sh(t): return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (sh(t[1]), sh(t[2]))
def which(u, v):
    for i, (conds, xx, tag) in enumerate(C.rules):
        if C.check(conds, u, v) and C.ev(xx, u, v) is not None:
            return i
    return -1

G = [g(i) for i in range(5)]
found = 0
for z, y1, W3, A1 in itertools.product(G, repeat=4):
    W2 = J(W3, y1)
    w = J(z, W2)
    y = J(y1, J(w, z))
    A = J(A1, z)
    q = J(y, A)
    x = J(q, y)
    try:
        a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
    except RecursionError:
        continue
    pat = (which(z, x), which(y, a), which(b, y), which(x, c), which(y, d))
    if pat[2] != -1 or pat[3] != -1 or top != x:
        found += 1
        if found <= 6:
            print('HIT pat=%s law_ok=%s' % (pat, top == x))
            print('  z=%s y1=%s W3=%s A1=%s' % (sh(z), sh(y1), sh(W3), sh(A1)))
            print('  x=%s' % sh(x)); print('  y=%s' % sh(y))
            print('  a=%s' % sh(a)); print('  b=%s' % sh(b)); print('  c=%s' % sh(c))
print('hits', found)

# report what actually happens on the first construction
z, y1, W3, A1 = g(2), g(0), g(1), g(3)
W2 = J(W3, y1); w = J(z, W2); y = J(y1, J(w, z)); A = J(A1, z); q = J(y, A); x = J(q, y)
a = C.op(z, x); b = C.op(y, a); c = C.op(b, y); d = C.op(x, c); top = C.op(y, d)
print('--- reference construction ---')
print('x   =', sh(x)); print('y   =', sh(y)); print('z   =', sh(z))
print('a=op(z,x) rule', which(z, x), '=', sh(a))
print('b=op(y,a) rule', which(y, a), '=', sh(b))
print('c=op(b,y) rule', which(b, y), '=', sh(c))
print('d=op(x,c) rule', which(x, c), '=', sh(d))
print('top       rule', which(y, d), '=', sh(top), ' ok', top == x)
