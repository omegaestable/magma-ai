"""Lean skeleton for a validated closed-form free model (the 5107 template, generated).

python leangen.py <eq_id> <out_dir>   writes <out_dir>/rec<eq>.lean (definition, refutation, law statement
with a `sorry`-free but incomplete proof marker), <out_dir>/rules<eq>.txt (the rule list), and
<out_dir>/chk<eq>.py (a Python evaluator of exactly the emitted rule chain, for the agent's checks).

The emitted `op` follows rec5107.lean: accessor guards `tg`/`a1`/`a2`, an ordered `if` chain (first rule
wins), every nested `op` call gated by an explicit size test `hs_k : sz a + sz b < sz u + sz v` so that
`decreasing_by` is trivial; the law proof must discharge the gates (they always hold on real readings,
by the same size argument as `hs_ok` in the template).
"""
import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import closedform as cf
from closedform import Extractor, Closed, show_rule, show_expr
from freemodel import normalise, catalog, pvars, rand_term, size
from laws import parse_eq, load_rows

def lean_expr(e):
    k = e[0]
    if k == 'U': return 'u'
    if k == 'V': return 'v'
    if k == 'A1': return 'a1 (%s)' % lean_expr(e[1]) if e[1][0] not in ('U', 'V') else 'a1 %s' % lean_expr(e[1])
    if k == 'A2': return 'a2 (%s)' % lean_expr(e[1]) if e[1][0] not in ('U', 'V') else 'a2 %s' % lean_expr(e[1])
    if k == 'OP': return 'op (%s) (%s)' % (lean_expr(e[1]), lean_expr(e[2]))
    if k == 'J': return 'J (%s) (%s)' % (lean_expr(e[1]), lean_expr(e[2]))
    raise ValueError(e)

def nested_ops(e, acc):
    """all OP subterms of an expression, innermost first"""
    if e[0] in ('A1', 'A2'): nested_ops(e[1], acc)
    elif e[0] in ('OP', 'J'):
        nested_ops(e[1], acc); nested_ops(e[2], acc)
        if e[0] == 'OP' and e not in acc: acc.append(e)
    return acc

def rule_lean(conds, x, k):
    """(guard string, result string, gates) for one rule; nested ops are let-bound with size gates"""
    ops = []
    for c in conds:
        for e in c[1:]: nested_ops(e, ops)
    nested_ops(x, ops)
    names = {}
    lets = []
    gates = []
    for i, e in enumerate(ops):
        nm = 'p%d_%d' % (k, i)
        names[e] = nm
    def le(e):
        if e in names: return names[e]
        kk = e[0]
        if kk == 'U': return 'u'
        if kk == 'V': return 'v'
        if kk == 'A1': return 'a1 (%s)' % le(e[1]) if e[1][0] not in ('U', 'V') else 'a1 %s' % le(e[1])
        if kk == 'A2': return 'a2 (%s)' % le(e[1]) if e[1][0] not in ('U', 'V') else 'a2 %s' % le(e[1])
        if kk == 'J': return 'J (%s) (%s)' % (le(e[1]), le(e[2]))
        raise ValueError(e)
    struct = []   # structural conditions (no nested op)
    opconds = []
    for c in conds:
        if c[0] == 'TG':
            s = 'tg (%s) = 2' % le(c[1]) if c[1][0] not in ('U', 'V') else 'tg %s = 2' % le(c[1])
            (opconds if nested_ops(c[1], []) else struct).append(s)
        elif c[0] == 'EQ':
            s = '%s = %s' % (le(c[1]), le(c[2]))
            (opconds if nested_ops(c[1], []) or nested_ops(c[2], []) else struct).append(s)
        else:
            opconds.append('%s = %s' % (le(c[2]), le(c[1])))
    for e in ops:
        a, b = e[1], e[2]
        lets.append((names[e], le(a), le(b)))
    return struct, opconds, lets, le(x)

def dual_pat(p):
    return p if isinstance(p, str) else (dual_pat(p[1]), dual_pat(p[0]))

