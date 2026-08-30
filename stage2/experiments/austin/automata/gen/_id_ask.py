"""Ask the forced congruence of a law about SPECIFIC candidate identities (any sizes).

python gen/_id_ask.py <eq> [base] [gens] [rounds]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _id_cong as C, _id_query as Q

def T(s):
    """parse 'a*a' style with * left-assoc only inside parens; use tuples instead."""
    raise NotImplementedError

def mk(t):
    if isinstance(t, str): return C.g('abcdefg'.index(t))
    return C.J(mk(t[0]), mk(t[1]))

CAND = [
    ("square idempotent          (u*u)*(u*u) = u*u,  u=a", (('a','a'),('a','a')), ('a','a')),
    ("square idempotent          u=a*b",               ((('a','b'),('a','b')),(('a','b'),('a','b'))), (('a','b'),('a','b'))),
    ("all squares equal          a*a = b*b",           ('a','a'), ('b','b')),
    ("idempotent                 a*a = a",             ('a','a'), 'a'),
    ("R_y constant on squares    (a*a)*a = (b*b)*a",   (('a','a'),'a'), (('b','b'),'a')),
    ("L_y constant on squares    a*(a*a) = a*(b*b)",   ('a',('a','a')), ('a',('b','b'))),
    ("sq absorb right            (a*a)*(a*a)=a",       (('a','a'),('a','a')), 'a'),
    ("R_a const on im R_a        (a*a)*a = (b*a)*a",   (('a','a'),'a'), (('b','a'),'a')),
    ("L_a const on im L_a        a*(a*a) = a*(a*b)",   ('a',('a','a')), ('a',('a','b'))),
]

def main(eq, base=3, gens=2, rounds=2):
    extra = []
    for _, l, r in CAND:
        extra.append(mk(l)); extra.append(mk(r))
    cc = Q.run(eq, base, gens, rounds, 99, extra=extra)
    print('  --- candidate identities ---')
    for name, l, r in CAND:
        a, b = mk(l), mk(r)
        ok = (a in cc.p and b in cc.p and cc.find(a) == cc.find(b))
        print('   %-42s %s' % (name, 'DERIVED' if ok else '.'))

if __name__ == '__main__':
    main(int(sys.argv[1]),
         int(sys.argv[2]) if len(sys.argv) > 2 else 3,
         int(sys.argv[3]) if len(sys.argv) > 3 else 2,
         int(sys.argv[4]) if len(sys.argv) > 4 else 2)
