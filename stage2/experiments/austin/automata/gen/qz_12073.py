"""Law 12073:  x = y * (((y * x) * x) * (z * z))

Carrier = inductive type with constructors  G n | P a b | D a b | C a b   (NOT the free magma).
op is non-recursive structural pattern matching.

Chain intent:  op(y,x)=P y x ; op(P y x, x)=D x y ; op(D x y, S)=C x y ; op(y, C x y)=x.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qz_lib as L

CT = ('P', 'D', 'C')


def op(u, v):
    # R1 decode
    if v[0] == 'C' and v[2] == u:
        return v[1]
    # R2 the second chain product
    if u[0] == 'P' and u[2] == v:
        return ('D', v, u[1])
    # R3 the third chain product
    if u[0] == 'D':
        return ('C', u[1], u[2])
    return ('P', u, v)


if __name__ == '__main__':
    law, txt = L.law_of(12073)
    print('law', txt, law)
    n, pool, fails = L.exhaustive(op, law, 5, 1, CT)
    print('exh 5/1', n, 'pool', len(pool), 'fails', len(fails))
    for s, r in fails[:5]:
        print('  FAIL', {k: L.show(v) for k, v in s.items()}, '->', L.show(r))
    if not fails:
        n, pool, fails = L.exhaustive(op, law, 7, 1, CT)
        print('exh 7/1', n, 'pool', len(pool), 'fails', len(fails))
        for s, r in fails[:5]:
            print('  FAIL', {k: L.show(v) for k, v in s.items()}, '->', L.show(r))
