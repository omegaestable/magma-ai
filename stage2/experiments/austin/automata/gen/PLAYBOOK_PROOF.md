# PLAYBOOK_PROOF — the Lean method that got 37 certificates accepted

From `rec5107.lean`, the 37 accepted `certs/*.lean`, the six partial proofs (`gen/rec5837_proof`,
`rec28626`, `rec24200`, `rec12087`, `rec12234`, `rec23354`), and **21 `lean` runs covering 27
snippets**, made while writing this (dev row `dev_5107_22818`, 1–3 s each). `AGENT_BRIEF.md` is
background; this is the procedure. Every Lean block is verbatim from a file that compiled — `…`
marks an elision, and the one block marked **SCHEMA** is the shape of a compiled instance with the
law-specific parts replaced by `<…>`. Every quoted error message is one I actually produced.

## 0. Orientation

`M = g Nat | J M M` is the free term algebra; `op u v` is an ordered if-chain of *rules* and returns
the free product `J u v` when none fires. The law holds because every product of `T(x,y,z)` is
either free (nothing lost) or is the single decoding step that returns `x`.

Every proof is these five things:

| # | name in the certs | statement |
| - | --- | --- |
| 1 | `op_cases` | `op.eq_1` restated with the `let`-bound nested calls packed as ∃-variables |
| 2 | the **digest** (`TRs`/`TR4`/`Wdig`) | `op u v = J u v ∨ (<precondition common to all rules> ∧ <bound on the result>)` |
| 3 | `Wne` / `Wsz` / `Wfree` | corollaries that make a *specific* product free |
| 4 | `op_R1 … op_Rk` | this shape fires this rule and returns this |
| 5 | `law` | walk `T` inside-out, `rcases` the digest at each product, close with 3 and 4 |

Everything else is size arithmetic.

## 1. The canonical file, and what you may not touch

`leangen.emit` produces:

```
import JudgeProblem                                -- + 3 set_option linter lines
inductive submission.M … | g : Nat → M | J : M → M → M   deriving DecidableEq
namespace submission ; open M
def tg / a1 / a2 / sz ; theorem sz_a1 / sz_a2 / tg_J / sz_tg ; @[simp] tg_J_eq / a1_J_eq / a2_J_eq …
def msr (u v : M) : Nat := max (sz u) (sz v) * max (sz u) (sz v) + sz u + sz v
def P1 … Pk (u v : M) : Prop  (+ a Decidable instance each)
def op (u v : M) : M := <let p1 … pn ; if-chain>   termination_by msr u v
def inst / def Pre / theorem op_free / theorem rhs ; <YOUR PROOF> ; theorem law ; theorem lhs
end submission ; def submission : Goal := …
```

**Do not change anything above `theorem rhs`, nor `lhs`, `rhs`, the namespace, or the final
`submission` term.** They are what the judge checks against `JudgeProblem`; a one-line `rhs` edit
already broke `dualcert.py` and burned a judge call.

