"""MECHANICAL CHECK of the derivation   22591  |-   a = I3(a)

Law 22591 (L-form as modelled):   x = (y*(y*x)) * ((x*x)*z)

    T  := a*a
    I1 := T*(T*a)
    I2 := a*(a*I1)
    I3 := I1*(I1*I2)
    Y  := b*(b*I2)                    (b any element; it cancels)

  (1) L[x:=a,  y:=T,  z:=T*a ]   is literally   a  = I1 * (T*(T*a))          ->  a  = I1*I1
  (2) L[x:=I1, y:=a,  z:=a*I1]   is literally   I1 = I2 * ((I1*I1)*(a*I1))   ->  I1 = I2*I2   [by (1)]
  (3) L[x:=I2, y:=I1, z:=I1*I2]  is literally   I2 = I3 * ((I2*I2)*(I1*I2))  ->  I2 = I3*I3   [by (2)]
  (4) L[x:=I2, y:=b,  z:=I1   ]  is literally   I2 = Y * ((I2*I2)*I1)        ->  I2 = Y*a     [by (2),(1)]
  (5) L[x:=I2, y:=b,  z:=I1*I2]  is literally   I2 = Y * ((I2*I2)*(I1*I2))   ->  I2 = Y*I3    [by (2)]
  (6) L[x:=a,  y:=Y,  z:=T*a ]   is literally   a  = (Y*(Y*a)) * ((a*a)*(T*a))
                                                                             ->  a  = (Y*I2)*I1  [by (4)]
  (7) L[x:=I3, y:=Y,  z:=I2  ]   is literally   I3 = (Y*(Y*I3)) * ((I3*I3)*I2)
                                                                             ->  I3 = (Y*I2)*I1  [by (5),(3),(2)]
  (6)+(7):   a = I3.

Every step is a substitution instance of the law plus replacement of a subterm by an
already-derived equal.  NO freeness of any product is assumed, so the conclusion holds in EVERY
magma satisfying 22591.

usage: python gen/_p2_ident22591.py
"""
import sys
sys.setrecursionlimit(10000)


def M(a, b):
    return ('*', a, b)


def show(t):
    return t if isinstance(t, str) else '(%s*%s)' % (show(t[1]), show(t[2]))


def sz(t):
    return 1 if isinstance(t, str) else 1 + sz(t[1]) + sz(t[2])


def subst(t, s):
    if isinstance(t, str):
        return s.get(t, t)
    return ('*', subst(t[1], s), subst(t[2], s))


def rw(t, a, b):
    """replace every occurrence of the subterm a by b (innermost-out)"""
    if t == a:
        return b
    if isinstance(t, str):
        return t
    r = ('*', rw(t[1], a, b), rw(t[2], a, b))
    return b if r == a else r


# law 22591 : x = (y*(y*x)) * ((x*x)*z)
RHS = M(M('y', M('y', 'x')), M(M('x', 'x'), 'z'))

a, b = 'a', 'b'
T = M(a, a)
I1 = M(T, M(T, a))
I2 = M(a, M(a, I1))
I3 = M(I1, M(I1, I2))
Y = M(b, M(b, I2))
print('T  =', show(T))
print('I1 =', show(I1))
print('I2 =', show(I2))
print('I3 =', show(I3), ' (size %d)' % sz(I3))
print('Y  =', show(Y))
print()

DERIVED = []          # list of (lhs, rhs) already proved equal


def step(n, sub, note, rewrites, want):
    """instantiate the law, apply the listed rewrites, assert the result is `want`."""
    t = subst(RHS, sub)
    print('(%d) L[%s]' % (n, ', '.join('%s:=%s' % (k, show(v)) for k, v in sub.items())))
    print('      %s = %s' % (show(sub['x']), show(t)))
    for (src, dst, why) in rewrites:
        t2 = rw(t, src, dst)
        if t2 != t:
            print('      rewrite %s -> %s   [%s]' % (show(src), show(dst), why))
        t = t2
    assert t == want, 'STEP %d\n  got  %s\n  want %s' % (n, show(t), show(want))
    print('      => %s = %s   %s' % (show(sub['x']), show(want), note))
    DERIVED.append((sub['x'], want))
    print()
    return want


# (1)  a = I1 * I1
step(1, {'x': a, 'y': T, 'z': M(T, a)}, '[every element is a square, constructively]',
     [], M(I1, I1))

# (2)  I1 = I2 * I2       (needs I1*I1 = a from (1))
step(2, {'x': I1, 'y': a, 'z': M(a, I1)}, '',
     [(M(I1, I1), a, 'by (1)')], M(I2, I2))

# (3)  I2 = I3 * I3       (needs I2*I2 = I1 from (2))
step(3, {'x': I2, 'y': I1, 'z': M(I1, I2)}, '',
     [(M(I2, I2), I1, 'by (2)')], M(I3, I3))

# (4)  I2 = Y * a         (needs I2*I2 = I1 and I1*I1 = a)
step(4, {'x': I2, 'y': b, 'z': I1}, '',
     [(M(I2, I2), I1, 'by (2)'), (M(I1, I1), a, 'by (1)')], M(Y, a))

# (5)  I2 = Y * I3        (needs I2*I2 = I1)
step(5, {'x': I2, 'y': b, 'z': M(I1, I2)}, '',
     [(M(I2, I2), I1, 'by (2)')], M(Y, I3))

# (6)  a = (Y*I2) * I1    (needs Y*a = I2 from (4))
step(6, {'x': a, 'y': Y, 'z': M(T, a)}, '',
     [(M(Y, a), I2, 'by (4)')], M(M(Y, I2), I1))

# (7)  I3 = (Y*I2) * I1   (needs Y*I3 = I2, I3*I3 = I2, I2*I2 = I1)
step(7, {'x': I3, 'y': Y, 'z': I2}, '',
     [(M(Y, I3), I2, 'by (5)'), (M(I3, I3), I2, 'by (3)'), (M(I2, I2), I1, 'by (2)')],
     M(M(Y, I2), I1))

print('=' * 78)
print('(6) and (7) have the same right-hand side, so 22591 |-')
print()
print('    a  =  %s' % show(I3))
print()
print('with I1 = (a*a)*((a*a)*a),  I2 = a*(a*I1).   size 1 vs size %d.' % sz(I3))
print('These are DISTINCT terms of the free magma, so 22591 has NO model whose carrier is the')
print('free term algebra -- no rule system, tag automaton or extractor repair can exist for it.')
