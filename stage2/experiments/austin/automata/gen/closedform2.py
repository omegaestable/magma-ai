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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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

def prune(rules):
    """FIX-2 (subsumption): exact dedup on the condition SET (`Closed.check` sorts the conditions, so their
    order is not semantics) plus SUBSUMPTION -- rule j is unreachable when an EARLIER rule i has
    conds_i subset-of conds_j and the SAME result expression: every pair satisfying j satisfies i, i is
    tried first, and the same result expression evaluates identically (`ev` is a pure function of the
    expression and the pair), so j can never fire.  Behaviour-preserving.
    It is the RULE COUNT, not the extraction, that drives the validate/minimise cost (quadratic in
    revalidate.py) and the Lean proof size, so this is the cheap half of the cost fix."""
    seen = set(); uniq = []
    for r in rules:
        key = (frozenset(r[0]), r[1])
        if key in seen: continue
        seen.add(key); uniq.append((frozenset(r[0]), r[1], r))
    out = []
    for cs, x, r in uniq:
        if any(x0 == x and c0 <= cs for c0, x0, _ in out):
            continue
        out.append((cs, x, r))
    return [r for _, _, r in out]

class Extractor:
    def __init__(self, law):
        self.lhs, self.rhs = law
        self.A, self.B = self.rhs
        self.vars = pvars(self.rhs)
        self.lform = isinstance(self.A, str)     # x = y * B
        self.rform = isinstance(self.B, str)     # x = A * y
        # FIX-1 (decvar): the DECODER variable is the bare side's variable, whatever it is named.
        # closedform.py hardcodes the name 'y' in decoder_expr/decoder_of, which is wrong for every law
        # whose bare side is not called 'y' -- i.e. for dualised laws (32281 'z', 34889 'z', 40037 'z').
        self.decvar = self.A if self.lform else (self.B if self.rform else None)
        # FIX-3 (decoder occurrence): the decoder may occur SEVERAL times in the encoding pattern.
        # closedform.py always reads the FIRST one (`path_to`), which is the deepest-left occurrence and is
        # often the one that is itself inside a decoded node; the shallow occurrence is the provably free
        # one.  Every occurrence is an admissible reading position, so they become a choice dimension
        # (`choices[('DECOCC',)+path] = index`) enumerated by rules().  This is the generic form of the
        # hand repair PLAYBOOK_REPAIR.md 4(a) did per law (9667, 40057).
        encpat = self.B if self.lform else (self.A if self.rform else None)
        if self.decvar is None or isinstance(encpat, str) or encpat is None:
            self.decpaths = []
        else:
            self.decpaths = self.paths_to(self.decvar, encpat)
            # closedform.py's legacy position (the first literal 'y') stays as candidate 0 whenever it is a
            # real position, so that occurrence 0 reproduces the old extractor exactly and nothing that
            # worked before can be lost; the correct decoder occurrences are the alternatives, enumerated
            # by rules() as |dec:k.  A wrong decoder position only makes a rule fire LESS often (the
            # OPEQ guard still certifies the reading), so extra candidates are safe -- they add coverage.
            legacy = self.path_to('y', encpat)
            if legacy is not None and legacy not in self.decpaths:
                self.decpaths = [legacy] + self.decpaths
            elif legacy is not None:
                self.decpaths = [legacy] + [q for q in self.decpaths if q != legacy]
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
            occ = choices.get(('DECOCC',) + path, 0)
            if self.lform and a is None and b is not None and isinstance(p[0], str) and not has_free(b):
                dec = self.decoder_expr(b, conds, occ); env.bind(p[0], dec, conds); return ('OP', dec, b)
            if self.rform and b is None and a is not None and isinstance(p[1], str) and not has_free(a):
                dec = self.decoder_expr(a, conds, occ); env.bind(p[1], dec, conds); return ('OP', a, dec)
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
        order = [(P, self.A, path + (0,), ('A',)), (Q, self.B, path + (1,), ('B',))]
        if vP is None and vQ is not None: order = [(Q, self.B, path + (1,), ('B',)), (P, self.A, path + (0,), ('A',))]
        for pp, qq, ppath, qpath in order:
            self.unify(pp, env, qq, r, conds, ppath=ppath, choices=choices, qpath=qpath)
        self.resolve_rdefer(conds)
        vP2, vQ2 = self.val(P, env, path + (0,), choices, conds), self.val(Q, env, path + (1,), choices, conds)
        if vP2 is None or vQ2 is None or has_free(vP2) or has_free(vQ2):
            return                  # a free decoder/payload: the structural conditions already say it all (vacuous)
        c = ('OPEQ', ('OP', vP2, vQ2), w)
        conds.append(c)
        self.soft.append(c)         # implied by the structure when the inner products are free: droppable (see rules())

    def decoder_of(self, enc, w, path, conds, choices):
        """the decoder inside an encoding `enc` of `w`: read the root pattern against `enc` with x := w; the
        pattern's inner nodes follow the level-2 mode vector choices[('L2',) + path] (default: all free)."""
        self.used_lazy.add(path)
        sub = choices.get(('L2',) + path)
        if sub is None:
            return self.decoder_expr(enc, conds, choices.get(('DECOCC',) + path, 0))
        pat = self.B if self.lform else self.A
        r = Env({'x': w}); D2 = {p for p, m in sub.items() if m in ('lazy', 'struct')}
        deferred = []
        self.traverse(pat, ('L2',) + path, enc, r, D2, conds, sub, deferred)
        self.run_deferred(deferred, r, D2, conds, sub)
        return r.get(self.decvar)

    def decoder_expr(self, enc, conds, occ=0):
        """expression of the decoder inside an encoding `enc`: the `occ`-th occurrence of the decoder
        variable in the root pattern's encoding side (shallowest first)."""
        if occ >= len(self.decpaths): raise Infeasible()
        path = self.decpaths[occ]
        e = enc
        for step in path:
            conds.append(('TG', e))
            e = ('A1', e) if step == 0 else ('A2', e)
        return e

    def paths_to(self, v, p, path=()):
        """ALL paths at which variable v occurs in pattern p, shallowest first"""
        if isinstance(p, str): return [path] if p == v else []
        out = self.paths_to(v, p[0], path + (0,)) + self.paths_to(v, p[1], path + (1,))
        out.sort(key=len)
        return out

    def path_to(self, v, p, path=()):
        if isinstance(p, str): return path if p == v else None
        for i in (0, 1):
            r = self.path_to(v, p[i], path + (i,))
            if r is not None: return r
        return None

    def unify(self, p, s, q, r, conds, ppath=None, choices=None, qpath=None):
        """eval(p, s) = eval(q, r): p is a law pattern under env s, q a root-pattern under env r.
        A compound law-side node whose mode (choices[ppath]) is not `free` is DECODED: it is unified as its
        nested-op value (when determined), not decomposed as a free product — the mode the 5837/33020/23357
        holes needed (a decoded product inside the struct-decoded root of the encoding)."""
        if not isinstance(p, str) and ppath is not None and choices is not None and choices.get(ppath, 'free') != 'free':
            e = self.val(p, s, ppath, choices, conds)
            if e is not None:
                self.unify_expr(q, e, r, conds); return
        qc0 = None if qpath is None else qpath + (0,)
        qc1 = None if qpath is None else qpath + (1,)
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
                if qpath is not None and qpath in self.rdec:
                    self.rdefer.append((q, e, r)); return
                if e[0] == 'F':
                    v = self.val(q, r)
                    if v is not None:
                        assign(e, v); return
                    # refine the placeholder structurally: F := J(F1, F2)
                    f1, f2 = self.fresh(), self.fresh(); assign(e, ('J', f1, f2))
                    r1 = Env(); r1.b = r.b; r1.parent = r.parent
                    self.unify_expr(q[0], f1, r, conds, qc0)
                    self.unify_expr(q[1], f2, r, conds, qc1)
                    return
                conds.append(('TG', e))
                self.unify_expr(q[0], ('A1', e), r, conds, qc0)
                self.unify_expr(q[1], ('A2', e), r, conds, qc1)
            else:
                v = self.val(q, r)
                if v is not None: s.bind(p, v, conds)
                else:
                    f1, f2 = self.fresh(), self.fresh(); s.bind(p, ('J', f1, f2), conds)
                    self.unify_expr(q[0], f1, r, conds, qc0); self.unify_expr(q[1], f2, r, conds, qc1)
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
        cp0 = None if ppath is None else ppath + (0,)
        cp1 = None if ppath is None else ppath + (1,)
        self.unify(p[0], s, q[0], r, conds, ppath=cp0, choices=choices, qpath=qc0)
        self.unify(p[1], s, q[1], r, conds, ppath=cp1, choices=choices, qpath=qc1)

    def unify_expr(self, q, e, r, conds, rpath=None):
        """pattern q under env r equals expression e.  A compound q is read freely (e is a J whose children match)
        unless its root-pattern path `rpath` is in self.rdec: then q's value is DECODED - op(q[0], q[1]) under r
        equals e - recorded as a deferred guard, resolved once r's variables are bound (the both-compound
        24200 shape: the encoding x = J(op(w, z'), z') has its inner product decoded)."""
        e = subst(e)
        if isinstance(q, str):
            r.bind(q, e, conds); return
        if rpath is not None and rpath in self.rdec:
            self.rdefer.append((q, e, r)); return
        c0 = None if rpath is None else rpath + (0,)
        c1 = None if rpath is None else rpath + (1,)
        if e[0] == 'F':
            f1, f2 = self.fresh(), self.fresh(); assign(e, ('J', f1, f2))
            self.unify_expr(q[0], f1, r, conds, c0); self.unify_expr(q[1], f2, r, conds, c1); return
        if e[0] == 'J':
            self.unify_expr(q[0], e[1], r, conds, c0); self.unify_expr(q[1], e[2], r, conds, c1); return
        conds.append(('TG', e))
        self.unify_expr(q[0], ('A1', e), r, conds, c0)
        self.unify_expr(q[1], ('A2', e), r, conds, c1)

    def resolve_rdefer(self, conds):
        """deferred root-side decodes: op(q[0], q[1]) under r must now be determined"""
        pending = self.rdefer; self.rdefer = []
        for q, e, r in pending:
            v = self.val(q, r)
            if v is None or has_free(v): raise Infeasible()
            conds.append(('OPEQ', v, e))

    def one_rule(self, choices):
        nodes = [('A',) + path for path, _ in positions(self.A)] + [('B',) + path for path, _ in positions(self.B)]
        D = {p for p, m in choices.items() if p[0] in ('A', 'B') and m in ('lazy', 'struct', 'exist')}
        env = Env(); conds = []
        SUBST.clear(); self.nfree = 0; self.used_lazy = set(); self.soft = []
        self.rdec = set(choices.get(('RD',), ())); self.rdefer = []
        deferred = []
        for pat, root, side in ((self.A, ('U',), 'A'), (self.B, ('V',), 'B')):
            if isinstance(pat, str): env.bind(pat, root, conds)
            else: self.traverse(pat, (side,), root, env, D, conds, choices, deferred)
        self.run_deferred(deferred, env, D, conds, choices)
        x = env.get('x')
        if x is None or has_free(x): raise Infeasible()
        soft = [(c[0],) + tuple(subst(e) for e in c[1:]) for c in self.soft]
        conds = self.simplify([(c[0],) + tuple(subst(e) for e in c[1:]) for c in conds])
        self.last_soft = [c for c in conds if c in soft]
        return conds, subst(x), set(self.used_lazy)

    def rules(self, exist=False, level2=True, cap2=64, softdrop=True, decocc=True):
        """softdrop: for every struct-mode rule also emit, LAST in the order, the variant without the redundant
        evaluation guard (the guard is implied by the structure whenever the inner products are free; keeping only
        the guarded form loses readings whose guard pair is not below the msr gate — 6912, y = S*(a*S))."""
        nodes = [('A',) + path for path, _ in positions(self.A)] + [('B',) + path for path, _ in positions(self.B)]
        modes = (['free', 'lazy', 'struct', 'vdec'] + (['exist'] if exist else [])) if (self.lform or self.rform) else ['free', 'struct']
        encpat = self.B if self.lform else self.A
        encnodes = [p for p, _ in positions(encpat)] if not isinstance(encpat, str) else []
        out = []; late = []
        # root-side decoded node sets: internal nodes of A and B below their roots, at most 2 at a time
        rnodes = [('A',) + path for path, _ in positions(self.A) if path] + [('B',) + path for path, _ in positions(self.B) if path]
        rdsets = [()] + [(n,) for n in rnodes] + [c for c in itertools.combinations(rnodes, 2)]
        for mode in itertools.product(modes, repeat=len(nodes)):
            base = dict(zip(nodes, mode))
            rds = [()] if all(m == 'free' for m in mode) else rdsets
            used = None
            for rd in rds:
                choices = dict(base)
                if rd: choices[('RD',)] = rd
                try:
                    conds, x, used_rd = self.one_rule(choices)
                except Infeasible:
                    continue
                if not rd: used = used_rd
                tag = ','.join((''.join(map(str, p)) or 'e') + m[0] for p, m in base.items() if m != 'free') or 'free'
                if rd: tag += '|rd:' + ';'.join(''.join(map(str, p)) for p in rd)
                out.append((conds, x, tag))
                if softdrop and self.last_soft:
                    soft = set(self.last_soft)
                    late.append(([c for c in conds if c not in soft], x, tag + '~'))
            choices = base
            tag = ','.join((''.join(map(str, p)) or 'e') + m[0] for p, m in base.items() if m != 'free') or 'free'
            # FIX-3: the same rule with the decoder read at each OTHER occurrence of the decoder variable
            if decocc and used and len(self.decpaths) > 1:
                uu = sorted(used)[:2]
                for occ in itertools.product(range(len(self.decpaths)), repeat=len(uu)):
                    if all(o == 0 for o in occ): continue
                    chd = dict(base)
                    for pth, o in zip(uu, occ): chd[('DECOCC',) + pth] = o
                    for rd in rds:
                        chr_ = dict(chd)
                        if rd: chr_[('RD',)] = rd
                        try:
                            conds, x, _u = self.one_rule(chr_)
                        except Infeasible:
                            continue
                        t = tag + '|dec:' + ''.join(map(str, occ))
                        if rd: t += '|rd:' + ';'.join(''.join(map(str, pp)) for pp in rd)
                        out.append((conds, x, t))
                        if softdrop and self.last_soft:
                            soft = set(self.last_soft)
                            late.append(([c for c in conds if c not in soft], x, t + '~'))
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
        return prune(out + late)

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