The preamble is **not uniform**: `rec11081` has no `sz_pos`/`sz_a1_lt`/`sz_a2_lt`, `rec18137b`
calls them `szP`/`s1L`/`s2L`. Paste these three at the top of your proof (compiled against
`rec11081`'s preamble):

```lean
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
```

Compile loop (measured: `rec5107` 15 KB → 3 s, `rec18137b` 23 KB → 1 s, a 24-rule skeleton → 2 s;
the judge takes 4–42 s for the same files, which is Mathlib import + phase 2, not your proof):

```bash
export PYTHONIOENCODING=utf-8
python devrow.py <eq1_id> <eq2_id>                        # once per row
D=/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official/.artifacts/dev_<eq1>_<eq2> \
  bash devlean2.sh gen/rec<eq>.lean                       # T=<sec> C=<chars> tune timeout/output
```

## 2. `op_cases` — the packing recipe

`op.eq_1` is **zeta-expanded**: every `let p_k := if hs_k : … then op … else J u v` is inlined into
each later gate *and* into each rule condition mentioning `p_k`. At 4 lets / 6 rules the unfolded
goal already repeats the `p1` dite six times; at 20 lets it is unusable.

Restate `op.eq_1` with the lets as ∃-variables. **The statement is the body of `op` copied
verbatim** (the `p_k` in it are already the right names) and the proof is always the same
anonymous constructor — `n` underscores, `n` `rfl`s, `op.eq_1 u v`:

```lean
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 : M,
    p1 = (if hs1 : msr (a1 u) u < msr u v then op (a1 u) u else J u v) ∧
    p2 = (if hs2 : msr (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 u)) (a1 u) < msr u v then op (a1 (a1 u)) (a1 u) else J u v) ∧
    p4 = (if hs4 : msr (a1 p1) p1 < msr u v then op (a1 p1) p1 else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a2 v))
  else if P2 u v ∧ msr (a1 u) u < msr u v ∧ a2 (a2 v) = p1 then a1 u
  …
  else J u v) :=
  ⟨_, _, _, _, rfl, rfl, rfl, rfl, op.eq_1 u v⟩
```

**Do not write it by hand** — `python gen/_pb_gencases.py gen/rec<eq>.lean` emits it from the
skeleton. Compiled at n = 4 (6878) and at **n = 20 / 24 rules (11081), 2 s**: `op_cases` scales.

Using it (`rec6878_rep`, compiled):

```lean
theorem L1 (x y : M) : op y (J y (J x y)) = J y (J y (J x y)) := by
  obtain ⟨p1, p2, p3, p4, hp1, -, hp3, hp4, hop⟩ := op_cases y (J y (J x y))
  have hs1 : msr (a1 y) y < msr y (J y (J x y)) := gJ (Or.inl (sz_a1 _)) (Or.inl (Nat.le_refl _))
  rw [dif_pos hs1] at hp1; subst hp1
  rw [hop]; split
  · rename_i h; exfalso
    obtain ⟨-, -, -, -, h5, -, h7⟩ := h
    simp only [a2_J_eq] at h5 h7
    have := sz_tg y h5; have := congrArg sz h7; omega
  · split
    …
```

Three fixed moves, in this order: `obtain ⟨p…, hp…, hop⟩ := op_cases u v` (drop unneeded `hp_k`
with `-`); per gate you need, `have hs_k : msr … < msr u v := <size proof>` then
`rw [dif_pos hs_k] at hp_k` then `subst hp_k`; finally `rw [hop]; split` and `rename_i h` in each
`isTrue` branch.

### Why `rw [op.eq_1]; split` alone dies — three reproduced deaths

* `simp [op]` → `warning: Possibly looping simp theorem: 'op.eq_1'`, then
  `error: Tactic 'simp' failed with a nested error: maximum recursion depth has been reached`.
  `op.eq_1` rewrites `op u v` into a body containing `op`, forever.
* `rw [op.eq_1]; split` at 6 rules "succeeds" and leaves a 90-line `isFalse` goal in which the `p1`
  dite appears **six** times; every later tactic pays for all six.
* at 24 rules the **first** `split` after `rw [hop]` fails outright:
  `error: 'simp' failed: maximum number of steps exceeded`. There is no knob —
  `set_option maxSteps 4000000` gives `error: Unknown option 'maxSteps'`. Use §3 instead.

## 3. Most rules are dead code — collapsing 10–70 rules to 2–3 live ones

**The** lever for the heavy laws: 11081 has 24 validated rules, 32281 26, 9663 49, 13764 67. You
will not write 24 rule lemmas and you do not have the bytes for them (§8).

### 3.1 The `Pre` route — no `split` at any rule count

Every rule needs its `P_k u v`. Prove one fact all of them imply and the whole rule set collapses,
without ever touching the if-chain:

```lean
theorem TRpre (u v : M) : op u v = J u v ∨ Pre u v := by
  by_cases h : Pre u v
  · exact Or.inr h
  · exact Or.inl (op_free h)
```

### 3.2 Find the common conjunct mechanically — do not eyeball it

`python gen/_pb_common.py gen/rec<eq>.lean` prints the conjuncts shared by every `P_k`, the
near-common ones with counts, and the distinct results of the if-chain. Measured:

| law | rules | common to ALL | best near-common |
| --- | --- | --- | --- |
| 11081 | 24 | *none* | `tg u = 2` (22/24) |
| 13764 | 67 | *none* | `tg u = 2` (66/67), `tg (a1 u) = 2` (65/67) |
| 24200 | 15 | `tg v = 2` | `tg u = 2` (13/15) |
| 28626 | 10 | `tg u = 2` | `tg (a1 u) = 2` (5/10) |

Guessing `tg u = 2 ∧ tg (a1 u) = 2` for 11081 produced
`error: Application type mismatch: The argument h.left has type tg v = 2 but is expected to have
type tg u = 2` — the first conjunct is a different conjunct in different rules. When the common set
is empty, read the 1–2 exceptions: 11081's are `P1` and `P8`, and both carry
`tg v = 2 ∧ u = a2 (a2 v)`, i.e. `sz u < sz v`, giving a two-branch digest.

### 3.3 The digest, emitted mechanically

The projection path into `P_k`'s conjunction is `h` + `.2`×i + `.1` (no final `.1` when the conjunct
is last). Generate one `·` line per rule with a five-line Python loop; never count `.2`s by hand.
Compiled against `rec11081`, 24 rules, 1,913 bytes, 2 s:

