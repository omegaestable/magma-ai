# Proof-agent brief: certify a recursive free model (the 5107 template)

You are given ONE law `x = T(x,y,z)` from the Austin research set and a generated Lean skeleton
`gen/rec<eq>.lean` whose `op` (an infinite magma on the free term algebra `M`) is empirically a model
of the law (3,000 deep adversarial tests, 0 failures — `gen/rules<eq>.txt` lists the rules and the test
result; `gen/chk<eq>.py N` re-runs the check on N tests). The skeleton compiles: the definition, the
termination proof, the refutation of the goal (`rhs`) and the final `submission` term are done. **Your
only job is to replace the `sorry` in `theorem law` by a proof**, then get the certificate ACCEPTED by
the judge for every row of that law, and report.

Work directory: `c:/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata/`
(bash shell on Windows; forward-slash paths; always `export PYTHONIOENCODING=utf-8`; Python is
`c:/Users/nacho/Documents/GitHub/magma-ai/.venv311/Scripts/python.exe`).

## The worked example — read it first, in full

`rec5107.lean` is the ACCEPTED certificate for law 5107 (`x = y◇(y◇(y◇(z◇(x◇y))))`), 15 KB, proved
by hand in 26 minutes. Its structure is the template for every law:

1. `op_nJ` / `op_free`: when the structural precondition fails, `op u v = J u v`.
2. **`TR3` / `TR4` — the one-unfold characterisation**: `op u v = J u v ∨ (Pre u v ∧ (result is one of
   the rules' results, each with the rule's shape as an ∃-statement))`. Proved by
   `rw [op.eq_1, dif_pos ..]` (in the generated skeleton: `rw [op.eq_1]; simp only; split ...` — the
   generated `op` is a flat `if … then … else …` chain after `let`-bound nested calls) and `split`
   (core `split`, NOT Mathlib `split_ifs` — the judge has NO Mathlib, only `JudgeMagma.Magma`).
   Every nested `op` term that appears in a guard is characterised by applying `TR` to it; a weaker
   `TR` (`op u v = J u v ∨ (Pre ∧ sz (op u v) < sz v)`) is often all a size argument needs.
3. **Rule lemmas** `op_R1 …`: each rule fires on its shape and returns its result — proved by
   `rw [op.eq_1]; simp [P1, P2, …]` plus, when an earlier rule's guard could also fire, a size/shape
   contradiction (`grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, …]`).
4. **No-fire lemmas** for the intermediate products of the law's evaluation (`N3`, `N4`, `S4`, `SELF`
   in the template): the k-th product of `T(x,y,z)` is a free product unless the variables coincide in
   a specific way, which is then reduced to a rule lemma.
5. `law`: unfold the evaluation inside-out; at every product do `rcases TR … with h | ⟨hg, …⟩`, rewrite
   with `h`, and close with the rule lemmas; leaves close with
   `grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, <the G0_sz-style size lemmas of your law>]`.

Lessons recorded by the author of the template (they cost real iterations):
- `simp [op]` unfolds the nested calls forever; use `rw [op.eq_1]` (one level) then `simp only` /
  `split`. `decide` cannot evaluate a well-founded definition.
- `grind` closes leaves fast ONLY with a restricted lemma list (the `J`-equations, `sz`, `sz_a1`,
  `sz_a2` and size lemmas triggered by a shape hypothesis); passing the catch-all `a1`/`a2` equations
  or a `tg t = 2 → …` lemma makes it enumerate `tg (a1 (a1 …))` forever.
- Never `generalize` away an `op`-term whose identity with another `op`-term matters; congruence
  closure needs the shared expression.
- `split` must run before any `simp only [...]` on the goal — rewriting inside an `ite` condition
  leaves a term `split` refuses.
- A size lemma per shape (like `G0_sz : G0 u v → sz v = sz u + sz u + sz (a2 (a2 v)) + 2`) is what
  lets `omega`/`grind` refute impossible coincidences ("a term equals its own proper subterm").
- The generated `op` gates every nested call with `hs_k : sz a + sz b < sz u + sz v`; on any real
  reading the gate holds (the encoding `v` contains `u` and the nested pair is built from proper
  subterms) — prove a `hs_ok`-style lemma once and reuse it.

## Lessons from the laws already proved on generated skeletons (4952, 5012, 5066, 5295 — all accepted)

- **Pack the nested calls before splitting.** `op.eq_1` is zeta-expanded: the `let p_k := if hs_k : … then op … else J u v`
  bindings get inlined into every later gate, so `rw [op.eq_1]; split` or `simp only` dies with "maximum number of steps".
  The fix every agent converged on:
  ```lean
  theorem op_cases (u v : M) : ∃ p1 p2 …, p1 = (if hs1 : msr … < msr u v then op … else J u v) ∧ p2 = (…) ∧ … ∧
      op u v = (if P1 u v then … else if P2 u v ∧ msr … < msr u v ∧ … = p1 then … else J u v) :=
    ⟨_, _, …, rfl, rfl, …, op.eq_1 u v⟩
  ```
  (the if-chain is the `op` body verbatim with the `let` names as variables). Then
  `obtain ⟨p1, …, hp1, …, hop⟩ := op_cases u v; rw [hop]; split` is instant, and inside a branch a gate is recovered by
  `rw [dif_pos hs_k] at hp_k; subst hp_k` (`subst` by hypothesis NAME — a bare `subst p2` may grab the rule's own
  `a2 (a2 v) = p2` equation instead). Rewrite `dif_pos` BEFORE any `simp only […] at h`, or the rewrite fails.