GATE = 'msr'   # 'msr': max^2 + sum (the 5107 template);  'lex': lexicographic (size of the ENCODING = right arg, size of the decoder)

def msr(a, b):
    m = max(size(a), size(b))
    return m * m + size(a) + size(b)

def gate_ok(a, b, u, v):
    """may op(a, b) be evaluated inside op(u, v)?  (the well-founded recursion's guard)"""
    if GATE == 'lex':
        sb, sv = size(b), size(v)
        return sb < sv or (sb == sv and size(a) < size(u))
    return msr(a, b) < msr(u, v)

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
            if not gate_ok(a, b, u, v): return None   # the Lean definition's size gate
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

def terms_upto(maxsize, gens):
    """every free-magma term of size <= maxsize over `gens` generators (J-trees, not values)"""
    by = {1: [('g', i) for i in range(gens)]}
    for n in range(3, maxsize + 1, 2):
        by[n] = []
        for a in range(1, n - 1, 2):
            b = n - 1 - a
            if b in by:
                for t1 in by[a]:
                    for t2 in by[b]:
                        by[n].append(('J', t1, t2))
    out = []
    for n in sorted(by): out += by[n]
    return out

def firing_rule(C, u, v):
    for i, (conds, x, tag) in enumerate(C.rules):
        if C.check(conds, u, v):
            r = C.ev(x, u, v)
            if r is not None: return i
    return None

