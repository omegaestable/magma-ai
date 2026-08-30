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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 v) = 2 ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v
  let p2 := if hs2 : msr (a1 (a2 (a1 u))) (u) < msr u v then op (a1 (a2 (a1 u))) (u) else J u v
  let p3 := if hs3 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v
  if P1 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p1 then a1 (a1 v)
  else if P2 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p2 then a1 (a1 v)
  else if P3 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p3 then a1 (a1 v)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (op (op (op (g 0) (g 0)) (g 1)) (g 2)) (g 2)) (g 1)
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3]



theorem szp (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem s1L {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := szp b; omega
theorem s2L {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := szp a; omega
@[simp] theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem gle {a b u v : M} (h1 : sz a ≤ sz u) (h2 : sz b ≤ sz v) (h3 : sz a + sz b < sz u + sz v) :
    msr a b < msr u v := by
  rcases Nat.lt_or_ge (max (sz a) (sz b)) (max (sz u) (sz v)) with h | h
  · exact msr_lt_of_max_lt h
  · exact msr_lt_of_max_eq (by omega) h3

theorem op_cases (u v : M) : ∃ p1 p2 p3 : M,
    p1 = (if hs1 : msr (u) (a1 (a1 v)) < msr u v then op (u) (a1 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (a1 (a2 (a1 u))) (u) < msr u v then op (a1 (a2 (a1 u))) (u) else J u v) ∧
    p3 = (if hs3 : msr (a2 (a2 u)) (u) < msr u v then op (a2 (a2 u)) (u) else J u v) ∧
    op u v = (
  if P1 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ a2 (a1 v) = p1 then a1 (a1 v)
  else if P2 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a1 (a2 (a1 u))) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p2 then a1 (a1 v)
  else if P3 u v ∧ msr (u) (a1 (a1 v)) < msr u v ∧ msr (a2 (a2 u)) (u) < msr u v ∧ a2 (a1 v) = p1 ∧ a2 v = p3 then a1 (a1 v)
  else J u v
    ) :=
  ⟨_, _, _, rfl, rfl, rfl, op.eq_1 u v⟩

/-- "a2 v is `op z u` for some z", in its two canonical readings -/
def CK (u C : M) : Prop :=
  (tg C = 2 ∧ u = a2 C)
  ∨ (tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ C = op (a1 (a2 (a1 u))) u)
  ∨ (tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 u) = 2 ∧ C = op (a2 (a2 u)) u)

/-- one unfold: free, or the single decode shape with all of the firing rule's data -/
theorem TR (u v : M) : op u v = J u v ∨
    (op u v = a1 (a1 v) ∧ tg v = 2 ∧ tg (a1 v) = 2 ∧ a2 (a1 v) = op u (a1 (a1 v)) ∧ CK u (a2 v)) := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h
    obtain ⟨hP, g1, he⟩ := h
    rw [dif_pos g1] at hp1; subst hp1
    exact Or.inr ⟨rfl, hP.1, hP.2.1, he, Or.inl ⟨hP.2.2.1, hP.2.2.2⟩⟩
  · split
    · rename_i h
      obtain ⟨hP, g1, g2, he, he2⟩ := h
      rw [dif_pos g1] at hp1; subst hp1
      rw [dif_pos g2] at hp2; subst hp2
      exact Or.inr ⟨rfl, hP.1, hP.2.1, he,
        Or.inr (Or.inl ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2, he2⟩)⟩
    · split
      · rename_i h
        obtain ⟨hP, g1, g3, he, he3⟩ := h
        rw [dif_pos g1] at hp1; subst hp1
        rw [dif_pos g3] at hp3; subst hp3
        exact Or.inr ⟨rfl, hP.1, hP.2.1, he,
          Or.inr (Or.inr ⟨hP.2.2.1, hP.2.2.2.1, hP.2.2.2.2, he3⟩)⟩
      · exact Or.inl rfl

/-- a decoded result is at least four smaller than the right argument -/
theorem Wsz {u v : M} (h : op u v ≠ J u v) : op u v = a1 (a1 v) ∧ sz (a1 (a1 v)) + 4 ≤ sz v := by
  rcases TR u v with hf | ⟨hr, h1, h2, -, -⟩
  · exact absurd hf h
  · refine ⟨hr, ?_⟩
    have e1 := sz_tg v h1
    have e2 := sz_tg (a1 v) h2
    have e3 := szp (a2 v)
    have e4 := szp (a2 (a1 v))
    omega

/-- no term is `op k` of itself -/
theorem NF {k t : M} (h : t = op k t) : False := by
  rcases TR k t with hf | ⟨hr, h1, h2, -, -⟩
  · rw [hf] at h; have := congrArg sz h; simp only [szJ] at this; have := szp k; omega
  · rw [hr] at h
    have e1 := sz_tg t h1
    have e2 := sz_tg (a1 t) h2
    have e3 := szp (a2 t)
    have e4 := szp (a2 (a1 t))
    have := congrArg sz h
    omega


/-- a decoded result is never the free product -/
theorem NJ {u v : M} (h1 : tg v = 2) (h2 : tg (a1 v) = 2) (h : op u v = a1 (a1 v)) :
    op u v ≠ J u v := by
  intro c
  rw [c] at h
  have := congrArg sz h
  have e1 := sz_tg v h1
  have e2 := sz_tg (a1 v) h2
  have e3 := szp (a2 v)
  have e4 := szp (a2 (a1 v))
  have e5 := szp u
  simp only [szJ] at this
  omega

/-- if `op y x` decodes then `sz y < sz x` -/
theorem KY (n : Nat) : ∀ x y : M, sz x ≤ n → op y x ≠ J y x → sz y < sz x := by
  induction n with
  | zero => intro x y hn _; have := szp x; omega
  | succ n ih =>
    intro x y hn hne
    rcases TR y x with hf | ⟨hr, h1, h2, hA, hC⟩
    · exact absurd hf hne
    · have e1 := sz_tg x h1
      have e2 := sz_tg (a1 x) h2
      have e3 := szp (a2 x)
      have e4 := szp (a2 (a1 x))
      have e5 := sz_a1 (a1 x)
      have e6 := sz_a2 (a2 x)
      rcases hC with ⟨q1, q2⟩ | ⟨-, -, -, q⟩ | ⟨-, -, -, q⟩
      · have := sz_a2 (a2 x); have := sz_a2 x; rw [q2]; omega
      · rcases TR (a1 (a2 (a1 y))) y with hf2 | ⟨hr2, -, -, -, -⟩
        · rw [hf2] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a1 (a2 (a1 y))); omega
        · rw [hr2] at q
          rcases TR y (a1 (a1 x)) with hf3 | ⟨hr3, t1, t2, -, -⟩
          · rw [hf3] at hA; have := congrArg sz hA; simp only [szJ] at this; omega
          · have := ih (a1 (a1 x)) y (by omega) (NJ t1 t2 hr3)
            omega
      · rcases TR (a2 (a2 y)) y with hf2 | ⟨hr2, -, -, -, -⟩
        · rw [hf2] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a2 (a2 y)); omega
        · rw [hr2] at q
          rcases TR y (a1 (a1 x)) with hf3 | ⟨hr3, t1, t2, -, -⟩
          · rw [hf3] at hA; have := congrArg sz hA; simp only [szJ] at this; omega
          · have := ih (a1 (a1 x)) y (by omega) (NJ t1 t2 hr3)
            omega