- **Most rules are dead code.** Prove first that the products of the decoding chain are free (`op u q = J u q`,
  `op u (J u q) = …`, …, by size: a `J`-term is never a proper subterm of its own argument), then the rule set collapses to
  R1 + one recursive rule and the law is a rewrite chain. 5012 used a single invariant
  `NOFIRE : ∀ z w, sz w ≤ sz z → op z w = J z w` (induction on a size bound); 5066 proved a one-shot characterisation
  `Sh u v (op u v)` by strong induction `MainN (n) : ∀ u v r, sz u + sz v < n → op u v = r → Sh u v r`; 4952/5295 proved
  `TR` as a recursive theorem (`termination_by`/`decreasing_by exact hs1`) with chain lemmas `C2/C3/C4`.
- **Leaf tactic: `have := congrArg sz h; simp only [sz_J] at this; omega`** with the size facts in context
  (`sz_a1`, `sz_a2`, `sz_a1_lt : tg t = 2 → sz (a1 t) < sz t`, the rule-shape size lemma `P1_sz`, `sz_op_le`).
  Nobody needed `grind` on the generated skeletons.
- Refute a gate by reading it as `sz p < sz p` (`Nat.lt_irrefl`) when the guard identifies `p` with a term containing
  itself; `msr_J_nlt : ¬ msr w (J u v) < msr u v` shows the `J u v` fallback of a gate never passes the next gate.
- `simp only … at h` does nothing on an `abbrev` application — destructure it in the `rcases` pattern or `unfold` first.
- The shell heredoc strips backslashes: write helper scripts with the Write tool; set `PYTHONIOENCODING=utf-8`.
- `split` reduces a gate `dite` only when the gate or its negation is a hypothesis in context; otherwise it case-splits
  the `Nat.lt` proof and fails with "Dependent elimination failed … Nat.le.refl". Put every gate fact (`by_cases g_k`,
  or the always-false gates `ngJ : ¬ msr (J u v) u < msr u v`) in context before `split`. `rw [hP]` on
  `op (op (a2 u) u) u` needs `rw [hP, hP]` (the rewrite creates a new occurrence).
- If the skeleton turns out FALSE (9345, 13992 did — the generator located a payload through an accessor path that is
  wrong when an inner product of the encoding is itself decoded), the repair that worked twice: recover the payload
  through the occurrence that is provably free (`u = v.2`-type invariants: every rule carries it), drop the R1-shape
  guards, keep 3–4 rules, re-validate with `cf.deep_tests` (≥ 40k, several seeds) and critical-pair-shaped instances,
  regenerate the skeleton via `leangen.emit` with the new rules, then prove. Report the repaired rule set verbatim.
- Before opening the proof, run a coincidence-targeted check of the rule set (x, z drawn from subterms/products of an
  R-shaped y; `gen/chk<eq>.py`'s `cf.Closed.evp` reproduces any instance in milliseconds, and
  `simp (config := {decide := true}) [op.eq_1, sz, P1, …]` decides a concrete instance in Lean in ~1 s). If you find a
  counterexample, STOP and report it with the instance — the skeleton is not a model and no proof exists.

## Iterating

Fast local compile (2–5 s), exactly the judge's `JudgeProblem` for your row:
```
export PYTHONIOENCODING=utf-8
python devrow.py <eq1_id> <eq2_id>          # once per row: builds .artifacts/dev_<eq1>_<eq2>/
D=/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official/.artifacts/dev_<eq1>_<eq2> bash devlean2.sh gen/rec<eq>.lean
```
Real judge (60 s first call, ~10 s after), the only acceptance that counts:
```
python judge1.py gen/rec<eq>.lean <eq1_id>:<eq2_id>
```
Never run two judge calls at once; do not start CPU-heavy batch jobs.

Constraints: certificate ≤ 20,000 UTF-8 bytes; ≤ 300 s judge time; axioms only
propext/Quot.sound/Classical.choice (no `native_decide`, no `sorry`); banned tokens anywhere in the
text, comments included: `run_cmd`, `run_elab`, `@[init`, `skipKernelTC`, `notation`, `notation3`,
`infix`, `infixl`, `infixr`, `prefix`, `postfix`, `axiom`, `unsafe`, `implemented_by`, `extern`.
Keep the namespace layout and the final `submission` term exactly as generated.

If a law has several rows (several goals), the `rhs` block in the skeleton handles the first goal;
for the other rows copy the certificate and replace `rhs` by the corresponding refutation (the
generated `simp (config := {decide := true}) [op.eq_1, sz, P1, …]` evaluates any concrete instance;
pick x, y, z among `g 0`, `g 1`, `g 2` such that the goal fails — `gen/chk<eq>.py` has the
evaluator, `cf.Closed.evp`, to find one).

## What to report (verbatim, it is fed into the next law)

- Judge STATUS per row, byte size, judge seconds; the path of each accepted `.lean`.
- The lemma structure that worked (names + statements) and the leaf tactic.
- If not accepted after ~30 judge iterations: the exact remaining goal(s) and your diagnosis
  (which nested-call case resists, and what invariant it needs).