def drop_unsound(law, rules, maxsize=7, gens=2, verbose=False):
    """FIX-4 (soundness filter).  A rule that FIRES on a small pair and returns something other than the
    SEMANTIC free model's answer is wrong, full stop; drop it (greedily, worst first, re-checking after
    each drop).  This is not a heuristic: `freemodel.Free` is the object the rule system is supposed to
    be a closed form of.

    Motivation, measured on 34889 (`x = ((y*y)*((x*z)*x))*z`, dualised): `rules(softdrop=True)` emits the
    struct rule WITHOUT its evaluation guard, on the theory that the guard is implied by the structure
    whenever the inner products are free.  It is not: on u=(g0*((g0*g0)*g0)), v=(g0*(g0*g0)) the softdrop
    rule `B0l~` fires and returns (g0*g0) where the free model has the free product -- 6 such pairs of
    size <= 7 over 2 generators, 8 over 1..2 generators.  Dropping it removes every disagreement.
    Softdrop rules exist to recover gate-cut readings (6912), so they are kept by default and filtered
    here instead of being switched off.

    Only rules that fire wrongly can be dropped; a pair where NO rule fires and the free model reads a
    value is a missing mode, not an unsound rule, and is left alone (it shows in the return value)."""
    F = fm.Free(law)
    pool = terms_upto(maxsize, gens)
    keep = list(rules)
    dropped = []
    holes = 0
    for _ in range(len(rules)):
        C = Closed(law, keep)
        bad = {}; holes = 0
        for u in pool:
            for v in pool:
                try:
                    fr = F.op(u, v)
                except Exception:
                    continue
                try:
                    cr = C.op(u, v)
                except RecursionError:
                    continue
                if cr == fr: continue
                i = firing_rule(C, u, v)
                if i is None: holes += 1
                else: bad[i] = bad.get(i, 0) + 1
        if not bad: break
        worst = max(bad, key=lambda k: bad[k])
        if verbose: print('  drop unsound rule %d [%s] (%d wrong pairs)' % (worst, keep[worst][2], bad[worst]))
        dropped.append(keep[worst][2])
        keep = [r for j, r in enumerate(keep) if j != worst]
    return keep, dropped, holes

