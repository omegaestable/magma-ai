"""Trace the 2 semantic failures of 34889 in the SEMANTIC free model, step by step."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import freemodel as fm
from freemodel import normalise, catalog, pvars, size
from laws import parse_eq

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))

def T(s):
    # parse "(g0*g0)" style
    s = s.strip()
    if s.startswith('g'): return ('g', int(s[1:]))
    assert s[0] == '(' and s[-1] == ')'
    d = 0
    for i in range(1, len(s)-1):
        if s[i] == '(': d += 1
        elif s[i] == ')': d -= 1
        elif s[i] == '*' and d == 0:
            return ('J', T(s[1:i]), T(s[i+1:-1]))
    raise ValueError(s)

EQ = 34889
cat = catalog()
orig = normalise(parse_eq(cat[EQ]))
dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
law = ('x', dual_pat(orig[1])) if dualized else orig
print('orig  ', orig)
print('law(L)', law, 'dualized', dualized)
F = fm.Free(law)

def op(a, b):
    r = F.op(a, b)
    print('   op(%s, %s) = %s   %s' % (show(a), show(b), show(r),
          'FREE' if r == ('J', a, b) else 'DECODE'))
    return r

for inst in [{'y': 'g0', 'x': '(g0*g0)', 'z': '(g0*((g0*g0)*g0))'},
             {'y': '(g0*g0)', 'x': '(g0*g0)', 'z': '(g0*((g0*g0)*g0))'},
             {'y': 'g0', 'x': '(g0*g0)', 'z': 'g0'},
             {'y': 'g0', 'x': '(g0*(g0*g0))', 'z': '((g0*g0)*((g0*(g0*g0))*(g0*g0)))'}]:
    s = {k: T(v) for k, v in inst.items()}
    print('--- instance', inst)
    # L-form eval:  x = z * ((x * (z * x)) * (y * y))
    zx = op(s['z'], s['x'])
    B = op(s['x'], zx)
    C = op(s['y'], s['y'])
    D = op(B, C)
    R = op(s['z'], D)
    print('   RESULT', show(R), 'EXPECTED', show(s['x']), 'OK' if R == s['x'] else '*** FAIL')
print(json.dumps(dict(conflicts=len(F.conflicts), cycles=F.cycles, bail=F.bail, rbail=F.rbail,
                      spurious=F.spurious, unverified=F.unverified, cuts=F.cuts, tainted=F.tainted)))
for u, v, xs in F.conflicts[:5]:
    print('CONFLICT', show(u), show(v), [show(x) for x in xs])
