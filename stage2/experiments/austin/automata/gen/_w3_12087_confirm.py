import sys, os, json
D = r'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata'
sys.path.insert(0, D); sys.path.insert(0, os.path.join(D, 'gen'))
import closedform as cf, closedform2 as cf2
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
EQ = 12087
law = normalise(parse_eq(catalog()[EQ]))
R1 = cf.Extractor(law).rules(exist=False)
S7 = [R1[i] for i in [0,1,2,3,5,8,10]]
R2, _ = cf2.extract(law)
d = json.load(open(os.path.join(D, 'gen', '_w3_12087_deep3_bad.json')))
y, x, z = [tuple_of for tuple_of in (None,)] and None, None, None
def T(o):
    return ('g', o[1]) if o[0] == 'g' else ('J', T(o[1]), T(o[2]))
y, x, z = T(d['y']), T(d['x']), T(d['z'])
print('sizes y=%d x=%d z=%d' % (size(y), size(x), size(z)))
def chain(C, tag):
    N1 = C.op(y, x); N2 = C.op(N1, z); N3 = C.op(x, z); V = C.op(N2, N3); R = C.op(y, V)
    fr = lambda u, v: C.op(u, v) == ('J', u, v)
    print('%-10s N1=%s N2=%s N3=%s V=%s  op(x,N3)=%s  RESULT==x : %s  cycles=%d' % (
        tag, 'F' if fr(y,x) else 'D', 'F' if fr(N1,z) else 'D', 'F' if fr(x,z) else 'D',
        'F' if fr(N2,N3) else 'D', 'F' if fr(x,N3) else 'D', R == x, getattr(C, 'cycles', -1)))
    return R == x
for tag, rr in (('S7', S7), ('full13', R1), ('cf2_11', R2)):
    chain(cf.Closed(law, rr), tag)
# the SEMANTIC free model
try:
    F = fm.Free(law)
    def ev(p, s):
        if isinstance(p, str): return s[p]
        return F.op(ev(p[0], s), ev(p[1], s))
    s = {'x': x, 'y': y, 'z': z}
    r = ev(law[1], s)
    print('semantic free model: RESULT==x :', r == x, ' cycles=', getattr(F, 'cycles', -1))
except Exception as e:
    print('semantic free model: ERROR', type(e).__name__, e)