def first_bad_rule(law, keep, F, s, C=None):
    """evaluate the law's pattern under assignment s in the closed form and in the semantic free model;
    at the first product where they differ AND a rule fired, return that rule's index (else None)."""
    C = C or Closed(law, keep)
    bad = [None]
    def go(p):
        if isinstance(p, str): return s[p], s[p]
        ca, fa = go(p[0]); cb, fb = go(p[1])
        try:
            cr = C.op(ca, cb)
        except RecursionError:
            raise Infeasible()
        try:
            fr = F.op(fa, fb)
        except Exception:
            raise Infeasible()
        if cr != fr and bad[0] is None:
            i = firing_rule(C, ca, cb)
            if i is not None: bad[0] = i
        return cr, fr
    A, B = law[1]
    try:
        ua, uf = go(A); va, vf = go(B)
        cr = C.op(ua, va); fr = F.op(uf, vf)
        if cr != fr and bad[0] is None:
            i = firing_rule(C, ua, va)
            if i is not None: bad[0] = i
    except Infeasible:
        pass
    except RecursionError:
        pass
    return bad[0]

def drop_unsound_deep(law, rules, N=1500, secs=60, seeds=(11, 22, 33, 96844, 4444), maxrounds=8, verbose=False):
    """FIX-4b: the small-pair filter (`drop_unsound`) only sees terms of size <= 7.  Some unsound rules only
    misbehave on the deep nested instances `deep_tests` builds -- 32281's legacy-occurrence rule and 8485's
    are both of that kind.  Here: run deep_tests on the closed model; for each failing law instance replay
    its evaluation chain against the SEMANTIC free model and drop the rule that fired at the first product
    where they differ.  Repeat.  A failure at which NO rule fired is a missing mode, not an unsound rule,
    and stops the loop (nothing to drop)."""
    import fuzz as fz
    F = fm.Free(law)
    keep = list(rules); dropped = []
    for _ in range(maxrounds):
        bad = None
        for sd in seeds:
            gens = []
            C = Closed(law, keep)
            gens.append(deep_tests(C, law, N, secs, sd)[1])
            gens.append(fz.fuzz(Closed(law, keep), law, keep, N * 3, seed=sd + 100)[1])
            gens.append(fz.closure_fuzz(Closed(law, keep), law, N * 3, seed=sd + 200)[1])
            gens.append(fz.critical_fuzz(Closed(law, keep), law, N * 3, seed=sd + 300)[1])
            for f in gens:
                for st, r in f:
                    if r == 'recursion': continue
                    i = first_bad_rule(law, keep, F, st)
                    if i is not None:
                        bad = i; break
                if bad is not None: break
            if bad is not None: break
        if bad is None: break
        if verbose: print('  drop deep-unsound rule %d [%s]' % (bad, keep[bad][2]))
        dropped.append(keep[bad][2])
        keep = [r for j, r in enumerate(keep) if j != bad]
    return keep, dropped

def extract(law, sound=True, maxsize=7, gens=2, deep=True, deepN=1500, **kw):
    """the recommended entry point: Extractor(law).rules(**kw) followed by the soundness filter.
    Returns (rules, info)."""
    rules = Extractor(law).rules(**kw)
    n0 = len(rules)
    if not sound:
        return rules, dict(nrules=n0, dropped=[], holes=None)
    keep, dropped, holes = drop_unsound(law, rules, maxsize, gens)
    ddropped = []
    if deep:
        keep, ddropped = drop_unsound_deep(law, keep, N=deepN)
    return keep, dict(nrules0=n0, nrules=len(keep), dropped=dropped + ddropped,
                      dropped_small=dropped, dropped_deep=ddropped, small_pair_holes=holes)

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
