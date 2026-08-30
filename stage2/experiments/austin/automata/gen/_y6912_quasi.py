"""_y6912_quasi.py : finite models of law 6912, using the DERIVED structure.

6912 :  x = y * (y * ((z*z) * (x*y)))
Derived (gen/_x6912_derive2.py): all squares equal ONE idempotent e, so the law is the
two-variable law   x = y * (y * (e * (x*y)))   with  t[a][a] = e  for every a.

Write t[a][b] = a*b.  For each fixed y the law reads
      row_y ( row_y ( row_e ( col_y (x) ) ) ) = x        for all x
where col_y(x) = t[x][y] and row_y(v) = t[y][v].  A composite of maps equal to the identity on a
FINITE set forces every factor to be a bijection, so:

   * every column is a permutation, every row is a permutation  ->  the magma is a QUASIGROUP;
   * the diagonal is constant (= e), i.e. a UNIPOTENT Latin square;
   * for every y:   row_y o row_y o row_e  =  (col_y)^-1 .

So finite models of 6912 are exactly the unipotent Latin squares satisfying that identity, which is
a small DFS.  If one exists of order >= 2, 6912 does NOT force the trivial magma.

Usage: python -u gen/_y6912_quasi.py <n> [maxmodels]
"""
import sys, time

def search(n, want=2, deadline=None):
    E = 0
    t = [[-1] * n for _ in range(n)]
    colused = [[False] * n for _ in range(n)]   # colused[c][val]
    found = []
    t0 = time.time()

    def law_ok_full():
        for y in range(n):
            for x in range(n):
                if t[y][t[y][t[E][t[x][y]]]] != x:
                    return False
        return True

    def rec(i, j):
        if deadline and time.time() > deadline:
            raise TimeoutError
        if found and len(found) >= want:
            return
        if i == n:
            if law_ok_full():
                found.append([r[:] for r in t])
            return
        ni, nj = (i, j + 1) if j + 1 < n else (i + 1, 0)
        if i == j:
            if colused[j][E]:
                return
            t[i][j] = E; colused[j][E] = True
            rec(ni, nj)
            colused[j][E] = False; t[i][j] = -1
            return
        rowvals = set(t[i][k] for k in range(j) if t[i][k] >= 0)
        for v in range(n):
            if v in rowvals or colused[j][v]:
                continue
            t[i][j] = v; colused[j][v] = True
            rec(ni, nj)
            colused[j][v] = False; t[i][j] = -1

    try:
        rec(0, 0)
    except TimeoutError:
        return found, True
    return found, False


if __name__ == '__main__':
    n = int(sys.argv[1]); want = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    t0 = time.time()
    res, to = search(n, want, deadline=time.time() + 540)
    print('order %d: %d model(s)%s  %.1fs' % (n, len(res), '  (TIMEOUT)' if to else '', time.time() - t0))
    for m in res:
        print('   ', m)
