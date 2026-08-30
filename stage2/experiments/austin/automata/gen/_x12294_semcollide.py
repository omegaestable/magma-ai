"""Is the collision real in the SEMANTIC free model (freemodel.Free) of 12294?

If  s4(x1,y,z1) = s4(x2,y,z2)  with x1 != x2  then no magma whose products evaluate that way can satisfy
x = y*(((z*y)*x)*(x*y)):  op(y, s4) would have to be both x1 and x2.
"""
import sys
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
import freemodel as fm
from freemodel import normalise, catalog
from laws import parse_eq
import smallcheck as sc

law = normalise(parse_eq(catalog()[12294]))
A, B = law[1]


def show(t):
    return 'g%d' % t[1] if t[0] == 'g' else '(%s*%s)' % (show(t[1]), show(t[2]))


g = lambda i: ('g', i)
J = lambda a, b: ('J', a, b)
a = g(0)
y = J(J(a, a), a)
aa = J(a, a)
x1 = J(y, aa); z1 = J(aa, aa)
x2 = J(J(y, a), aa); z2 = J(y, aa)

F = fm.Free(law)
print('y  =', show(y))
for nm, x, z in (('x1', x1, z1), ('x2', x2, z2)):
    s = {'x': x, 'y': y, 'z': z}

    def ev(p):
        if isinstance(p, str):
            return s[p]
        return F.op(ev(p[0]), ev(p[1]))
    s1 = F.op(z, y)
    s2 = F.op(s1, x)
    s3 = F.op(x, y)
    s4 = F.op(s2, s3)
    top = F.op(y, s4)
    print('%s = %s   z = %s' % (nm, show(x), show(z)))
    print('   op(a,x)  =', show(F.op(a, x)))
    print('   s1 = op(z,y) =', show(s1))
    print('   s2 = op(s1,x) =', show(s2))
    print('   s3 = op(x,y) =', show(s3))
    print('   s4 =', show(s4))
    print('   op(y,s4) =', show(top), '   expected', show(x))
print('conflicts recorded by Free:', len(F.conflicts), 'cuts', F.cuts, 'rcycles', F.rcycles)

# exhaustive collision scan in the semantic model
pool = sc.terms_upto(9, 1)
F2 = fm.Free(law)
hits = 0
shown = 0
for yy in pool:
    seen = {}
    for xx in pool:
        for zz in pool:
            try:
                s1 = F2.op(zz, yy); s2 = F2.op(s1, xx); s3 = F2.op(xx, yy); s4 = F2.op(s2, s3)
            except RecursionError:
                continue
            prev = seen.get(s4)
            if prev is None:
                seen[s4] = (xx, zz)
            elif prev[0] != xx:
                hits += 1
                if shown < 4:
                    shown += 1
                    print('SEM COLLISION y=%s  x1=%s x2=%s  s4=%s' % (show(yy), show(prev[0]), show(xx), show(s4)))
print('semantic collisions (size<=9, 1 generator):', hits)
