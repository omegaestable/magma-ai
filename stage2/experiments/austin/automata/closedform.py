"""Closed-form (finite, recursive) rule systems for the free model of a law  x = A * B.

A rule is a symbolic *reading* of the pair (u, v): the pattern is traversed against accessor
expressions over u and v; every internal node of the pattern is read either freely (the target is a
J-node whose children are matched) or as a decode (the node's value is a root reading of the law with
x-value = the target).  A decode whose encoding side is fully determined and whose decoder side is not
becomes a *nested op guard*  op(dec, enc) = w  (the recursion that makes the rule set finite); every
other decode is unified structurally with the root pattern (unbound leaves are free).

Expressions:  ('U',) ('V',) ('A1',e) ('A2',e) ('OP',e,e) ('J',e,e) ('F',k) (free/junk placeholder).
Conditions:   ('TG',e) e is a J-node;  ('EQ',e1,e2);  ('OPEQ',e_op,e_w) evaluated op-term equals target.
Rule:         (conds, result_expr, tag).

`Closed(law).op(u,v)` evaluates the rule list (first match, else J) with memoisation;
`validate(eq)` runs the deep law tests + goal refutations.
"""
import sys, os, json, random, time, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.setrecursionlimit(20000)
import freemodel as fm
from freemodel import size, normalise, pvars, catalog, rand_term
from laws import parse_eq, load_rows

class Infeasible(Exception): pass

def positions(p, path=()):
    """internal nodes of a pattern with their paths"""
    if isinstance(p, str): return []
    return [(path, p)] + positions(p[0], path + (0,)) + positions(p[1], path + (1,))

def is_accessor_chain(e):
    return e[0] in ('U', 'V') or (e[0] in ('A1', 'A2') and is_accessor_chain(e[1]))

def root_and_path(e):
    path = []
    while e[0] in ('A1', 'A2'):
        path.append(e[0]); e = e[1]
    return e, tuple(reversed(path))

def strict_descendant(e1, e2):
    """e1 is a strict accessor-descendant of e2 (both accessor chains on the same root)"""
    r1, p1 = root_and_path(e1); r2, p2 = root_and_path(e2)
    return r1 == r2 and len(p1) > len(p2) and p1[:len(p2)] == p2

def has_free(e):
    if e[0] == 'F': return True
    return any(has_free(c) for c in e[1:] if isinstance(c, tuple))

SUBST = {}
def occurs(f, e):
    e = subst_shallow(e)
    if e == f: return True
    return any(occurs(f, c) for c in e[1:] if isinstance(c, tuple))
def subst_shallow(e):
    while e[0] == 'F' and e in SUBST: e = SUBST[e]
    return e
def assign(f, e):
    """F := e with the occurs check (a cyclic placeholder is an infeasible rule)"""
    e = subst(e)
    if e == f: return
    if occurs(f, e): raise Infeasible()
    SUBST[f] = e
def subst(e):
    """apply the global free-placeholder substitution"""
    if e[0] == 'F':
        t = SUBST.get(e)
        return subst(t) if t is not None else e
    if e[0] in ('A1', 'A2'): return (e[0], subst(e[1]))
    if e[0] in ('OP', 'J'): return (e[0], subst(e[1]), subst(e[2]))
    return e

class Env:
    """variable bindings with aliasing of unbound variables (union-find over names)."""
    def __init__(self, init=None):
        self.b = dict(init or {})
        self.parent = {}
    def find(self, v):
        while v in self.parent: v = self.parent[v]
        return v
    def get(self, v):
        e = self.b.get(self.find(v))
        return subst(e) if e is not None else None
    def bound(self, v):
        return self.find(v) in self.b
    def bind(self, v, e, conds):
        r = self.find(v)
        if r in self.b:
            old = subst(self.b[r]); e = subst(e)
            if old == e: return
            if old[0] == 'F': assign(old, e)
            elif e[0] == 'F': assign(e, old)
            else: conds.append(('EQ', old, e))
        else: self.b[r] = e
    def alias(self, v1, v2, conds):
        r1, r2 = self.find(v1), self.find(v2)
        if r1 == r2: return
        if r1 in self.b and r2 in self.b: conds.append(('EQ', self.b[r1], self.b[r2]))
        elif r1 in self.b: self.parent[r2] = r1
        else: self.parent[r1] = r2

