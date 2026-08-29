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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2 ∧ a1 (a1 (a1 u)) = a2 (a1 u) ∧ a1 (a1 (a1 u)) = a2 u ∧ tg v = 2 ∧ a2 (a1 (a1 u)) = a1 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2 ∧ a1 (a1 (a1 u)) = a2 (a1 u) ∧ a1 (a1 (a1 u)) = a2 u ∧ tg (a2 (a1 (a1 u))) = 2 ∧ tg (a1 (a2 (a1 (a1 u)))) = 2 ∧ tg (a1 (a1 (a2 (a1 (a1 u))))) = 2 ∧ v = a2 (a1 (a1 (a2 (a1 (a1 u))))) ∧ a1 (a1 (a1 (a2 (a1 (a1 u))))) = a2 (a1 (a2 (a1 (a1 u)))) ∧ a1 (a1 (a1 (a2 (a1 (a1 u))))) = a2 (a2 (a1 (a1 u)))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2 ∧ a1 (a1 (a1 u)) = a2 (a1 u) ∧ a1 (a1 (a1 u)) = a2 u ∧ tg (a2 (a1 (a1 u))) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2 ∧ a1 (a1 (a1 u)) = a2 (a1 u) ∧ a1 (a1 (a1 u)) = a2 u ∧ tg (a2 (a1 (a1 u))) = 2 ∧ tg (a1 (a2 (a1 (a1 u)))) = 2 ∧ a2 (a1 (a2 (a1 (a1 u)))) = a2 (a2 (a1 (a1 u)))
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u ∧ tg v = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2 ∧ tg v = 2
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 (a2 u)) = 2 ∧ a1 u = a2 (a1 (a2 u)) ∧ a1 (a1 (a2 u)) = a2 (a2 u) ∧ tg (a1 (a1 (a2 u))) = 2 ∧ tg (a1 (a1 (a1 (a2 u)))) = 2 ∧ tg (a1 (a1 (a1 (a1 (a2 u))))) = 2 ∧ v = a2 (a1 (a1 (a1 (a1 (a2 u))))) ∧ a1 (a1 (a1 (a1 (a1 (a2 u))))) = a2 (a1 (a1 (a1 (a2 u)))) ∧ a1 (a1 (a1 (a1 (a1 (a2 u))))) = a2 (a1 (a1 (a2 u)))
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ a2 (a1 (a2 (a2 u))) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a1 (a2 u)) = 2 ∧ a1 u = a2 (a1 (a2 u)) ∧ a1 (a1 (a2 u)) = a2 (a2 u) ∧ tg (a1 (a1 (a2 u))) = 2 ∧ tg (a1 (a1 (a1 (a2 u)))) = 2 ∧ tg (a1 (a1 (a1 (a1 (a2 u))))) = 2 ∧ v = a2 (a1 (a1 (a1 (a1 (a2 u))))) ∧ a1 (a1 (a1 (a1 (a1 (a2 u))))) = a2 (a1 (a1 (a1 (a2 u)))) ∧ a1 (a1 (a1 (a1 (a1 (a2 u))))) = a2 (a1 (a1 (a2 u)))
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ a1 u = a1 (a2 u) ∧ tg (a2 (a2 u)) = 2 ∧ tg (a1 (a2 (a2 u))) = 2 ∧ a2 (a1 (a2 (a2 u))) = a2 (a2 (a2 u))
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v then op (a2 (a2 (a1 (a1 u)))) (v) else J u v
  let p2 := if hs2 : msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v then op (p1) (a2 (a2 (a1 (a1 u)))) else J u v
  let p3 := if hs3 : msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v then op (a2 (a1 (a2 (a1 (a1 u))))) (v) else J u v
  let p4 := if hs4 : msr (a2 (a1 u)) (a1 v) < msr u v then op (a2 (a1 u)) (a1 v) else J u v
  let p5 := if hs5 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p6 := if hs6 : msr (p5) (a2 u) < msr u v then op (p5) (a2 u) else J u v
  let p7 := if hs7 : msr (a2 u) (a1 (a1 (a2 u))) < msr u v then op (a2 u) (a1 (a1 (a2 u))) else J u v
  let p8 := if hs8 : msr (p7) (a2 u) < msr u v then op (p7) (a2 u) else J u v
  let p9 := if hs9 : msr (a2 (a2 u)) (a1 u) < msr u v then op (a2 (a2 u)) (a1 u) else J u v
  let p10 := if hs10 : msr (a2 u) (a2 (a2 u)) < msr u v then op (a2 u) (a2 (a2 u)) else J u v
  let p11 := if hs11 : msr (p10) (a2 u) < msr u v then op (p10) (a2 u) else J u v
  let p12 := if hs12 : msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v then op (a2 (a1 (a2 (a2 u)))) (v) else J u v
  if P1 u v then a2 (a1 (a1 u))
  else if P2 u v then a2 (a1 (a1 u))
  else if P3 u v ∧ msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v ∧ msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v ∧ a1 (a2 (a1 (a1 u))) = p2 then a2 (a1 (a1 u))
  else if P4 u v ∧ msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v ∧ a1 (a1 (a2 (a1 (a1 u)))) = p3 then a2 (a1 (a1 u))
  else if P5 u v ∧ msr (a2 (a1 u)) (a1 v) < msr u v ∧ a1 (a1 u) = p4 then a1 v
  else if P6 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (p5) (a2 u) < msr u v ∧ a1 u = p6 then a1 v
  else if P7 u v ∧ msr (a2 u) (a1 (a1 (a2 u))) < msr u v ∧ msr (p7) (a2 u) < msr u v ∧ a1 u = p8 then a1 (a1 (a2 u))
  else if P8 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 u) (a2 (a2 u)) < msr u v ∧ msr (p10) (a2 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 u = p11 ∧ a1 (a1 (a2 (a2 u))) = p12 then a2 (a2 u)
  else if P9 u v then a1 (a1 (a2 u))
  else if P10 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 (a1 (a2 (a2 u))) = p12 then a2 (a2 u)
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
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 : M,
    p1 = (if hs1 : msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v then op (a2 (a2 (a1 (a1 u)))) (v) else J u v) ∧
    p2 = (if hs2 : msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v then op (p1) (a2 (a2 (a1 (a1 u)))) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v then op (a2 (a1 (a2 (a1 (a1 u))))) (v) else J u v) ∧
    p4 = (if hs4 : msr (a2 (a1 u)) (a1 v) < msr u v then op (a2 (a1 u)) (a1 v) else J u v) ∧
    p5 = (if hs5 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p6 = (if hs6 : msr (p5) (a2 u) < msr u v then op (p5) (a2 u) else J u v) ∧
    p7 = (if hs7 : msr (a2 u) (a1 (a1 (a2 u))) < msr u v then op (a2 u) (a1 (a1 (a2 u))) else J u v) ∧
    p8 = (if hs8 : msr (p7) (a2 u) < msr u v then op (p7) (a2 u) else J u v) ∧
    p9 = (if hs9 : msr (a2 (a2 u)) (a1 u) < msr u v then op (a2 (a2 u)) (a1 u) else J u v) ∧
    p10 = (if hs10 : msr (a2 u) (a2 (a2 u)) < msr u v then op (a2 u) (a2 (a2 u)) else J u v) ∧
    p11 = (if hs11 : msr (p10) (a2 u) < msr u v then op (p10) (a2 u) else J u v) ∧
    p12 = (if hs12 : msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v then op (a2 (a1 (a2 (a2 u)))) (v) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a1 u))
  else if P2 u v then a2 (a1 (a1 u))
  else if P3 u v ∧ msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v ∧ msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v ∧ a1 (a2 (a1 (a1 u))) = p2 then a2 (a1 (a1 u))
  else if P4 u v ∧ msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v ∧ a1 (a1 (a2 (a1 (a1 u)))) = p3 then a2 (a1 (a1 u))
  else if P5 u v ∧ msr (a2 (a1 u)) (a1 v) < msr u v ∧ a1 (a1 u) = p4 then a1 v
  else if P6 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (p5) (a2 u) < msr u v ∧ a1 u = p6 then a1 v
  else if P7 u v ∧ msr (a2 u) (a1 (a1 (a2 u))) < msr u v ∧ msr (p7) (a2 u) < msr u v ∧ a1 u = p8 then a1 (a1 (a2 u))
  else if P8 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 u) (a2 (a2 u)) < msr u v ∧ msr (p10) (a2 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 u = p11 ∧ a1 (a1 (a2 (a2 u))) = p12 then a2 (a2 u)
  else if P9 u v then a1 (a1 (a2 u))
  else if P10 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 (a1 (a2 (a2 u))) = p12 then a2 (a2 u)
  else J u v) :=
  ⟨_, _, _, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩


