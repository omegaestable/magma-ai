"""Targeted unary saturation for the remaining 6912 cancellation lemma.

Assumptions are exactly the already-proved reduced theory

    t*t = e
    y*(y*(e*(x*y))) = x,

plus the sound quasi-equational inference A*r=B*r -> A=B (right
translations are injective).  This is a target probe for

    y*e = e*(e*y)

and is not evidence when it returns no derivation.
"""
import collections
import sys


MAX_POOL_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ROUNDS = int(sys.argv[2]) if len(sys.argv) > 2 else 5
CAP = int(sys.argv[3]) if len(sys.argv) > 3 else 300_000


def C(name):
    return ("C", name)


def J(a, b):
    return ("J", a, b)


A, E = C("a"), C("e")


def show(t):
    if t[0] == "C":
        return t[1]
    return "(%s*%s)" % (show(t[1]), show(t[2]))


ids = {}
terms = []
kids = []
size = []
parent = []
why = []


def find(i):
    while parent[i] != i:
        parent[i] = parent[parent[i]]
        i = parent[i]
    return i


def add(t):
    if t in ids:
        return ids[t]
    ch = None if t[0] == "C" else (add(t[1]), add(t[2]))
    i = len(terms)
    ids[t] = i
    terms.append(t)
    kids.append(ch)
    size.append(1 if ch is None else size[ch[0]] + size[ch[1]] + 1)
    parent.append(i)
    why.append(None)
    return i


def union(i, j, reason):
    i, j = find(i), find(j)
    if i == j:
        return False
    if size[i] > size[j]:
        i, j = j, i
    parent[j] = i
    why[j] = reason
    return True


eid = add(E)
aid = add(A)


def close():
    total = collections.Counter()
    cancellations = []
    changed = True
    while changed:
        changed = False

        # Congruence.
        sig = {}
        for i, ch in enumerate(kids):
            if ch is None:
                continue
            key = (find(ch[0]), find(ch[1]))
            if key in sig and union(i, sig[key], ("cong", i, sig[key])):
                total["cong"] += 1
                changed = True
            else:
                sig[key] = i

        # Every square is e.
        for i, ch in enumerate(kids):
            if ch is not None and find(ch[0]) == find(ch[1]):
                if union(i, eid, ("square", i)):
                    total["square"] += 1
                    changed = True

        # E-match y*(y*(e*(x*y))) = x modulo current classes.
        for i, ch0 in enumerate(kids):
            if ch0 is None:
                continue
            y0, n1 = ch0
            ch1 = kids[n1]
            if ch1 is None or find(ch1[0]) != find(y0):
                continue
            n2 = ch1[1]
            ch2 = kids[n2]
            if ch2 is None or find(ch2[0]) != find(eid):
                continue
            xy = ch2[1]
            ch3 = kids[xy]
            if ch3 is None or find(ch3[1]) != find(y0):
                continue
            x0 = ch3[0]
            if union(i, x0, ("law", i, x0)):
                total["law"] += 1
                changed = True

        # Right cancellation: equal products with equal right arguments.
        seen = {}
        for i, ch in enumerate(kids):
            if ch is None:
                continue
            key = (find(i), find(ch[1]))
            if key in seen:
                j = seen[key]
                if union(ch[0], kids[j][0], ("rcancel", i, j)):
                    total["rcancel"] += 1
                    cancellations.append((terms[ch[0]], terms[kids[j][0]],
                                          terms[ch[1]], terms[i], terms[j]))
                    changed = True
            else:
                seen[key] = i
    return total, cancellations


def all_terms(max_size):
    by = {1: [A, E]}
    for n in range(3, max_size + 1, 2):
        by[n] = [J(s, t)
                 for left_size in range(1, n - 1, 2)
                 for s in by[left_size]
                 for t in by[n - 1 - left_size]]
    return [t for n in sorted(by) for t in by[n]]


for term in all_terms(MAX_POOL_SIZE):
    add(term)

q = J(A, E)
p = J(E, J(E, A))
qid, pid = add(q), add(p)
close()

for round_no in range(1, ROUNDS + 1):
    reps = sorted({find(i) for i in range(len(terms))})
    pool = [terms[i] for i in reps if size[i] <= MAX_POOL_SIZE]
    before = len(terms)
    for x in pool:
        for y in pool:
            lhs = J(y, J(y, J(E, J(x, y))))
            union(add(lhs), add(x), ("instance", x, y))
            if len(terms) >= CAP:
                break
        if len(terms) >= CAP:
            break
    stats, cancellations = close()
    print("round", round_no, "pool", len(pool), "nodes", len(terms),
          "added", len(terms) - before, "close", dict(stats),
          "q=p", find(qid) == find(pid), "a=e", find(aid) == find(eid),
          flush=True)
    for left, right, suffix, whole_left, whole_right in cancellations[:12]:
        print("  rcancel", show(left), "=", show(right), "at *", show(suffix),
              "from", show(whole_left), "=", show(whole_right))
    if find(qid) == find(pid) or find(aid) == find(eid) or len(terms) >= CAP:
        break
