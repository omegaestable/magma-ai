"""Targeted census for the direct-U branch in `_x17286_mut.lean:F2`.

This imports the receipt-scanning mirror and records whether the problematic
branch is reachable, whether F2 fails there, and whether the parent/right-child
collision forced by any decoded outer result actually occurs.
"""
import itertools

import _s10_17286_receipt_scan as rec


g, J, tg, a1, a2, sz = rec.g, rec.J, rec.tg, rec.a1, rec.a2, rec.sz


def terms(max_size, generators):
    by_size = {1: [g(i) for i in range(generators)]}
    for n in range(3, max_size + 1, 2):
        layer = []
        for left_size in range(1, n - 1, 2):
            right_size = n - left_size - 1
            for left in by_size.get(left_size, []):
                for right in by_size.get(right_size, []):
                    layer.append(J(left, right))
        by_size[n] = layer
    return [term for n in sorted(by_size) for term in by_size[n]]


def cd(v):
    return tg(v) == 2 and tg(a2(v)) == 2 and a1(v) == a1(a2(v))


def run():
    pool = terms(7, 2)
    direct_pool = terms(9, 2)
    m = rec.Mod()
    direct = 0
    f2_bad = []
    collisions = []
    # In this branch p = a2(x) and a1(p) = z, so p = J(z,r).  The
    # irrelevant first child of x can be fixed to one atom.
    for z, r in itertools.product(direct_pool, repeat=2):
        if not cd(z) or sz(z) + sz(r) > 17:
            continue
        p = J(z, r)
        x = J(g(99), p)
        if m.op(x, z) != p:
            continue
        direct += 1
        q = m.op(z, J(z, p))
        if q != J(z, J(z, p)):
            f2_bad.append((x, z, p, q))
    for s, r, w in itertools.product(pool, repeat=3):
        if sz(s) + sz(r) + sz(w) > 17:
            continue
        p = J(s, r)
        if m.op(p, w) == m.op(r, w):
            collisions.append((s, r, w, m.op(r, w)))
            if len(collisions) >= 20:
                break
    print("pool", len(pool), "direct_pool", len(direct_pool), "direct", direct, "f2_bad", len(f2_bad),
          "collisions", len(collisions), "branches", dict(sorted(m.fired.items())))
    for row in f2_bad[:3]:
        print("F2_BAD", row)
    for row in collisions[:3]:
        print("COLLISION", row)

    # Hand-forced direct-U control: op (J(z,r)) w = r because w codes the
    # free cell op r t = J(r,t).
    r, t = g(7), g(8)
    w = J(t, J(t, J(r, t)))
    z = J(w, J(w, r))
    p = J(z, r)
    x = J(g(9), p)
    got_p = m.op(x, z)
    got_f2 = m.op(z, J(z, got_p))
    print("forced_direct", got_p == p, "forced_f2", got_f2 == J(z, J(z, p)),
          "sizes", tuple(map(sz, (r, w, z, p))))


def counterfamily():
    """Independent check of the ambient-size-gate counterfamily."""
    C = lambda w, p: J(w, J(w, p))
    s, a, c, q, b = (g(i) for i in range(5))
    t0 = J(J(J(J(g(5), g(6)), g(7)), g(8)), g(9))
    t = J(t0, g(10))
    A = J(a, s)
    k = C(t, J(s, t))
    x = C(k, s)
    R = a2(x)
    h = C(c, J(s, c))
    w = C(h, s)
    P = C(w, R)
    z = C(q, J(P, q))
    y = J(b, A)
    m = rec.Mod()
    cells = {
        "Ak": (m.op(A, k), s),
        "yx": (m.op(y, x), A),
        "Rh": (m.op(R, h), s),
        "xw": (m.op(x, w), R),
        "xz": (m.op(x, z), P),
    }
    Q = m.op(z, P)
    B = m.op(z, Q)
    top = m.op(A, B)
    receipt = J(a1(R), R)
    # At T=R, final find(A,P,z,P) considers exactly this receipt.
    receipt_pair_gate = sz(receipt) + sz(z) < sz(A) + 2 * sz(z) + sz(R) + 2
    receipt_payload_gate = sz(receipt) < sz(P)
    print("counter_sizes", {name: sz(term) for name, term in
          (("t0", t0), ("t", t), ("k", k), ("R", R), ("x", x),
           ("h", h), ("w", w), ("P", P), ("z", z))})
    print("counter_cells", {name: got == want for name, (got, want) in cells.items()})
    print("counter_tail", {
        "Qfree": Q == J(z, P),
        "Bfree": B == J(z, Q),
        "top_free": top == J(A, B),
        "law": top == x,
        "receipt_is_x": receipt == x,
        "receipt_codes_A": (cd(receipt) and m.op(A, a1(receipt)) == a2(a2(receipt))),
        "receipt_reproduces_P": m.op(receipt, z) == P,
        "pair_gate": receipt_pair_gate,
        "payload_gate": receipt_payload_gate,
        "find_is_sentinel": m.find(A, P, z, P)[0] == J(A, A),
    })
    print("counter_branches", dict(sorted(m.fired.items())))


if __name__ == "__main__":
    run()
    counterfamily()
