"""Render a verified tag-automaton model as a Lean 4 FALSE certificate (binary-split version).

op is defined through accessors  tg : M → Nat (tag code), a1 a2 : M → M (arguments), so every
rule is a conjunction of tests `tg (path) = k` / `path = path'` and the result is a path.
The proof mirrors the verifier's binary case tree:
  * tag test on a variable      -> by_cases h : tg t = k ; positive branch destructs t
  * equality test               -> by_cases h : s = t ; equal branch substs (injection-decomposed)
  * cyclic equality             -> `sz` + omega hypothesis
  * leaf                        -> simp [op, tg, a1, a2, *]
"""
import itertools, json, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from symb import Var, State, Model, _vars
from laws import parse_eq


class Ctx:
    def __init__(self):
        self.names = {}
        self.hyps = []
        self.eqhyps = set()
        self.counter = itertools.count(1)

    def copy(self):
        c = Ctx()
        c.names = dict(self.names)
        c.hyps = list(self.hyps)
        c.eqhyps = set(self.eqhyps)
        c.counter = self.counter
        return c

    def fresh(self, prefix):
        return f'{prefix}{next(self.counter)}'


def lean_term(t, st, ctx, R):
    t = st.resolve(t)
    if isinstance(t, Var):
        if t not in ctx.names:
            ctx.names[t] = ctx.fresh('n' if t.sort == 'N' else 'v')
        return ctx.names[t]
    if t[0] == 'G':
        return f'(g {lean_term(t[1], st, ctx, R)})'
    return '(' + R.tagname[t[0]] + ''.join(' ' + lean_term(a, st, ctx, R) for a in t[1:]) + ')'


class Renderer:
    def __init__(self, m):
        self.m = m
        self.tags = list(m.tags)
        self.tagname = {t: ('g' if t == 'G' else t) for t in self.tags}
        self.code = {t: i for i, t in enumerate(self.tags)}
        self.maxar = max(m.tags.values())

    # ---- op via accessors ----
    def path_expr(self, base, path):
        e = base
        for i in path:
            e = f'(a{i} {e})'
        return e

    def rule_tests(self, pu, pv, rhs):
        """returns (list of test strings, result expr) for the rule."""
        tests = []
        bound = {}

        def walk(p, base, path):
            if isinstance(p, str):
                e = self.path_expr(base, path)
                if p in bound:
                    tests.append(f'{bound[p]} = {e}')
                else:
                    bound[p] = e
                return
            e = self.path_expr(base, path)
            if p[0] == 'AS':
                if p[1] in bound:
                    tests.append(f'{bound[p[1]]} = {e}')
                else:
                    bound[p[1]] = e
                walk(p[2], base, path)
                return
            tests.append(f'tg {e} = {self.code[p[0]]}')
            for i, a in enumerate(p[1:], 1):
                walk(a, base, path + (i,))
        walk(pu, 'u', ())
        walk(pv, 'v', ())

        def res(r):
            if isinstance(r, str):
                return bound[r]
            return '(M.' + self.tagname[r[0]] + ''.join(' ' + res(a) for a in r[1:]) + ')'
        return tests, res(rhs)

    def render_op(self):
        parts = []
        for (pu, pv, rhs) in self.m.rules:
            tests, r = self.rule_tests(pu, pv, rhs)
            if pu == pv and isinstance(pu, str):
                cond = 'u = v'
            else:
                cond = ' ∧ '.join(tests) if tests else 'True'
            parts.append((cond, r))
        body = f'M.{self.tagname[self.m.default]} u v'
        for cond, r in reversed(parts):
            body = f'if {cond} then {r} else {body}'
        return 'def op (u v : M) : M :=\n  ' + body

    def render_defs(self):
        ctors = []
        for t in self.tags:
            if t == 'G':
                ctors.append('  | g : Nat → submission.M')
            else:
                ctors.append(f'  | {self.tagname[t]} : ' + ' → '.join(['submission.M'] * (self.m.tags[t] + 1)))
        tg = [f'  | .{self.tagname[t]}{" _" * self.m.tags[t]} => {self.code[t]}' for t in self.tags]
        acc = []
        for i in range(1, self.maxar + 1):
            lines = [f'def a{i} : M → M']
            for t in self.tags:
                ar = self.m.tags[t]
                if t != 'G' and ar >= i:
                    args = ' '.join('x' if j == i else '_' for j in range(1, ar + 1))
                    lines.append(f'  | .{self.tagname[t]} {args} => x')
            lines.append('  | t => t')
            acc.append('\n'.join(lines))
        sz = ['  | .g _ => 1']
        for t in self.tags:
            if t == 'G':
                continue
            ar = self.m.tags[t]
            args = ' '.join(f'b{i}' for i in range(ar))
            sz.append(f'  | .{self.tagname[t]} {args} => ' + ' + '.join([f'sz {"b%d" % i}' for i in range(ar)] + ['1']))
        # destructuring lemmas
        lem = []
        for t in self.tags:
            ar = self.m.tags[t]
            if t == 'G':
                lem.append(f'theorem tg_g (t : M) (h : tg t = {self.code[t]}) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]')
            elif ar == 0:
                lem.append(f'theorem tg_{t} (t : M) (h : tg t = {self.code[t]}) : t = M.{t} := by cases t <;> simp_all [tg]')
            else:
                vs = ' '.join(f'b{i}' for i in range(ar))
                lem.append(f'theorem tg_{t} (t : M) (h : tg t = {self.code[t]}) : ∃ {vs}, t = M.{self.tagname[t]} {vs} := by cases t <;> simp_all [tg]')
        lem.append(f'theorem tg_range (t : M) : tg t < {len(self.tags)} := by cases t <;> simp [tg]')
        # constructor-case simp lemmas (so a variable argument stays an atom)
        for t in self.tags:
            ar = self.m.tags[t]
            if t == 'G':
                lem.append(f'@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = {self.code[t]} := rfl')
                continue
            args = ' '.join(f'b{i}' for i in range(ar))
            binder = f'({args} : M) ' if ar else ''
            lem.append(f'@[simp] theorem tg_{t}_eq {binder}: tg (M.{self.tagname[t]}{" " + args if ar else ""}) = {self.code[t]} := rfl')
            for i in range(1, ar + 1):
                lem.append(f'@[simp] theorem a{i}_{t}_eq {binder}: a{i} (M.{self.tagname[t]} {args}) = b{i - 1} := rfl')
        return (ctors, tg, acc, sz, lem)


