"""Term-algebra models for collapsing laws x = T(x, ybar).

Model R ("root-reduce"): carrier = all terms over leaves 0,1,2,...;
   op(a, b) = sigma(x) if node(a, b) matches T with substitution sigma, else node(a, b).
Model N ("normal forms"): carrier = terms; op(a, b) = innermost normal form of node(a,b)
   under the single rule T -> x (this is the free model iff the rule is confluent).

For each hypothesis we test eq1 on random + adversarial assignments, then eq2
on leaves and random terms. We also compute the critical pairs of T with itself
and check their joinability under N.
"""
from __future__ import annotations
import json, sys, random, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from austin_z3 import parse, variables  # noqa: E402

LEAF = 'L'


def to_term(t):
    """austin_z3 tuple -> ('v', name) | ('n', l, r)."""
    if t[0] == 'v':
        return ('v', t[1])
    return ('n', to_term(t[1]), to_term(t[2]))


def match(pat, term, sub):
    if pat[0] == 'v':
        b = sub.get(pat[1])
        if b is None:
            sub[pat[1]] = term
            return True
        return b == term
    if term[0] != 'n':
        return False
    return match(pat[1], term[1], sub) and match(pat[2], term[2], sub)


def subst(pat, sub):
    if pat[0] == 'v':
        return sub[pat[1]]
    return ('n', subst(pat[1], sub), subst(pat[2], sub))


def unify(a, b, sub):
    """Syntactic unification of two patterns (variables shared namespace)."""
    a = walk(a, sub); b = walk(b, sub)
    if a == b:
        return True
    if a[0] == 'v':
        if occurs(a[1], b, sub):
            return False
        sub[a[1]] = b
        return True
    if b[0] == 'v':
        if occurs(b[1], a, sub):
            return False
        sub[b[1]] = a
        return True
    return unify(a[1], b[1], sub) and unify(a[2], b[2], sub)


def walk(t, sub):
    while t[0] == 'v' and t[1] in sub:
        t = sub[t[1]]
    return t


def resolve(t, sub):
    t = walk(t, sub)
    if t[0] == 'v':
        return t
    return ('n', resolve(t[1], sub), resolve(t[2], sub))


def occurs(v, t, sub):
    t = walk(t, sub)
    if t[0] == 'v':
        return t[1] == v
    return occurs(v, t[1], sub) or occurs(v, t[2], sub)


def rename(t, suffix):
    if t[0] == 'v':
        return ('v', t[1] + suffix)
    return ('n', rename(t[1], suffix), rename(t[2], suffix))


def positions(t, pos=()):
    """Non-variable positions with their subterms."""
    if t[0] == 'v':
        return []
    out = [(pos, t)]
    out += positions(t[1], pos + (1,))
    out += positions(t[2], pos + (2,))
    return out


def replace(t, pos, new):
    if not pos:
        return new
    if pos[0] == 1:
        return ('n', replace(t[1], pos[1:], new), t[2])
    return ('n', t[1], replace(t[2], pos[1:], new))


def size(t):
    return 1 if t[0] in ('v', LEAF, 'J') else 1 + size(t[1]) + size(t[2])


class Law:
    def __init__(self, text):
        l, r = parse(text)
        self.lhs, self.rhs = to_term(l), to_term(r)
        assert self.lhs[0] == 'v', 'expected x = T'
        self.x = self.lhs[1]
        self.T = self.rhs
        self.vars = variables(l, variables(r, []))

    # ---- model R
    def op_R(self, a, b):
        t = ('n', a, b)
        sub = {}
        if match(self.T, t, sub):
            return sub[self.x]
        return t

    # ---- model N: innermost normal form under T -> x
    def nf(self, t, fuel=200):
        if t[0] != 'n':
            return t
        l = self.nf(t[1], fuel); r = self.nf(t[2], fuel)
        t = ('n', l, r)
        sub = {}
        if match(self.T, t, sub):
            if fuel <= 0:
                raise RuntimeError('fuel')
            return self.nf(sub[self.x], fuel - 1)
        return t

    def op_N(self, a, b):
        return self.nf(('n', a, b))

    def critical_pairs(self):
        """Overlaps of T with its own proper non-variable subterms."""
        T2 = rename(self.T, "'")
        x2 = ('v', self.x + "'")
        pairs = []
        for pos, sub_t in positions(self.T):
            if not pos:
                continue
            sub = {}
            if unify(sub_t, T2, sub):
                U = resolve(self.T, sub)               # the overlapped term
                p1 = resolve(('v', self.x), sub)        # root reduction
                p2 = resolve(replace(self.T, pos, x2), sub)  # inner reduction
                pairs.append((pos, p1, p2, U))
        return pairs