/-- one unfold of `op`: free, or one of the ten rules fired (with its op-guards) -/
theorem TR10 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 (a1 u))) ∨
    (P2 u v ∧ op u v = a2 (a1 (a1 u))) ∨
    (P3 u v ∧ ∃ q1, q1 = op (a2 (a2 (a1 (a1 u)))) v ∧ a1 (a2 (a1 (a1 u))) = op q1 (a2 (a2 (a1 (a1 u)))) ∧ op u v = a2 (a1 (a1 u))) ∨
    (P4 u v ∧ a1 (a1 (a2 (a1 (a1 u)))) = op (a2 (a1 (a2 (a1 (a1 u))))) v ∧ op u v = a2 (a1 (a1 u))) ∨
    (P5 u v ∧ a1 (a1 u) = op (a2 (a1 u)) (a1 v) ∧ op u v = a1 v) ∨
    (P6 u v ∧ ∃ q5, q5 = op (a2 u) (a1 v) ∧ a1 u = op q5 (a2 u) ∧ op u v = a1 v) ∨
    (P7 u v ∧ ∃ q7, q7 = op (a2 u) (a1 (a1 (a2 u))) ∧ a1 u = op q7 (a2 u) ∧ op u v = a1 (a1 (a2 u))) ∨
    (P8 u v ∧ ∃ q9 q10, q9 = op (a2 (a2 u)) (a1 u) ∧ a1 (a2 u) = q9 ∧ q10 = op (a2 u) (a2 (a2 u)) ∧ a1 u = op q10 (a2 u) ∧
        a1 (a1 (a2 (a2 u))) = op (a2 (a1 (a2 (a2 u)))) v ∧ op u v = a2 (a2 u)) ∨
    (P9 u v ∧ op u v = a1 (a1 (a2 u))) ∨
    (P10 u v ∧ ∃ q9, q9 = op (a2 (a2 u)) (a1 u) ∧ a1 (a2 u) = q9 ∧
        a1 (a1 (a2 (a2 u))) = op (a2 (a1 (a2 (a2 u)))) v ∧ op u v = a2 (a2 u)) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hp12, hop⟩ := op_cases u v
  by_cases h1 : P1 u v
  · exact Or.inr (Or.inl ⟨h1, by rw [hop, if_pos h1]⟩)
  by_cases h2 : P2 u v
  · exact Or.inr (Or.inr (Or.inl ⟨h2, by rw [hop, if_neg h1, if_pos h2]⟩))
  by_cases h3c : P3 u v ∧ msr (a2 (a2 (a1 (a1 u)))) (v) < msr u v ∧ msr (p1) (a2 (a2 (a1 (a1 u)))) < msr u v ∧ a1 (a2 (a1 (a1 u))) = p2
  · obtain ⟨h3, hs1, hs2, he⟩ := h3c
    rw [dif_pos hs1] at hp1; subst hp1
    rw [dif_pos hs2] at hp2; subst hp2
    refine Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, _, rfl, he, ?_⟩)))
    rw [hop, if_neg h1, if_neg h2, if_pos ⟨h3, hs1, hs2, he⟩]
  by_cases h4c : P4 u v ∧ msr (a2 (a1 (a2 (a1 (a1 u))))) (v) < msr u v ∧ a1 (a1 (a2 (a1 (a1 u)))) = p3
  · obtain ⟨h4, hs3, he⟩ := h4c
    rw [dif_pos hs3] at hp3; subst hp3
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h4, he, ?_⟩))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_pos ⟨h4, hs3, he⟩]
  by_cases h5c : P5 u v ∧ msr (a2 (a1 u)) (a1 v) < msr u v ∧ a1 (a1 u) = p4
  · obtain ⟨h5, hs4, he⟩ := h5c
    rw [dif_pos hs4] at hp4; subst hp4
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h5, he, ?_⟩)))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_pos ⟨h5, hs4, he⟩]
  by_cases h6c : P6 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (p5) (a2 u) < msr u v ∧ a1 u = p6
  · obtain ⟨h6, hs5, hs6, he⟩ := h6c
    rw [dif_pos hs5] at hp5; subst hp5
    rw [dif_pos hs6] at hp6; subst hp6
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h6, _, rfl, he, ?_⟩))))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_pos ⟨h6, hs5, hs6, he⟩]
  by_cases h7c : P7 u v ∧ msr (a2 u) (a1 (a1 (a2 u))) < msr u v ∧ msr (p7) (a2 u) < msr u v ∧ a1 u = p8
  · obtain ⟨h7, hs7, hs8, he⟩ := h7c
    rw [dif_pos hs7] at hp7; subst hp7
    rw [dif_pos hs8] at hp8; subst hp8
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h7, _, rfl, he, ?_⟩)))))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_neg h6c, if_pos ⟨h7, hs7, hs8, he⟩]
  by_cases h8c : P8 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 u) (a2 (a2 u)) < msr u v ∧ msr (p10) (a2 u) < msr u v ∧
      msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧ a1 (a2 u) = p9 ∧ a1 u = p11 ∧ a1 (a1 (a2 (a2 u))) = p12
  · obtain ⟨h8, hs9, hs10, hs11, hs12, he9, he11, he12⟩ := h8c
    rw [dif_pos hs9] at hp9; subst hp9
    rw [dif_pos hs10] at hp10; subst hp10
    rw [dif_pos hs11] at hp11; subst hp11
    rw [dif_pos hs12] at hp12; subst hp12
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h8, _, _, rfl, he9, rfl, he11, he12, ?_⟩))))))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_neg h6c, if_neg h7c,
        if_pos ⟨h8, hs9, hs10, hs11, hs12, he9, he11, he12⟩]
  by_cases h9 : P9 u v
  · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h9, by
      rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_neg h6c, if_neg h7c, if_neg h8c,
          if_pos h9]⟩)))))))))
  by_cases h10c : P10 u v ∧ msr (a2 (a2 u)) (a1 u) < msr u v ∧ msr (a2 (a1 (a2 (a2 u)))) (v) < msr u v ∧
      a1 (a2 u) = p9 ∧ a1 (a1 (a2 (a2 u))) = p12
  · obtain ⟨h10, hs9, hs12, he9, he12⟩ := h10c
    rw [dif_pos hs9] at hp9; subst hp9
    rw [dif_pos hs12] at hp12; subst hp12
    refine Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ⟨h10, _, rfl, he9, he12, ?_⟩)))))))))
    rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_neg h6c, if_neg h7c, if_neg h8c, if_neg h9,
        if_pos ⟨h10, hs9, hs12, he9, he12⟩]
  left
  rw [hop, if_neg h1, if_neg h2, if_neg h3c, if_neg h4c, if_neg h5c, if_neg h6c, if_neg h7c, if_neg h8c, if_neg h9, if_neg h10c]

theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- weak characterisation: `op u v` is free, or a proper accessor of `u`, or a proper accessor of `v` -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ sz (op u v) < sz u) ∨ (tg v = 2 ∧ sz (op u v) < sz v) := by
  rcases TR10 u v with h | ⟨h1,he⟩ | ⟨h2,he⟩ | ⟨h3,_,_,_,he⟩ | ⟨h4,_,he⟩ | ⟨h5,_,he⟩ | ⟨h6,_,_,_,he⟩ | ⟨h7,_,_,_,he⟩ |
      ⟨h8,_,_,_,_,_,_,_,he⟩ | ⟨h9,he⟩ | ⟨h10,_,_,_,_,he⟩
  · exact Or.inl h
  · obtain ⟨t1,t2,t3,-,-,-,-⟩ := h1
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t3; have := sz_a1 (a1 u); have := sz_a1 u; omega
  · obtain ⟨t1,t2,t3,-,-,-,-,-,-,-,-⟩ := h2
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t3; have := sz_a1 (a1 u); have := sz_a1 u; omega
  · obtain ⟨t1,t2,t3,-,-,-⟩ := h3
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t3; have := sz_a1 (a1 u); have := sz_a1 u; omega
  · obtain ⟨t1,t2,t3,-,-,-,-,-⟩ := h4
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t3; have := sz_a1 (a1 u); have := sz_a1 u; omega
  · obtain ⟨-,-,-,t4⟩ := h5
    right; right; refine ⟨t4, ?_⟩; rw [he]
    exact sz_a1_lt t4
  · obtain ⟨-,t2⟩ := h6
    right; right; refine ⟨t2, ?_⟩; rw [he]
    exact sz_a1_lt t2
  · obtain ⟨t1,-,-,t4,-,-,-,-,-,-,-,-⟩ := h7
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a1_lt t4; have := sz_a1 (a2 u); have := sz_a2 u; omega
  · obtain ⟨t1,t2,-,-,-,-⟩ := h8
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t2; have := sz_a2 u; omega
  · obtain ⟨t1,-,-,t4,-,-,-,-,-,-,-,-⟩ := h9
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a1_lt t4; have := sz_a1 (a2 u); have := sz_a2 u; omega
  · obtain ⟨t1,t2,-,-,-,-⟩ := h10
    right; left; refine ⟨t1, ?_⟩; rw [he]
    have := sz_a2_lt t2; have := sz_a2 u; omega


theorem P1_of_free (y x z : M) : P1 (J (J (J y x) y) y) (J x z) :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (g 0) (op (op (op (g 1) (op (g 2) (g 2))) (g 0)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10]


/-- THE LAW: x = (((y * x) * y) * y) * (x * z) -/
theorem law (x y z : M) : op (op (op (op (y) (x)) (y)) (y)) (op (x) (z)) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