```lean
theorem Pdig {u v : M} (h : Pre u v) : tg u = 2 ∨ (tg v = 2 ∧ u = a2 (a2 v)) := by
  rcases h with h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h|h
  · exact Or.inr ⟨h.1, h.2.2.2.2.2.2⟩          -- P1  (one of the two without `tg u = 2`)
  · exact Or.inl h.2.2.2.2.2.1                  -- P2
  …                                             -- one generated line per rule
  · exact Or.inl h.1                            -- P24

theorem Wdig (u v : M) : op u v = J u v ∨ tg u = 2 ∨ sz u < sz v := by
  rcases TRpre u v with hf | hp
  · exact Or.inl hf
  · rcases Pdig hp with h | ⟨h1, h2⟩
    · exact Or.inr (Or.inl h)
    · refine Or.inr (Or.inr ?_)
      have e1 := sz_a2_lt h1
      have e2 := sz_a2 (a2 v)
      rw [h2]; omega

theorem Wfree {u v : M} (h1 : tg u ≠ 2) (h2 : sz v ≤ sz u) : op u v = J u v := by
  rcases Wdig u v with hf | h | h
  · exact hf
  · exact absurd h h1
  · omega
```

### 3.4 How to attack a 24-rule model, in order

1. `python revalidate.py <eq>` — confirm it is still a model and let the **validated-removal
   minimiser** drop every rule it can. First, always: at ~600 B per rule a 24-rule skeleton is
   already 84 % of the byte cap with zero proof written (§8).
2. `python gen/_pb_common.py gen/rec<eq>.lean` — get the digest precondition and the result set.
3. Write `TRpre` (2 lines), `Pdig` (generated), `Wdig` (size form). ≈ 2 KB total.
4. Free the law's own chain products. For each `op A B` in `T`, prove `op A B = J A B` from the
   digest; one of three arguments always works — `A` is not a `J` of the required depth so the
   precondition fails (`Wfree`); `sz B ≤ sz A`, so the result would be both `< sz B` and `> sz A`
   (`Wsz`); or `a1 B ≠ A` when every rule demands `u = a1 v` (`Wne`).
5. **Only now** write rule lemmas, and only for the rules that can still fire on the *last* product —
   the one that must return `x`. In 6878 that is 6 of 6 (four decoding shapes); in 9345 it is 2.
6. `law` (§6).

