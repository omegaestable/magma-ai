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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2 ∧ a1 v = a2 (a1 (a2 (a2 v))) ∧ a1 (a1 (a2 (a2 v))) = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ u = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a2 (a2 (a1 v))) = 2 ∧ tg (a1 (a2 (a2 (a1 v)))) = 2 ∧ a2 (a1 (a2 (a2 (a1 v)))) = a1 (a1 v) ∧ a1 (a1 (a2 (a2 (a1 v)))) = a2 (a2 (a2 (a1 v)))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a2 (a2 v) = a1 v
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a2 (a2 v))) (a1 v) < msr u v then op (a2 (a2 (a2 v))) (a1 v) else J u v
  let p2 := if hs2 : msr (a1 (a2 (a1 v))) (a1 v) < msr u v then op (a1 (a2 (a1 v))) (a1 v) else J u v
  let p3 := if hs3 : msr (p2) (a1 (a2 (a1 v))) < msr u v then op (p2) (a1 (a2 (a1 v))) else J u v
  let p4 := if hs4 : msr (u) (p3) < msr u v then op (u) (p3) else J u v
  let p5 := if hs5 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v
  let p6 := if hs6 : msr (p5) (a1 (a2 v)) < msr u v then op (p5) (a1 (a2 v)) else J u v
  let p7 := if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a2 v))) (a1 v) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p2) (a1 (a2 (a1 v))) < msr u v ∧ msr (u) (p3) < msr u v ∧ a2 v = p4 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p5) (a1 (a2 v)) < msr u v ∧ msr (u) (p6) < msr u v ∧ a2 v = p7 then a1 v
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 2) (g 2)) (op (op (g 0) (op (g 1) (g 1))) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 : M,
    p1 = (if hs1 : msr (a2 (a2 (a2 v))) (a1 v) < msr u v then op (a2 (a2 (a2 v))) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 (a1 v))) (a1 v) < msr u v then op (a1 (a2 (a1 v))) (a1 v) else J u v) ∧
    p3 = (if hs3 : msr (p2) (a1 (a2 (a1 v))) < msr u v then op (p2) (a1 (a2 (a1 v))) else J u v) ∧
    p4 = (if hs4 : msr (u) (p3) < msr u v then op (u) (p3) else J u v) ∧
    p5 = (if hs5 : msr (a1 (a2 v)) (a1 v) < msr u v then op (a1 (a2 v)) (a1 v) else J u v) ∧
    p6 = (if hs6 : msr (p5) (a1 (a2 v)) < msr u v then op (p5) (a1 (a2 v)) else J u v) ∧
    p7 = (if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a2 v))) (a1 v) < msr u v ∧ a1 (a2 (a2 v)) = p1 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p2) (a1 (a2 (a1 v))) < msr u v ∧ msr (u) (p3) < msr u v ∧ a2 v = p4 then a1 v
  else if P4 u v ∧ msr (a1 (a2 v)) (a1 v) < msr u v ∧ msr (p5) (a1 (a2 v)) < msr u v ∧ msr (u) (p6) < msr u v ∧ a2 v = p7 then a1 v
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guard). -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a1 v) ∨
    (P2 u v ∧ a1 (a2 (a2 v)) = op (a2 (a2 (a2 v))) (a1 v) ∧ op u v = a1 v) ∨
    (P3 u v ∧ a2 v = op u (op (op (a1 (a2 (a1 v))) (a1 v)) (a1 (a2 (a1 v)))) ∧ op u v = a1 v) ∨
    (P4 u v ∧ a2 v = op u (op (op (a1 (a2 v)) (a1 v)) (a1 (a2 v))) ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h
      obtain ⟨h2, hs1, he⟩ := h
      rw [dif_pos hs1] at hp1; subst hp1
      exact Or.inr (Or.inr (Or.inl ⟨h2, he, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs2, hs3, hs4, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        rw [dif_pos hs4] at hp4; subst hp4
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs5, hs6, hs7, he⟩ := h
          rw [dif_pos hs5] at hp5; subst hp5
          rw [dif_pos hs6] at hp6; subst hp6
          rw [dif_pos hs7] at hp7; subst hp7
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he, rfl⟩)))
        · left; rfl

/-- the digest: every rule needs `tg v = 2` and returns `a1 v`. -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v) := by
  rcases TR4 u v with h | ⟨h, e⟩ | ⟨h, -, e⟩ | ⟨h, -, e⟩ | ⟨h, -, e⟩
  · exact Or.inl h
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩
  · exact Or.inr ⟨h.1, e⟩

/-- a decoded product is strictly smaller than its right argument. -/
theorem TRsz (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  rcases TRs u v with h | ⟨ht, e⟩
  · exact Or.inl h
  · exact Or.inr (by rw [e]; exact sz_a1_lt ht)

theorem law (x y z : M) : op (z) (op (x) (op (z) (op (op (y) (x)) (y)))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
