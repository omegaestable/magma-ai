"""For the actual failing (x,y,z) of a rule set: which accessor-path key k of y makes op k y decode,
and what does the model need at the TOP product?  usage: python gen/_v11081_key.py <setname>"""
import sys, itertools, pickle
HERE = 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, HERE); sys.path.insert(0, HERE + '/gen')
import closedform as cf
from freemodel import normalise, catalog, size
from laws import parse_eq
from _v11081_rs import SETS
law = normalise(parse_eq(catalog()[11081]))
rules = SETS[sys.argv[1] if len(sys.argv) > 1 else 'w123']
S = pickle.load(open(HERE + '/gen/_v11081_fail.pkl', 'rb'))
x, y, z = S[0]['x'], S[0]['y'], S[0]['z']
C = cf.Closed(law, rules)
a = C.op(y, x); b = C.op(x, a); c = C.op(z, y); d = C.op(b, c); r = C.op(y, d)
print('sizes x=%d y=%d z=%d  C=op(z,y) sz=%d  D sz=%d' % (size(x), size(y), size(z), size(c), size(d)))
print('C decodes:', c != ('J', z, y), ' C == a1(a1 y):', c == y[1][1], ' D free:', d == ('J', b, c))
print('TOP op(y,D) = x ?', r == x)


def acc(t, path):
    for s in path:
        if t[0] != 'J':
            return None
        t = t[1] if s == '1' else t[2]
    return t


hits = []
for L in range(1, 8):
    for path in itertools.product('12', repeat=L):
        p = ''.join(path)
        k = acc(y, p)
        if k is None:
            continue
        C2 = cf.Closed(law, rules)
        if C2.op(k, y) != ('J', k, y):
            hits.append((p, size(k), C2.op(k, y) == c, k == z))
print('accessor keys k = y.<path> with op k y decoding:  (path, sz k, result==C, k==z)')
for h in hits[:25]:
    print('  ', h)
print('total', len(hits))
zp = [''.join(p) for L in range(1, 8) for p in itertools.product('12', repeat=L) if acc(y, ''.join(p)) == z]
print('z occurs in y at:', zp[:5])
# what the TOP needs: some key k with op k D = a1(a1 D) = x
D = d
hits2 = []
for L in range(1, 8):
    for path in itertools.product('12', repeat=L):
        p = ''.join(path)
        k = acc(y, p)
        if k is None:
            continue
        C2 = cf.Closed(law, rules)
        if C2.op(k, D) == x:
            hits2.append((p, size(k)))
print('keys k = y.<path> with op k D = x:', hits2[:10], 'total', len(hits2))