The compiled 6-rule example of the whole shape is `gen/rec6878_rep.lean` →
`certs/research_order5_hard_0034.lean`, accepted at 19,205 B after `squeeze.py`: `TRs`, `NE`,
`Wne`, `Wsz`, `red1`, `red2`, `L1`, `SELF`, `L1'`, `op_R1 … op_R6`, then a 20-line `law`.

```lean
/-- free, or `v = J u _` with a strictly smaller result — the 6-rule digest.  Proof: `op_cases`,
    `rw [hop]`, then one `split` branch per rule, each three lines: `rename_i h`, two size `have`s,
    `exact Or.inr ⟨h.1, h.2.1.symm, by omega⟩`; the last branch is `exact Or.inl rfl`. -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ a1 v = u ∧ sz (op u v) < sz v) := …

theorem Wne {u a : M} (b : M) (h : a ≠ u) : op u (J a b) = J u (J a b) :=
  op_free (fun hp => by
    rcases hp with h1 | h1 | h1 | h1 | h1 | h1 <;>
      exact h (by have e := h1.2.1; simp only [a1_J_eq] at e; exact e.symm))

theorem Wsz {u c : M} (h : sz c ≤ sz u) : op u c = J u c := by
  rcases TRs u c with h' | ⟨hct, hcu, -⟩
  · exact h'
  · exfalso; have := sz_tg c hct; rw [hcu] at this; omega
```

`TRs` (one `split` branch per rule) is affordable to ~10 rules; past that use §3.1–3.3.

## 4. When a chain product can recursively coincide — the `CMP` invariant

Sometimes no size argument closes a case, because a decoded value can legitimately equal a subterm
another product produced. Then you need an invariant on the **shape** of a decoded value, proved by
**fuel induction on `Nat`**. Pattern: `gen/rec18137b.lean` → `certs/research_order5_hard_0042.lean`,
accepted at 19,705 B. Compiled ingredients:

```lean
-- (a) name the shape a non-free product has
def Enc (a w : M) : Prop := Sh w ∧ op a (a1 w) = a1 (a2 w)
def RF (u x : M) : Prop := (tg u = 2 ∧ a2 u = x ∧ op (a1 u) (a2 u) = u) ∨ Enc u x

-- (b) SND (u v : M) (h : op u v ≠ J u v) : Enc (op u v) v ∧ RF u (op u v)
--     one branch per rule, `termination_by msr u v`, `decreasing_by exact <gate lemma>`

theorem oD (a b : M) : op a b = J a b ∨ (Enc (op a b) b ∧ RF a (op a b)) := by
  by_cases h : op a b = J a b
  · exact Or.inl h
  · exact Or.inr (SND a b h)

-- (c) fuel induction: the numeric consequence of the shape
theorem encA (n : Nat) : ∀ a w, sz w ≤ n → Enc a w → sz (a2 a) < sz w := by
  induction n with
  | zero => intro a w h _; have := szP w; omega
  | succ n ih =>
    intro a w hn dq; obtain ⟨ab, he⟩ := dq
    have s1 := szT w ab.1; have s2 := szT _ ab.2.1; have s4 := sA2 a
    rcases oD a (a1 w) with hf | ⟨-, cq⟩
    · rw [hf] at he; have := sJz he; omega
    · rcases cq with ⟨-, hx, -⟩ | aa
      · rw [hx, he]; omega
      · have := ih a (op a (a1 w)) (by rw [he]; omega) aa; rw [he] at this; omega
theorem eA1 {a w : M} (h : Enc a w) : sz (a2 a) < sz w := encA _ a w (Nat.le_refl _) h

-- (d) the converse: if v encodes x and u is in the right form, op u v really is x
theorem CMP (n : Nat) : ∀ u v x, msr u v < n → Enc x v → RF u x → op u v = x := by
  induction n with
  | zero => intro u v x h; omega
  | succ n ih => intro u v x hn cy bg; …
```