class Extractor:
    def __init__(self, law):
        self.lhs, self.rhs = law
        self.A, self.B = self.rhs
        self.vars = pvars(self.rhs)
        self.lform = isinstance(self.A, str)     # x = y * B
        self.rform = isinstance(self.B, str)     # x = A * y
        self.nfree = 0

    def fresh(self):
        self.nfree += 1; return ('F', self.nfree)

    def val(self, p, env, path=None, choices=None, conds=None):
        """expression for pattern p under env (None if some variable is unbound).
        With choices[path] == 'vdec' a node whose decoder side is an unbound variable and whose encoding
        side is determined is read as a decode: decoder := dec(encoding)."""
        if isinstance(p, str):
            return env.get(p)
        cp = None if path is None else path + (0,); cq = None if path is None else path + (1,)
        a = self.val(p[0], env, cp, choices, conds); b = self.val(p[1], env, cq, choices, conds)
        if choices is not None and path is not None and choices.get(path) == 'vdec':
            if self.lform and a is None and b is not None and isinstance(p[0], str) and not has_free(b):
                dec = self.decoder_expr(b, conds); env.bind(p[0], dec, conds); return ('OP', dec, b)
            if self.rform and b is None and a is not None and isinstance(p[1], str) and not has_free(a):
                dec = self.decoder_expr(a, conds); env.bind(p[1], dec, conds); return ('OP', a, dec)
        if a is None or b is None: return None
        return ('OP', a, b)

    # ---- traverse pattern p against target expression w; D = decode nodes (by path) ----
    def traverse(self, p, path, w, env, D, conds, choices, deferred=None):
        if isinstance(p, str):
            env.bind(p, w, conds); return
        if path in D:
            if deferred is not None:
                deferred.append((p, path, w)); return      # decodes wait for the free structure to bind variables
            self.decode(p, path, w, env, D, conds, choices)
            return
        conds.append(('TG', w))
        self.traverse(p[0], path + (0,), ('A1', w), env, D, conds, choices, deferred)
        self.traverse(p[1], path + (1,), ('A2', w), env, D, conds, choices, deferred)

    def run_deferred(self, deferred, env, D, conds, choices):
        """process deferred decode nodes: those whose encoding side is determined first (they may bind more)."""
        pending = list(deferred)
        while pending:
            pick = None
            for item in pending:
                p, path, w = item
                P, Q = p
                encside = Q if self.lform else (P if self.rform else None)
                if encside is not None and self.val(encside, env) is not None:
                    pick = item; break
            if pick is None: pick = pending[0]
            pending.remove(pick)
            p, path, w = pick
            self.decode(p, path, w, env, D, conds, choices)

    def occurrences(self, v):
        def cnt(p):
            if isinstance(p, str): return 1 if p == v else 0
            return cnt(p[0]) + cnt(p[1])
        return cnt(self.rhs)

    def decode(self, p, path, w, env, D, conds, choices):
        """the value of node p (= op(val P, val Q)) is a root reading with x-value w."""
        P, Q = p
        if choices.get(path) == 'exist':
            dec = P if self.lform else (Q if self.rform else None)
            if isinstance(dec, str) and not env.bound(dec) and self.occurrences(dec) == 1:
                env.bind(dec, self.fresh(), conds)   # some decoder exists; the target is unconstrained
                return
            raise Infeasible()
        vP = self.val(P, env, path + (0,), choices, conds); vQ = self.val(Q, env, path + (1,), choices, conds)
        r = Env({'x': w})
        if vP is not None and vQ is not None:
            conds.append(('OPEQ', ('OP', vP, vQ), w)); return
        # lazy guard: encoding side bound, decoder side not (L-form: decoder = left, encoding = right)
        if self.lform and vQ is not None and vP is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_of(vQ, w, path, conds, choices)
            if dec is None or has_free(dec): raise Infeasible()   # a lazy decode needs a located decoder
            conds.append(('OPEQ', ('OP', dec, vQ), w))
            self.traverse(P, path + (0,), dec, env, D, conds, choices)
            return
        if self.rform and vP is not None and vQ is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_of(vP, w, path, conds, choices)
            if dec is None or has_free(dec): raise Infeasible()
            conds.append(('OPEQ', ('OP', vP, dec), w))
            self.traverse(Q, path + (1,), dec, env, D, conds, choices)
            return
        # structural: unify (P under env) with (A under r), (Q under env) with (B under r)
        # process the side that is bound first so the other side's variables get determined
        order = [(P, self.A), (Q, self.B)]
        if vP is None and vQ is not None: order = [(Q, self.B), (P, self.A)]
        for pp, qq in order:
            self.unify(pp, env, qq, r, conds)
        vP2, vQ2 = self.val(P, env, path + (0,), choices, conds), self.val(Q, env, path + (1,), choices, conds)
        if vP2 is None or vQ2 is None or has_free(vP2) or has_free(vQ2):
            return                  # a free decoder/payload: the structural conditions already say it all (vacuous)
        conds.append(('OPEQ', ('OP', vP2, vQ2), w))

    def decoder_of(self, enc, w, path, conds, choices):
        """the decoder inside an encoding `enc` of `w`: read the root pattern against `enc` with x := w; the
        pattern's inner nodes follow the level-2 mode vector choices[('L2',) + path] (default: all free)."""
        self.used_lazy.add(path)
        sub = choices.get(('L2',) + path)
        if sub is None:
            return self.decoder_expr(enc, conds)
        pat = self.B if self.lform else self.A
        r = Env({'x': w}); D2 = {p for p, m in sub.items() if m in ('lazy', 'struct')}
        deferred = []
        self.traverse(pat, ('L2',) + path, enc, r, D2, conds, sub, deferred)
        self.run_deferred(deferred, r, D2, conds, sub)
        return r.get('y')

    def decoder_expr(self, enc, conds):
        """expression of the decoder inside an encoding `enc` (path to the first y in the root pattern)"""
        pat = self.B if self.lform else self.A
        path = self.path_to('y', pat)
        e = enc
        for step in path:
            conds.append(('TG', e))
            e = ('A1', e) if step == 0 else ('A2', e)
        return e

    def path_to(self, v, p, path=()):
        if isinstance(p, str): return path if p == v else None
        for i in (0, 1):
            r = self.path_to(v, p[i], path + (i,))
            if r is not None: return r
        return None

    def unify(self, p, s, q, r, conds):
        """eval(p, s) = eval(q, r): p is a law pattern under env s, q a root-pattern under env r."""
        if isinstance(p, str) and isinstance(q, str):
            bp, bq = s.bound(p), r.bound(q)
            if bp and bq: conds.append(('EQ', s.get(p), r.get(q)))
            elif bp: r.bind(q, s.get(p), conds)
            elif bq: s.bind(p, r.get(q), conds)
            else:
                f = self.fresh(); s.bind(p, f, conds); r.bind(q, f, conds)
            return
        if isinstance(p, str):
            if s.bound(p):
                e = s.get(p)
                if e[0] == 'F':
                    v = self.val(q, r)
                    if v is not None:
                        assign(e, v); return
                    # refine the placeholder structurally: F := J(F1, F2)
                    f1, f2 = self.fresh(), self.fresh(); assign(e, ('J', f1, f2))
                    r1 = Env(); r1.b = r.b; r1.parent = r.parent
                    self.unify_expr(q[0], f1, r, conds)
                    self.unify_expr(q[1], f2, r, conds)
                    return
                conds.append(('TG', e))
                self.unify_expr(q[0], ('A1', e), r, conds)
                self.unify_expr(q[1], ('A2', e), r, conds)
            else:
                v = self.val(q, r)
                if v is not None: s.bind(p, v, conds)
                else:
                    f1, f2 = self.fresh(), self.fresh(); s.bind(p, ('J', f1, f2), conds)
                    self.unify_expr(q[0], f1, r, conds); self.unify_expr(q[1], f2, r, conds)
            return
        if isinstance(q, str):
            if r.bound(q):
                e = r.get(q)
                if e[0] == 'F':
                    v = self.val(p, s)
                    if v is not None:
                        assign(e, v); return
                    f1, f2 = self.fresh(), self.fresh(); assign(e, ('J', f1, f2))
                    self.unify_expr(p[0], f1, s, conds); self.unify_expr(p[1], f2, s, conds)
                    return
                conds.append(('TG', e))
                self.unify_expr(p[0], ('A1', e), s, conds)
                self.unify_expr(p[1], ('A2', e), s, conds)
            else:
                v = self.val(p, s)
                if v is not None: r.bind(q, v, conds)
                else:
                    f1, f2 = self.fresh(), self.fresh(); r.bind(q, ('J', f1, f2), conds)
                    self.unify_expr(p[0], f1, s, conds); self.unify_expr(p[1], f2, s, conds)
            return
        self.unify(p[0], s, q[0], r, conds)
        self.unify(p[1], s, q[1], r, conds)

    def unify_expr(self, q, e, r, conds):
        """pattern q under env r equals expression e (structurally, all nodes free)"""
        e = subst(e)
        if isinstance(q, str):
            r.bind(q, e, conds); return
        if e[0] == 'F':
            f1, f2 = self.fresh(), self.fresh(); assign(e, ('J', f1, f2))
            self.unify_expr(q[0], f1, r, conds); self.unify_expr(q[1], f2, r, conds); return
        if e[0] == 'J':
            self.unify_expr(q[0], e[1], r, conds); self.unify_expr(q[1], e[2], r, conds); return
        conds.append(('TG', e))
        self.unify_expr(q[0], ('A1', e), r, conds)
        self.unify_expr(q[1], ('A2', e), r, conds)

    def one_rule(self, choices):
        nodes = [('A',) + path for path, _ in positions(self.A)] + [('B',) + path for path, _ in positions(self.B)]
        D = {p for p, m in choices.items() if p[0] in ('A', 'B') and m in ('lazy', 'struct', 'exist')}
        env = Env(); conds = []
        SUBST.clear(); self.nfree = 0; self.used_lazy = set()
        deferred = []
        for pat, root, side in ((self.A, ('U',), 'A'), (self.B, ('V',), 'B')):
            if isinstance(pat, str): env.bind(pat, root, conds)
            else: self.traverse(pat, (side,), root, env, D, conds, choices, deferred)
        self.run_deferred(deferred, env, D, conds, choices)
        x = env.get('x')
        if x is None or has_free(x): raise Infeasible()
        conds = self.simplify([(c[0],) + tuple(subst(e) for e in c[1:]) for c in conds])
        return conds, subst(x), set(self.used_lazy)

    def rules(self, exist=False, level2=True, cap2=64):
        nodes = [('A',) + path for path, _ in positions(self.A)] + [('B',) + path for path, _ in positions(self.B)]
        modes = (['free', 'lazy', 'struct', 'vdec'] + (['exist'] if exist else [])) if (self.lform or self.rform) else ['free', 'struct']
        encpat = self.B if self.lform else self.A
        encnodes = [p for p, _ in positions(encpat)] if not isinstance(encpat, str) else []
        out = []
        for mode in itertools.product(modes, repeat=len(nodes)):
            choices = dict(zip(nodes, mode))
            try:
                conds, x, used = self.one_rule(choices)
            except Infeasible:
                continue
            tag = ','.join((''.join(map(str, p)) or 'e') + m[0] for p, m in choices.items() if m != 'free') or 'free'
            out.append((conds, x, tag))
            if not level2 or not used: continue
            used = sorted(used)[:2]
            subs = list(itertools.product(['free', 'lazy'], repeat=len(encnodes)))
            combos = list(itertools.product(subs, repeat=len(used)))[:cap2]
            for combo in combos:
                if all(all(m == 'free' for m in sv) for sv in combo): continue
                ch2 = dict(choices)
                for p, sv in zip(used, combo):
                    ch2[('L2',) + p] = {('L2',) + p + q: m for q, m in zip(encnodes, sv)}
                try:
                    conds2, x2, _ = self.one_rule(ch2)
                except Infeasible:
                    continue
                tag2 = tag + '|' + ';'.join(''.join(map(str, p)) + ':' + ''.join(m[0] for m in sv) for p, sv in zip(used, combo))
                out.append((conds2, x2, tag2))
        seen = set(); uniq = []
        for r in out:
            key = (tuple(r[0]), r[1])
            if key not in seen: seen.add(key); uniq.append(r)
        return uniq

    def unify_eq(self, a, b, out):
        a, b = subst(a), subst(b)
        if a == b: return
        if a[0] == 'F': assign(a, b); return
        if b[0] == 'F': assign(b, a); return
        if a[0] == 'J' and b[0] == 'J':
            self.unify_eq(a[1], b[1], out); self.unify_eq(a[2], b[2], out); return
        if a[0] == 'J':
            out.append(('TG', b)); self.unify_eq(a[1], ('A1', b), out); self.unify_eq(a[2], ('A2', b), out); return
        if b[0] == 'J':
            out.append(('TG', a)); self.unify_eq(('A1', a), b[1], out); self.unify_eq(('A2', a), b[2], out); return
        out.append(('EQ', a, b))

    def simplify(self, conds):
        # unification pass: resolve placeholders through the equalities (repeat until stable)
        for _ in range(4):
            work = []
            for c in conds:
                c = (c[0],) + tuple(subst(e) for e in c[1:])
                if c[0] == 'EQ': self.unify_eq(c[1], c[2], work)
                else: work.append(c)
            conds = work
        out = []
        for c in conds:
            c = (c[0],) + tuple(subst(e) for e in c[1:])
            if c[0] == 'EQ':
                a, b = c[1], c[2]
                if a == b: continue
                if (is_accessor_chain(a) and is_accessor_chain(b)) and (strict_descendant(a, b) or strict_descendant(b, a)):
                    raise Infeasible()
                if has_free(a) or has_free(b): raise Infeasible()   # an unresolved placeholder in a condition: not expressible
                out.append(c)
            elif c[0] == 'OPEQ':
                if has_free(c[1]) or has_free(c[2]): raise Infeasible()
                out.append(c)
            else:
                if has_free(c[1]): continue                          # a shape condition on a free term is vacuous
                if c[1][0] == 'J': continue                          # trivially a J
                if c not in out: out.append(c)
        return out

