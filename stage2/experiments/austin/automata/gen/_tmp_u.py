import sys
sys.path.insert(0, 'stage2/experiments/austin/automata/gen')
from _x17286_leanmirror import Mod
from _x17286_lab import terms, sz, a2, tg, J, show, g, deep, encB

M = Mod(); T = terms(7, 2)
for base in [g(0), g(1), J(g(0),g(1)), J(g(1),g(0))]:
    t = base
    for i in range(5):
        T.append(t); T.append(J(deep(5), t));
        t = encB(t, g(20+i))
        T.append(t); T.append(J(deep(5), t))
T = list(set(T)); C = []; U = []
for x in list(T):
    for w in [g(30), J(g(30),g(31)), deep(8)]:
        p2 = M.op(a2(x), w)
        T.append(encB(p2, w))
T = list(set(T))
for lvl in range(6):
    ws = [g(20+i) for i in range(lvl)]
    for pay in (g(0), J(g(0),g(1)), encB(g(0),g(1))):
        x = pay
        for w in ws: x = encB(x,w)
        for wz in (g(30), J(g(30),g(31))):
            for zl in range(3):
                z = x
                for i in range(zl+1): z = encB(z,J(wz,g(40+i)))
                T.extend([x,z,a2(x),a2(z),J(g(9),x),J(g(9),z)])
T=list(set(T))
for x in T:
    for z in T:
        if sz(x) + sz(z) > 16:
            continue
        P = M.op(x, z); v = J(z, P)
        if M.Cd(v) and tg(x) == 2 and P == a2(x):
            C.append((x, z, P))
            B = M.op(z, v)
            if tg(z) == 2 and M.op(a2(z), z) == a2(P):
                U.append((x, z, P, B))
print('cases', len(C), 'U', len(U))
print('badU', sum(B != J(z, J(z, P)) for x,z,P,B in U))
for x,z,P,B in U[:10]:
    print(show(x), show(z), show(P), show(B))
