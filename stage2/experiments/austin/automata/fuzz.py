"""Structured (rule-shaped) fuzzing of a closed form: instances of the rules' own u/v shapes, nested 2-3 deep,
are far more likely to hit derailment coincidences than random trees (the 11081 hole: a decoder relocated by
an inner decode was missed by 3,000 random tests).

fuzz(C, law, rules, N) -> (tested, fails)
"""
import random
from freemodel import size, pvars, rand_term
from closedform import is_accessor_chain, root_and_path

def skeletons(rules):
    """for each rule: the u/v shapes as nested tuples of paths ('leaf', path) / ('J', a, b), plus EQ pairs of paths"""
    out = []
    for conds, x, tag in rules:
        jpaths = set(); eqs = []
        for c in conds:
            if c[0] == 'TG' and is_accessor_chain(c[1]):
                jpaths.add(root_and_path(c[1]))
            elif c[0] == 'EQ' and is_accessor_chain(c[1]) and is_accessor_chain(c[2]):
                eqs.append((root_and_path(c[1]), root_and_path(c[2])))
        out.append((jpaths, eqs))
    return out

def build(root, path, jpaths, leaves, pool, depth):
    if (root, path) in jpaths:
        return ('J', build(root, path + ('A1',), jpaths, leaves, pool, depth), build(root, path + ('A2',), jpaths, leaves, pool, depth))
    t = random.choice(pool) if pool and random.random() < 0.7 else rand_term(1)
    leaves.append((root, path, t))
    return t

def get_path(t, path):
    for step in path:
        if t[0] != 'J': return None
        t = t[1] if step == 'A1' else t[2]
    return t

def set_path(t, path, val):
    if not path: return val
    if t[0] != 'J': return None
    if path[0] == 'A1':
        s = set_path(t[1], path[1:], val); return None if s is None else ('J', s, t[2])
    s = set_path(t[2], path[1:], val); return None if s is None else ('J', t[1], s)

def instances(rules, pool, n_per_rule, depth, C=None):
    """concrete (u, v) pairs shaped like each rule, leaves drawn from the pool; EQ conditions are imposed by
    copying, and nested op-guards `op(P,Q) == target` by computing op(P,Q) in the model and writing it at the
    target position (that is how the 11081-type coincidences arise)."""
    out = []
    for (jpaths, eqs), (conds, x, tag) in zip(skeletons(rules), rules):
        opeqs = [(c[1], c[2]) for c in conds if c[0] == 'OPEQ' and is_accessor_chain(c[2])]
        for _ in range(n_per_rule):
            leaves = []
            u = build(('U',), (), jpaths, leaves, pool, depth)
            v = build(('V',), (), jpaths, leaves, pool, depth)
            terms = {('U',): u, ('V',): v}
            ok = True
            for (r1, p1), (r2, p2) in eqs:
                val = get_path(terms[r2], p2)
                if val is None: ok = False; break
                t2 = set_path(terms[r1], p1, val)
                if t2 is None: ok = False; break
                terms[r1] = t2
            if ok and C is not None:
                for _round in range(2):
                    for ope, tgt in opeqs:
                        try:
                            val = C.ev(ope, terms[('U',)], terms[('V',)])
                        except RecursionError:
                            val = None
                        if val is None: continue
                        r, p = root_and_path(tgt)
                        t2 = set_path(terms[r], p, val)
                        if t2 is not None: terms[r] = t2
            if ok: out.append((terms[('U',)], terms[('V',)]))
    return out

def fuzz(C, law, rules, N=20000, seed=7, maxsize=140):
    random.seed(seed)
    A, B = law[1]; vs = pvars(law[1])
    pool = [('g', i) for i in range(3)]
    for d in range(3):
        inst = instances(rules, pool, 6, d, C)
        for u, v in inst:
            for t in (u, v):
                if size(t) <= 60 and t not in pool: pool.append(t)
            # products and their values are the richest sources of coincidences
            try:
                r = C.op(u, v)
                if size(r) <= 60 and r not in pool: pool.append(r)
            except RecursionError:
                pass
        if len(pool) > 3000: pool = pool[:3000]
    fails = []; tested = 0
    while tested < N:
        s = {v: random.choice(pool) for v in vs}
        r = random.random()
        if r < 0.3:
            a, b = random.sample(vs, 2); s[a] = s[b]
        elif r < 0.5:
            # a variable equal to a product of two pool terms
            a, b = random.choice(pool), random.choice(pool)
            try: s[random.choice(vs)] = C.op(a, b)
            except RecursionError: pass
        if max(size(t) for t in s.values()) > maxsize: continue
        try:
            lhs = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            fails.append((s, 'recursion')); tested += 1; continue
        tested += 1
        if lhs != s['x']: fails.append((s, lhs))
        if len(fails) > 20: break
    return tested, fails

