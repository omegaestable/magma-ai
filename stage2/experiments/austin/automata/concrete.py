"""Concrete (ground) implementation of a tag-automaton model for random testing."""
import random
from laws import parse_eq
from symb import _vars


def match(pat, t, b):
    if isinstance(pat, str):
        if pat in b:
            return b[pat] == t
        b[pat] = t
        return True
    if pat[0] == 'AS':
        name, sub = pat[1], pat[2]
        if name in b:
            if b[name] != t:
                return False
        else:
            b[name] = t
        return match(sub, t, b)
    if not isinstance(t, tuple) or t[0] != pat[0] or len(t) != len(pat):
        return False
    return all(match(p, a, b) for p, a in zip(pat[1:], t[1:]))


def inst(rhs, b):
    if isinstance(rhs, str):
        return b[rhs]
    return (rhs[0],) + tuple(inst(a, b) for a in rhs[1:])


def make_op(m):
    def op(u, v):
        for pu, pv, rhs in m.rules:
            b = {}
            if match(pu, u, b) and match(pv, v, b):
                return inst(rhs, b)
        return (m.default, u, v)
    return op


def rand_term(m, depth, ngen=4):
    tags = [t for t in m.tags if t != 'G']
    if depth <= 0 or random.random() < 0.25:
        return ('G', random.randrange(ngen))
    t = random.choice(tags)
    return (t,) + tuple(rand_term(m, depth - 1, ngen) for _ in range(m.tags[t]))


def evaluate(op, term, env):
    if isinstance(term, str):
        return env[term]
    return op(evaluate(op, term[0], env), evaluate(op, term[1], env))


def random_test(m, law, n=100000, depth=5, seed=0):
    random.seed(seed)
    op = make_op(m)
    lhs, rhs = law
    vs = sorted(set(_vars(rhs)) | {lhs})
    bad = 0
    ex = None
    for i in range(n):
        env = {v: rand_term(m, random.randint(0, depth)) for v in vs}
        # sometimes force coincidences: reuse values
        if random.random() < 0.3:
            a, b = random.sample(vs, 2)
            env[a] = env[b]
        if random.random() < 0.3:
            # make one variable a product of others
            a = random.choice(vs)
            env[a] = op(env[random.choice(vs)], env[random.choice(vs)])
        if random.random() < 0.3:
            a = random.choice(vs)
            env[a] = evaluate(op, random.choice([rhs[0], rhs[1], rhs]), env)
        if evaluate(op, rhs, env) != env[lhs]:
            bad += 1
            if ex is None:
                ex = env
    return bad, ex


def goal_fails(m, goal, ngen=3):
    op = make_op(m)
    lhs, rhs = goal
    vs = sorted(set(_vars(rhs)) | {lhs})
    env = {v: ('G', i) for i, v in enumerate(vs)}
    return evaluate(op, rhs, env) != env[lhs]
