"""Tag-automaton models for collapsing laws x = T(x, ybar) (Kisielewicz-style, generic).

Carrier: leaves ('L', i), junk ('J',), stage nodes ('S', tag, payload) where
tag names a compound subterm U of T and payload is the tuple of values of U's
variables (in a fixed order).

Rules: for each compound subterm U = A ◇ B of T (root included), a rule keyed
on (key(A), key(B)) where key(child) is ('var', v) for a variable (bound, with
an equality guard if v is already bound), ('tag', t) for a compound child, or
('any',) for an *ignored* child. Result: ('S', tag(U), payload) or, for the
root, the value bound to x. A pure-variable product p ◇ q (p != q) off the
spine is ignored iff every consumer keys on its other (compound) side; its
value is then irrelevant and it is junk. v ◇ v products are never ignored:
the guard a = b makes them recognisable (Kisielewicz's square rule).
Everything unmatched -> junk.

Search: rule order by specificity (optionally v ◇ v rules first), the law
checked EXHAUSTIVELY over the universe reachable from 3 leaves + junk in two
op-steps, derailments repaired by adding a top-priority rule keyed on the tag
shapes of the offending pair that returns the intended stage element
(expressed via projections of the pair), iterated with dedupe.
"""
from __future__ import annotations
import json, sys, itertools
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from austin_z3 import parse, variables  # noqa: E402
from term_model import to_term  # noqa: E402

JUNK = ('J',)


def tvars(t, out=None):
    out = [] if out is None else out
    if t[0] == 'v':
        if t[1] not in out:
            out.append(t[1])
    else:
        tvars(t[1], out); tvars(t[2], out)
    return out


def subterms(t, pos=()):
    if t[0] == 'v':
        return []
    return [(pos, t)] + subterms(t[1], pos + (1,)) + subterms(t[2], pos + (2,))


def find_x(t, x, pos=()):
    if t[0] == 'v':
        return [pos] if t[1] == x else []
    return find_x(t[1], x, pos + (1,)) + find_x(t[2], x, pos + (2,))


class Automaton:
    def __init__(self, text, guards=True, square_first=False, spine_choice=0):
        l, r = parse(text)
        self.x = l[1]
        self.T = to_term(r)
        self.vars = variables(l, variables(r, []))
        xs = find_x(self.T, self.x)
        self.xpos = xs[spine_choice % len(xs)]
        self.spine = set(self.xpos[:k] for k in range(len(self.xpos)))
        self.tag_of, self.term_of = {}, {}
        for pos, t in subterms(self.T):
            if pos != () and t not in self.tag_of:
                name = f's{len(self.tag_of)}'
                self.tag_of[t] = name
                self.term_of[name] = t
        parents = {}
        for pos, t in subterms(self.T):
            for i in (1, 2):
                if t[i][0] == 'n':
                    parents.setdefault(t[i], []).append(t[3 - i])
        self.ignored = set()
        for pos, t in subterms(self.T):
            if (pos != () and t[1][0] == 'v' and t[2][0] == 'v' and t[1] != t[2]
                    and pos not in self.spine
                    and all(o[0] == 'n' for o in parents.get(t, []))):
                self.ignored.add(t)
        self.guards = guards
        self.square_first = square_first
        self.rules = self._base_rules()

    def _key(self, child):
        if child[0] == 'v':
            return ('var', child[1])
        if child in self.ignored:
            return ('any',)
        return ('tag', self.tag_of[child])

    def _base_rules(self):
        rules = []
        for pos, t in subterms(self.T):
            if t in self.ignored:
                continue
            kl, kr = self._key(t[1]), self._key(t[2])
            result = 'ROOT' if pos == () else self.tag_of[t]
            rules.append({'left': kl, 'right': kr, 'term': t, 'result': result,
                          'spec': (kl[0] == 'tag') + (kr[0] == 'tag'), 'size': len(str(t))})

        def is_square(r):
            return r['term'][1][0] == 'v' and r['term'][1] == r['term'][2]
        rules.sort(key=lambda r: (-(self.square_first and is_square(r)), -r['spec'], -r['size']))
        return rules

    def payload_vars(self, tag):
        return tvars(self.term_of[tag])

    def _bind(self, key, elem, bind):
        kind = key[0]
        if kind == 'any':
            return True
        if kind == 'var':
            v = key[1]
            if v in bind and self.guards and bind[v] != elem:
                return False
            bind.setdefault(v, elem)
            return True
        tag = key[1]
        if elem[0] != 'S' or elem[1] != tag:
            return False
        for v, val in zip(self.payload_vars(tag), elem[2]):
            if v in bind and self.guards and bind[v] != val:
                return False
            bind.setdefault(v, val)
        return True

    def op(self, a, b):
        for r in self.rules:
            if r.get('repair'):
                got = r['fn'](a, b)
                if got is not None:
                    return got
                continue
            bind = {}
            if self._bind(r['left'], a, bind) and self._bind(r['right'], b, bind):
                if r['result'] == 'ROOT':
                    return bind.get(self.x, JUNK)
                tag = r['result']
                return ('S', tag, tuple(bind.get(v, JUNK) for v in self.payload_vars(tag)))
        return JUNK

    def eval(self, t, env):
        if t[0] == 'v':
            return env[t[1]]
        return self.op(self.eval(t[1], env), self.eval(t[2], env))

    def universe(self, leaves=3, depth=2, cap=250):
        elems = {('L', i) for i in range(leaves)} | {JUNK}
        for _ in range(depth):
            new = set()
            lst = list(elems)
            for a in lst:
                for b in lst:
                    e = self.op(a, b)
                    if e not in elems:
                        new.add(e)
            elems |= new
            if len(elems) > cap:
                break
        return sorted(elems, key=lambda e: (len(str(e)), str(e)))[:cap]

    def check(self, elems, limit=1):
        bad = []
        for vals in itertools.product(elems, repeat=len(self.vars)):
            env = dict(zip(self.vars, vals))
            got = self.eval(self.T, env)
            if got != env[self.x]:
                bad.append((env, got))
                if len(bad) >= limit:
                    return bad
        return bad

    def refute(self, eq2_text, elems):
        l, r = parse(eq2_text)
        l, r = to_term(l), to_term(r)
        vs = variables(parse(eq2_text)[0], variables(parse(eq2_text)[1], []))
        for vals in itertools.product(elems[:16], repeat=len(vs)):
            env = dict(zip(vs, vals))
            if self.eval(l, env) != self.eval(r, env):
                return env
        return None