theorem KY' {x y : M} (h : op y x ≠ J y x) : sz y < sz x := KY (sz x) x y (Nat.le_refl _) h

/-- the second chain product is always free -/
theorem Bfree (x y : M) : op x (op y x) = J x (op y x) := by
  apply Classical.byContradiction; intro hne
  rcases TR x (op y x) with hf | ⟨-, h1, h2, hA, hC⟩
  · exact hne hf
  · rcases TR y x with hb | ⟨hbr, hb1, hb2, -, -⟩
    · rw [hb] at h1 h2 hA hC
      rcases hC with ⟨q1, q2⟩ | ⟨-, -, -, q⟩ | ⟨-, -, -, q⟩
      · simp only [a2_J_eq] at q1 q2
        have := s2L q1; rw [← q2] at this; omega
      · simp only [a2_J_eq] at q; exact NF q
      · simp only [a2_J_eq] at q; exact NF q
    · rw [hbr] at h1 h2 hA hC
      have f1 := sz_tg x hb1
      have f2 := sz_tg (a1 x) hb2
      have f3 := szp (a2 x)
      have f4 := szp (a2 (a1 x))
      have f5 := s2L h1
      rcases hC with ⟨q1, q2⟩ | ⟨-, -, -, q⟩ | ⟨-, -, -, q⟩
      · have := congrArg sz q2
        have := sz_a2 (a2 (a1 (a1 x)))
        omega
      · rcases TR (a1 (a2 (a1 x))) x with hg | ⟨hgr, -, -, -, -⟩
        · rw [hg] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a1 (a2 (a1 x))); omega
        · rw [hgr] at q; have := congrArg sz q; omega
      · rcases TR (a2 (a2 x)) x with hg | ⟨hgr, -, -, -, -⟩
        · rw [hg] at q; have := congrArg sz q; simp only [szJ] at this
          have := szp (a2 (a2 x)); omega
        · rw [hgr] at q; have := congrArg sz q; omega

