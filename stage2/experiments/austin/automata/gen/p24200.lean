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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u ∧ tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 (a1 u) = a1 (a1 v) ∧ a2 (a1 v) = a2 v
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u ∧ tg v = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2 ∧ v = a2 (a2 (a1 u)) ∧ tg v = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 u = a1 (a1 v) ∧ a2 (a1 v) = a2 v ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a1 u = a1 (a1 (a2 u)) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 u = a1 (a1 v) ∧ a2 (a1 v) = a2 v ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a1 u = a1 (a1 (a2 u)) ∧ a2 (a1 (a2 u)) = a2 (a2 u)
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def P8 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ v = a2 (a2 u) ∧ tg v = 2
instance (u v : M) : Decidable (P8 u v) := by unfold P8; infer_instance
def P9 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = a2 v ∧ tg (a1 (a1 v)) = 2 ∧ tg (a1 (a1 (a1 v))) = 2 ∧ u = a1 (a1 (a1 (a1 v))) ∧ a2 (a1 (a1 (a1 v))) = a2 (a1 (a1 v)) ∧ a1 (a1 v) = u
instance (u v : M) : Decidable (P9 u v) := by unfold P9; infer_instance
def P10 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = a2 v ∧ tg (a1 (a1 v)) = 2 ∧ a1 (a1 v) = u
instance (u v : M) : Decidable (P10 u v) := by unfold P10; infer_instance
def P11 (u v : M) : Prop := tg v = 2 ∧ tg u = 2
instance (u v : M) : Decidable (P11 u v) := by unfold P11; infer_instance
def P12 (u v : M) : Prop := tg u = 2 ∧ v = a2 u ∧ tg v = 2
instance (u v : M) : Decidable (P12 u v) := by unfold P12; infer_instance
def P13 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u ∧ tg (a2 (a1 u)) = 2 ∧ v = a2 (a2 (a1 u)) ∧ tg v = 2
instance (u v : M) : Decidable (P13 u v) := by unfold P13; infer_instance
def P14 (u v : M) : Prop := tg u = 2 ∧ tg (a2 u) = 2 ∧ v = a2 (a2 u) ∧ tg v = 2
instance (u v : M) : Decidable (P14 u v) := by unfold P14; infer_instance
def P15 (u v : M) : Prop := tg u = 2 ∧ v = a2 u ∧ tg v = 2
instance (u v : M) : Decidable (P15 u v) := by unfold P15; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 u)) (a2 v) < msr u v then op (a2 (a1 u)) (a2 v) else J u v
  let p2 := if hs2 : msr (v) (a2 v) < msr u v then op (v) (a2 v) else J u v
  let p3 := if hs3 : msr (a2 (a1 u)) (v) < msr u v then op (a2 (a1 u)) (v) else J u v
  let p4 := if hs4 : msr (p3) (v) < msr u v then op (p3) (v) else J u v
  let p5 := if hs5 : msr (a1 u) (a2 (a2 u)) < msr u v then op (a1 u) (a2 (a2 u)) else J u v
  let p6 := if hs6 : msr (a2 u) (a2 v) < msr u v then op (a2 u) (a2 v) else J u v
  let p7 := if hs7 : msr (a2 u) (v) < msr u v then op (a2 u) (v) else J u v
  let p8 := if hs8 : msr (p7) (v) < msr u v then op (p7) (v) else J u v
  let p9 := if hs9 : msr (u) (a2 (a1 (a1 v))) < msr u v then op (u) (a2 (a1 (a1 v))) else J u v
  let p10 := if hs10 : msr (u) (a2 u) < msr u v then op (u) (a2 u) else J u v
  let p11 := if hs11 : msr (u) (a2 v) < msr u v then op (u) (a2 v) else J u v
  let p12 := if hs12 : msr (u) (v) < msr u v then op (u) (v) else J u v
  let p13 := if hs13 : msr (p12) (v) < msr u v then op (p12) (v) else J u v
  if P1 u v then a2 (a1 u)
  else if P2 u v ∧ msr (a2 (a1 u)) (a2 v) < msr u v ∧ a1 v = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 (a1 u)) (v) < msr u v ∧ msr (p3) (v) < msr u v ∧ a1 v = p2 ∧ v = p4 then a2 (a1 u)
  else if P4 u v then a2 u
  else if P5 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ a1 (a2 u) = p5 then a2 u
  else if P6 u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 v = p6 then a2 u
  else if P7 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p6 then a2 u
  else if P8 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 u) (v) < msr u v ∧ msr (p7) (v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 ∧ v = p8 then a2 u
  else if P9 u v then a1 (a1 v)
  else if P10 u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ a1 (a1 (a1 v)) = p9 then a1 (a1 v)
  else if P11 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (u) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p11 then u
  else if P12 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (u) (v) < msr u v ∧ msr (p12) (v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 ∧ v = p13 then u
  else if P13 u v ∧ msr (v) (a2 v) < msr u v ∧ a1 v = p2 then a2 (a1 u)
  else if P14 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 then a2 u
  else if P15 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 then u
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
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v ∨ P8 u v ∨ P9 u v ∨ P10 u v ∨ P11 u v ∨ P12 u v ∨ P13 u v ∨ P14 u v ∨ P15 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 1) (g 0) (g 2)
  revert this
  change ¬ g 1 = op (op (g 0) (op (g 1) (g 1))) (op (op (g 0) (g 2)) (g 0))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

theorem itec (R : M → Prop) {c : Prop} [inst : Decidable c] {a b : M}
    (h1 : c → R a) (h2 : ¬ c → R b) : R (if c then a else b) := by
  cases inst with
  | isTrue h => exact h1 h
  | isFalse h => exact h2 h

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10 p11 p12 p13 : M,
    p1 = (if hs1 : msr (a2 (a1 u)) (a2 v) < msr u v then op (a2 (a1 u)) (a2 v) else J u v) ∧
    p2 = (if hs2 : msr (v) (a2 v) < msr u v then op (v) (a2 v) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a1 u)) (v) < msr u v then op (a2 (a1 u)) (v) else J u v) ∧
    p4 = (if hs4 : msr (p3) (v) < msr u v then op (p3) (v) else J u v) ∧
    p5 = (if hs5 : msr (a1 u) (a2 (a2 u)) < msr u v then op (a1 u) (a2 (a2 u)) else J u v) ∧
    p6 = (if hs6 : msr (a2 u) (a2 v) < msr u v then op (a2 u) (a2 v) else J u v) ∧
    p7 = (if hs7 : msr (a2 u) (v) < msr u v then op (a2 u) (v) else J u v) ∧
    p8 = (if hs8 : msr (p7) (v) < msr u v then op (p7) (v) else J u v) ∧
    p9 = (if hs9 : msr (u) (a2 (a1 (a1 v))) < msr u v then op (u) (a2 (a1 (a1 v))) else J u v) ∧
    p10 = (if hs10 : msr (u) (a2 u) < msr u v then op (u) (a2 u) else J u v) ∧
    p11 = (if hs11 : msr (u) (a2 v) < msr u v then op (u) (a2 v) else J u v) ∧
    p12 = (if hs12 : msr (u) (v) < msr u v then op (u) (v) else J u v) ∧
    p13 = (if hs13 : msr (p12) (v) < msr u v then op (p12) (v) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v ∧ msr (a2 (a1 u)) (a2 v) < msr u v ∧ a1 v = p1 then a2 (a1 u)
  else if P3 u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 (a1 u)) (v) < msr u v ∧ msr (p3) (v) < msr u v ∧ a1 v = p2 ∧ v = p4 then a2 (a1 u)
  else if P4 u v then a2 u
  else if P5 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ a1 (a2 u) = p5 then a2 u
  else if P6 u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 v = p6 then a2 u
  else if P7 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (a2 u) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p6 then a2 u
  else if P8 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (a2 u) (v) < msr u v ∧ msr (p7) (v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 ∧ v = p8 then a2 u
  else if P9 u v then a1 (a1 v)
  else if P10 u v ∧ msr (u) (a2 (a1 (a1 v))) < msr u v ∧ a1 (a1 (a1 v)) = p9 then a1 (a1 v)
  else if P11 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (u) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p11 then u
  else if P12 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ msr (u) (v) < msr u v ∧ msr (p12) (v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 ∧ v = p13 then u
  else if P13 u v ∧ msr (v) (a2 v) < msr u v ∧ a1 v = p2 then a2 (a1 u)
  else if P14 u v ∧ msr (a1 u) (a2 (a2 u)) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 (a2 u) = p5 ∧ a1 v = p2 then a2 u
  else if P15 u v ∧ msr (u) (a2 u) < msr u v ∧ msr (v) (a2 v) < msr u v ∧ a1 u = p10 ∧ a1 v = p2 then u
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, _, _, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

def Dg (u v w : M) : Prop := w = J u v ∨ (tg u = 2 ∧ tg v = 2 ∧
  ((w = a2 u ∧ ((tg (a1 v) = 2 ∧ a1 (a1 v) = a2 u ∧ a2 (a1 v) = a2 v)
      ∨ a1 v = op (a2 u) (a2 v) ∨ a1 v = op v (a2 v)))
   ∨ (w = u ∧ a1 u = op u (a2 u))))

theorem Dg0 (u v : M) : Dg u v (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13,
    hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hp12, hp13, hop⟩ := op_cases u v
  rw [hop]
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, -, A3, A4, A5, A6, A7⟩ := k
    exact Or.inr ⟨A1, A4, Or.inl ⟨A3, Or.inl ⟨A5, A6.symm.trans A3, A7⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, A4⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp1
    rw [A3] at hp1
    exact Or.inr ⟨A1, A4, Or.inl ⟨A3, Or.inr (Or.inl (ge.trans hp1))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, -, -, A6⟩, g2, -, -, ge, -⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A6, Or.inl ⟨A3, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, A2, A3, A4, A5, -, -, -, -⟩ := k
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inl ⟨A3, A4.symm, A5⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, A3, A4, A5, -⟩, -, -⟩ := k
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inl ⟨A3, A4.symm, A5⟩⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, -, -, -, -⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp6
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inr (Or.inl (ge.trans hp6))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, -⟩, -, gg, -, ge⟩ := k
    rw [dif_pos gg] at hp6
    exact Or.inr ⟨A1, A2, Or.inl ⟨rfl, Or.inr (Or.inl (ge.trans hp6))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4⟩, -, g2, -, -, -, ge, -⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A4, Or.inl ⟨rfl, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · exfalso
    obtain ⟨-, -, -, A4, -, A6, -, A8⟩ := k
    rw [A8] at A4 A6
    have h1 := sz_a1_lt A4
    have h2 := sz_a1 (a1 u)
    have h3 := congrArg sz A6
    omega
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4, A5⟩, gg, ge⟩ := k
    rw [A5] at A4 gg ge hp9
    rw [dif_pos gg] at hp9
    exact Or.inr ⟨A4, A1, Or.inr ⟨A5, ge.trans hp9⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2⟩, g10, -, e1, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A2, A1, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3⟩, g10, -, -, -, e1, -, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A1, A3, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3, -, -, A6⟩, g2, ge⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A6, Or.inl ⟨A3, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, -, A4⟩, -, g2, -, ge⟩ := k
    rw [dif_pos g2] at hp2
    exact Or.inr ⟨A1, A4, Or.inl ⟨rfl, Or.inr (Or.inr (ge.trans hp2))⟩⟩
  refine itec (Dg u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -, A3⟩, g10, -, e1, -⟩ := k
    rw [dif_pos g10] at hp10
    exact Or.inr ⟨A1, A3, Or.inr ⟨rfl, e1.trans hp10⟩⟩
  exact Or.inl rfl

theorem NOQ (n : Nat) : ∀ u : M, sz u ≤ n → tg u = 2 → a1 u ≠ op u (a2 u) := by
  induction n with
  | zero => intro u hn _ _; have := sz_pos u; omega
  | succ n ih =>
    intro u hn ht he
    have h2 := sz_a1_lt ht
    have h3 := sz_a2_lt ht
    rcases Dg0 u (a2 u) with hf | ⟨-, hv, hd⟩
    · rw [hf] at he
      have := congrArg sz he
      rw [szJ] at this
      have := sz_pos (a2 u)
      omega
    · rcases hd with ⟨hr, hb⟩ | ⟨hr, -⟩
      · rw [hr] at he
        rcases hb with ⟨-, q2, -⟩ | q | q
        · have e1 := sz_a1_lt hv
          have e2 := sz_a1 (a1 (a2 u))
          have e3 := congrArg sz q2
          omega
        · exact ih (a2 u) (by omega) hv q
        · exact ih (a2 u) (by omega) hv q
      · rw [hr] at he
        have := congrArg sz he
        omega

theorem Dg3 (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ tg v = 2 ∧ op u v = a2 u ∧
    ((tg (a1 v) = 2 ∧ a1 (a1 v) = a2 u ∧ a2 (a1 v) = a2 v) ∨ a1 v = op (a2 u) (a2 v))) := by
  rcases Dg0 u v with hf | ⟨hu, hv, hd⟩
  · exact Or.inl hf
  · rcases hd with ⟨hr, hb⟩ | ⟨-, hq⟩
    · rcases hb with q | q | q
      · exact Or.inr ⟨hu, hv, hr, Or.inl q⟩
      · exact Or.inr ⟨hu, hv, hr, Or.inr q⟩
      · exact absurd q (NOQ (sz v) v (Nat.le_refl _) hv)
    · exact absurd hq (NOQ (sz u) u (Nat.le_refl _) hu)

theorem DD (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ op u v = a2 u) := by
  rcases Dg3 u v with h | ⟨hu, -, hr, -⟩
  · exact Or.inl h
  · exact Or.inr ⟨hu, hr⟩

theorem key {b w : M} (hw : tg w = 2)
    (hi : (tg (a1 b) = 2 ∧ a1 (a1 b) = w ∧ a2 (a1 b) = a2 b) ∨ a1 b = op w (a2 b))
    (ho : (tg (a1 b) = 2 ∧ a1 (a1 b) = a2 w ∧ a2 (a1 b) = a2 b) ∨ a1 b = op (a2 w) (a2 b)) :
    False := by
  have s1 := sz_a2_lt hw
  have s2 := sz_a2 (a2 w)
  have s3 := sz_pos (a2 b)
  have s4 := sz_a1 (a1 b)
  rcases hi with ⟨q1, q2, -⟩ | q
  · have s5 := sz_a1_lt q1
    rcases ho with ⟨-, r2, -⟩ | r
    · have := congrArg sz (q2.symm.trans r2); omega
    · rcases DD (a2 w) (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at r
      · rw [r] at q2
        simp only [a1_J_eq] at q2
        have := congrArg sz q2; omega
      · have e1 := congrArg sz r
        have e2 := congrArg sz q2
        omega
  · rcases ho with ⟨r1, r2, -⟩ | r
    · have s5 := sz_a1_lt r1
      rcases DD w (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at q
      · rw [q] at r2
        simp only [a1_J_eq] at r2
        have := congrArg sz r2; omega
      · have e1 := congrArg sz q
        have e2 := congrArg sz r2
        omega
    · rcases DD w (a2 b) with hd | ⟨-, hd⟩ <;> rw [hd] at q <;>
        rcases DD (a2 w) (a2 b) with he | ⟨ht, he⟩ <;> rw [he] at r
      · have := congrArg sz (q.symm.trans r)
        rw [szJ, szJ] at this; omega
      · have := congrArg sz (q.symm.trans r)
        rw [szJ] at this; omega
      · have := congrArg sz (q.symm.trans r)
        rw [szJ] at this; omega
      · have h9 := sz_a2_lt ht
        have := congrArg sz (q.symm.trans r)
        omega

theorem FREE (a b : M) : op (op a b) b = J (op a b) b := by
  by_cases hF : op (op a b) b = J (op a b) b
  · exact hF
  exfalso
  rcases Dg3 (op a b) b with h | ⟨hu, hv, -, hb⟩
  · exact hF h
  rcases Dg3 a b with hi | ⟨-, -, hres, hbi⟩
  · rw [hi] at hb
    simp only [a2_J_eq] at hb
    rcases hb with ⟨q1, q2, -⟩ | q
    · have e1 := sz_a1_lt hv
      have e2 := sz_a1_lt q1
      have e3 := congrArg sz q2
      omega
    · exact NOQ (sz b) b (Nat.le_refl _) hv q
  · rw [hres] at hb hu
    exact key hu hbi hb

theorem fires {u v : M} (hu : tg u = 2) (hv : tg v = 2)
    (g1 : msr (a2 u) (a2 v) < msr u v)
    (gv : a1 v = op (a2 u) (a2 v))
    (h : (tg (a1 u) = 2 ∧ a2 (a1 u) = a2 u)
       ∨ (tg (a2 u) = 2 ∧ tg (a1 (a2 u)) = 2 ∧ a1 (a1 (a2 u)) = a1 u ∧ a2 (a1 (a2 u)) = a2 (a2 u))
       ∨ (tg (a2 u) = 2 ∧ a1 (a2 u) = op (a1 u) (a2 (a2 u))
            ∧ msr (a1 u) (a2 (a2 u)) < msr u v)) :
    op u v = a2 u := by
  obtain ⟨p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13,
    hp1, hp2, hp3, hp4, hp5, hp6, hp7, hp8, hp9, hp10, hp11, hp12, hp13, hop⟩ := op_cases u v
  rw [hop]
  refine itec (fun t => t = a2 u) (fun k => k.2.2.1) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun k => k.1.2.2.1) (fun n2 => ?_)
  refine itec (fun t => t = a2 u) (fun k => k.1.2.2.1) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun _ => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun n6 => ?_)
  refine itec (fun t => t = a2 u) (fun _ => rfl) (fun n7 => ?_)
  exfalso
  rcases h with ⟨ht, he⟩ | ⟨t1, t2, t3, t4⟩ | ⟨t1, t2, t3⟩
  · have gg : msr (a2 (a1 u)) (a2 v) < msr u v := by rw [he]; exact g1
    rw [dif_pos gg] at hp1
    rw [he] at hp1
    exact n2 ⟨⟨hu, ht, he, hv⟩, gg, gv.trans hp1.symm⟩
  · rw [dif_pos g1] at hp6
    exact n6 ⟨⟨hu, hv, t1, t2, t3.symm, t4⟩, g1, gv.trans hp6.symm⟩
  · rw [dif_pos t3] at hp5
    rw [dif_pos g1] at hp6
    exact n7 ⟨⟨hu, hv, t1⟩, t3, g1, t2.trans hp5.symm, gv.trans hp6.symm⟩

theorem law (x y z : M) : op (op (op (y) (x)) (x)) (op (op (x) (z)) (z)) = x := by
  rw [FREE y x, FREE x z]
  show op (J (op y x) x) (J (op x z) z) = a2 (J (op y x) x)
  refine fires rfl rfl ?_ ?_ ?_
  · simp only [a2_J_eq]
    apply msr_lt_of_max_lt
    simp only [szJ]
    have := sz_pos (op y x); have := sz_pos (op x z); have := sz_pos x; have := sz_pos z
    omega
  · simp only [a1_J_eq, a2_J_eq]
  · simp only [a1_J_eq, a2_J_eq]
    rcases Dg3 y x with hf | ⟨-, hx, hres, hb⟩
    · exact Or.inl ⟨by rw [hf]; rfl, by rw [hf]; rfl⟩
    · rcases hb with ⟨q1, q2, q3⟩ | q
      · exact Or.inr (Or.inl ⟨hx, q1, q2.trans hres.symm, q3⟩)
      · refine Or.inr (Or.inr ⟨hx, q.trans (by rw [hres]), ?_⟩)
        apply msr_lt_of_max_lt
        simp only [szJ]
        have := sz_a2 x; have := sz_pos (op x z); have := sz_pos z; have := sz_pos x
        omega


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