def shape(e, depth=2):
    if e[0] != 'S' or depth == 0:
        return e[0]
    return (e[1],) + tuple(shape(p, depth - 1) for p in e[2])


def _paths(e, prefix):
    out = [(prefix, e)]
    if e[0] == 'S':
        for i, p in enumerate(e[2]):
            out += _paths(p, prefix + (i,))
    return out


def _projection(target, a, b):
    avail = {}
    for path, sub in _paths(a, ('a',)) + _paths(b, ('b',)):
        avail.setdefault(sub, path)

    def build(t):
        if t in avail:
            return ('proj', avail[t])
        if t[0] == 'S':
            parts = [build(p) for p in t[2]]
            if any(p is None for p in parts):
                return None
            return ('mk', t[1], parts)
        if t[0] == 'J':
            return ('junk',)
        return None
    plan = build(target)
    if plan is None:
        return None

    def run(plan, a, b):
        if plan[0] == 'proj':
            e = a if plan[1][0] == 'a' else b
            for i in plan[1][1:]:
                e = e[2][i]
            return e
        if plan[0] == 'junk':
            return JUNK
        return ('S', plan[1], tuple(run(p, a, b) for p in plan[2]))
    return (lambda x, y: run(plan, x, y)), plan


def repair(A, env):
    """First derailed spine node -> a top-priority rule on the pair's tag shapes."""
    path = A.xpos
    for k in range(len(path) - 1, -1, -1):
        pos = path[:k]
        t = A.T
        for p in pos:
            t = t[p]
        if t[0] == 'v':
            continue
        a = A.eval(t[1], env); b = A.eval(t[2], env)
        actual = A.op(a, b)
        if pos == ():
            intended = env[A.x]
        else:
            tag = A.tag_of[t]
            intended = ('S', tag, tuple(env[v] for v in A.payload_vars(tag)))
        if actual == intended:
            continue
        proj = _projection(intended, a, b)
        if proj is None:
            return False
        fn, plan = proj
        sa, sb = shape(a), shape(b)
        desc = f'{sa} ◇ {sb} -> {plan}'
        if any(r.get('repair') and r['desc'] == desc for r in A.rules):
            return False

        def rfn(x, y, sa=sa, sb=sb, fn=fn):
            if shape(x) == sa and shape(y) == sb:
                try:
                    return fn(x, y)
                except Exception:
                    return None
            return None
        A.rules.insert(0, {'repair': True, 'fn': rfn, 'desc': desc})
        return True
    return False


def search(text, eq2_texts, max_repairs=12):
    l, _ = parse(text)
    nspines = len(find_x(to_term(parse(text)[1]), l[1]))
    for spine_choice in range(nspines):
        for square_first in (False, True):
            for guards in (True, False):
                A = Automaton(text, guards=guards, square_first=square_first, spine_choice=spine_choice)
                for rnd in range(max_repairs + 1):
                    elems = A.universe()
                    bad = A.check(elems)
                    if not bad:
                        refs = {t: A.refute(t, elems) is not None for t in eq2_texts}
                        return A, elems, refs, rnd
                    if not repair(A, bad[0][0]):
                        break
    return None


def main():
    rows = [json.loads(l) for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    groups = {}
    for r in rows:
        groups.setdefault(r['equation1'], []).append(r)
    wins = 0
    results = []
    for eq1_text, rs in groups.items():
        tag = rs[0].get('eq1_id', rs[0]['id'])
        eq2s = sorted({r['equation2'] for r in rs})
        found = search(eq1_text, eq2s)
        if found is None:
            print(f"{tag}: {eq1_text} | no model", flush=True)
            continue
        A, elems, refs, rnd = found
        wins += 1
        repairs = [r['desc'] for r in A.rules if r.get('repair')]
        print(f"{tag}: {eq1_text} | MODEL guards={A.guards} sqfirst={A.square_first} spine={A.xpos} repairs={len(repairs)} elems={len(elems)} | refutes {refs}", flush=True)
        results.append({'eq1': eq1_text, 'guards': A.guards, 'square_first': A.square_first,
                        'spine': A.xpos, 'repairs': repairs, 'refutes': refs})
    print('laws with a tag-automaton model:', wins, '/', len(groups))
    if len(sys.argv) > 2:
        json.dump(results, open(sys.argv[2], 'w'), indent=1)


if __name__ == '__main__':
    main()