/-- the top product of the law always fires -/
theorem FIRE {u v : M} (hs : sz u < sz v) (hv : tg v = 2) (hv1 : tg (a1 v) = 2)
    (hA : a2 (a1 v) = op u (a1 (a1 v))) (hC : CK u (a2 v)) : op u v = a1 (a1 v) := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u v
  have b0 := s1L hv
  have b1 := sz_a1 (a1 v)
  have g1 : msr u (a1 (a1 v)) < msr u v := gle (Nat.le_refl _) (by omega) (by omega)
  have c1 := sz_a1 (a2 (a1 u))
  have c2 := sz_a2 (a1 u)
  have c3 := sz_a1 u
  have g2 : msr (a1 (a2 (a1 u))) u < msr u v := gle (by omega) (by omega) (by omega)
  have d1 := sz_a2 (a2 u)
  have d2 := sz_a2 u
  have g3 : msr (a2 (a2 u)) u < msr u v := gle (by omega) (by omega) (by omega)
  rw [dif_pos g1] at hp1; subst hp1
  rw [dif_pos g2] at hp2; subst hp2
  rw [dif_pos g3] at hp3; subst hp3
  rw [hop]
  split
  · rfl
  · split
    · rfl
    · split
      · rfl
      · rename_i n1 n2 n3
        exfalso
        rcases hC with ⟨k1, k2⟩ | ⟨k1, k2, k3, k4⟩ | ⟨k1, k2, k3, k4⟩
        · exact n1 ⟨⟨hv, hv1, k1, k2⟩, g1, hA⟩
        · exact n2 ⟨⟨hv, hv1, k1, k2, k3⟩, g1, g2, hA, k4⟩
        · exact n3 ⟨⟨hv, hv1, k1, k2, k3⟩, g1, g3, hA, k4⟩

/-- CLOSURE: `a2 v = op z u` is recognised for every z.  TWO CASES REMAIN OPEN (see NOTES_11081.md). -/
theorem CKlem (z y : M) : CK y (op z y) := by
  rcases TR z y with hf | ⟨hr, h1, h2, hA, hC⟩
  · rw [hf]; exact Or.inl ⟨rfl, rfl⟩
  · rw [hr]
    rcases TR z (a1 (a1 y)) with hg | ⟨hgr, -, -, -, -⟩
    · rw [hg] at hA
      refine Or.inr (Or.inl ⟨h1, h2, by rw [hA]; rfl, ?_⟩)
      rw [hA]; simp only [a1_J_eq]; exact hr.symm
    · rcases hC with ⟨q1, q2⟩ | ⟨-, -, -, q⟩ | ⟨-, -, -, q⟩
      · refine Or.inr (Or.inr ⟨h1, h2, q1, ?_⟩)
        rw [← q2]; exact hr.symm
      · rcases TR (a1 (a2 (a1 z))) z with hh | ⟨hhr, -, -, -, -⟩
        · rw [hh] at q
          refine Or.inr (Or.inr ⟨h1, h2, by rw [q]; rfl, ?_⟩)
          rw [q]; simp only [a2_J_eq]; exact hr.symm
        · sorry
      · rcases TR (a2 (a2 z)) z with hh | ⟨hhr, -, -, -, -⟩
        · rw [hh] at q
          refine Or.inr (Or.inr ⟨h1, h2, by rw [q]; rfl, ?_⟩)
          rw [q]; simp only [a2_J_eq]; exact hr.symm
        · sorry

