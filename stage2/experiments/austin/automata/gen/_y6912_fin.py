"""_y6912_fin.py : does 6912 have a NON-TRIVIAL finite model?  (the trivial-magma question)

6912 :  x = y * (y * ((z*z) * (x*y)))
Derived (gen/_x6912_derive2.py): all squares are equal to one idempotent e.  So in any model the
diagonal is constant = e.  We enumerate tables with that constraint by DFS and test the law.

Usage: python -u gen/_y6912_fin.py <n> [limit_models]
"""
import sys, itertools

def law_ok(t, n):
    for y in range(n):
        for z in range(n):
            s = t[z][z]
            for x in range(n):
                if t[y][t[y][t[s][t[x][y]]]] != x:
                    return False
    return True


def search(n, want=3):
    """DFS over the off-diagonal cells; diagonal fixed to a constant e."""
    found = []
    cells = [(i, j) for i in range(n) for j in range(n) if i != j]
    for e in range(n):
        t = [[e] * n for _ in range(n)]

        def rec(k):
            if found and len(found) >= want:
                return
            if k == len(cells):
                if law_ok(t, n):
                    found.append([row[:] for row in t])
                return
            i, j = cells[k]
            for val in range(n):
                t[i][j] = val
                rec(k + 1)
            t[i][j] = e
        rec(0)
        if len(found) >= want:
            break
    return found


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    want = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    res = search(n, want)
    print('order %d: %d model(s) found (want<=%d)' % (n, len(res), want))
    for t in res[:3]:
        print('   ', t, 'trivial' if all(all(c == t[0][0] for c in r) for r in t) else 'NON-TRIVIAL')