def emit(eq, outdir, seed=0, rules_override=None):
    cat = catalog(); orig = normalise(parse_eq(cat[eq]))
    # R-form laws (x = A * y) are served by the model of the dual L-form law with the operation flipped
    dualized = isinstance(orig[1][1], str) and not isinstance(orig[1][0], str)
    law = ('x', dual_pat(orig[1])) if dualized else orig
    if rules_override is not None:
        rules = list(rules_override); C = Closed(law, rules); tested, fails = cf.deep_tests(C, law, 3000, 200, eq * 3 + 1)
    else:
        rules, tested, fails, C = cf.best_rules(law, 3000, 200, eq * 3 + 1)
    keep = list(rules)
    C2 = Closed(law, keep)
    tested2, fails2 = cf.deep_tests(C2, law, 3000, 200, eq * 5 + 7)
    import fuzz as fz
    ftested, ffails = fz.fuzz(Closed(law, keep), law, keep, 12000, seed=eq)
    fails2 = fails2 + ffails
    rows = [r for r in load_rows() if int(r['eq1_id']) == eq]
    A, B = law[1]
    def evg(p, s):
        """evaluate a goal pattern in the *served* magma (flipped when dualized)"""
        if isinstance(p, str): return s[p]
        a, b = evg(p[0], s), evg(p[1], s)
        return C2.op(b, a) if dualized else C2.op(a, b)
    # refutation triples for each goal: generators first (all products free), else random
    refs = {}
    for r in rows:
        g = normalise(parse_eq(cat[int(r['eq2_id'])])); gv = pvars(g[1])
        cand = []
        for perm in [(0, 1, 2), (1, 2, 0), (2, 0, 1), (0, 0, 1), (1, 0, 0), (0, 1, 1)]:
            s = {v: ('g', perm[i % 3]) for i, v in enumerate(gv)}
            if s[g[0]] != evg(g[1], s): cand.append(s); break
        if not cand:
            random.seed(eq)
            for _ in range(3000):
                s = {v: rand_term(2) for v in gv}
                if s[g[0]] != evg(g[1], s): cand.append(s); break
        refs[r['eq2_id']] = (cand[0] if cand else None, r)
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, 'rules%d.txt' % eq), 'w', encoding='utf-8') as f:
        f.write('law %d: %s   (normalised: x = %s)%s\n' % (eq, cat[eq], str(law[1]), '   DUALIZED: rules/op are for the dual L-form law; the served magma is op flipped' if dualized else ''))
        f.write('deep tests: all rules %d/%d fails; kept rules %d/%d fails\n' % (len(fails), tested, len(fails2), tested2))
        for i, r in enumerate(keep): f.write('R%d %s\n' % (i + 1, show_rule(r)))
    # ---- Lean
    L = []
    L.append('import JudgeProblem\nset_option linter.unusedSimpArgs false\nset_option linter.unusedVariables false\nset_option warn.classDefReducibility false\n')
    L.append('inductive submission.M : Type where\n  | g : Nat → submission.M\n  | J : submission.M → submission.M → submission.M\n  deriving DecidableEq\n\nnamespace submission\nopen M\n')
    L.append('''def tg : M → Nat
  | .g _ => 1
  | .J _ _ => 2
def a1 : M → M
  | .J x _ => x
  | t => t
def a2 : M → M
  | .J _ x => x
  | t => t
def sz : M → Nat
  | .g _ => 1
  | .J b0 b1 => sz b0 + sz b1 + 1
theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem tg_g (t : M) (h : tg t ≠ 2) : ∃ n, t = M.g n := by cases t <;> simp_all [tg]
theorem sz_tg (t : M) (h : tg t = 2) : sz t = sz (a1 t) + sz (a2 t) + 1 := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1, a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n) = 1 := rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n) = M.g n := rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n) = M.g n := rfl
/-- the recursion measure: lexicographic (max size, total size), packed into one Nat -/
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
theorem msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b) < max (sz u) (sz v)) : msr a b < msr u v := by
  unfold msr
  have h1 : sz a + sz b ≤ 2 * max (sz a) (sz b) := by omega
  have h2 : (max (sz a) (sz b) + 1) * (max (sz a) (sz b) + 1) ≤ max (sz u) (sz v) * max (sz u) (sz v) := Nat.mul_le_mul h h
  simp only [Nat.mul_succ, Nat.succ_mul] at h2
  omega
theorem msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b) = max (sz u) (sz v)) (h2 : sz a + sz b < sz u + sz v) : msr a b < msr u v := by
  unfold msr; rw [h]; omega
''')
    # op definition: all nested op-terms let-bound once (innermost first), each gated by a size test;
    # then a flat ordered if-chain over the rules (structural guards, then the gates, then op-guards).
    allops = []
    for conds, x, tag in keep:
        for c in conds:
            for e in c[1:]: nested_ops(e, allops)
        nested_ops(x, allops)
    names = {e: 'p%d' % (i + 1) for i, e in enumerate(allops)}
    def le(e):
        if e in names: return names[e]
        kk = e[0]
        if kk == 'U': return 'u'
        if kk == 'V': return 'v'
        if kk == 'A1': return 'a1 (%s)' % le(e[1]) if e[1][0] not in ('U', 'V') else 'a1 %s' % le(e[1])
        if kk == 'A2': return 'a2 (%s)' % le(e[1]) if e[1][0] not in ('U', 'V') else 'a2 %s' % le(e[1])
        if kk == 'J': return 'J (%s) (%s)' % (le(e[1]), le(e[2]))
        raise ValueError(e)
    def gate(e):
        return 'msr (%s) (%s) < msr u v' % (le(e[1]), le(e[2]))
    lets = ''.join('  let %s := if hs%d : %s then op (%s) (%s) else J u v\n' % (names[e], i + 1, gate(e), le(e[1]), le(e[2])) for i, e in enumerate(allops))
    def deps(e, acc):
        if e[0] in ('OP', 'J'):
            deps(e[1], acc); deps(e[2], acc)
        elif e[0] in ('A1', 'A2'):
            deps(e[1], acc)
        if e[0] == 'OP' and e not in acc: acc.append(e)
        return acc
    chain = []
    pres = []
    for k, (conds, x, tag) in enumerate(keep):
        struct = []; opc = []; used = []
        for c in conds:
            for e in c[1:]: deps(e, used)
            if c[0] == 'TG':
                s = 'tg (%s) = 2' % le(c[1]) if c[1][0] not in ('U', 'V') else 'tg %s = 2' % le(c[1])
            elif c[0] == 'EQ':
                s = '%s = %s' % (le(c[1]), le(c[2]))
            else:
                s = '%s = %s' % (le(c[2]), le(c[1]))
            hasop = bool(nested_ops(c[1], [])) or (len(c) > 2 and bool(nested_ops(c[2], [])))
            (opc if hasop else struct).append(s)
        deps(x, used)
        gates = [gate(e) for e in used]
        pres.append(' ∧ '.join(struct) if struct else 'True')
        cond = ' ∧ '.join(['P%d u v' % (k + 1)] + gates + opc)
        chain.append('if %s then %s' % (cond, le(x)))
    body = lets + '  ' + '\n  else '.join(chain) + '\n  else J u v'
    pdefs = ''.join('def P%d (u v : M) : Prop := %s\ninstance (u v : M) : Decidable (P%d u v) := by unfold P%d; infer_instance\n' % (k + 1, p, k + 1, k + 1) for k, p in enumerate(pres))
    pnames = ', '.join('P%d' % (k + 1) for k in range(len(pres)))
    L.append(pdefs + 'def op (u v : M) : M :=\n' + body + '\ntermination_by msr u v\ndecreasing_by\n' + ''.join('  · assumption\n' for _ in allops))
    L.append('\ndef inst : Magma M := { op := fun a b => op b a }\n' if dualized else '\ndef inst : Magma M := { op := op }\n')
    L.append('def Pre (u v : M) : Prop := ' + ' ∨ '.join('P%d u v' % (k + 1) for k in range(len(pres))) + '\n')
    L.append('theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by\n  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]\n')
    # refutations
    for gid, (s, r) in refs.items():
        if s is None: continue
        g = normalise(parse_eq(cat[int(gid)]))
        def lt(t):
            if t[0] == 'g': return 'g %d' % t[1]
            return 'J (%s) (%s)' % (lt(t[1]), lt(t[2]))
        def lp(p):
            if isinstance(p, str): return lt(s[p])
            return ('op (%s) (%s)' % (lp(p[1]), lp(p[0]))) if dualized else ('op (%s) (%s)' % (lp(p[0]), lp(p[1])))
        L.append(('theorem rhs : ¬ @EquationRHS M inst := by\n  intro h\n  have := h %s\n  revert this\n  change ¬ %s = %s\n  simp (config := {decide := true}) [op.eq_1, sz, ' + pnames + ']\n')
                 % (' '.join('(%s)' % lt(s[v]) for v in ['x'] + [w for w in pvars(g[1]) if w != 'x'] if v in s), lt(s[g[0]]), lp(g[1])))
        break
    # law statement
    def lawterm(p):
        if isinstance(p, str): return p
        return 'op (%s) (%s)' % (lawterm(p[0]), lawterm(p[1]))
    L.append('\n/-- THE LAW: %s%s -/\ntheorem law (x y z : M) : %s = x := by\n  sorry\n' % (cat[eq], ' (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this)' if dualized else '', lawterm(law[1])))
    L.append('\ntheorem lhs : @EquationLHS M inst := by\n  intro x y z\n  exact (law x y z).symm\n\nend submission\n\ndef submission : Goal :=\n  Exists.intro submission.M (Exists.intro submission.inst\n    (And.intro submission.lhs submission.rhs))\n')
    txt = '\n'.join(L)
    with open(os.path.join(outdir, 'rec%d.lean' % eq), 'w', encoding='utf-8', newline='\n') as f: f.write(txt)
    # python checker of exactly the kept rules
    with open(os.path.join(outdir, 'chk%d.py' % eq), 'w', encoding='utf-8') as f:
        f.write('import sys, os, json\nsys.path.insert(0, %r)\nimport closedform as cf\nfrom freemodel import normalise, catalog\nfrom laws import parse_eq\n' % os.path.dirname(os.path.abspath(__file__)))
        f.write('law = normalise(parse_eq(catalog()[%d]))\nrules = %r\nC = cf.Closed(law, rules)\n' % (eq, keep))
        f.write('tested, fails = cf.deep_tests(C, law, int(sys.argv[1]) if len(sys.argv) > 1 else 3000, 300, 11)\nprint("tested", tested, "fails", len(fails))\n')
    return dict(eq=eq, dualized=dualized, nrules=len(keep), fails_all=len(fails), fails_kept=len(fails2), refuted=[g for g, (s, r) in refs.items() if s is not None], rows=[r['id'] for r in rows])

if __name__ == '__main__':
    print(json.dumps(emit(int(sys.argv[1]), sys.argv[2])))
