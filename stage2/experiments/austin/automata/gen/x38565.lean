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

def P1 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ tg (a2 (a1 (a2 v))) = 2 ∧ a1 (a1 (a2 v)) = a2 (a2 (a1 (a2 v))) ∧ u = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg (a2 v) = 2 ∧ tg (a1 (a2 v)) = 2 ∧ u = a2 (a2 v) ∧ tg (a1 (a1 (a2 v))) = 2
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a2 (a1 u)) = 2 ∧ a1 (a1 u) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ u = a1 v ∧ tg u = 2 ∧ tg (a1 u) = 2 ∧ tg (a1 (a1 u)) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) else J u v
  let p2 := if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v
  let p3 := if hs3 : msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v then op (a1 (a1 (a1 u))) (a1 (a1 u)) else J u v
  if P1 u v then a1 (a2 (a1 (a2 v)))
  else if P2 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v ∧ a2 (a1 (a2 v)) = p1 then a1 (a1 (a1 (a2 v)))
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p2 then a1 (a2 (a1 u))
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p3 then a1 (a1 (a1 u))
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption
  · assumption


def inst : Magma M := { op := fun a b => op b a }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (g 1) (op (g 2) (op (g 2) (op (g 1) (op (g 0) (g 0)))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem szP (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem szJ (a b : M) : sz (J a b) = sz a + sz b + 1 := by simp [sz]
theorem sA1 {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, szJ]; have := szP b; omega
theorem sA2 {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a2_J_eq, szJ]; have := szP a; omega

theorem op_cases (u v : M) : ∃ p1 p2 p3 : M,
    p1 = (if hs1 : msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v then op (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) else J u v) ∧
    p2 = (if hs2 : msr (a1 u) (u) < msr u v then op (a1 u) (u) else J u v) ∧
    p3 = (if hs3 : msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v then op (a1 (a1 (a1 u))) (a1 (a1 u)) else J u v) ∧
    op u v = (
  if P1 u v then a1 (a2 (a1 (a2 v)))
  else if P2 u v ∧ msr (a1 (a1 (a1 (a2 v)))) (a1 (a1 (a2 v))) < msr u v ∧ a2 (a1 (a2 v)) = p1 then a1 (a1 (a1 (a2 v)))
  else if P3 u v ∧ msr (a1 u) (u) < msr u v ∧ a2 v = p2 then a1 (a2 (a1 u))
  else if P4 u v ∧ msr (a1 u) (u) < msr u v ∧ msr (a1 (a1 (a1 u))) (a1 (a1 u)) < msr u v ∧ a2 v = p2 ∧ a2 (a1 u) = p3 then a1 (a1 (a1 u))
  else J u v
    ) :=
  ⟨_, _, _, rfl, rfl, rfl, op.eq_1 u v⟩

/-- the digest: a product is free, or `v = J u _`, its value is a proper subterm of `v`, and
    either the encoding's outer shape is visible (`a2 (a2 v) = u`) or `a2 v` is the value of
    `op (a1 u) u`. -/
theorem TRa (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ a1 v = u ∧ sz (op u v) < sz v ∧
    ((tg (a2 v) = 2 ∧ a2 (a2 v) = u) ∨ a2 v = op (a1 u) u)) := by
  obtain ⟨p1, p2, p3, hp1, hp2, hp3, hop⟩ := op_cases u v
  split at hop
  · rename_i h
    obtain ⟨h1, h2, h3, h4, h5, h6, h7⟩ := h
    refine Or.inr ⟨h1, h2.symm, ?_, Or.inl ⟨h3, h7.symm⟩⟩
    rw [hop]
    have e1 := sA1 h5; have e2 := sA2 h4; have e3 := sA1 h3; have e4 := sA2 h1
    omega
  · split at hop
    · rename_i h
      obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, -, -⟩ := h
      refine Or.inr ⟨h1, h2.symm, ?_, Or.inl ⟨h3, h5.symm⟩⟩
      rw [hop]
      have e1 := sA1 h6; have e2 := sA1 h4; have e3 := sA1 h3; have e4 := sA2 h1
      omega
    · split at hop
      · rename_i h
        obtain ⟨⟨h1, h2, h3, h4, h5, h6⟩, hg, he⟩ := h
        rw [dif_pos hg] at hp2
        subst hp2
        refine Or.inr ⟨h1, h2.symm, ?_, Or.inr he⟩
        rw [hop]
        have e0 := congrArg sz h2
        have e1 := sA1 h5; have e2 := sA2 h4; have e3 := sA1 h3; have e4 := sA1 h1
        omega
      · split at hop
        · rename_i h
          obtain ⟨⟨h1, h2, h3, h4, h5⟩, hg, hg2, he, he2⟩ := h
          rw [dif_pos hg] at hp2
          subst hp2
          refine Or.inr ⟨h1, h2.symm, ?_, Or.inr he⟩
          rw [hop]
          have e0 := congrArg sz h2
          have e1 := sA1 h5; have e2 := sA1 h4; have e3 := sA1 h3; have e4 := sA1 h1
          omega
        · exact Or.inl hop

/-- no product returns its own right argument -/
theorem NF (a b : M) : op a b ≠ b := by
  intro h
  rcases TRa a b with hf | ⟨-, -, hs, -⟩
  · rw [hf] at h
    have e := congrArg sz h
    rw [szJ] at e
    have := szP a; omega
  · rw [h] at hs; omega

/-- every product of the shape `a * (b * a)` is free: this covers both `z * (x * z)` and
    `y * (((z * (x * z))) * y)`, so the chain's 2nd and 4th products are never decoded. -/
theorem FREE2 (a b : M) : op a (op b a) = J a (op b a) := by
  rcases TRa a (op b a) with hf | ⟨h1, h2, h3, hd⟩
  · exact hf
  · exfalso
    rcases TRa b a with hf2 | ⟨g1, g2, g3, -⟩
    · rw [hf2] at h2 hd
      simp only [a1_J_eq, a2_J_eq] at h2 hd
      subst h2
      rcases hd with ⟨hd1, hd2⟩ | hd
      · have := sA2 hd1
        have e := congrArg sz hd2
        omega
      · exact NF _ _ hd.symm
    · have e := sz_a1 (op b a)
      rw [h2] at e
      omega

/-- everything free -/
theorem op_R1 (x y z : M) : op y (J y (J (J z (J x z)) y)) = x := by
  obtain ⟨p1, p2, p3, -, -, -, hop⟩ := op_cases y (J y (J (J z (J x z)) y))
  have hP : P1 y (J y (J (J z (J x z)) y)) := ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩
  split at hop
  · rw [hop]; simp only [a1_J_eq, a2_J_eq]
  · exact absurd hP (by assumption)

/-- `x * z` decoded, the rest free -/
theorem op_R2 {x y z S : M} (hz : tg z = 2) (hx : a1 z = x) (hS : op x z = S) (hlt : sz S < sz z) :
    op y (J y (J (J z S) y)) = x := by
  obtain ⟨p1, p2, p3, hp1, -, -, hop⟩ := op_cases y (J y (J (J z S) y))
  have hg : msr (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) <
      msr y (J y (J (J z S) y)) := by
    simp only [a1_J_eq, a2_J_eq]
    exact msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 z; have := szP y; have := szP S; omega)
  rw [dif_pos hg] at hp1
  subst hp1
  have hc2 : P2 y (J y (J (J z S) y)) ∧
      msr (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) <
        msr y (J y (J (J z S) y)) ∧
      a2 (a1 (a2 (J y (J (J z S) y)))) =
        op (a1 (a1 (a1 (a2 (J y (J (J z S) y)))))) (a1 (a1 (a2 (J y (J (J z S) y))))) := by
    refine ⟨⟨rfl, rfl, rfl, rfl, rfl, hz⟩, hg, ?_⟩
    simp only [a1_J_eq, a2_J_eq]
    rw [hx, hS]
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, h6, -⟩ := h
    simp only [a1_J_eq, a2_J_eq] at h6
    have e := congrArg sz h6
    have := sz_a2 S
    omega
  · rw [hop]
    simp only [a1_J_eq, a2_J_eq]
    exact hx

/-- `(z * (x * z)) * y` decoded, `x * z` free -/
theorem op_R3 {x y z S3 : M} (hy : tg y = 2) (hay : a1 y = J z (J x z))
    (hS3 : op (a1 y) y = S3) (hlt : sz S3 < sz y) : op y (J y S3) = x := by
  obtain ⟨p1, p2, p3, -, hp2, -, hop⟩ := op_cases y (J y S3)
  have hg : msr (a1 y) (y) < msr y (J y S3) :=
    msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 y; have := szP S3; omega)
  rw [dif_pos hg] at hp2
  subst hp2
  have hc3 : P3 y (J y S3) ∧ msr (a1 y) (y) < msr y (J y S3) ∧
      a2 (J y S3) = op (a1 y) y := by
    refine ⟨⟨rfl, rfl, hy, ?_, ?_, ?_⟩, hg, ?_⟩
    · simp only [hay, tg_J_eq]
    · simp only [hay, a2_J_eq, tg_J_eq]
    · simp only [hay, a1_J_eq, a2_J_eq]
    · simp only [a2_J_eq]
      exact hS3.symm
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have e := congrArg sz h7
    have := sz_a2 S3
    omega
  · split at hop
    · rename_i h
      exfalso
      obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
      simp only [a2_J_eq] at h5
      have e := congrArg sz h5
      have := sz_a2 S3
      omega
    · rw [hop]
      simp only [hay, a1_J_eq, a2_J_eq]

/-- both `x * z` and `(z * (x * z)) * y` decoded -/
theorem op_R4 {x y z S1 S3 : M} (hz : tg z = 2) (hx : a1 z = x) (hS1 : op x z = S1)
    (hlt1 : sz S1 < sz z) (hy : tg y = 2) (hay : a1 y = J z S1)
    (hS3 : op (a1 y) y = S3) (hlt3 : sz S3 < sz y) : op y (J y S3) = x := by
  obtain ⟨p1, p2, p3, -, hp2, hp3, hop⟩ := op_cases y (J y S3)
  have hyz : sz z < sz y := by
    have e := sz_a1 y
    rw [hay, szJ] at e
    have := szP S1; omega
  have hg2 : msr (a1 y) (y) < msr y (J y S3) :=
    msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 y; have := szP S3; omega)
  have hg3 : msr (a1 (a1 (a1 y))) (a1 (a1 y)) < msr y (J y S3) := by
    simp only [hay, a1_J_eq]
    exact msr_lt_of_max_lt (by simp only [szJ]; have := sz_a1 z; have := szP S3; omega)
  rw [dif_pos hg2] at hp2
  subst hp2
  rw [dif_pos hg3] at hp3
  subst hp3
  have hc4 : P4 y (J y S3) ∧ msr (a1 y) (y) < msr y (J y S3) ∧
      msr (a1 (a1 (a1 y))) (a1 (a1 y)) < msr y (J y S3) ∧
      a2 (J y S3) = op (a1 y) y ∧
      a2 (a1 y) = op (a1 (a1 (a1 y))) (a1 (a1 y)) := by
    refine ⟨⟨rfl, rfl, hy, ?_, ?_⟩, hg2, hg3, ?_, ?_⟩
    · simp only [hay, tg_J_eq]
    · simp only [hay, a1_J_eq]
      exact hz
    · simp only [a2_J_eq]
      exact hS3.symm
    · simp only [hay, a1_J_eq, a2_J_eq]
      rw [hx, hS1]
  split at hop
  · rename_i h
    exfalso
    obtain ⟨-, -, -, -, -, -, h7⟩ := h
    simp only [a2_J_eq] at h7
    have e := congrArg sz h7
    have := sz_a2 S3
    omega
  · split at hop
    · rename_i h
      exfalso
      obtain ⟨⟨-, -, -, -, h5, -⟩, -, -⟩ := h
      simp only [a2_J_eq] at h5
      have e := congrArg sz h5
      have := sz_a2 S3
      omega
    · split at hop
      · rename_i h
        exfalso
        obtain ⟨⟨-, -, -, -, -, h6⟩, -, -⟩ := h
        simp only [hay, a1_J_eq, a2_J_eq] at h6
        have e := congrArg sz h6
        have := sz_a2 S1
        omega
      · rw [hop]
        simp only [hay, a1_J_eq]
        exact hx

/-- THE LAW: x = ((y * ((z * x) * z)) * y) * y (stated for the DUAL L-form law; the served magma flips op, so EquationLHS unfolds to exactly this) -/
theorem law (x y z : M) : op (y) (op (y) (op (op (z) (op (x) (z))) (y))) = x := by
  rw [FREE2 z x, FREE2 y (J z (op x z))]
  by_cases h1 : op x z = J x z
  · rw [h1]
    by_cases h3 : op (J z (J x z)) y = J (J z (J x z)) y
    · rw [h3]
      exact op_R1 x y z
    · rcases TRa (J z (J x z)) y with hf | ⟨g1, g2, g3, -⟩
      · exact absurd hf h3
      · exact op_R3 g1 g2 (by rw [g2]) g3
  · rcases TRa x z with hf | ⟨q1, q2, q3, -⟩
    · exact absurd hf h1
    · by_cases h3 : op (J z (op x z)) y = J (J z (op x z)) y
      · rw [h3]
        exact op_R2 q1 q2 rfl q3
      · rcases TRa (J z (op x z)) y with hf2 | ⟨g1, g2, g3, -⟩
        · exact absurd hf2 h3
        · exact op_R4 q1 q2 rfl q3 g1 g2 (by rw [g2]) g3


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