class Emitter:
    def __init__(self, m, R, law):
        self.m = m
        self.R = R
        self.law = law
        self.out = []
        self.nleaves = 0

    def emit(self, depth, s):
        self.out.append(' ' * depth + s)

    def run(self):
        lhs, rhs = self.law
        vs = sorted(set(_vars(rhs)) | {lhs})
        env = {v: Var('M', v) for v in vs}
        ctx = Ctx()
        for v in vs:
            ctx.names[env[v]] = v
        prods = []

        def collect(t):
            if isinstance(t, str):
                return t
            if self.m.rev:
                b = collect(t[1])
                a = collect(t[0])
            else:
                a = collect(t[0])
                b = collect(t[1])
            prods.append((a, b))
            return len(prods) - 1
        collect(rhs)
        self.goal_x = env[lhs]
        self.env = env
        self.prods = prods
        self.eval_products(0, [], State(), ctx, 1)

    def val_of(self, ref, vals):
        return self.env[ref] if isinstance(ref, str) else vals[ref]

    def eval_products(self, k, vals, st, ctx, depth):
        if k == len(self.prods):
            self.leaf(vals, st, ctx, depth)
            return
        a, b = self.prods[k]
        self.apply_rules(k, 0, self.val_of(a, vals), self.val_of(b, vals), vals, st, ctx, depth)

    def apply_rules(self, k, ri, u, v, vals, st, ctx, depth):
        if ri == len(self.m.rules):
            self.eval_products(k + 1, vals + [(self.m.default, u, v)], st, ctx, depth)
            return
        pu, pv, rhs = self.m.rules[ri]
        pairs = [(pv, v), (pu, u)] if self.m.vfirst else [(pu, u), (pv, v)]
        for st2, ctx2, b, d2 in self.match_seq(pairs, st, ctx, {}, depth):
            if b is None:
                self.apply_rules(k, ri + 1, u, v, vals, st2, ctx2, d2)
            else:
                for st3, ctx3, ok, d3 in self.finish(b.get('__d', ()), 0, st2, ctx2, b, d2):
                    if ok:
                        self.eval_products(k + 1, vals + [self.m.inst(rhs, b)], st3, ctx3, d3)
                    else:
                        self.apply_rules(k, ri + 1, u, v, vals, st3, ctx3, d3)

    def finish(self, pairs, i, st, ctx, b, depth):
        """decide deferred equality checks in order; yields (st, ctx, ok, depth)."""
        if i == len(pairs):
            yield (st, ctx, True, depth)
            return
        a, c = pairs[i]
        for st2, ctx2, bb, d2 in self.eq_split(a, c, st, ctx, b, depth):
            if bb is None:
                yield (st2, ctx2, False, d2)
            else:
                yield from self.finish(pairs, i + 1, st2, ctx2, b, d2)

    def match_seq(self, pairs, st, ctx, b, depth):
        if not pairs:
            yield (st, ctx, b, depth)
            return
        (pat, t), rest = pairs[0], pairs[1:]
        for st2, ctx2, b2, d2 in self.match_one(pat, t, st, ctx, b, depth):
            if b2 is None:
                yield (st2, ctx2, None, d2)
            else:
                yield from self.match_seq(rest, st2, ctx2, b2, d2)

    def match_one(self, pat, t, st, ctx, b, depth):
        if isinstance(pat, str):
            b2 = dict(b)
            if pat in b:
                b2['__d'] = b.get('__d', ()) + ((b[pat], t),)
            else:
                b2[pat] = t
            yield (st, ctx, b2, depth)
            return
        tag = pat[0]
        if tag == 'AS':
            name, sub = pat[1], pat[2]
            b2 = dict(b)
            if name in b:
                b2['__d'] = b.get('__d', ()) + ((b[name], t),)
            else:
                b2[name] = t
            yield from self.match_one(sub, t, st, ctx, b2, depth)
            return
        t = st.resolve(t)
        if isinstance(t, Var):
            excl = st.excl.get(t, set())
            if tag in excl:
                yield (st, ctx, None, depth)
                return
            ctx = ctx.copy()
            tname = lean_term(t, st, ctx, self.R)
            code = self.R.code[tag]
            ar = self.m.tags[tag]
            fresh = [Var('N' if tag == 'G' else 'M') for _ in range(ar)]
            st_yes = st.copy()
            st_yes.sub[t] = (tag, *fresh)
            ctx_yes = ctx.copy()
            fnames = [ctx_yes.fresh('n' if f.sort == 'N' else 'v') for f in fresh]
            for f, nm in zip(fresh, fnames):
                ctx_yes.names[f] = nm
            st_no = st.copy()
            st_no.excl.setdefault(t, set()).add(tag)
            hn = ctx.fresh('h')
            self.emit(depth, f'by_cases {hn} : tg {tname} = {code}')
            self.emit(depth, '·')
            if fnames:
                self.emit(depth + 1, f'obtain ⟨{", ".join(fnames)}, rfl⟩ := tg_{self.R.tagname[tag] if tag != "G" else "g"} _ {hn}')
            else:
                self.emit(depth + 1, f'obtain rfl := tg_{tag} _ {hn}')
            if st_yes.consistent():
                yield from self.match_one(pat, (tag, *fresh), st_yes, ctx_yes, b, depth + 1)
            else:
                self.emit(depth + 1, 'simp_all')
            self.emit(depth, '·')
            ctx_no = ctx.copy()
            ctx_no.hyps.append(hn)
            if len(st_no.excl[t]) == len(self.m.tags):
                self.emit(depth + 1, f'have := tg_range {tname}; omega')
                return
            yield (st_no, ctx_no, None, depth + 1)
            return
        if t[0] != tag:
            yield (st, ctx, None, depth)
            return
        yield from self.match_seq(list(zip(pat[1:], t[1:])), st, ctx, b, depth)

    def eq_split(self, s, t, st, ctx, b, depth):
        s = st.resolve(s)
        t = st.resolve(t)
        if s == t:
            yield (st, ctx, b, depth)
            return
        u = st.unify(s, t)
        if u is None:
            yield (st, ctx, None, depth)
            return
        ctx = ctx.copy()
        hn = ctx.fresh('h')
        ls = lean_term(s, st, ctx, self.R)
        lt = lean_term(t, st, ctx, self.R)
        self.emit(depth, f'by_cases {hn} : {ls} = {lt}')
        self.emit(depth, '·')
        ctx_eq = ctx.copy()
        self.emit_subst(hn, s, t, st, u, ctx_eq, depth + 1)
        yield (u, ctx_eq, b, depth + 1)
        self.emit(depth, '·')
        st_ne = st.copy()
        st_ne.diseq.append((s, t))
        ctx_ne = ctx.copy()
        ctx_ne.hyps.append(hn)
        ctx_ne.eqhyps.add(hn)
        yield (st_ne, ctx_ne, None, depth + 1)

    def is_clash(self, s, t, st):
        stack = [(st.resolve(s), st.resolve(t))]
        while stack:
            a, c = stack.pop()
            if isinstance(a, Var) or isinstance(c, Var):
                if isinstance(a, Var) and isinstance(c, Var):
                    continue
                if isinstance(c, Var):
                    a, c = c, a
                if a.sort == 'N':
                    return True
                continue
            if a[0] != c[0]:
                return True
            stack.extend(zip(a[1:], c[1:]))
        return False

    def emit_subst(self, hn, s, t, st, u, ctx, depth):
        eliminated = [k for k in u.sub if k not in st.sub]

        def go(hname, a, c):
            a = st.resolve(a)
            c = st.resolve(c)
            if a == c:
                return
            if isinstance(a, Var) or isinstance(c, Var):
                if isinstance(a, Var) and isinstance(c, Var):
                    var = a if a in eliminated else c
                elif isinstance(a, Var):
                    var = a
                else:
                    var = c
                self.emit(depth, f'subst {ctx.names[var]}')
                return
            names = [ctx.fresh('h') for _ in a[1:]]
            self.emit(depth, f'injection {hname} with ' + ' '.join(names))
            for nm, x, y in zip(names, a[1:], c[1:]):
                go(nm, x, y)
        go(hn, s, t)

    def leaf(self, vals, st, ctx, depth):
        self.nleaves += 1
        if st.resolve(vals[-1]) != st.resolve(self.goal_x):
            raise RuntimeError('leaf does not prove the law')
        extra = ''.join(f', Ne.symm {h}' for h in ctx.hyps if h in ctx.eqhyps)
        self.emit(depth, f'simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *{extra}]')


