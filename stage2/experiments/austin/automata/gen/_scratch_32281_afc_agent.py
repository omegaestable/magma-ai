"""Fast exact-model falsifier for the proposed 32281 conditional AF cell.

Terms are hash-consed integer DAG nodes, avoiding the repr-key bottleneck in
_x32281_leanmirror.py.  This is scratch evidence, not a certificate.
"""
from __future__ import annotations

import random

tag: list[int] = []
aa: list[int] = []
bb: list[int] = []
ss: list[int] = []
nodes: dict[tuple[int, int, int], int] = {}


def node(t: int, a: int, b: int) -> int:
    k = (t, a, b)
    q = nodes.get(k)
    if q is not None:
        return q
    q = len(tag)
    nodes[k] = q
    tag.append(t)
    aa.append(a)
    bb.append(b)
    ss.append(1 if t == 1 else ss[a] + ss[b] + 1)
    return q


def G(n: int) -> int:
    return node(1, n, n)


def J(a: int, b: int) -> int:
    return node(2, a, b)


def a1(t: int) -> int:
    return aa[t] if tag[t] == 2 else t


def a2(t: int) -> int:
    return bb[t] if tag[t] == 2 else t


def msr(u: int, v: int) -> int:
    m = max(ss[u], ss[v])
    return m * m + ss[u] + ss[v]


def p1(u: int, v: int) -> bool:
    return (tag[v] == 2 and tag[a1(v)] == 2 and u == a1(a1(v))
            and tag[a2(a1(v))] == 2 and tag[a1(a2(a1(v)))] == 2
            and a2(a1(a2(a1(v)))) == a2(a2(a1(v)))
            and a2(a1(a2(a1(v)))) == a2(v))


def p2(_u: int, v: int) -> bool:
    return tag[v] == 2 and tag[a2(v)] == 2 and tag[a1(a2(v))] == 2


def p3(_u: int, v: int) -> bool:
    return (tag[v] == 2 and tag[a2(v)] == 2 and tag[a2(a2(v))] == 2
            and tag[a1(a2(a2(v)))] == 2)


memo: dict[tuple[int, int], int] = {}
prod: dict[tuple[int, int], str] = {}


def op(u: int, v: int) -> int:
    k = (u, v)
    q = memo.get(k)
    if q is not None:
        return q
    m = msr(u, v)
    free = J(u, v)
    w = a2(v)
    h1 = msr(a1(a1(w)), w) < m
    q1 = op(a1(a1(w)), w) if h1 else free
    h2 = msr(q1, w) < m
    q2 = op(q1, w) if h2 else free
    h3 = msr(u, q2) < m
    q3 = op(u, q2) if h3 else free
    ww = a2(w)
    h4 = msr(a1(a1(ww)), ww) < m
    q4 = op(a1(a1(ww)), ww) if h4 else free
    h5 = msr(q4, ww) < m
    q5 = op(q4, ww) if h5 else free
    h6 = msr(a1(w), q5) < m
    q6 = op(a1(w), q5) if h6 else free
    h7 = msr(u, q6) < m
    q7 = op(u, q6) if h7 else free
    h8 = msr(u, J(q7, q5)) < m
    q8 = op(u, J(q7, q5)) if h8 else free
    h9 = msr(q8, w) < m
    q9 = op(q8, w) if h9 else free
    h10 = msr(q9, w) < m
    q10 = op(q9, w) if h10 else free
    h11 = msr(u, q10) < m
    q11 = op(u, q10) if h11 else free
    if p1(u, v):
        q, r = a1(a1(a2(a1(v)))), "R1"
    elif p2(u, v) and h1 and h2 and h3 and a1(v) == q3:
        q, r = a1(a1(w)), "R2"
    elif p3(u, v) and h4 and h5 and h6 and h7 and h8 and h9 and h10 and h11 and a1(v) == q11:
        q, r = q8, "R3"
    else:
        q, r = free, "F"
    memo[k] = q
    prod[k] = r
    return q


GS = [G(i) for i in range(8)]


def enc(u: int, p: int, w: int) -> int:
    return J(J(u, J(J(p, w), w)), w)


def openc(u: int, p: int, w: int) -> int:
    return J(op(u, op(op(p, w), w)), w)


def r3enc(u: int, w: int) -> int:
    """Choose the header making R3's final equality tautological.

    Whether R3 actually wins still depends on P3, all eight strict gates, and
    the priority failures of R1/R2; callers inspect the recorded producer.
    """
    ww = a2(w)
    q4 = op(a1(a1(ww)), ww)
    q5 = op(q4, ww)
    q6 = op(a1(w), q5)
    q7 = op(u, q6)
    q8 = op(u, J(q7, q5))
    q9 = op(q8, w)
    q10 = op(q9, w)
    q11 = op(u, q10)
    return J(q11, w)


def rnd(rng: random.Random, d: int) -> int:
    if d <= 0 or rng.random() < .40:
        return rng.choice(GS)
    choice = rng.randrange(4)
    if choice == 0:
        return J(rnd(rng, d - 1), rnd(rng, d - 1))
    if choice <= 2:
        return enc(rnd(rng, d - 1), rnd(rng, d - 1), rnd(rng, d - 1))
    return openc(rnd(rng, d - 1), rnd(rng, d - 1), rnd(rng, d - 1))