and then `law` is three lines — rewrite the two free products away, then hand the last product to
`CMP` with the two side conditions:

```lean
theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (op (x) (z)) (z))) = x := by
  rw [H2, H1]; apply CMP (msr (op y x) (J z (J (op x z) z)) + 1) _ _ x (Nat.lt_succ_self _)
  · exact ⟨⟨rfl, rfl, rfl⟩, rfl⟩
  · by_cases h : op y x = J y x
    · left; rw [h]; exact ⟨rfl, rfl, by simp only [aJ1, aJ2]; exact h⟩
    · right; exact (SND y x h).1
```

**SCHEMA** — the four slots to fill:

```lean
def Enc (a w : M) : Prop := <the guard the rule that produced `a` from `w` imposed on w>
def RF (u x : M) : Prop := <u free with payload x> ∨ Enc u x
theorem SND (u v : M) (h : op u v ≠ J u v) : Enc (op u v) v ∧ RF u (op u v) := by
  obtain ⟨p…, hp…, hop⟩ := op_cases u v; rw [hop] at h ⊢; split
  · <rule 1: `rw [dif_pos (g_k …)] at hp_k; subst hp_k`, then `exact ⟨…, …⟩`>
  · split … · <no rule fires: `rw [if_neg …] at h; exact absurd rfl h`>
termination_by msr u v
decreasing_by exact <the gate lemma of the recursive rule>
theorem <numeric> (n : Nat) : ∀ <args>, sz <shrinking arg> ≤ n → Enc … → <inequality> :=
  <`induction n`; zero `have := sz_pos _; omega`; succ `rcases oD …`, free case by `sJz`/
   `congrArg sz` + omega, Enc case by `have := ih … (by …) …; omega`>
theorem CMP (n : Nat) : ∀ u v x, msr u v < n → Enc x v → RF u x → op u v = x :=
  <`induction n`; one branch per rule; the recursive rule closes with
   `exact ih u <smaller v> x (by have := <gate lemma> …; omega) … …`>
```

Write `CMP` when, and only when, a case survives every size argument (§9). 18137 needed seven such
invariants (`encA`, `eB`, `opB`, `Q`, `Q2`, `eD`, `eF`) and then every case closed.

## 5. Leaf tactic menu, ranked by occurrences across the 37 accepted certificates

| # | tactic | count | needs in context |
| - | --- | --- | --- |
| 1 | `omega` | 1231 | the size facts as `have`s — it sees only linear `Nat` hypotheses |
| 2 | `rfl` | 1218 | nothing; closes the `else J u v` branch of every `split` |
| 3 | `simp only [a1_J_eq, a2_J_eq, tg_J_eq] at h ⊢` | 1087 | the `@[simp]` rfl-lemmas; **never bare `simp`** |
| 4 | `obtain` / `rcases` | 699 / 476 | destructure `P_k` and the digest disjunction |
| 5 | `subst` | 462 | **by hypothesis name** (pitfall 3) |
| 6 | `congrArg sz h` | 395 | turns a term equation into a `Nat` equation — the workhorse |
| 7 | `split` + `rename_i h` | 386 / 344 | ≤ ~10 rules only |
| 8 | `by_cases` | 267 | put the gate or `Pre` in context *before* you need it |
| 9 | `sz_tg` | 177 | `tg t = 2 → sz t = sz (a1 t) + sz (a2 t) + 1` |
| 10 | `exact absurd h1 h2` | 76 | closing an `isTrue` branch whose guard you refuted |
| 11 | `grind [sz, a1_J_eq, a2_J_eq, sz_a1, sz_a2, <G0_sz-style>]` | 50, in 5 certs | a **restricted** list; the catch-all `a1`/`a2` equations make it enumerate forever |
| 12 | `apply Classical.byContradiction; intro h` | 4 | `by_contra` is Mathlib and is **not** available |

The leaf that closes most goals, and its commonest instance (both compiled):

