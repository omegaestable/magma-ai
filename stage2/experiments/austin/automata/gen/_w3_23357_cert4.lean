-- REFUTED MODEL: the 4-rule set this file proves things about is FALSE (gen/NOTES_23357.md, families C1/C2). Kept for its model-independent lemmas only. DO NOT SHIP.
import JudgeProblem
set_option linter.unusedSimpArgs false
set_option linter.unusedVariables false
set_option warn.classDefReducibility false

inductive submission.M : Type where
  | g : Nat → submission.M
  | J : submission.M → submission.M → submission.M
  deriving DecidableEq

namespace submission
open M

def tg : M → Nat
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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a2 v) = 2 ∧ a1 (a1 u) = a1 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else J u v
  let p2 := if hs2 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p3 := if hs3 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v
  let p4 := if hs4 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v
  let p5 := if hs5 : msr (p4) (a1 (a2 v)) < msr u v then op (p4) (a1 (a2 v)) else J u v
  if P1 u v then a2 (a1 u)
  else if P2 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p2 ∧ a1 (a2 u) = p3 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p4) (a1 (a2 v)) < msr u v ∧ u = p5 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (g 1) (g 1))) (op (op (g 0) (g 2)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
@[simp] theorem sz_J (a b : M) : sz (M.J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem a1_ne {t : M} (h : tg t = 2) : a1 t ≠ t := by
  intro hc; have := sz_a1_lt h; rw [hc] at this; omega
theorem a2_ne {t : M} (h : tg t = 2) : a2 t ≠ t := by
  intro hc; have := sz_a2_lt h; rw [hc] at this; omega

/-- the `op` body with the five nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
    p1 = (if hs1 : msr (a2 (a2 (a1 u))) (v) < msr u v then op (a2 (a2 (a1 u))) (v) else J u v) ∧
    p2 = (if hs2 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a2 u)) (a2 v) < msr u v then op (a2 (a2 u)) (a2 v) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v) ∧
    p5 = (if hs5 : msr (p4) (a1 (a2 v)) < msr u v then op (p4) (a1 (a2 v)) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v ∧ msr (a2 (a2 (a1 u))) (v) < msr u v ∧ a1 (a2 (a1 u)) = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a2 (a2 u)) (a2 v) < msr u v ∧ a1 u = p2 ∧ a1 (a2 u) = p3 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p4) (a1 (a2 v)) < msr u v ∧ u = p5 then a1 v
  else J u v) :=
  ⟨_, _, _, _, _, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired, with its op-guards -/
theorem D (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 u)) ∨
    (P2 u v ∧ a1 (a2 (a1 u)) = op (a2 (a2 (a1 u))) v ∧ op u v = a2 (a1 u)) ∨
    (P3 u v ∧ a1 u = op (a2 u) (a1 v) ∧ a1 (a2 u) = op (a2 (a2 u)) (a2 v) ∧ op u v = a1 v) ∨
    (P4 u v ∧ u = op (op (a1 (a2 v)) (a1 v)) (a1 (a2 v)) ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨q, hs, he⟩ := h
      rw [dif_pos hs] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨q, he, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨q, hsa, hsb, hea, heb⟩ := h
        rw [dif_pos hsa] at hp2; rw [dif_pos hsb] at hp3
        subst hp2; subst hp3
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨q, hea, heb, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨q, hsa, hsb, he⟩ := h
          rw [dif_pos hsa] at hp4; subst hp4
          rw [dif_pos hsb] at hp5; subst hp5
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨q, he, rfl⟩)))
        · left; rfl

/-- the two-branch digest: a decode is an L-read `a2 (a1 u)` off a u-shaped `u`, or an R-read `a1 v`. -/
theorem TR (u v : M) : op u v = J u v ∨
    (tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ op u v = a2 (a1 u)) ∨
    (tg v = 2 ∧ op u v = a1 v) := by
  rcases D u v with h | ⟨q, h⟩ | ⟨q, -, h⟩ | ⟨q, -, -, h⟩ | ⟨q, -, h⟩
  · exact Or.inl h
  · exact Or.inr (Or.inl ⟨q.1, q.2.1, q.2.2.1, h⟩)
  · exact Or.inr (Or.inl ⟨q.1, q.2.1, q.2.2.1, h⟩)
  · exact Or.inr (Or.inr ⟨q.2.1, h⟩)
  · exact Or.inr (Or.inr ⟨q.1, h⟩)