def msr(a, b):
    m = max(size(a), size(b))
    return m * m + size(a) + size(b)

def nested_op(e):
    if e[0] == 'OP': return True
    return any(nested_op(c) for c in e[1:] if isinstance(c, tuple))

# ---------------- evaluation ----------------
class Closed:
    def __init__(self, law, rules):
        self.law = law; self.rules = rules
        self.memo = {}; self.inprog = set(); self.cycles = 0; self.fired = {}

    def ev(self, e, u, v):
        k = e[0]
        if k == 'U': return u
        if k == 'V': return v
        if k == 'A1':
            t = self.ev(e[1], u, v)
            if t is None or t[0] != 'J': return None
            return t[1]
        if k == 'A2':
            t = self.ev(e[1], u, v)
            if t is None or t[0] != 'J': return None
            return t[2]
        if k == 'OP':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None: return None
            if msr(a, b) >= msr(u, v): return None   # the Lean definition's size gate (lex (max, sum))
            return self.op(a, b)
        if k == 'J':
            a = self.ev(e[1], u, v); b = self.ev(e[2], u, v)
            if a is None or b is None: return None
            return ('J', a, b)
        raise ValueError(e)

    def check(self, conds, u, v):
        # structural conditions first (cheap, no nested op), then the op-guards
        for c in sorted(conds, key=lambda c: 1 if c[0] == 'OPEQ' or any(nested_op(e) for e in c[1:]) else 0):
            if c[0] == 'TG':
                t = self.ev(c[1], u, v)
                if t is None or t[0] != 'J': return False
            elif c[0] == 'EQ':
                a = self.ev(c[1], u, v); b = self.ev(c[2], u, v)
                if a is None or b is None or a != b: return False
            elif c[0] == 'OPEQ':
                a = self.ev(c[1], u, v); b = self.ev(c[2], u, v)
                if a is None or b is None or a != b: return False
        return True

    def op(self, u, v):
        key = (u, v)
        m = self.memo.get(key)
        if m is not None: return m
        if key in self.inprog:
            self.cycles += 1; return ('J', u, v)
        self.inprog.add(key)
        res = None
        for i, (conds, x, tag) in enumerate(self.rules):
            if self.check(conds, u, v):
                r = self.ev(x, u, v)
                if r is not None:
                    res = r; self.fired[i] = self.fired.get(i, 0) + 1; break
        self.inprog.discard(key)
        if res is None: res = ('J', u, v)
        self.memo[key] = res
        return res

    def evp(self, p, s):
        if isinstance(p, str): return s[p]
        return self.op(self.evp(p[0], s), self.evp(p[1], s))