```lean
theorem probe_leaf (a b : M) (h : a = J a b) : False := by
  have := congrArg sz h; simp only [sz_J] at this; omega

theorem probe_no_fix (u v : M) (h : op u v = v) : False := by
  rcases TRs u v with hf | ⟨-, -, hs⟩
  · rw [hf] at h; have := congrArg sz h; simp only [sz_J] at this; omega
  · rw [h] at hs; exact Nat.lt_irrefl _ hs
```

Have in context before `omega`: `sz_a1`/`sz_a2` (`≤`), `sz_a1_lt`/`sz_a2_lt` (`<`, need
`tg t = 2`), `sz_tg`, `sz_pos`, `@[simp] sz_J`, and your law's rule-shape size lemma (`G0_sz` in
`rec5107`, `Sh_sz` in `rec18137b`). `grind` was needed on the hand-written 5107 model and on nothing
generated — try `omega` first.

A concrete instance (needed when you copy the cert for a second row and must rewrite `rhs`) is
decided by `simp`, not by `decide` (compiled):

```lean
theorem probe_concrete : op (g 0) (g 1) = J (g 0) (g 1) := by
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6]
```

## 6. Assembling `law`

Walk `T(x,y,z)` **inside out**. At each product either a free lemma of §3.4 rewrites it away, or you
`rcases` the digest and get one case per rule shape. `rec6878_rep`'s `law` (compiled) — two digest
splits, three outcomes each, dispatched to `op_R1 … op_R6`:

```lean
theorem law (x y z : M) : op (y) (op (y) (op (op (z) (x)) (op (x) (y)))) = x := by
  rcases TRs z x with ha | ⟨hxt, hxz, hsa⟩
  · rw [ha]
    rcases TRs x y with hb | ⟨hyt, hyx, hsb⟩
    · rw [hb, Wne _ (ne_of_sz (szJ1 z x))]; exact op_R1 x y z
    · obtain ⟨x', y2, rfl⟩ := tg_J y hyt
      simp only [a1_J_eq] at hyx; subst x'
      rcases TRs (J z x) (op x (J x y2)) with hc | ⟨hbt, hba, hsc⟩
      · rw [hc]; exact op_R2 _ _ _ _ rfl hsb
      · obtain ⟨a', b2, hb'⟩ := tg_J _ hbt
        rw [hb'] at hba; simp only [a1_J_eq] at hba; subst a'
        rw [hb'] at hsb hsc ⊢; exact op_R5 _ _ _ _ _ _ rfl hb' rfl hsb hsc
  · <the dual three cases, with op_R3 / op_R4 / op_R6>
```

Rule lemmas take the derived facts as hypotheses (`hsa : sz (op z x) < sz x`) instead of re-deriving
them — that is what keeps them short, and why the digest returns the size bound.

## 7. Pitfalls, each with the error it produces

1. **`simp [op]` / `simp only [op]`** → `warning: Possibly looping simp theorem: 'op.eq_1'` then
   `error: Tactic 'simp' failed with a nested error: maximum recursion depth has been reached`.
   Use `op_cases`. Raising `maxRecDepth` only buys a slower loop.
2. **`split` on a long if-chain** → `error: 'simp' failed: maximum number of steps exceeded`,
   reported at the `split`; reproduced at 24 rules on the *first* split even with `op_cases` applied.
   No knob exists (`error: Unknown option 'maxSteps'`). Use the `Pre` digest (§3.1).
3. **`subst p1` instead of `subst hp1`** → later
   `error(lean.unknownIdentifier): Unknown identifier 'he'`. Reproduced: with
   `he : a2 (a2 v) = p1` standing *before* `hp1 : p1 = op (a1 u) u`, `subst p1` consumes `he`.
   Always `subst <hypothesis name>`.
