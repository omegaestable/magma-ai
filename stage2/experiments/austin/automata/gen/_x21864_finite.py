"""Quick exhaustive-ish finite model search for law 21864 (and dual 24199), orders 2..5,
refuting the row goals.  Backtracking over the Cayley table with propagation-free brute force
on small orders; order 5 uses randomized restarts.
"""
import sys, itertools, random, time
sys.path.insert(0, 'c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata')
from freemodel import normalise, catalog
from laws import parse_eq

cat = catalog()


def pat(eq):
    return normalise(parse_eq(cat[eq]))


def ev(p, s, t, n):
    if isinstance(p, str):
        return s[p]
    a = ev(p[0], s, t, n)
    b = ev(p[1], s, t, n)
    return t[a * n + b]


def holds(law, t, n):
    vs = sorted(set(_vars(law[1])))
    for vals in itertools.product(range(n), repeat=len(vs)):
        s = dict(zip(vs, vals))
        if ev(law[1], s, t, n) != s[law[0]]:
            return False
    return True


def fails(law, t, n):
    vs = sorted(set(_vars(law[1])))
    for vals in itertools.product(range(n), repeat=len(vs)):
        s = dict(zip(vs, vals))
        if ev(law[1], s, t, n) != s[law[0]]:
            return True
    return False


def _vars(p, acc=None):
    if acc is None:
        acc = []
    if isinstance(p, str):
        if p not in acc:
            acc.append(p)
    else:
        _vars(p[0], acc); _vars(p[1], acc)
    return acc


def search(eq, goal, n, tries=200000, seed=1):
    law = pat(eq); g = pat(goal)
    random.seed(seed)
    cells = n * n
    t0 = time.time()
    for it in range(tries):
        if time.time() - t0 > 60:
            break
        t = [random.randrange(n) for _ in range(cells)]
        # local repair
        for step in range(4000):
            bad = []
            vs = _vars(law[1])
            for vals in itertools.product(range(n), repeat=len(vs)):
                s = dict(zip(vs, vals))
                if ev(law[1], s, t, n) != s['x']:
                    bad.append(s)
            if not bad:
                if fails(g, t, n):
                    return t
                break
            s = random.choice(bad)
            i = random.randrange(cells)
            t[i] = random.randrange(n)
    return None


for eq, goal in ((21864, 20034), (24199, 22455)):
    for n in (2, 3, 4, 5):
        r = search(eq, goal, n)
        print(eq, 'order', n, '->', r, flush=True)