/-- `sz x < sz (J x (op y x))` and, when `op y x` decodes, `sz y < sz x` -/
theorem BS (x y : M) : sz x < sz (J x (op y x)) ∧ (op y x = J y x ∨ sz y < sz x) := by
  have := szp (op y x)
  rcases TR y x with hb | ⟨hbr, hb1, hb2, -, -⟩
  · exact ⟨by simp only [szJ]; omega, Or.inl hb⟩
  · exact ⟨by simp only [szJ]; omega, Or.inr (KY' (NJ hb1 hb2 hbr))⟩

/-- the fourth chain product is always free.  TWO LEAVES OPEN (see NOTES_11081.md). -/
theorem Dfree (x y z : M) : op (J x (op y x)) (op z y) = J (J x (op y x)) (op z y) := by
  apply Classical.byContradiction; intro hne
  rcases TR (J x (op y x)) (op z y) with hf | ⟨-, h1, h2, hA, hC⟩
  · exact hne hf
  · have m0 := szp x
    have m1 := szp (op y x)
    have m2 := szp (op z y)
    have m3 := s2L h1
    have m4 := sz_a2 (a2 (op z y))
    have m7 : sz (a2 (op z y)) ≤ sz y := by
      rcases TR z y with hc | ⟨hcr, hc1, hc2, -, -⟩
      · rw [hc]; simp only [a2_J_eq]; omega
      · have := (Wsz (NJ hc1 hc2 hcr)).2
        have := sz_a2 (op z y)
        rw [hcr] at this ⊢
        omega
    obtain ⟨mA, mB⟩ := BS x y
    have m6 : sz (op y x) = sz y + sz x + 1 ∨ sz y < sz x := by
      rcases mB with h | h
      · left; rw [h]; simp only [szJ]
      · right; exact h
    rcases hC with ⟨q1, q2⟩ | ⟨-, -, q3, q⟩ | ⟨-, -, q3, q⟩
    · have := congrArg sz q2
      rcases TR z y with hc | ⟨hcr, hc1, hc2, -, -⟩
      · rw [hc] at this q1; simp only [a2_J_eq, szJ] at this q1
        have := s2L q1
        rcases m6 with h | h <;> omega
      · have hw := (Wsz (NJ hc1 hc2 hcr)).2
        rw [hcr] at this m3 m4
        simp only [szJ] at this
        rcases m6 with h | h <;> omega
    · simp only [a1_J_eq, a2_J_eq] at q q3
      rcases TR (a1 (a2 x)) (J x (op y x)) with hg | ⟨hgr, -, -, -, -⟩
      · rw [hg] at q
        have := congrArg sz q
        simp only [szJ] at this
        have := szp (a1 (a2 x))
        rcases m6 with h | h <;> omega
      · sorry
    · simp only [a1_J_eq, a2_J_eq] at q q3
      rcases TR (a2 (op y x)) (J x (op y x)) with hg | ⟨hgr, -, -, -, -⟩
      · rw [hg] at q
        have := congrArg sz q
        simp only [szJ] at this
        have := szp (a2 (op y x))
        rcases m6 with h | h <;> omega
      · sorry

/-- the key is strictly smaller than the encoding: what every msr gate at the top needs -/
theorem SZV (x y z : M) : sz y < sz (J (J x (op y x)) (op z y)) := by
  have s1 := szp (op z y)
  have s2 := szp x
  rcases TR y x with hb | ⟨hbr, hb1, hb2, -, -⟩
  · rw [hb]; simp only [szJ]; omega
  · have := KY' (NJ hb1 hb2 hbr)
    have := szp (op y x)
    simp only [szJ]
    omega

/-- THE LAW: x = y * ((x * (y * x)) * (z * y)) -/
theorem law (x y z : M) : op (y) (op (op (x) (op (y) (x))) (op (z) (y))) = x := by
  rw [Bfree x y, Dfree x y z]
  exact FIRE (SZV x y z) rfl rfl rfl (CKlem z y)


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
