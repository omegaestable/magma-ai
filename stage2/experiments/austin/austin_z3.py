"""Austin research set: z3 attempts.

mode=prove   : for each of the 100 rows, ask z3 whether eq1 (universally
               quantified) plus the negation of eq2 (skolemised) is UNSAT
               -> eq1 => eq2 (TRUE).  Also eq1 => x = y per distinct eq1.
mode=finite  : for each distinct eq1 (Table 3 first), search a nontrivial
               finite model at orders 2..N with a finite-domain encoding.
mode=linear  : affine templates x*y = a x + b y + c over Q: eq1 identically,
               then look for a point violating eq2.
"""
from __future__ import annotations
import json, sys, time, re
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

SP = Path(__file__).resolve().parent
ROWS = [json.loads(l) for l in open(str(Path(__file__).resolve().parents[3] / 'data' / 'hf_cache' / 'research_order5_hard.jsonl'), encoding='utf-8') if l.strip()]
TABLE3 = {12294, 33856, 13102, 33273, 17260, 28740, 17286, 28626, 20911, 25087, 21714, 24200,
          21864, 24199, 21865, 24197, 21866, 24201, 22446, 22591, 23337, 23354, 23357, 23653}


def parse(text):
    """Parse 'x = (y * x) * z' into nested tuples; vars are single letters."""
    lhs, rhs = text.split('=')
    def term(s):
        s = s.strip()
        toks = re.findall(r'[A-Za-z0-9]+|\(|\)|\*', s)
        pos = 0
        def atom():
            nonlocal pos
            t = toks[pos]
            if t == '(':
                pos += 1
                v = expr()
                assert toks[pos] == ')'; pos += 1
                return v
            pos += 1
            return ('v', t)
        def expr():
            nonlocal pos
            left = atom()
            while pos < len(toks) and toks[pos] == '*':
                pos += 1
                right = atom()
                left = ('op', left, right)
            return left
        v = expr(); assert pos == len(toks), (s, toks, pos)
        return v
    return term(lhs), term(rhs)


def variables(t, out=None):
    out = out if out is not None else []
    if t[0] == 'v':
        if t[1] not in out: out.append(t[1])
    else:
        variables(t[1], out); variables(t[2], out)
    return out


def z3_term(t, env, op):
    if t[0] == 'v':
        return env[t[1]]
    return op(z3_term(t[1], env, op), z3_term(t[2], env, op))


def prove_one(args):
    idx, eq1_text, eq2_text, timeout_ms = args
    import z3
    S = z3.DeclareSort('M')
    op = z3.Function('op', S, S, S)
    l1, r1 = parse(eq1_text); l2, r2 = parse(eq2_text)
    v1 = variables(l1, variables(r1, []))
    consts = {v: z3.Const(v, S) for v in v1}
    ax = z3.ForAll([consts[v] for v in v1], z3_term(l1, consts, op) == z3_term(r1, consts, op))
    v2 = variables(l2, variables(r2, []))
    sk = {v: z3.Const('sk_' + v, S) for v in v2}
    goal_neg = z3_term(l2, sk, op) != z3_term(r2, sk, op)
    s = z3.Solver()
    s.set('timeout', timeout_ms)
    s.add(ax, goal_neg)
    t0 = time.time()
    r = s.check()
    return idx, str(r), round(time.time() - t0, 1)


def finite_one(args):
    eq_id, eq1_text, n, timeout_ms = args
    import z3
    l1, r1 = parse(eq1_text)
    vs = variables(l1, variables(r1, []))
    # table cells as ints in [0,n)
    T = [[z3.Int(f't_{i}_{j}') for j in range(n)] for i in range(n)]
    s = z3.Solver(); s.set('timeout', timeout_ms)
    for i in range(n):
        for j in range(n):
            s.add(T[i][j] >= 0, T[i][j] < n)
    def ev(t, env):
        if t[0] == 'v':
            return env[t[1]]
        a = ev(t[1], env); b = ev(t[2], env)
        # symbolic lookup: sum_{i,j} (a==i & b==j) * T[i][j]
        expr = z3.IntVal(0)
        for i in range(n):
            for j in range(n):
                expr = z3.If(z3.And(a == i, b == j), T[i][j], expr)
        return expr
    from itertools import product
    for vals in product(range(n), repeat=len(vs)):
        env = {v: z3.IntVal(val) for v, val in zip(vs, vals)}
        s.add(ev(l1, env) == ev(r1, env))
    # nontrivial: forbid a constant table? A trivial model is n=1; for n>=2 any table on n elements is nontrivial.
    t0 = time.time()
    r = s.check()
    table = None
    if r == z3.sat:
        m = s.model()
        table = [[m.eval(T[i][j]).as_long() for j in range(n)] for i in range(n)]
    return eq_id, n, str(r), round(time.time() - t0, 1), table