4. **`simp only […] at hp_k` before `rw [dif_pos hs_k] at hp_k`** →
   `error: Tactic 'rewrite' failed: Did not find an occurrence of the pattern dite (msr (a1 (x.J y2)) … ) ?m ?m`,
   because the `simp only` rewrote `a1 (J x y2)` to `x` *inside the dite's condition* while `hs_k`
   still says `a1 (J x y2)`. Order: `rw [dif_pos hs_k]` first, then `simp only`, then `subst hp_k`.
5. **`decide` on `op`** → `error: Tactic 'decide' failed … its 'Decidable' instance did not reduce
   to 'isTrue' or 'isFalse'`. `op` is well-founded; use `simp (config := {decide := true}) [op.eq_1, …]`.
6. **`by_contra`** → `error: unknown tactic`. There is no Mathlib: `tauto`, `split_ifs`, `linarith`,
   `norm_num` are all absent. Use `apply Classical.byContradiction; intro h`. Core and available:
   `omega`, `grind`, `simp_all`, `split`, `rcases`, `obtain`, `rintro`, `by_cases`, `rename_i`.
7. **`rw [hP]` when the rewrite creates a new occurrence** — `rw [hP]` on `op (op (a2 u) u) u` with
   `hP : op (a2 u) u = a2 u` leaves `op (a2 u) u = a2 u`, not `rfl`. Write `rw [hP, hP]` or finish
   with `exact hP`.
8. **Guessing the common conjunct** → `error: Application type mismatch: The argument h.left has
   type tg v = 2 but is expected to have type tg u = 2`. Run `gen/_pb_common.py`.
9. **The preamble differs between skeletons** →
   `error(lean.unknownIdentifier): Unknown identifier 'sz_a2_lt'`. Paste the three lemmas from §1.
10. **`squeeze.py` deletes every `set_option` line.** A proof that needs one will not compile after
    squeezing. Recompile after every squeeze, always.
11. `simp only … at h` does nothing on an `abbrev` application — destructure it in the `rcases`
    pattern or `unfold` first; and never `generalize` away an `op`-term whose identity with another
    `op`-term matters (congruence closure needs the shared expression).
12. **For an R-form (dualised) law the old `gen/chk<eq>.py` tests the wrong orientation** and prints
    3000/3000 fails. Validate with `revalidate.run_tests` on the dualised law (`WAVE2_PROMPT.md` §1).

## 8. Byte budget — the cap is 20,000 UTF-8 bytes

| item | bytes |
| --- | --- |
| fixed boilerplate (`import` … `msr`, no rules) | **2,171** |
| per rule (`def P_k` + instance + one `let` + one if-chain line) | **≈ 530–780** (24200 363, 28626 527, 11081 601, 13764 778) |
| definition block (`M` … `def inst`) | 5107 **2,286** · 12087 3,963 · 18137 4,020 · 6878 4,066 · 12234 5,043 · 28626 7,572 · 24200 7,742 · **11081 16,723** · 32281 21,615 · 9663 30,212 · **13764 54,402** |
| a finished certificate | 294–515 B per declaration; 26 decls → 7.9 KB, 44 → 19.2 KB, 51 → 19.7 KB |
| the 24-rule digest of §3.3 | 1,913 |
| `python squeeze.py in out --rename` | **−13 to −15 %** (18137 23,064→19,705 accepted; 6878 22,681→19,205 accepted; 11081 skeleton 17,891→15,334) |
| solver-side margin under the judge cap | 50 B — aim for ≤ **19,900** after squeezing |

**Read the definition-block row before starting.** 11081's definitions alone are 16,723 B (14,371
squeezed) — 84 % of the cap with no proof written; 13764's are 54,402 B, 2.7× the cap. For those the
first move is not Lean, it is the minimiser: **a law you cannot fit is a modelling problem, not a
proof problem.**

Shrink in this order: (1) **fewer rules** — −530 to −780 B each and fewer proof obligations;
(2) **fewer lemmas** — merge the per-shape no-fire lemmas into one digest (§3): 24 rule lemmas
≈ 10 KB versus ≈ 2 KB; (3) **`squeeze.py … --rename`** (−14 %), then **recompile the output**, it is
only syntax-preserving in practice; (4) **shorten hypothesis names by hand** — `rec18137b`'s
two-character names are a large part of why it fits; (5) **drop doc-comments** — bytes, and the
judge scans them for banned tokens anyway.