def inspect(x: int, y: int, z: int, counts: dict[tuple[str, ...], int]) -> bool:
    p = op(x, y)
    if p == J(x, y):
        return False
    w = a2(y)
    c = op(op(p, w), w)
    d = op(x, c)
    if not (msr(x, c) < msr(x, y) and a1(y) == d and d != J(x, c)):
        return False
    q = op(p, y)
    a = op(z, q)
    if not counts:
        k0 = op(p, w)
        print("first cell sizes x y z p q a c d b",
              [ss[t] for t in (x, y, z, p, q, a, c, d, w)],
              "k", ss[k0], "prod", prod[(x, y)], prod[(p, w)],
              prod[(k0, w)], prod[(x, c)], prod[(p, y)], prod[(z, q)])
    key = (prod[(x, y)], prod[(x, c)], prod[(p, y)], prod[(z, q)])
    counts[key] = counts.get(key, 0) + 1
    if a != J(z, q):
        print("BAD", [ss[t] for t in (x, y, z, p, q, a, c)],
              prod[(x, y)], prod[(p, y)], prod[(z, q)])
        return True
    return False


def main() -> None:
    rng = random.Random(32281)
    counts: dict[tuple[str, ...], int] = {}
    cells = 0
    # Adversarial fixed-result attack: force the R2 output P=a1(a1(b))
    # to equal x.  Then Q=op(P,y) would repeat P by first-argument
    # functionality, and choosing x as a z-encoding would refute AFc if all
    # cell gates could coexist.
    fixed_cells = 0
    for _ in range(30000):
        z0 = rnd(rng, 1)
        x = enc(z0, rnd(rng, 1), rnd(rng, 1))
        b = J(J(x, rnd(rng, 2)), rnd(rng, 2))
        c = op(op(x, b), b)
        d = op(x, c)
        y = J(d, b)
        if op(x, y) == x and d != J(x, c):
            fixed_cells += 1
            if inspect(x, y, z0, counts):
                print("fixed attack succeeded after", fixed_cells, "cells")
                return
    print("fixed-result candidate cells", fixed_cells)
    direct_r2_cells = 0
    for _ in range(50000):
        x, z0 = rnd(rng, 1), rnd(rng, 1)
        # P2 only needs b and a1(b) to be constructors.  Bias b toward the
        # recursive encodings that can make D=op(x,C) decoded.
        b = enc(rnd(rng, 2), rnd(rng, 2), rnd(rng, 2))
        p = a1(a1(b))
        c = op(op(p, b), b)
        d = op(x, c)
        y = J(d, b)
        if op(x, y) != J(x, y) and prod[(x, y)] == "R2" and d != J(x, c):
            direct_r2_cells += 1
            if inspect(x, y, z0, counts):
                print("direct R2 attack succeeded after", direct_r2_cells, "cells")
                return
    print("direct R2 candidate cells", direct_r2_cells)
    r3made = 0
    for i in range(60000):
        if i % 6 == 0:
            # Exact lift used by _x32281_cellgen: an AF counterexample one
            # level down supplies a decoded guard for the new pair.
            z0, r, w, v = (rnd(rng, 1) for _ in range(4))
            q0 = enc(z0, r, w)
            x0, y0 = q0, enc(q0, q0, v)
            q = op(op(x0, y0), y0)
            a = op(z0, q)
            s = op(a, y0)
            x, y, z = z0, s, rnd(rng, 1)
        elif i % 6 == 1:
            # Same lift, but make its decoded guard be an R2 result.  Taking
            # x0=q0 and y0=enc(q0,q0,v) fixes both first chain products at q0.
            z0, v = rnd(rng, 1), rnd(rng, 1)
            w = enc(rnd(rng, 1), rnd(rng, 1), rnd(rng, 1))
            q0 = openc(z0, rnd(rng, 1), w)
            x0, y0 = q0, enc(q0, q0, v)
            q = op(op(x0, y0), y0)
            a = op(z0, q)
            s = op(a, y0)
            x, y, z = z0, s, rnd(rng, 1)
        elif i % 6 == 2:
            # The *top* of the first lifted cell is an actual R3 decoding.
            # Use that whole right parameter in the payload==decoder AF
            # constructor and lift again, forcing the new guard decoder to R3.
            z0, z2, r, w, v0, v1 = (rnd(rng, 1) for _ in range(6))
            base = enc(z0, r, w)
            y0 = enc(base, base, v0)
            q0 = op(op(base, y0), y0)
            a0 = op(z0, q0)
            s0 = op(a0, y0)
            p1v = op(z0, s0)
            q1v = op(p1v, s0)
            a1v = op(z2, q1v)
            r3right = op(a1v, s0)
            y1 = enc(r3right, r3right, v1)
            q1 = op(op(r3right, y1), y1)
            a2v = op(z2, q1)
            s1 = op(a2v, y1)
            x, y, z = z2, s1, rnd(rng, 1)
        elif i % 6 == 3:
            x, y, z = rnd(rng, 2), rnd(rng, 2), rnd(rng, 1)
        elif i % 6 == 4:
            x, w, z = rnd(rng, 1), rnd(rng, 1), rnd(rng, 1)
            y = openc(x, rnd(rng, 1), w)
        else:
            x, z = rnd(rng, 1), rnd(rng, 1)
            # P3 wants w and its right child to be constructors.  A free
            # encoding is a compact source of such separators.
            w = enc(rnd(rng, 1), rnd(rng, 1), rnd(rng, 1))
            y = r3enc(x, w)
            if op(x, y) != J(x, y) and prod[(x, y)] == "R3":
                r3made += 1
        before = sum(counts.values())
        if inspect(x, y, z, counts):
            return
        cells += sum(counts.values()) - before
    print("cells", cells, "bad 0", "r3 products", r3made,
          "producer census", sorted(counts.items()))
    print("terms", len(tag), "op-pairs", len(memo))


if __name__ == "__main__":
    main()
