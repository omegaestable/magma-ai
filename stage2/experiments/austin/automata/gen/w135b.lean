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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ u = a1 (a1 v) ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ a2 (a1 (a2 (a1 v))) = a2 (a2 (a1 v)) ∧ a2 (a1 (a2 (a1 v))) = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a2 (a2 v)) = 2 ∧ tg (a1 (a2 (a2 v))) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v then op (a1 (a1 (a2 v))) (a2 v) else J u v
  let p2 := if hs2 : msr (p1) (a2 v) < msr u v then op (p1) (a2 v) else J u v
  let p3 := if hs3 : msr (u) (p2) < msr u v then op (u) (p2) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v
  let p5 := if hs5 : msr (p4) (a2 (a2 v)) < msr u v then op (p4) (a2 (a2 v)) else J u v
  let p6 := if hs6 : msr (a1 (a2 v)) (p5) < msr u v then op (a1 (a2 v)) (p5) else J u v
  let p7 := if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v
  let p8 := if hs8 : msr (u) (J (p7) (p5)) < msr u v then op (u) (J (p7) (p5)) else J u v
  let p9 := if hs9 : msr (p8) (a2 v) < msr u v then op (p8) (a2 v) else J u v
  let p10 := if hs10 : msr (p9) (a2 v) < msr u v then op (p9) (a2 v) else J u v
  let p11 := if hs11 : msr (u) (p10) < msr u v then op (u) (p10) else J u v
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ msr (p1) (a2 v) < msr u v ∧ msr (u) (p2) < msr u v ∧ a1 v = p3 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p4) (a2 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (p5) < msr u v ∧ msr (u) (p6) < msr u v ∧ msr (u) (J (p7) (p5)) < msr u v ∧ msr (p8) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ msr (u) (p10) < msr u v ∧ a1 v = p11 then p8
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
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sA1 {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sA2 {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem mx {a b u v : M} (h : msr a b < msr u v) : max (sz a) (sz b) ≤ max (sz u) (sz v) := by
  apply Classical.byContradiction; intro hc
  have := msr_lt_of_max_lt (a := u) (b := v) (u := a) (v := b) (by omega)
  omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 : M,
    p1 = (if hs1 : msr (a1 (a1 (a2 v))) (a2 v) < msr u v then op (a1 (a1 (a2 v))) (a2 v) else J u v) ∧
    p2 = (if hs2 : msr (p1) (a2 v) < msr u v then op (p1) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (u) (p2) < msr u v then op (u) (p2) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v then op (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) else J u v) ∧
    p5 = (if hs5 : msr (p4) (a2 (a2 v)) < msr u v then op (p4) (a2 (a2 v)) else J u v) ∧
    p6 = (if hs6 : msr (a1 (a2 v)) (p5) < msr u v then op (a1 (a2 v)) (p5) else J u v) ∧
    p7 = (if hs7 : msr (u) (p6) < msr u v then op (u) (p6) else J u v) ∧
    p8 = (if hs8 : msr (u) (J (p7) (p5)) < msr u v then op (u) (J (p7) (p5)) else J u v) ∧
    p9 = (if hs9 : msr (p8) (a2 v) < msr u v then op (p8) (a2 v) else J u v) ∧
    p10 = (if hs10 : msr (p9) (a2 v) < msr u v then op (p9) (a2 v) else J u v) ∧
    p11 = (if hs11 : msr (u) (p10) < msr u v then op (u) (p10) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a1 (a2 (a1 v)))
  else if P2 u v ∧ msr (a1 (a1 (a2 v))) (a2 v) < msr u v ∧ msr (p1) (a2 v) < msr u v ∧ msr (u) (p2) < msr u v ∧ a1 v = p3 then a1 (a1 (a2 v))
  else if P3 u v ∧ msr (a1 (a1 (a2 (a2 v)))) (a2 (a2 v)) < msr u v ∧ msr (p4) (a2 (a2 v)) < msr u v ∧ msr (a1 (a2 v)) (p5) < msr u v ∧ msr (u) (p6) < msr u v ∧ msr (u) (J (p7) (p5)) < msr u v ∧ msr (p8) (a2 v) < msr u v ∧ msr (p9) (a2 v) < msr u v ∧ msr (u) (p10) < msr u v ∧ a1 v = p11 then p8
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the full one-unfold digest: free, or R1, or R2 (with its gate), or R3 (recursive, with its gate) -/
theorem TR (u v : M) : op u v = J u v ∨ (P1 u v ∧ op u v = a1 (a1 (a2 (a1 v)))) ∨
    (tg v = 2 ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ op u v = a1 (a1 (a2 v)) ∧
      msr u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v)) < msr u v ∧
      a1 v = op u (op (op (a1 (a1 (a2 v))) (a2 v)) (a2 v))) ∨
    (tg v = 2 ∧ ∃ q, msr u q < msr u v ∧ op u v = op u q ∧
      msr u (op (op (op u q) (a2 v)) (a2 v)) < msr u v ∧
      a1 v = op u (op (op (op u q) (a2 v)) (a2 v))) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h
      obtain ⟨h2, g1, g2, g3, he⟩ := h
      rw [dif_pos g1] at hp1; subst hp1
      rw [dif_pos g2] at hp2; subst hp2
      rw [dif_pos g3] at hp3; subst hp3
      exact Or.inr (Or.inr (Or.inl ⟨h2.1, h2.2.1, h2.2.2, rfl, g3, he⟩))
    · split
      · rename_i h
        obtain ⟨h3, g1, g2, g3, g4, g5, g6, g7, g8, he⟩ := h
        rw [dif_pos g1] at hp4; subst hp4
        rw [dif_pos g2] at hp5; subst hp5
        rw [dif_pos g3] at hp6; subst hp6
        rw [dif_pos g4] at hp7; subst hp7
        rw [dif_pos g5] at hp8; subst hp8
        rw [dif_pos g6] at hp9; subst hp9
        rw [dif_pos g7] at hp10; subst hp10
        rw [dif_pos g8] at hp11; subst hp11
        exact Or.inr (Or.inr (Or.inr ⟨h3.1, _, g5, rfl, g8, he⟩))
      · exact Or.inl rfl

theorem SUn (n : Nat) : ∀ u v : M, msr u v < n → op u v ≠ J u v → sz u < sz v := by
  induction n with
  | zero => intro u v h; omega
  | succ n ih =>
    intro u v hn hne
    have key : ∀ q : M, tg v = 2 → msr u q < msr u v → a1 v = op u q → sz u < sz v := by
      intro q h1 hg he
      have hv := sA1 h1
      have hm := mx hg
      by_cases hf : op u q = J u q
      · rw [hf] at he; have := congrArg sz he; simp only [sz] at this; omega
      · have := ih u q (by omega) hf; omega
    rcases TR u v with h | ⟨h1, -⟩ | ⟨h1, -, -, -, hg, he⟩ | ⟨h1, q, -, -, hg, he⟩
    · exact absurd h hne
    · have e1 := sz_a1 (a1 v); have e2 := sA1 h1.1; rw [h1.2.2.1]; omega
    · exact key _ h1 hg he
    · exact key _ h1 hg he

theorem SU {u v : M} (h : op u v ≠ J u v) : sz u < sz v := SUn (msr u v + 1) u v (Nat.lt_succ_self _) h

theorem Wf {u v : M} (h : sz v ≤ sz u) : op u v = J u v := by
  apply Classical.byContradiction; intro hc; have := SU hc; omega

theorem oR1 {u v : M} (h : P1 u v) : op u v = a1 (a1 (a2 (a1 v))) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, -, -, -, -, -, -, -, -, -, -, -, hop⟩ := op_cases u v
  rw [hop, if_pos h]

theorem law (x y z : M) : op (z) (op (op (z) (op (op (x) (y)) (y))) (y)) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
