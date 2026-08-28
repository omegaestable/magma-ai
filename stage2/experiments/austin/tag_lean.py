"""Render a tag-automaton model (no repairs) as a Lean 4 FALSE certificate.

Carrier: inductive with `leaf : Nat -> M`, `junk : M`, and one constructor per
tag with arity = number of payload variables. `op` is a chain of `Option`
helpers in rule order (a failed guard falls through, as in the Python search).
eq1: `cases` on every variable, then simp with the definitions plus
"no-fixpoint" lemmas (a term never equals a constructor applied to itself),
then `split_ifs` on the remaining undecidable guards. not-eq2: a concrete
refuting instance closed by `decide`.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tag_automaton import Automaton  # noqa: E402


def lean_elem(e):
    if e[0] == 'L':
        return f'(.leaf {e[1]})'
    if e[0] == 'J':
        return '.junk'
    return '(.' + e[1] + ''.join(' ' + lean_elem(p) for p in e[2]) + ')'


def text_order(text):
    seen, out = set(), []
    for v in re.findall(r'[A-Za-z][A-Za-z0-9]*', text):
        if v not in seen:
            seen.add(v); out.append(v)
    return out


def A_terms(A):
    return ('v', A.x), A.T


def rule_arms(A):
    arms = []
    for r in A.rules:
        if r.get('repair'):
            raise ValueError('repairs not supported in the Lean renderer yet')
        names = {}
        fresh = [0]

        def binder(v):
            fresh[0] += 1
            n = f'{v}{fresh[0]}'
            names.setdefault(v, []).append(n)
            return n

        def pat(key):
            if key[0] == 'any':
                return '_'
            if key[0] == 'var':
                return binder(key[1])
            tag = key[1]
            return '(.' + tag + ''.join(' ' + binder(v) for v in A.payload_vars(tag)) + ')'
        pa = pat(r['left']); pb = pat(r['right'])
        conds = []
        if A.guards:
            for v, ns in names.items():
                for n in ns[1:]:
                    conds.append(f'{ns[0]} = {n}')
        if r['result'] == 'ROOT':
            res = names[A.x][0] if A.x in names else '.junk'
        else:
            tag = r['result']
            res = '(.' + tag + ''.join(' ' + (names[v][0] if v in names else '.junk')
                                      for v in A.payload_vars(tag)) + ')'
        # unused binders -> underscore-prefixed to silence the linter
        binders = {n for ns in names.values() for n in ns}
        used = set(re.findall(r'[A-Za-z]+\d+', ' '.join(conds) + ' ' + res))
        def silence(p):
            return re.sub(r'\b([A-Za-z]+\d+)\b',
                          lambda m: m.group(1) if (m.group(1) in used or m.group(1) not in binders) else '_' + m.group(1), p)
        arms.append((silence(pa), silence(pb), conds, res))
    return arms


def render(A, eq1_text, eq2_text, refuting_env):
    tags = list(A.term_of.keys())
    ctors = ['  | leaf : Nat → submission.M', '  | junk : submission.M']
    for t in tags:
        ar = len(A.payload_vars(t))
        ctors.append(f'  | {t} : ' + ' → '.join(['submission.M'] * (ar + 1)))
    arms = rule_arms(A)
    helpers = []
    for k, (pa, pb, conds, res) in enumerate(arms):
        body = f'some {res}' if not conds else f'if {" ∧ ".join(conds)} then some {res} else none'
        catch_all = not pa.startswith('(') and not pb.startswith('(')
        arms_txt = f'  | {pa}, {pb} => {body}' + ('' if catch_all else '\n  | _, _ => none')
        helpers.append(f'def submission.try{k} : submission.M → submission.M → Option submission.M\n' + arms_txt)
    chain = '.junk'
    for k in reversed(range(len(arms))):
        chain = f'(submission.try{k} a b).getD {chain}' if chain == '.junk' else f'(submission.try{k} a b).getD ({chain})'
    op_def = f'def submission.op (a b : submission.M) : submission.M :=\n  {chain}'
    nofix, nf_names = [], []
    for t in tags:
        ar = len(A.payload_vars(t))
        for i in range(ar):
            args = ' '.join('a' if j == i else f'b{j}' for j in range(ar))
            others = ''.join(f' (b{j} : submission.M)' for j in range(ar) if j != i)
            quant = ('∀' + others + ', ') if others else ''
            intro = ('intro' + ''.join(f' b{j}' for j in range(ar) if j != i) + ' <;> ') if others else ''
            nofix.append(f'theorem submission.nf_{t}_{i} (a : submission.M) : {quant}(a = .{t} {args}) = False := by\n'
                         f'  induction a <;> {intro}simp_all')
            nofix.append(f"theorem submission.nf_{t}_{i}' (a : submission.M) : {quant}(.{t} {args} = a) = False := by\n"
                         f'  induction a <;> {intro}simp_all')
            nf_names += [f'submission.nf_{t}_{i}', f"submission.nf_{t}_{i}'"]
    vs1 = text_order(eq1_text)
    vs2 = text_order(eq2_text)
    inst_args = ' '.join(lean_elem(refuting_env[v]) for v in vs2)
    simp_set = ', '.join(['submission.op'] + [f'submission.try{k}' for k in range(len(arms))] + nf_names)
    def op_term(t):
        if t[0] == 'v':
            return t[1]
        return f'(submission.op {op_term(t[1])} {op_term(t[2])})'
    lhs_term, rhs_term = A_terms(A)
    proof_lhs = (
        f'theorem submission.lhs : @EquationLHS submission.M submission.inst := by\n'
        f'  intro {" ".join(vs1)}\n'
        f'  show {op_term(lhs_term)} = {op_term(rhs_term)}\n'
        + ''.join(f'  cases {v} <;>\n' for v in vs1)
        + f'  simp [{simp_set}] <;>\n'
        + f'  (try (repeat (split <;> simp_all [{simp_set}])))')
    return '\n\n'.join([
        'import JudgeProblem',
        'inductive submission.M : Type\n' + '\n'.join(ctors) + '\n  deriving DecidableEq',
        '\n\n'.join(helpers),
        op_def,
        '\n\n'.join(nofix),
        'instance submission.inst : Magma submission.M := ⟨submission.op⟩',
        proof_lhs,
        f'theorem submission.rhs : ¬ @EquationRHS submission.M submission.inst := by\n'
        f'  intro h\n'
        f'  exact absurd (h {inst_args}) (by decide)',
        'def submission : Goal :=\n  Exists.intro submission.M (Exists.intro submission.inst\n'
        '    (And.intro submission.lhs submission.rhs))',
    ]) + '\n'


def main():
    eq1_text, eq2_text = sys.argv[1], sys.argv[2]
    A = Automaton(eq1_text, guards=True, square_first=False)
    elems = A.universe()
    assert not A.check(elems), 'model does not satisfy eq1'
    env = A.refute(eq2_text, elems)
    assert env is not None, 'model does not refute eq2'
    print(render(A, eq1_text, eq2_text, env))


if __name__ == '__main__':
    main()