def closure_fuzz(C, law, N=12000, seed=3, maxsize=140, rounds=6, per_round=120):
    """law-instance CLOSURE fuzz: the pool is closed under (i) evaluations of the law's subpatterns at pool
    assignments, (ii) products of pool elements and (iii) subterms; tests draw variables from the pool with a
    bias towards 'critical pairs' (a variable set to a term that was produced with the same decoder).  This is
    the shape of every hole the proof agents found by hand (9667, 40057, 5837, 33020: a variable equal to an
    encoding of another variable's value, nested once or twice)."""
    random.seed(seed)
    A, B = law[1]; vs = pvars(law[1])
    subs = []
    def collect(p):
        if isinstance(p, str): return
        subs.append(p); collect(p[0]); collect(p[1])
    collect(law[1])
    pool = [('g', i) for i in range(3)]; seen = set(pool); encs = []
    def add(t):
        if size(t) <= 60 and t not in seen and len(pool) < 4000:
            seen.add(t); pool.append(t)
            if t[0] == 'J': add(t[1]); add(t[2])
    for _ in range(rounds):
        for _ in range(per_round):
            p = random.choice(subs)
            s = {v: random.choice(pool) for v in vs}
            if encs and random.random() < 0.5:
                t0, s0 = random.choice(encs)
                for v in vs:
                    if random.random() < 0.5: s[v] = s0[v]
                if random.random() < 0.5: s[random.choice(vs)] = t0
            try:
                t = C.evp(p, s)
            except RecursionError:
                continue
            if size(t) > maxsize: continue
            add(t)
            if p is law[1] or p is B: encs.append((t, s))
            if random.random() < 0.5:
                a, b = random.choice(pool), random.choice(pool)
                try: add(C.op(a, b))
                except RecursionError: pass
    fails = []; tested = 0
    while tested < N:
        s = {v: random.choice(pool) for v in vs}
        r = random.random()
        if r < 0.4 and encs:
            t0, s0 = random.choice(encs)
            for v in vs:
                if random.random() < 0.6: s[v] = s0[v]
            s[random.choice(vs)] = t0
        elif r < 0.6:
            a, b = random.sample(vs, 2); s[a] = s[b]
        if max(size(t) for t in s.values()) > maxsize: continue
        try:
            lhs = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            fails.append((s, 'recursion')); tested += 1; continue
        tested += 1
        if lhs != s['x']: fails.append((s, lhs))
        if len(fails) > 20: break
    return tested, fails

def critical_fuzz(C, law, N=12000, seed=5, maxsize=160):
    """critical-pair fuzz: a law variable is REBUILT as an encoding B[payload, decoder, z] (or as a product term
    of depth <= 2) whose parts are the other variables' values, their products, or one more nested encoding —
    the 9667 / 40057 / 5837 hole shapes (an encoding of an encoding; a product of products of an encoding)."""
    random.seed(seed)
    A, B = law[1]; vs = pvars(law[1])
    gens = [('g', i) for i in range(4)]
    def prod(a, b):
        try: return C.op(a, b)
        except RecursionError: return None
    def term(vals, depth):
        if depth == 0 or random.random() < 0.3: return random.choice(vals)
        a, b = term(vals, depth - 1), term(vals, depth - 1)
        r = prod(a, b)
        return r if r is not None else a
    subs = []
    def collect(p):
        if isinstance(p, str): return
        subs.append(p); collect(p[0]); collect(p[1])
    collect(law[1])
    def enc(vals, depth):
        """an evaluation of the law's RHS, of B, or of any compound subpattern, whose variables are terms
        over vals — with a bias towards REPEATED variables (x = y = t), the 5837 shape"""
        s = {v: term(vals, 1) for v in vs}
        if random.random() < 0.4:
            a, b = random.sample(vs, 2); s[a] = s[b]
        if depth > 0 and random.random() < 0.5:
            s[random.choice(vs)] = enc(vals, depth - 1)
        r = random.random()
        p = B if r < 0.4 else (law[1] if r < 0.6 else random.choice(subs))
        try: return C.evp(p, s)
        except RecursionError: return random.choice(vals)
    fails = []; tested = 0
    while tested < N:
        base = {v: random.choice(gens) for v in vs}
        vals = list(base.values()) + gens[:2]
        s = dict(base)
        for _ in range(random.choice([1, 1, 2, 2, 3])):
            v = random.choice(vs)
            r = random.random()
            if r < 0.5: s[v] = enc(vals, random.choice([0, 1, 1, 2]))
            elif r < 0.8: s[v] = term(vals, 2)
            else:
                w = random.choice(vs); s[v] = s[w]
            vals = list(s.values()) + gens[:2]
        if max(size(t) for t in s.values()) > maxsize: continue
        try:
            lhs = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            fails.append((s, 'recursion')); tested += 1; continue
        tested += 1
        if lhs != s['x']: fails.append((s, lhs))
        if len(fails) > 20: break
    return tested, fails
