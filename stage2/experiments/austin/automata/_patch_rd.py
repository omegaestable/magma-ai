p = 'closedform.py'; s = open(p, encoding='utf-8').read()
old = '''    def unify_expr(self, q, e, r, conds):
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
        self.unify_expr(q[1], ('A2', e), r, conds)'''
new = '''    def unify_expr(self, q, e, r, conds, rpath=None):
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
            conds.append(('OPEQ', v, e))'''
assert old in s; s = s.replace(old, new)
old2 = '''            if s.bound(p):
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
            return'''
new2 = '''            if s.bound(p):
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
            return'''
assert old2 in s; s = s.replace(old2, new2)
old3 = '''        if isinstance(p, str) and isinstance(q, str):
            bp, bq = s.bound(p), r.bound(q)'''
new3 = '''        qc0 = None if qpath is None else qpath + (0,)
        qc1 = None if qpath is None else qpath + (1,)
        if isinstance(p, str) and isinstance(q, str):
            bp, bq = s.bound(p), r.bound(q)'''
assert old3 in s; s = s.replace(old3, new3)
old4 = '''    def unify(self, p, s, q, r, conds, ppath=None, choices=None):'''
new4 = '''    def unify(self, p, s, q, r, conds, ppath=None, choices=None, qpath=None):'''
assert old4 in s; s = s.replace(old4, new4)
old5 = '''        cp0 = None if ppath is None else ppath + (0,)
        cp1 = None if ppath is None else ppath + (1,)
        self.unify(p[0], s, q[0], r, conds, ppath=cp0, choices=choices)
        self.unify(p[1], s, q[1], r, conds, ppath=cp1, choices=choices)'''
new5 = '''        cp0 = None if ppath is None else ppath + (0,)
        cp1 = None if ppath is None else ppath + (1,)
        self.unify(p[0], s, q[0], r, conds, ppath=cp0, choices=choices, qpath=qc0)
        self.unify(p[1], s, q[1], r, conds, ppath=cp1, choices=choices, qpath=qc1)'''
assert old5 in s; s = s.replace(old5, new5)
old6 = '''        order = [(P, self.A, path + (0,)), (Q, self.B, path + (1,))]
        if vP is None and vQ is not None: order = [(Q, self.B, path + (1,)), (P, self.A, path + (0,))]
        for pp, qq, ppath in order:
            self.unify(pp, env, qq, r, conds, ppath=ppath, choices=choices)
        vP2, vQ2 = self.val(P, env, path + (0,), choices, conds), self.val(Q, env, path + (1,), choices, conds)'''
new6 = '''        order = [(P, self.A, path + (0,), ('A',)), (Q, self.B, path + (1,), ('B',))]
        if vP is None and vQ is not None: order = [(Q, self.B, path + (1,), ('B',)), (P, self.A, path + (0,), ('A',))]
        for pp, qq, ppath, qpath in order:
            self.unify(pp, env, qq, r, conds, ppath=ppath, choices=choices, qpath=qpath)
        self.resolve_rdefer(conds)
        vP2, vQ2 = self.val(P, env, path + (0,), choices, conds), self.val(Q, env, path + (1,), choices, conds)'''
assert old6 in s; s = s.replace(old6, new6)
old7 = '''        env = Env(); conds = []
        SUBST.clear(); self.nfree = 0; self.used_lazy = set(); self.soft = []
        deferred = []'''
new7 = '''        env = Env(); conds = []
        SUBST.clear(); self.nfree = 0; self.used_lazy = set(); self.soft = []
        self.rdec = set(choices.get(('RD',), ())); self.rdefer = []
        deferred = []'''
assert old7 in s; s = s.replace(old7, new7)
old8 = '''        out = []; late = []
        for mode in itertools.product(modes, repeat=len(nodes)):
            choices = dict(zip(nodes, mode))
            try:
                conds, x, used = self.one_rule(choices)
            except Infeasible:
                continue
            tag = ','.join((''.join(map(str, p)) or 'e') + m[0] for p, m in choices.items() if m != 'free') or 'free'
            out.append((conds, x, tag))
            if softdrop and self.last_soft:
                soft = set(self.last_soft)
                late.append(([c for c in conds if c not in soft], x, tag + '~'))
            if not level2 or not used: continue
            used = sorted(used)[:2]
            subs = list(itertools.product(['free', 'lazy'], repeat=len(encnodes)))'''
new8 = '''        out = []; late = []
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
            if not level2 or not used: continue
            used = sorted(used)[:2]
            subs = list(itertools.product(['free', 'lazy'], repeat=len(encnodes)))'''
assert old8 in s; s = s.replace(old8, new8)
open(p, 'w', encoding='utf-8', newline='\n').write(s); print('root-side decoded modes added')