def show_expr(e):
    k = e[0]
    if k in ('U', 'V'): return k.lower()
    if k == 'A1': return show_expr(e[1]) + '.1'
    if k == 'A2': return show_expr(e[1]) + '.2'
    if k == 'OP': return 'op(%s, %s)' % (show_expr(e[1]), show_expr(e[2]))
    if k == 'J': return 'J(%s, %s)' % (show_expr(e[1]), show_expr(e[2]))
    if k == 'F': return '_'
    return str(e)

def show_rule(rule):
    conds, x, tag = rule
    parts = []
    for c in conds:
        if c[0] == 'TG': parts.append('J?' + show_expr(c[1]))
        elif c[0] == 'EQ': parts.append(show_expr(c[1]) + ' = ' + show_expr(c[2]))
        else: parts.append(show_expr(c[1]) + ' == ' + show_expr(c[2]))
    return '[%s] %s -> %s' % (tag, ' & '.join(parts), show_expr(x))

def deep_tests(C, law, N, secs, seed):
    import freetest2 as ft
    random.seed(seed)
    class Shim:
        pass
    F = Shim(); F.vars = pvars(law[1]); F.rhs = law[1]; F.ev = lambda p, s: C.evp(p, s)
    pool = []; fails = []; tested = 0; t0 = time.time()
    A, B = law[1]
    while tested < N and time.time() - t0 < secs:
        s = ft.nested_triple(F, pool)
        if max(size(t) for t in s.values()) > 120: continue
        try:
            lhs = C.op(C.evp(A, s), C.evp(B, s))
        except RecursionError:
            fails.append((s, 'recursion')); tested += 1; continue
        tested += 1
        for t in s.values():
            if size(t) <= 40 and len(pool) < 400: pool.append(t)
        if lhs != s['x']: fails.append((s, lhs))
    return tested, fails

