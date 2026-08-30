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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ a2 u = a1 (a2 (a2 v)) ∧ a1 v = a2 (a2 (a2 v))
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v)
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg v = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ a1 v = a2 (a2 (a2 v)) ∧ tg (a1 (a2 (a2 v))) = 2 ∧ tg (a2 (a1 (a2 (a2 v)))) = 2 ∧ a1 (a1 (a2 (a2 v))) = a1 (a2 (a1 (a2 (a2 v)))) ∧ tg (a2 (a2 (a1 (a2 (a2 v))))) = 2 ∧ u = a1 (a2 (a2 (a1 (a2 (a2 v))))) ∧ a1 (a1 (a2 (a2 v))) = a2 (a2 (a2 (a1 (a2 (a2 v)))))
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def P5 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ a1 v = a2 (a2 (a2 v)) ∧ tg (a1 (a2 (a2 v))) = 2
instance (u v : M) : Decidable (P5 u v) := by unfold P5; infer_instance
def P6 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2 ∧ a1 v = a2 (a2 (a2 v)) ∧ tg (a1 (a2 (a2 v))) = 2 ∧ tg (a2 (a1 (a2 (a2 v)))) = 2 ∧ a1 (a1 (a2 (a2 v))) = a1 (a2 (a1 (a2 (a2 v))))
instance (u v : M) : Decidable (P6 u v) := by unfold P6; infer_instance
def P7 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2
instance (u v : M) : Decidable (P7 u v) := by unfold P7; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p2 := if hs2 : msr (a1 v) (p1) < msr u v then op (a1 v) (p1) else J u v
  let p3 := if hs3 : msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v then op (u) (a1 (a1 (a2 (a2 v)))) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a2 (a2 v)))) (p3) < msr u v then op (a1 (a1 (a2 (a2 v)))) (p3) else J u v
  let p5 := if hs5 : msr (u) (a1 (a2 (a2 v))) < msr u v then op (u) (a1 (a2 (a2 v))) else J u v
  let p6 := if hs6 : msr (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) < msr u v then op (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) else J u v
  if P1 u v then a2 u
  else if P2 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a2 (a2 v) = p1 then a2 u
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a1 v) (p1) < msr u v ∧ a2 v = p2 then a2 u
  else if P4 u v then a1 (a2 (a2 v))
  else if P5 u v ∧ msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v ∧ msr (a1 (a1 (a2 (a2 v)))) (p3) < msr u v ∧ a2 (a1 (a2 (a2 v))) = p4 then a1 (a2 (a2 v))
  else if P6 u v ∧ msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v ∧ a2 (a2 (a1 (a2 (a2 v)))) = p3 then a1 (a2 (a2 v))
  else if P7 u v ∧ msr (u) (a1 (a2 (a2 v))) < msr u v ∧ msr (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) < msr u v ∧ a2 (a2 (a2 v)) = p5 ∧ a2 (a2 v) = p6 then J (a1 (a2 (a2 v))) (a2 (a2 v))
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v ∨ P5 u v ∨ P6 u v ∨ P7 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (g 0)) (op (op (g 1) (op (g 2) (g 2))) (g 1))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4, P5, P6, P7]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl

theorem Z (R : M → Prop) {c : Prop} [inst : Decidable c] {a b : M}
    (h1 : c → R a) (h2 : ¬ c → R b) : R (if c then a else b) := by
  cases inst with
  | isTrue h => exact h1 h
  | isFalse h => exact h2 h

theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 p6 : M,
    p1 = (if hs1 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (a1 v) (p1) < msr u v then op (a1 v) (p1) else J u v) ∧
    p3 = (if hs3 : msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v then op (u) (a1 (a1 (a2 (a2 v)))) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a2 (a2 v)))) (p3) < msr u v then op (a1 (a1 (a2 (a2 v)))) (p3) else J u v) ∧
    p5 = (if hs5 : msr (u) (a1 (a2 (a2 v))) < msr u v then op (u) (a1 (a2 (a2 v))) else J u v) ∧
    p6 = (if hs6 : msr (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) < msr u v then op (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) else J u v) ∧
    op u v = (
  if P1 u v then a2 u
  else if P2 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a2 (a2 v) = p1 then a2 u
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ msr (a1 v) (p1) < msr u v ∧ a2 v = p2 then a2 u
  else if P4 u v then a1 (a2 (a2 v))
  else if P5 u v ∧ msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v ∧ msr (a1 (a1 (a2 (a2 v)))) (p3) < msr u v ∧ a2 (a1 (a2 (a2 v))) = p4 then a1 (a2 (a2 v))
  else if P6 u v ∧ msr (u) (a1 (a1 (a2 (a2 v)))) < msr u v ∧ a2 (a2 (a1 (a2 (a2 v)))) = p3 then a1 (a2 (a2 v))
  else if P7 u v ∧ msr (u) (a1 (a2 (a2 v))) < msr u v ∧ msr (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) < msr u v ∧ a2 (a2 (a2 v)) = p5 ∧ a2 (a2 v) = p6 then J (a1 (a2 (a2 v))) (a2 (a2 v))
  else J u v
    ) :=
  ⟨_, _, _, _, _, _, rfl, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the digest: every rule either returns `a2 u` (needs `tg u = 2`) or reads the encoding out of
    `v` (needs the four `v`-conjuncts). -/
def E (u v w : M) : Prop :=
  w = J u v ∨ (tg u = 2 ∧ w = a2 u)
  ∨ (tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2
     ∧ (w = a1 (a2 (a2 v)) ∨ (w = J (a1 (a2 (a2 v))) (a2 (a2 v)) ∧ msr w (a1 v) < msr u v)))