def linear_one(args):
    eq_id, eq1_text, eq2_texts = args
    import sympy as sp
    a, b, c, x, y, z, w = sp.symbols('a b c x y z w')
    l1, r1 = parse(eq1_text)
    env = {'x': x, 'y': y, 'z': z, 'w': w}
    def ev(t):
        if t[0] == 'v': return env[t[1]]
        return a * ev(t[1]) + b * ev(t[2]) + c
    poly = sp.Poly(sp.expand(ev(l1) - ev(r1)), x, y, z, w)
    eqs = [sp.Eq(co, 0) for co in poly.coeffs()]
    sols = sp.solve(eqs, [a, b, c], dict=True)
    out = []
    for sol in sols:
        aa, bb, cc = sol.get(a, a), sol.get(b, b), sol.get(c, c)
        # nontrivial: not (a=0,b=0)?? magma x*y=c is a model only if eq1 forces x=c; skip degenerate
        for eq2_text in eq2_texts:
            l2, r2 = parse(eq2_text)
            def ev2(t):
                if t[0] == 'v': return env[t[1]]
                return aa * ev2(t[1]) + bb * ev2(t[2]) + cc
            d = sp.simplify(ev2(l2) - ev2(r2))
            out.append((str(sol), eq2_text, str(d)))
    return eq_id, out


def main():
    mode = sys.argv[1]
    if mode == 'prove':
        jobs = []
        for r in ROWS:
            jobs.append((r['id'], r['equation1'], r['equation2'], 120_000))
        seen = set()
        for r in ROWS:
            if r['eq1_id'] not in seen:
                seen.add(r['eq1_id'])
                jobs.append((f"collapse_{r['eq1_id']}", r['equation1'], 'x = y', 120_000))
        res = []
        with ProcessPoolExecutor(14) as ex:
            for idx, verdict, secs in ex.map(prove_one, jobs):
                res.append((idx, verdict, secs))
                if verdict != 'unknown':
                    print('RESULT', idx, verdict, secs, flush=True)
        json.dump(res, open(SP / 'austin_prove.json', 'w'), indent=1)
        from collections import Counter
        print('summary', Counter(v for _, v, _ in res))
    elif mode == 'finite':
        maxn = int(sys.argv[2]); timeout = int(sys.argv[3])
        eq1s = {}
        for r in ROWS:
            eq1s[r['eq1_id']] = r['equation1']
        order = sorted(eq1s, key=lambda i: (i not in TABLE3, i))
        if len(sys.argv) > 4 and sys.argv[4] == 'table3':
            order = [i for i in order if i in TABLE3]
        jobs = [(i, eq1s[i], n, timeout * 1000) for n in range(2, maxn + 1) for i in order]
        res = []
        with ProcessPoolExecutor(14) as ex:
            for eq_id, n, verdict, secs, table in ex.map(finite_one, jobs):
                res.append((eq_id, n, verdict, secs, table))
                if verdict == 'sat':
                    print('MODEL', eq_id, n, table, flush=True)
        json.dump(res, open(SP / f'austin_finite_{maxn}.json', 'w'), indent=1)
        from collections import Counter
        print('summary', Counter((n, v) for _, n, v, _, _ in res))
    elif mode == 'linear':
        eq1s = {}
        for r in ROWS:
            eq1s.setdefault((r['eq1_id'], r['equation1']), []).append(r['equation2'])
        jobs = [(i, t, e2) for (i, t), e2 in eq1s.items()]
        with ProcessPoolExecutor(14) as ex:
            for eq_id, out in ex.map(linear_one, jobs):
                for sol, e2, d in out:
                    print(eq_id, sol, '| eq2', e2, '| eq2 residual', d, flush=True)


if __name__ == '__main__':
    main()