def minimise(law, rules, N=3000, secs=200, seed=1):
    """keep only the rules that fire on the deep tests and the structured fuzz; re-validate; fall back to all"""
    import fuzz as fz
    C = Closed(law, rules)
    deep_tests(C, law, N, secs, seed)
    fz.fuzz(C, law, rules, 8000, seed=seed + 1)
    keep = [r for i, r in enumerate(rules) if i in C.fired or r[2] == 'free']
    if len(keep) == len(rules): return rules
    C2 = Closed(law, keep)
    t, f = deep_tests(C2, law, N, secs, seed + 2)
    t2, f2 = fz.fuzz(C2, law, keep, 8000, seed=seed + 3)
    return keep if not f and not f2 else rules

def best_rules(law, N=3000, secs=200, seed=1, minimize=True):
    """extract without the existential mode; if the law fails, try with it; return (rules, tested, fails, C)"""
    X = Extractor(law)
    best = None
    for exist in (False, True):
        rules = X.rules(exist=exist); C = Closed(law, rules)
        tested, fails = deep_tests(C, law, N, secs, seed)
        if best is None or len(fails) < len(best[2]):
            best = (rules, tested, fails, C)
        if not fails: break
    rules, tested, fails, C = best
    if minimize and not fails:
        rules = minimise(law, rules, N, secs, seed)
        C = Closed(law, rules)
    return rules, tested, fails, C