def render(m, law, goal):
    R = Renderer(m)
    ctors, tg, acc, sz, lem = R.render_defs()
    em = Emitter(m, R, law)
    em.run()
    lhs, rhs = law
    vs = sorted(set(_vars(rhs)) | {lhs})
    glhs, grhs = goal
    gvs = sorted(set(_vars(grhs)) | {glhs})
    nl = chr(10)
    text = f'''import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
{nl.join(ctors)}
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
{nl.join(tg)}

{(nl + nl).join(acc)}

def sz : M → Nat
{nl.join(sz)}

{R.render_op()}

def inst : Magma M := {{ op := op }}

theorem eqf (a b : M) (h : sz a ≠ sz b) : (a = b) = False := eq_false (fun e => h (congrArg sz e))

{nl.join(lem)}

theorem law ({' '.join(vs)} : M) : {rhs_lean(rhs)} = {lhs} := by
{nl.join(em.out)}

theorem lhs : @EquationLHS M inst := by
  intro {' '.join(vs)}
  exact (law {' '.join(vs)}).symm

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  exact absurd (h {' '.join(f'(M.g {i})' for i in range(len(gvs)))}) (by decide)

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
'''
    return text, em


def rhs_lean(t):
    if isinstance(t, str):
        return t
    return f'(op {rhs_lean(t[0])} {rhs_lean(t[1])})'


if __name__ == '__main__':
    law = parse_eq('x = y * ((x * (z * x)) * (y * y))')
    rules = [('$u', '$u', ('S', '$u')),
             ('$v', ('T3', ('T3', '$a', '$b'), ('S', '$v')), '$a')]
    m = Model({'S': 1, 'T3': 2}, rules, default='T3')
    goal = parse_eq('x = (y * (x * x)) * ((y * z) * y)')
    text, em = render(m, law, goal)
    print(text)
    print('-- leaves', em.nleaves, 'bytes', len(text.encode()))