theorem Dg (u v : M) : E u v (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, hp1, hp2, hp3, hp4, hp5, hp6, hop⟩ := op_cases u v
  rw [hop]
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, -⟩ := k; exact Or.inr (Or.inl ⟨A1, rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -⟩, -⟩ := k; exact Or.inr (Or.inl ⟨A1, rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, -⟩, -⟩ := k; exact Or.inr (Or.inl ⟨A1, rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, A2', A3, A4, -⟩ := k
    exact Or.inr (Or.inr ⟨A1, A2', A3, A4, Or.inl rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2', A3, A4, -⟩, -⟩ := k
    exact Or.inr (Or.inr ⟨A1, A2', A3, A4, Or.inl rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2', A3, A4, -⟩, -⟩ := k
    exact Or.inr (Or.inr ⟨A1, A2', A3, A4, Or.inl rfl⟩)
  refine Z (E u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2', A3, A4⟩, -, gg2, -⟩ := k
    exact Or.inr (Or.inr ⟨A1, A2', A3, A4, Or.inr ⟨rfl, gg2⟩⟩)
  exact Or.inl rfl

/-- `u` a generator and `v` not of the encoding shape forces the free product. -/
theorem Wf {u v : M} (h1 : tg u ≠ 2) (h2 : tg (a2 (a2 v)) ≠ 2) : op u v = J u v := by
  rcases Dg u v with h | ⟨h, -⟩ | ⟨-, -, -, h, -⟩
  · exact h
  · exact absurd h h1
  · exact absurd h h2

/-- "v encodes w": the three unfolding depths the rules read. -/
def Enc (w v : M) : Prop :=
  (tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ tg (a2 (a2 v)) = 2
     ∧ a1 (a2 (a2 v)) = w ∧ a1 v = a2 (a2 (a2 v)))
  ∨ (tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ a2 (a2 v) = op w (a1 v))
  ∨ (tg v = 2 ∧ a2 v = op (a1 v) (op w (a1 v)))

def RF (u w : M) : Prop := (tg u = 2 ∧ a2 u = w) ∨ Enc u w

def SNDp (u v w : M) : Prop := w = J u v ∨ (Enc w v ∧ RF u w)

theorem SND (u v : M) : SNDp u v (op u v) := by
  obtain ⟨p1, p2, p3, p4, p5, p6, hp1, hp2, hp3, hp4, hp5, hp6, hop⟩ := op_cases u v
  rw [hop]
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨A1, A2, A3, A4, A5, A6, A7⟩ := k
    exact Or.inr ⟨Or.inl ⟨A2, A3, A4, A5, A6.symm, A7⟩, Or.inl ⟨A1, rfl⟩⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2, A3, A4⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp1; subst hp1
    exact Or.inr ⟨Or.inr (Or.inl ⟨A2, A3, A4, ge⟩), Or.inl ⟨A1, rfl⟩⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨A1, A2⟩, gg, gg2, ge⟩ := k
    rw [dif_pos gg] at hp1; subst hp1
    rw [dif_pos gg2] at hp2; subst hp2
    exact Or.inr ⟨Or.inr (Or.inr ⟨A2, ge⟩), Or.inl ⟨A1, rfl⟩⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11⟩ := k
    exact Or.inr ⟨Or.inl ⟨B1, B2, B3, B4, rfl, B5⟩,
      Or.inr (Or.inl ⟨B6, B7, B8, B9, B10.symm, B11⟩)⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨B1, B2, B3, B4, B5, B6⟩, gg, gg2, ge⟩ := k
    rw [dif_pos gg] at hp3; subst hp3
    rw [dif_pos gg2] at hp4; subst hp4
    exact Or.inr ⟨Or.inl ⟨B1, B2, B3, B4, rfl, B5⟩, Or.inr (Or.inr (Or.inr ⟨B6, ge⟩))⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨B1, B2, B3, B4, B5, B6, B7, B8⟩, gg, ge⟩ := k
    rw [dif_pos gg] at hp3; subst hp3
    exact Or.inr ⟨Or.inl ⟨B1, B2, B3, B4, rfl, B5⟩,
      Or.inr (Or.inr (Or.inl ⟨B6, B7, B8, ge⟩))⟩
  refine Z (SNDp u v) (fun k => ?_) (fun _ => ?_)
  · obtain ⟨⟨C1, C2, C3, C4⟩, gg, gg2, ge1, ge2⟩ := k
    rw [dif_pos gg] at hp5; subst hp5
    rw [dif_pos gg2] at hp6; subst hp6
    refine Or.inr ⟨Or.inr (Or.inl ⟨C1, C2, C3, ge2⟩), Or.inr (Or.inr (Or.inl ⟨rfl, ?_, ?_, ?_⟩))⟩
    · exact C4
    · rfl
    · exact ge1
  exact Or.inl rfl

theorem mx {a b u v : M} (h : msr a b < msr u v) : max (sz a) (sz b) ≤ max (sz u) (sz v) := by
  apply Classical.byContradiction; intro hc
  exact Nat.lt_irrefl _ (Nat.lt_of_lt_of_le h (Nat.le_of_lt (msr_lt_of_max_lt (by omega))))

/-- the general result-size invariant: a decoded product never exceeds its larger argument.
    R1-R3 give `a2 u`; R4-R6 give a subterm of `v`; R7's J-result is bounded by its own gate (`mx`). -/
theorem RSZ (u v : M) : op u v = J u v ∨ sz (op u v) ≤ max (sz u) (sz v) := by
  rcases Dg u v with h | ⟨h1, h2⟩ | ⟨h1, h2, h3, h4, hr⟩
  · exact Or.inl h
  · refine Or.inr ?_
    have := sz_a2_lt h1; rw [h2]; omega
  · refine Or.inr ?_
    rcases hr with hr | ⟨hr, hg⟩
    · have e1 := sz_a2_lt h1; have e2 := sz_a2_lt h2; have e3 := sz_a1 (a2 (a2 v))
      rw [hr]; omega
    · have := mx hg; omega

/-- corollary: if `v` is not big enough, the product is free. -/
theorem WfL {u v : M} (h : max (sz u) (sz v) < sz (op u v)) : op u v = J u v := by
  rcases RSZ u v with hf | hs
  · exact hf
  · omega

/-- the A-free top product: `u = J y x` and `v` the free two-level encoding. -/
theorem TOPL (x y z Q : M) (hP : op x z = Q) : op (J y x) (J z (J z Q)) = x := by
  obtain ⟨p1, p2, p3, p4, p5, p6, hp1, hp2, hp3, hp4, hp5, hp6, hop⟩ :=
    op_cases (J y x) (J z (J z Q))
  have hs1 : msr (a2 (J y x)) (a1 (J z (J z Q))) < msr (J y x) (J z (J z Q)) := by
    simp only [a1_J_eq, a2_J_eq]
    apply msr_lt_of_max_lt
    have := sz_pos x; have := sz_pos y; have := sz_pos z; have := sz_pos Q
    simp only [sz_J]; omega
  rw [dif_pos hs1] at hp1
  simp only [a1_J_eq, a2_J_eq] at hp1
  subst hp1
  rw [hop]
  refine Z (fun t => t = x) (fun _ => rfl) (fun n2 => ?_)
  refine Z (fun t => t = x) (fun _ => rfl) (fun n3 => ?_)
  exact absurd ⟨⟨rfl, rfl, rfl, rfl⟩, hs1, by simp only [a2_J_eq]; exact hP.symm⟩ n3

theorem mxl {a b c d : M} (h1 : sz a < sz d) (h2 : sz b < sz d) :
    max (sz a) (sz b) < max (sz c) (sz d) := by
  rw [Nat.max_def, Nat.max_def]; split <;> split <;> omega

/-- `Enc` shape1 makes the payload a proper subterm of the encoding, two levels down. -/
theorem E1sz {r v : M} (h1 : tg v = 2) (h2 : tg (a2 v) = 2) (h4 : tg (a2 (a2 v)) = 2)
    (h5 : a1 (a2 (a2 v)) = r) : sz r + 2 ≤ sz v := by
  have e1 := sz_a2_lt h1
  have e2 := sz_a2_lt h2
  have e3 := sz_a1 (a2 (a2 v))
  have e4 := sz_pos (a2 (a2 v))
  rw [← h5]; omega

/-- REMAINING HOLE 1 -- the freeness invariant (W3-7). -/
theorem F1 (x z : M) : op z (op x z) = J z (op x z) := by
  by_cases hf : op z (op x z) = J z (op x z)
  · exact hf
  exfalso
  rcases SND z (op x z) with h | ⟨hE, hR⟩
  · exact hf h
  rcases hE with ⟨E1, E2, E3, E4, E5, E6⟩ | ⟨E1, E2, E3, E4⟩ | ⟨E1, E2⟩
  · -- Enc shape1 : op x z = J c (J c (J r c)) with c = a1 (op x z), r = op z (op x z)
    rcases hR with ⟨R1, R2⟩ | hz
    · sorry   -- L1
    · sorry   -- L2
  · rcases hR with ⟨R1, R2⟩ | hz
    · sorry   -- L3
    · sorry   -- L4
  · rcases hR with ⟨R1, R2⟩ | hz
    · sorry   -- L5
    · sorry   -- L6

/-- REMAINING HOLE 2 -- B free. Same shape as F1, one level out. -/
theorem F2 (x z : M) : op z (op z (op x z)) = J z (op z (op x z)) := by
  sorry

/-- REMAINING HOLE 3 -- the converse of SND (only the A-decoded half is still needed:
    `TOPL` above already discharges the A-free half without it). -/
theorem CMP (n : Nat) : ∀ u v w : M, msr u v < n → Enc w v → RF u w → op u v = w := by
  sorry

theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (z) (op (x) (z)))) = x := by
  rw [F2 x z]
  refine CMP (msr (op y x) (J z (op z (op x z))) + 1) _ _ x (Nat.lt_succ_self _) ?_ ?_
  · exact Or.inr (Or.inr ⟨rfl, rfl⟩)
  · by_cases h : op y x = J y x
    · exact Or.inl ⟨by rw [h]; rfl, by rw [h]; rfl⟩
    · rcases SND y x with hf | ⟨he, -⟩
      · exact absurd hf h
      · exact Or.inr he

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
