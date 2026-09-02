"""Targeted falsifier for the A-decoded/top-U branch of the unbounded locator."""
import _s10_17286_unbounded_receipt as rec

g, J, tg, a1, a2, sz = rec.g, rec.J, rec.tg, rec.a1, rec.a2, rec.sz


def terms(max_size, generators):
    by_size = {1: [g(i) for i in range(generators)]}
    for n in range(3, max_size + 1, 2):
        by_size[n] = [J(a, b)
                      for i in range(1, n - 1, 2)
                      for a in by_size.get(i, [])
                      for b in by_size.get(n - i - 1, [])]
    return [t for n in sorted(by_size) for t in by_size[n]]


def cds(m, u, c):
    return (tg(c) == 2 and tg(a2(c)) == 2 and a1(c) == a1(a2(c))
            and m.op(u, a1(c)) == a2(a2(c)))


def run():
    pool = terms(7, 2)
    n_dec = n_u = n_bad = 0
    examples = []
    for x in pool:
        for y in pool:
            for z in pool:
                if sz(x) + sz(y) + sz(z) > 15:
                    continue
                m = rec.Mod()
                A = m.op(y, x)
                if A == J(y, x):
                    continue
                n_dec += 1
                P = m.op(x, z)
                if tg(A) == 2 and m.op(a2(A), z) == P:
                    n_u += 1
                    good = a2(A) == x
                    n_bad += not good
                    if len(examples) < 12:
                        examples.append((good, x, y, z, A, P,
                                         cds(m, A, x),
                                         a2(y) == A if tg(y) == 2 else False,
                                         cds(m, y, A)))
    print('pool', len(pool), 'Adecoded', n_dec, 'topU', n_u, 'bad', n_bad)
    for row in examples:
        print(row)

    # The hard direct/recursive source combination reduces to this adjacent
    # commuting-square pattern at a common right argument.
    n_square = 0
    square_rows = []
    m = rec.Mod()
    for u in pool:
        if tg(u) != 2:
            continue
        for w in pool:
            r = m.op(u, w)
            if tg(r) == 2 and m.op(a2(u), w) == a2(r):
                n_square += 1
                if len(square_rows) < 8:
                    square_rows.append((u, w, r))
    print('adjacent_squares', n_square)
    for row in square_rows:
        print('SQUARE', row)


if __name__ == '__main__':
    run()
