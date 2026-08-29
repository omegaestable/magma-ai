import re
src = open('closedform.py', encoding='utf-8').read()

old = '''        if self.lform and vQ is not None and vP is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_expr(vQ, conds)
            conds.append(('OPEQ', ('OP', dec, vQ), w))
            self.traverse(P, path + (0,), dec, env, D, conds, choices)
            return
        if self.rform and vP is not None and vQ is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_expr(vP, conds)
            conds.append(('OPEQ', ('OP', vP, dec), w))
            self.traverse(Q, path + (1,), dec, env, D, conds, choices)
            return'''
new = '''        if self.lform and vQ is not None and vP is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_of(vQ, w, path, conds, choices)
            if dec is None: raise Infeasible()
            if has_free(dec):
                # existential decoder: no op-guard (the structural conditions say it all)
                self.traverse(P, path + (0,), dec, env, D, conds, choices)
                return
            conds.append(('OPEQ', ('OP', dec, vQ), w))
            self.traverse(P, path + (0,), dec, env, D, conds, choices)
            return
        if self.rform and vP is not None and vQ is None and choices.get(path, 'lazy') == 'lazy':
            dec = self.decoder_of(vP, w, path, conds, choices)
            if dec is None: raise Infeasible()
            if has_free(dec):
                self.traverse(Q, path + (1,), dec, env, D, conds, choices)
                return
            conds.append(('OPEQ', ('OP', vP, dec), w))
            self.traverse(Q, path + (1,), dec, env, D, conds, choices)
            return'''
assert old in src; src = src.replace(old, new)

old2 = '''    def decoder_expr(self, enc, conds):
        """expression of the decoder inside an encoding `enc` (path to the first y in the root pattern)"""
        pat = self.B if self.lform else self.A'''
new2 = '''    def decoder_of(self, enc, w, path, conds, choices):
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
        pat = self.B if self.lform else self.A'''
assert old2 in src; src = src.replace(old2, new2)

start = src.index('    def rules(self, exist=False):')
end = src.index('        seen = set(); uniq = []')
new4 = '''    def one_rule(self, choices):
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
'''
src = src[:start] + new4 + src[end:]
open('closedform.py', 'w', encoding='utf-8').write(src)
print('patched')
