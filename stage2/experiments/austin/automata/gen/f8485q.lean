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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a1 (a1 (a2 v))) = 2 ∧ a1 v = a2 (a1 (a1 (a2 v))) ∧ u = a2 (a1 (a2 v)) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg u = 2 ∧ tg (a2 u) = 2 ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v then op (a2 (a2 (a1 v))) (a1 v) else J u v
  let p2 := if hs2 : msr (p1) (u) < msr u v then op (p1) (u) else J u v
  let p3 := if hs3 : msr (p2) (u) < msr u v then op (p2) (u) else J u v
  let p4 := if hs4 : msr (a1 (a2 (a2 u))) (a1 v) < msr u v then op (a1 (a2 (a2 u))) (a1 v) else J u v
  let p5 := if hs5 : msr (p4) (u) < msr u v then op (p4) (u) else J u v
  let p6 := if hs6 : msr (p5) (u) < msr u v then op (p5) (u) else J u v
  let p7 := if hs7 : msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v then op (a1 (a1 (a2 (a2 u)))) (a1 v) else J u v
  let p8 := if hs8 : msr (p7) (u) < msr u v then op (p7) (u) else J u v
  let p9 := if hs9 : msr (p8) (u) < msr u v then op (p8) (u) else J u v
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (p2) (u) < msr u v ∧ a2 v = p3 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a2 u))) (a1 v) < msr u v ∧ msr (p4) (u) < msr u v ∧ msr (p5) (u) < msr u v ∧ a2 v = p6 then a1 v
  else if P4 u v ∧ msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v ∧ msr (p7) (u) < msr u v ∧ msr (p8) (u) < msr u v ∧ a2 v = p9 then a1 v
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
  change ¬ g 1 = op (g 0) (op (g 1) (op (g 1) (op (g 0) (op (g 2) (g 2)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 : M,
    p1 = (if hs1 : msr (a2 (a2 (a1 v))) (a1 v) < msr u v then op (a2 (a2 (a1 v))) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (p1) (u) < msr u v then op (p1) (u) else J u v) ∧
    p3 = (if hs3 : msr (p2) (u) < msr u v then op (p2) (u) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a2 (a2 u))) (a1 v) < msr u v then op (a1 (a2 (a2 u))) (a1 v) else J u v) ∧
    p5 = (if hs5 : msr (p4) (u) < msr u v then op (p4) (u) else J u v) ∧
    p6 = (if hs6 : msr (p5) (u) < msr u v then op (p5) (u) else J u v) ∧
    p7 = (if hs7 : msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v then op (a1 (a1 (a2 (a2 u)))) (a1 v) else J u v) ∧
    p8 = (if hs8 : msr (p7) (u) < msr u v then op (p7) (u) else J u v) ∧
    p9 = (if hs9 : msr (p8) (u) < msr u v then op (p8) (u) else J u v) ∧
    op u v = (
  if P1 u v then a1 v
  else if P2 u v ∧ msr (a2 (a2 (a1 v))) (a1 v) < msr u v ∧ msr (p1) (u) < msr u v ∧ msr (p2) (u) < msr u v ∧ a2 v = p3 then a1 v
  else if P3 u v ∧ msr (a1 (a2 (a2 u))) (a1 v) < msr u v ∧ msr (p4) (u) < msr u v ∧ msr (p5) (u) < msr u v ∧ a2 v = p6 then a1 v
  else if P4 u v ∧ msr (a1 (a1 (a2 (a2 u)))) (a1 v) < msr u v ∧ msr (p7) (u) < msr u v ∧ msr (p8) (u) < msr u v ∧ a2 v = p9 then a1 v
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- THE DIGEST.  Every one of the four rules returns `a1 v` and every one of them requires
    `tg v = 2`, so one two-line statement replaces all four rule lemmas. -/
theorem TR (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, -, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr ⟨h.1, rfl⟩
  · split
    · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩
    · split
      · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩
      · split
        · rename_i h; exact Or.inr ⟨h.1.1, rfl⟩
        · exact Or.inl rfl

theorem Wfree {u v : M} (h : tg v ≠ 2) : op u v = J u v := by
  rcases TR u v with hf | ⟨h2, -⟩
  · exact hf
  · exact absurd h2 h

theorem Wsz {u v : M} (h : op u v ≠ J u v) : sz (op u v) < sz v := by
  rcases TR u v with hf | ⟨h2, h3⟩
  · exact absurd hf h
  · rw [h3]; exact sz_a1_lt h2

/-- the payload is `a1 v` whenever anything fires: so on the law's top pair it is enough to
    show that the product is NOT free. -/
theorem Wpay {u v : M} (h : op u v ≠ J u v) : op u v = a1 v := by
  rcases TR u v with hf | ⟨-, h3⟩
  · exact absurd hf h
  · exact h3



theorem op_R1 {u v : M} (h : P1 u v) : op u v = a1 v := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, -, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  rw [hop, if_pos h]

theorem FREE (x y z : M)
    (hP : op z x = J z x) (hQ : op (J z x) y = J (J z x) y)
    (hR : op (J (J z x) y) y = J (J (J z x) y) y)
    (hS : op x (J (J (J z x) y) y) = J x (J (J (J z x) y) y)) :
    op (y) (op (x) (op (op (op (z) (x)) (y)) (y))) = x := by
  rw [hP, hQ, hR, hS]
  have h1 : P1 y (J x (J (J (J z x) y) y)) := by unfold P1; simp
  rw [op_R1 h1]; simp

/-- THE LAW: x = y * (x * (((z * x) * y) * y)) -/
theorem law (x y z : M) : op (y) (op (x) (op (op (op (z) (x)) (y)) (y))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