/-- sizes: a decode is a proper subterm of one of its two arguments -/
theorem SZ (u v : M) : op u v = J u v ∨ sz (op u v) + 3 ≤ sz u ∨ sz (op u v) < sz v := by
  rcases TR u v with h | ⟨h1, h2, -, h4⟩ | ⟨h1, h2⟩
  · exact Or.inl h
  · refine Or.inr (Or.inl ?_)
    have e1 := sz_tg u h1
    have e2 := sz_tg (a1 u) h2
    have e3 := sz_pos (a1 (a1 u))
    have e4 := sz_pos (a2 u)
    rw [h4]; omega
  · exact Or.inr (Or.inr (by rw [h2]; exact sz_a1_lt h1))

/-- the max form, which is what every `msr` gate wants.  Stated from `TR`, not from `SZ`:
    `omega` cannot see through a `max` on both sides (gen/LEMMA_LIBRARY.md, `mxl`), so keep the
    `max` on one side with `Nat.le_max_*` as the only bridge. -/
theorem SZM (u v : M) : op u v = J u v ∨ sz (op u v) + 2 ≤ max (sz u) (sz v) := by
  rcases TR u v with h | ⟨h1, h2, -, h4⟩ | ⟨h1, h2⟩
  · exact Or.inl h
  · refine Or.inr ?_
    have hm := Nat.le_max_left (sz u) (sz v)
    have e1 := sz_tg u h1
    have e2 := sz_tg (a1 u) h2
    have e3 := sz_pos (a1 (a1 u))
    have e4 := sz_pos (a2 u)
    rw [h4]; omega
  · refine Or.inr ?_
    have hm := Nat.le_max_right (sz u) (sz v)
    have e := sz_tg v h1
    have e2 := sz_pos (a2 v)
    rw [h2]; omega

/-- a product that shrank below its right argument is not the free product -/
theorem NEFREE {u v : M} (h : sz (op u v) < sz v) : op u v ≠ J u v := by
  intro hc; rw [hc] at h; simp only [sz_J] at h; have := sz_pos u; omega

/-- the all-free top cell: rule 1 fires and every one of its seven conjuncts is `rfl`. -/
theorem TOP1 (x y z : M) : op (J (J y x) y) (J x (J y z)) = x := by
  obtain ⟨p1, p2, p3, p4, p5, -, -, -, -, -, hop⟩ := op_cases (J (J y x) y) (J x (J y z))
  rw [hop, if_pos (show P1 (J (J y x) y) (J x (J y z)) from ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)]
  rfl

/-- **the lever that replaces 23354's `Ffree`**: rule 4 (`As`) recomputes `u` from `v`, and at the top
    of this law's chain, with `v = J x (J y z)`, that recomputation is `op (op y x) y` -- i.e. `u`
    itself, by `rfl`.  So rule 4's op-guard is free of charge in every cell where `V` and `B` are free,
    whatever `op y x` did.  What is left to show for those cells is only that the three earlier
    branches either do not fire or also return `x`. -/
theorem TOP4G (x y z : M) :
    op (op (a1 (a2 (J x (J y z)))) (a1 (J x (J y z)))) (a1 (a2 (J x (J y z)))) = op (op y x) y := rfl

/-- ... and its two `msr` gates hold as soon as `op y x` is free, which is the cell that matters. -/
theorem TOP4S (x y z : M) (hA : op y x = J y x) :
    msr (a1 (a2 (J x (J y z)))) (a1 (J x (J y z))) < msr (op (op y x) y) (J x (J y z)) := by
  apply msr_lt_of_max_lt
  have hu : op (op y x) y = J (J y x) y ∨ sz (op (op y x) y) + 2 ≤ max (sz (J y x)) (sz y) := by
    rw [hA] at *; exact SZM (J y x) y
  have h1 := sz_pos x
  have h2 := sz_pos y
  have h3 := sz_pos z
  have hm := Nat.le_max_right (sz (op (op y x) y)) (sz (J x (J y z)))
  simp only [a1_J_eq, a2_J_eq, sz_J] at *
  omega

/-- THE LAW: x = ((y * x) * y) * (x * (y * z)) -/
theorem law (x y z : M) : op (op (op (y) (x)) (y)) (op (x) (op (y) (z))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