def validate(eq, N=3000, secs=200, verbose=True):
    cat = catalog(); law = normalise(parse_eq(cat[eq]))
    rules, tested, fails, C = best_rules(law, N, secs, eq * 3 + 1)
    goals = {}
    for r in [r for r in load_rows() if int(r['eq1_id']) == eq]:
        g = normalise(parse_eq(cat[int(r['eq2_id'])])); gv = pvars(g[1]); ref = None
        random.seed(eq)
        for _ in range(2000):
            s = {v: rand_term(2) for v in gv}
            if random.random() < 0.3 and len(gv) > 1:
                a, b = random.sample(gv, 2); s[a] = s[b]
            if s[g[0]] != C.evp(g[1], s): ref = s; break
        goals[r['eq2_id']] = ref is not None
    used = sorted(C.fired.items())
    res = dict(eq=eq, law=cat[eq], nrules=len(rules), tested=tested, fails=len(fails), cycles=C.cycles,
               fired=[(rules[i][2], n) for i, n in used], goals_refuted=goals)
    if verbose:
        print(json.dumps(res))
        for i, n in used: print('  ', n, show_rule(rules[i]))
        for s, lhs in fails[:2]: print('  FAIL', {k: fm.size(v) for k, v in s.items()})
    return res, rules, C, fails

if __name__ == '__main__':
    eq = int(sys.argv[1])
    if '--rules' in sys.argv:
        cat = catalog(); law = normalise(parse_eq(cat[eq])); X = Extractor(law)
        for r in X.rules(): print(show_rule(r))
    else:
        validate(eq, int(sys.argv[2]) if len(sys.argv) > 2 else 3000, float(sys.argv[3]) if len(sys.argv) > 3 else 200)
