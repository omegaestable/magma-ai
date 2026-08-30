"""semantic-free-model verdict on named instances of 21864"""
import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import freemodel as fm
from freemodel import normalise, catalog, size
from laws import parse_eq
import trace as TR

show = TR.show
cat = catalog()
law = normalise(parse_eq(cat[21864]))
A, B = law[1]


def p(s):
    """parse '(g0*(g0*g0))' -> term"""
    s = s.replace(' ', '')
    pos = [0]

    def rd():
        if s[pos[0]] == '(':
            pos[0] += 1
            a = rd()
            assert s[pos[0]] == '*'
            pos[0] += 1
            b = rd()
            assert s[pos[0]] == ')'
            pos[0] += 1
            return ('J', a, b)
        assert s[pos[0]] == 'g'
        pos[0] += 1
        n = ''
        while pos[0] < len(s) and s[pos[0]].isdigit():
            n += s[pos[0]]; pos[0] += 1
        return ('g', int(n))
    return rd()


CASES = [
    ('(g0*((g0*g0)*g0))', '((g0*(g0*g0))*g0)', '((g0*(g0*g0))*g0)'),
    ('((g0*(g0*g0))*g0)', '(g0*(g0*g0))', 'g0'),
    ('(g0*(g0*g0))', '((g0*(g0*g0))*g0)', '((g0*(g0*g0))*g0)'),
    ('((g0*(g0*g0))*g0)', '((g0*(g0*g0))*g0)', '((g0*(g0*g0))*g0)'),
]
for ys, zs, xs in CASES:
    s = {'y': p(ys), 'z': p(zs), 'x': p(xs)}
    F = fm.Free(law)

    def evs(q):
        if isinstance(q, str):
            return s[q]
        return F.op(evs(q[0]), evs(q[1]))
    r = F.op(evs(A), evs(B))
    print('y=%-22s z=%-20s x=%-20s ->' % (ys, zs, xs),
          'HOLDS' if r == s['x'] else 'FAILS got ' + (show(r) if size(r) < 60 else '<%d>' % size(r)),
          '| conflicts', len(F.conflicts), 'cycles', F.cycles, 'cuts', F.cuts)
    print('     A =', show(evs(A)) if size(evs(A)) < 60 else '<%d>' % size(evs(A)),
          ' B =', show(evs(B)) if size(evs(B)) < 60 else '<%d>' % size(evs(B)))