def eval_term(t, env, op):
    if t[0] == 'v':
        return env[t[1]]
    return op(eval_term(t[1], env, op), eval_term(t[2], env, op))


def random_term(rng, depth, leaves=4):
    if depth == 0 or rng.random() < 0.3:
        return (LEAF, rng.randrange(leaves))
    return ('n', random_term(rng, depth - 1, leaves), random_term(rng, depth - 1, leaves))


def adversarial_terms(law, rng, n):
    """Instances of T's sub-patterns with random fillings, plus T-instances."""
    out = []
    subs = [t for _p, t in positions(law.T)]
    for _ in range(n):
        pat = rng.choice(subs)
        env = {v: random_term(rng, 2) for v in law.vars}
        out.append(subst(pat, env))
    return out


def test_law(law, op, rng, rounds=3000):
    pool = [(LEAF, i) for i in range(4)] + [random_term(rng, 3) for _ in range(40)]
    pool += adversarial_terms(law, rng, 60)
    # close pool a bit under op
    for _ in range(60):
        a, b = rng.choice(pool), rng.choice(pool)
        pool.append(op(a, b))
    bad = 0
    for _ in range(rounds):
        env = {v: rng.choice(pool) for v in law.vars}
        try:
            if eval_term(law.T, env, op) != env[law.x]:
                bad += 1
                if bad >= 3:
                    break
        except RuntimeError:
            bad += 1
    return bad


def refutes(law, eq2_text, op, rng):
    l, r = parse(eq2_text)
    l, r = to_term(l), to_term(r)
    vs = variables(parse(eq2_text)[0], variables(parse(eq2_text)[1], []))
    # leaves first
    env = {v: (LEAF, i) for i, v in enumerate(vs)}
    try:
        if eval_term(l, env, op) != eval_term(r, env, op):
            return env
    except RuntimeError:
        return None
    pool = [(LEAF, i) for i in range(4)] + [random_term(rng, 3) for _ in range(30)]
    for _ in range(300):
        env = {v: rng.choice(pool) for v in vs}
        try:
            if eval_term(l, env, op) != eval_term(r, env, op):
                return env
        except RuntimeError:
            return None
    return None


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    groups = {}
    for r in rows:
        groups.setdefault(r['equation1'], []).append(r)
    rng = random.Random(1)
    summary = []
    for eq1_text, rs in groups.items():
        law = Law(eq1_text)
        cps = law.critical_pairs()
        joinable = 0
        for pos, p1, p2, U in cps:
            try:
                # instantiate remaining variables by distinct leaves for a joinability check
                vs = sorted({v[1] for v in _vars(p1) + _vars(p2) + _vars(U)})
                env = {v: (LEAF, i) for i, v in enumerate(vs)}
                if law.nf(_inst(p1, env)) == law.nf(_inst(p2, env)):
                    joinable += 1
            except RuntimeError:
                pass
        badR = test_law(law, law.op_R, rng)
        badN = test_law(law, law.op_N, rng)
        line = f"{rs[0].get('eq1_id', rs[0]['id'])}: {eq1_text}  | CPs {len(cps)} joinable {joinable} | R-violations {badR} | N-violations {badN}"
        refs = []
        for r in rs:
            for name, op in (('R', law.op_R), ('N', law.op_N)):
                bad = badR if name == 'R' else badN
                if bad == 0:
                    env = refutes(law, r['equation2'], op, rng)
                    if env is not None:
                        refs.append((r['id'], name))
        if refs:
            line += f"  ==> refutes {refs}"
        print(line, flush=True)
        summary.append({'eq1': eq1_text, 'cps': len(cps), 'joinable': joinable, 'badR': badR, 'badN': badN, 'refutes': refs})
    out = sys.argv[2] if len(sys.argv) > 2 else None
    if out:
        json.dump(summary, open(out, 'w'), indent=1)


def _vars(t):
    if t[0] == 'v':
        return [t]
    if t[0] == LEAF:
        return []
    return _vars(t[1]) + _vars(t[2])


def _inst(t, env):
    if t[0] == 'v':
        return env[t[1]]
    if t[0] == LEAF:
        return t
    return ('n', _inst(t[1], env), _inst(t[2], env))


if __name__ == '__main__':
    main()