**Never define tactic macros.** `macro`, `macro_rules`, `syntax`, `elab`, `elab_rules`, `notation`,
`infix*`, `prefix`, `postfix`, `#eval`, `run_cmd`, `run_elab`, `@[init`, `skipKernelTC`, `axiom`,
`unsafe`, `sorry`, `admit`, `native_decide`, `implemented_by`, `extern` are banned tokens, scanned
over the raw text **including comments**. 39163 was proved complete at 24.5 KB with macros and
became unshippable; that cost a session.

### 4.1 Where the six partial proofs are stuck — it is one shape

`rec5837_proof` (6 sorries in `main`), `rec12087` (7, in `V_free_partial`), `rec12234` (8, in
`Dfree`), `rec23354` (4, incl. `core_no_fix`), `rec24200` (`law`), `rec28626` (`law`) all fail on
the same goal: **one chain product `P` is decoded while another is free, and a rule's guard demands
`P = <a specific subterm>`; the size facts give only `sz P < sz (right arg of P)`, so `omega` cannot
separate `P` from that subterm.** `rec12234` says so in its own comment — *"no pure size argument
found separates that value from `a2 y`; would need a genuine strong induction"* — and `rec23354`
states it as the lemma it could not prove,
`core_no_fix (x) (htx : tg x = 2) : a1 x ≠ op (a2 x) x`.

That is exactly what §4 is for: a decoded value is not an arbitrary smaller term, it satisfies
`Enc`/`RF`, and the `eA1`-style consequence of that shape *does* separate it. If you are staring at
one of these sorries, stop hunting for a size lemma — define `Enc` and prove the fuel induction.
`rec24200` and `rec28626` are different: they have no `law` proof at all but everything below it is
done (`op_cases`/`TR10`/`TRs`/`P1_of_free` for 28626, 15 validated rules for 24200), so start those
two at §3.3, not at §4.

## 9. Checklist before the first judge call

1. `revalidate.py <eq>` clean **plus** `cf.deep_tests` 20,000 on two more seeds, on the *dualised*
   law if the law is R-form. 7 of 10 wave-1 skeletons were not models.
2. `grep -n "sorry\|admit" <file>` → nothing.
3. `grep -nE "macro|syntax|elab|notation|infix|prefix|postfix|#eval|run_cmd|run_elab|@\[init|skipKernelTC|axiom|unsafe|native_decide|implemented_by|extern" <file>` → nothing (comments count).
4. No `by_contra`, `tauto`, `split_ifs`, `linarith`, `norm_num` (no Mathlib).
5. `wc -c <file>` ≤ 19,900; if not, §8 in that order.
6. `python squeeze.py <file> <out> --rename` **and recompile `<out>`**.
7. `python devrow.py <eq1> <eq2>` for *this* row, then `devlean2.sh` prints `exit=0` with no
   `error:` line and no `warning: declaration uses 'sorry'`.
8. Namespace layout and the final `submission` term byte-identical to the generated file.
9. Local compile < 60 s.
10. One judge call, `python judge1.py <file> <eq1_id>:<eq2_id>`, nothing else running; then
    `dualcert.py` for the dual rows, copy to `certs/<row id>.lean`, append the ledger.

---

**Helper scripts written for this playbook**, both used above: `gen/_pb_gencases.py <rec<eq>.lean>`
emits the `op_cases` packing theorem from the skeleton text; `gen/_pb_common.py <rec<eq>.lean>`
prints the common / near-common conjuncts and the if-chain results. Scratch files from the compiles:
`gen/_pb_pre.lean`, `gen/_pb_scratch.lean`, `gen/_pb_cases11081.txt`, `gen/_pb_dig11081.txt`.
