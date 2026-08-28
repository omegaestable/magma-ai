"""Tagged partial term models (Kisielewicz-style, generic).

Law: x = T(x, ybar). Sub-patterns: the proper non-variable subterms of T, taken
up to variable renaming (canonical shapes).

Elements:  ('L', i) generators, ('J',) junk, ('n', shape, a, b) tagged nodes.
op(a, b):
   1. if (a, b) instantiates T = T1 ◇ T2 consistently -> return the x-binding
   2. else the most specific proper sub-pattern P = P1 ◇ P2 that (a, b)
      instantiates consistently -> ('n', P, a, b)
   3. else junk
`a ⊨ P`: P a variable -> anything; P a node -> a is a node whose shape is P.

eq1 is checked EXHAUSTIVELY over all assignments drawn from the set of
elements reachable by op from k generators + junk up to depth D.
"""
from __future__ import annotations
import json, sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from austin_z3 import parse, variables  # noqa: E402
from term_model import to_term, positions  # noqa: E402

JUNK = ('J',)


def canon(pat, names=None):
    names = {} if names is None else names
    if pat[0] == 'v':
        if pat[1] not in names:
            names[pat[1]] = f'p{len(names)}'
        return ('v', names[pat[1]])
    return ('n', canon(pat[1], names), canon(pat[2], names))


def psize(p):
    return 1 if p[0] == 'v' else 1 + psize(p[1]) + psize(p[2])


class Tagged:
    def __init__(self, text, policy='root_first'):
        l, r = parse(text)
        self.x = l[1]
        self.T = to_term(r)
        self.vars = variables(l, variables(r, []))
        subs = {}
        for pos, t in positions(self.T):
            if pos:
                subs[canon(t)] = t
        # most specific first
        self.subpats = sorted(subs.keys(), key=lambda p: -psize(p))
        self.policy = policy

    def fits(self, elem, pat, bind):
        """Does elem instantiate pattern pat (canonical or raw)? Records bindings."""
        if pat[0] == 'v':
            prev = bind.get(pat[1])
            if prev is None:
                bind[pat[1]] = elem
                return True
            return prev == elem
        if elem[0] != 'n':
            return False
        if elem[1] != canon(pat):
            return False
        # same shape: bind pattern variables from the element's leaves
        return self.fits(elem[2], pat[1], bind) and self.fits(elem[3], pat[2], bind)

    def op(self, a, b):
        # 1. root
        bind = {}
        if self.fits(a, self.T[1], bind) and self.fits(b, self.T[2], bind):
            return bind[self.x]
        # 2. most specific sub-pattern
        for P in self.subpats:
            bind = {}
            if self.fits(a, P[1], bind) and self.fits(b, P[2], bind):
                return ('n', P, a, b)
        return JUNK

    def universe(self, gens=2, depth=2):
        elems = {('L', i) for i in range(gens)} | {JUNK}
        frontier = set(elems)
        for _ in range(depth):
            new = set()
            for a in elems:
                for b in elems:
                    e = self.op(a, b)
                    if e not in elems:
                        new.add(e)
            elems |= new
            if not new:
                break
        return sorted(elems, key=lambda e: (len(str(e)), str(e)))

    def check_law(self, elems, limit=None):
        bad = []
        for vals in itertools.product(elems, repeat=len(self.vars)):
            env = dict(zip(self.vars, vals))
            got = self.eval(self.T, env)
            if got != env[self.x]:
                bad.append((env, got))
                if limit and len(bad) >= limit:
                    break
        return bad

    def eval(self, t, env):
        if t[0] == 'v':
            return env[t[1]]
        return self.op(self.eval(t[1], env), self.eval(t[2], env))

    def refute(self, eq2_text, elems):
        l, r = parse(eq2_text)
        l, r = to_term(l), to_term(r)
        vs = variables(parse(eq2_text)[0], variables(parse(eq2_text)[1], []))
        gens = [e for e in elems if e[0] == 'L']
        for vals in itertools.product(gens + [JUNK], repeat=len(vs)):
            env = dict(zip(vs, vals))
            if self.eval(l, env) != self.eval(r, env):
                return env
        for vals in itertools.product(elems[:40], repeat=len(vs)):
            env = dict(zip(vs, vals))
            if self.eval(l, env) != self.eval(r, env):
                return env
        return None


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    depth = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    groups = {}
    for r in rows:
        groups.setdefault(r['equation1'], []).append(r)
    total_ok = 0
    for eq1_text, rs in groups.items():
        m = Tagged(eq1_text)
        elems = m.universe(gens=2, depth=depth)
        bad = m.check_law(elems, limit=1)
        tag = rs[0].get('eq1_id', rs[0]['id'])
        if bad:
            env, got = bad[0]
            print(f"{tag}: {eq1_text} | {len(elems)} elems | VIOLATION e.g. {dict((k,str(v)[:40]) for k,v in env.items())} -> {str(got)[:40]}", flush=True)
            continue
        refs = []
        for r in rs:
            env = m.refute(r['equation2'], elems)
            refs.append((r['id'], 'refuted' if env is not None else 'eq2 holds on sample'))
        total_ok += 1
        print(f"{tag}: {eq1_text} | {len(elems)} elems | eq1 HOLDS exhaustively | {refs}", flush=True)
    print('laws with a valid tagged model:', total_ok, '/', len(groups))


if __name__ == '__main__':
    main()
