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

def P1 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a2 v) = 2 ∧ a2 (a1 u) = a1 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a2 (a1 u)) = 2 ∧ tg (a1 (a2 (a1 u))) = 2 ∧ a2 v = a2 (a1 (a2 (a1 u))) ∧ a1 (a1 (a2 (a1 u))) = a2 (a2 (a1 u))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg u = 2 ∧ tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v)
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg u = 2 ∧ tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ tg v = 2 ∧ a2 (a1 u) = a1 v ∧ tg (a2 (a1 u)) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v
  let p2 := if hs2 : msr (a2 (a2 (a1 u))) (a2 v) < msr u v then op (a2 (a2 (a1 u))) (a2 v) else J u v
  if P1 u v then a2 (a1 u)
  else if P2 u v then a2 (a1 u)
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p1 then a1 v
  else if P4 u v ∧ msr (a2 (a2 (a1 u))) (a2 v) < msr u v ∧ a1 (a2 (a1 u)) = p2 then a2 (a1 u)
  else J u v
termination_by msr u v
decreasing_by
  · assumption
  · assumption


def inst : Magma M := { op := op }

def Pre (u v : M) : Prop := P1 u v ∨ P2 u v ∨ P3 u v ∨ P4 u v

theorem op_free {u v : M} (h : ¬ Pre u v) : op u v = J u v := by
  rw [op.eq_1]; simp only [Pre, not_or] at h; simp [h]

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 2) (g 0) (g 1)
  revert this
  change ¬ g 2 = op (op (g 0) (g 1)) (op (g 2) (op (g 1) (op (g 1) (g 1))))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem a1_ne {t : M} (h : tg t = 2) : a1 t ≠ t := by
  intro hc; have := sz_a1_lt h; rw [hc] at this; omega
theorem a2_ne {t : M} (h : tg t = 2) : a2 t ≠ t := by
  intro hc; have := sz_a2_lt h; rw [hc] at this; omega

/-- the unfolding of `op` with the two nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 : M,
    p1 = (if hs1 : msr (a2 u) (a1 v) < msr u v then op (a2 u) (a1 v) else J u v) ∧
    p2 = (if hs2 : msr (a2 (a2 (a1 u))) (a2 v) < msr u v then op (a2 (a2 (a1 u))) (a2 v) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 u)
  else if P2 u v then a2 (a1 u)
  else if P3 u v ∧ msr (a2 u) (a1 v) < msr u v ∧ a1 u = p1 then a1 v
  else if P4 u v ∧ msr (a2 (a2 (a1 u))) (a2 v) < msr u v ∧ a1 (a2 (a1 u)) = p2 then a2 (a1 u)
  else J u v) :=
  ⟨_, _, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guards) -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 u)) ∨
    (P2 u v ∧ op u v = a2 (a1 u)) ∨
    (P3 u v ∧ a1 u = op (a2 u) (a1 v) ∧ op u v = a1 v) ∨
    (P4 u v ∧ a1 (a2 (a1 u)) = op (a2 (a2 (a1 u))) (a2 v) ∧ op u v = a2 (a1 u)) := by
  obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases u v
  rw [hop]
  split
  · rename_i h; exact Or.inr (Or.inl ⟨h, rfl⟩)
  · split
    · rename_i h1 h; exact Or.inr (Or.inr (Or.inl ⟨h, rfl⟩))
    · split
      · rename_i h1 h2 h
        obtain ⟨h3, hs1, he⟩ := h
        rw [dif_pos hs1] at hp1; subst hp1
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs2, he⟩ := h
          rw [dif_pos hs2] at hp2; subst hp2
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he, rfl⟩)))
        · left; rfl

/-- every rule needs `tg v = 2` and returns `a1 v`, a proper subterm of `v` -/
theorem TRs (u v : M) : op u v = J u v ∨ (tg v = 2 ∧ op u v = a1 v ∧ sz (op u v) < sz v) := by
  rcases TR4 u v with h | ⟨h1, h⟩ | ⟨h2, h⟩ | ⟨h3, -, h⟩ | ⟨h4, -, h⟩
  · exact Or.inl h
  · obtain ⟨-, -, -, htv, heq, -, -⟩ := h1
    exact Or.inr ⟨htv, by rw [h, heq], by rw [h, heq]; exact sz_a1_lt htv⟩
  · obtain ⟨-, -, -, htv, heq, -, -, -, -⟩ := h2
    exact Or.inr ⟨htv, by rw [h, heq], by rw [h, heq]; exact sz_a1_lt htv⟩
  · obtain ⟨-, htv, -, -⟩ := h3
    exact Or.inr ⟨htv, h, by rw [h]; exact sz_a1_lt htv⟩
  · obtain ⟨-, -, -, htv, heq, -⟩ := h4
    exact Or.inr ⟨htv, by rw [h, heq], by rw [h, heq]; exact sz_a1_lt htv⟩

/-- `op u v` never returns `v` itself -/
theorem NOSELF {u v : M} (h : op u v = v) : False := by
  rcases TRs u v with hf | ⟨-, -, hs⟩
  · rw [hf] at h
    have e := congrArg sz h; simp only [sz_J] at e
    have := sz_pos u; omega
  · rw [h] at hs; exact Nat.lt_irrefl _ hs

/-- the two-branch digest: every rule needs `tg u = 2`, `tg v = 2`, returns `a1 v`, and either
    fixes `u = J (J (a2 u) (a1 v)) (a2 u)` (R1/R2/R4) or carries the guard of R3. -/
theorem DIG (u v : M) : op u v = J u v ∨ (tg u = 2 ∧ tg v = 2 ∧ op u v = a1 v ∧
    ((tg (a1 u) = 2 ∧ a1 (a1 u) = a2 u ∧ a2 (a1 u) = a1 v) ∨
     (tg (a2 v) = 2 ∧ a1 v = a1 (a2 v) ∧ op (a2 u) (a1 v) = a1 u))) := by
  rcases TR4 u v with h | ⟨q, h⟩ | ⟨q, h⟩ | ⟨q, hg, h⟩ | ⟨q, hg, h⟩
  · exact Or.inl h
  · exact Or.inr ⟨q.1, q.2.2.2.1, by rw [h, q.2.2.2.2.1], Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩⟩
  · exact Or.inr ⟨q.1, q.2.2.2.1, by rw [h, q.2.2.2.2.1], Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩⟩
  · exact Or.inr ⟨q.1, q.2.1, h, Or.inr ⟨q.2.2.1, q.2.2.2, hg.symm⟩⟩
  · exact Or.inr ⟨q.1, q.2.2.2.1, by rw [h, q.2.2.2.2.1], Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩⟩

/-- the hard core fact: `a1 x` can never be produced by recursing on `(a2 x, x)`. -/
theorem core_no_fix (x : M) (htx : tg x = 2) : a1 x ≠ op (a2 x) x := by
  intro hc
  have b1 := sz_a1 (a2 x)
  have b2 := sz_a2 x
  have b3 := sz_a1 x
  rcases TR4 (a2 x) x with h | ⟨q, h⟩ | ⟨q, h⟩ | ⟨q, hg, h⟩ | ⟨q, hg, h⟩
  · rw [h] at hc
    have e := congrArg sz hc; simp only [sz_J] at e
    have := sz_pos (a2 x); omega
  · -- R1 : `a2 (a1 (a2 x)) = a1 (a2 x)` is a proper subterm of itself
    have e := q.2.2.2.2.2.2
    have s := sz_a2_lt q.2.1
    rw [e] at s; omega
  · -- R2 : `a2 x = a2 (a1 K)` with `K = a2 (a1 (a2 x))`, so `sz (a2 x) < sz K ≤ sz (a2 x)`
    obtain ⟨-, t2, -, -, -, t6, t7, t8, -⟩ := q
    have e1 := sz_a2_lt t2
    have e3 := sz_a1_lt t6
    have e4 := sz_a2_lt t7
    rw [← t8] at e4
    omega
  · -- R3 : the guard says `op (a2 (a2 x)) (a1 x) = a1 (a2 x) = a1 x`
    obtain ⟨-, -, -, t4⟩ := q
    rw [← t4] at hg
    exact NOSELF hg.symm
  · -- R4 : the guard `op (a2 K) (a2 x) = a1 K` with `K = a2 (a1 (a2 x))`
    obtain ⟨-, t2, -, -, -, t6⟩ := q
    have e1 := sz_a2_lt t2
    have e3 := sz_a1_lt t6
    rcases TRs (a2 (a2 (a1 (a2 x)))) (a2 x) with hf | ⟨-, he, -⟩
    · rw [hf] at hg
      have e := congrArg sz hg; simp only [sz_J] at e
      have := sz_pos (a2 (a2 (a1 (a2 x)))); omega
    · rw [he] at hg
      have e := congrArg sz hg
      omega

/-- a product that shrank below its right argument is not the free product -/
theorem NEFREE {u v : M} (h : sz (op u v) < sz v) : op u v ≠ J u v := by
  intro hc; rw [hc] at h; simp only [sz_J] at h; have := sz_pos u; omega

/-- what a decoding pair says about its LEFT argument: either `x` has the u-shape, or R3 fired and
    its own guard decoded, which pushes the same situation onto `(a2 x, a1 w)`. -/
theorem LFT {x w : M} (h : op x w ≠ J x w) :
    (tg (a1 x) = 2 ∧ a1 (a1 x) = a2 x ∧ a2 (a1 x) = a1 w) ∨
    (op (a2 x) (a1 w) ≠ J (a2 x) (a1 w) ∧ tg (a1 w) = 2 ∧ a1 x = a1 (a1 w) ∧
      sz (a1 x) < sz (a1 w)) := by
  rcases TR4 x w with hf | ⟨q, -⟩ | ⟨q, -⟩ | ⟨q, hg, -⟩ | ⟨q, -, -⟩
  · exact absurd hf h
  · exact Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩
  · exact Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩
  · rcases TRs (a2 x) (a1 w) with hq | ⟨hq1, hq2, hq3⟩
    · rw [hq] at hg; rw [hg]; exact Or.inl ⟨rfl, rfl, rfl⟩
    · rw [hq2] at hg
      exact Or.inr ⟨NEFREE hq3, hq1, hg, by rw [hg]; exact sz_a1_lt hq1⟩
  · exact Or.inl ⟨q.2.1, q.2.2.1, q.2.2.2.2.1⟩

/-- what a decoding pair says about its RIGHT argument -/
theorem RGT {u x : M} (h : op u x ≠ J u x) : tg x = 2 ∧
    ((tg (a2 x) = 2 ∧ a1 x = a1 (a2 x)) ∨
     (tg (a1 x) = 2 ∧ tg (a1 (a1 x)) = 2 ∧ a2 x = a2 (a1 (a1 x)) ∧ a1 (a1 (a1 x)) = a2 (a1 x)) ∨
     (tg (a1 x) = 2 ∧ a1 (a1 x) = op (a2 (a1 x)) (a2 x))) := by
  rcases TR4 u x with hf | ⟨q, -⟩ | ⟨q, -⟩ | ⟨q, -, -⟩ | ⟨q, hg, -⟩
  · exact absurd hf h
  · exact ⟨q.2.2.2.1, Or.inl ⟨q.2.2.2.2.2.1, q.2.2.2.2.1.symm.trans q.2.2.2.2.2.2⟩⟩
  · obtain ⟨-, -, -, t4, t5, t6, t7, t8, t9⟩ := q
    rw [t5] at t6 t7 t8 t9
    exact ⟨t4, Or.inr (Or.inl ⟨t6, t7, t8, t9⟩)⟩
  · exact ⟨q.2.1, Or.inl ⟨q.2.2.1, q.2.2.2⟩⟩
  · obtain ⟨-, -, -, t4, t5, t6⟩ := q
    rw [t5] at t6 hg
    exact ⟨t4, Or.inr (Or.inr ⟨t6, hg⟩)⟩

/-- **ONESIDE**: no term is both the right argument and the left argument of a decoding pair.
    Fuel induction on `sz x`; the only recursive case hands `a2 x` both roles. -/
theorem ONE (n : Nat) : ∀ x u w, sz x ≤ n → op u x ≠ J u x → op x w ≠ J x w → False := by
  induction n with
  | zero => intro x u w hn _ _; have := sz_pos x; omega
  | succ n ih =>
    intro x u w hn h1 h2
    obtain ⟨htx, hR⟩ := RGT h1
    have c1 := sz_a1 x
    have c2 := sz_a2 x
    have c3 := sz_a1 (a1 x)
    have c4 := sz_a1 (a2 x)
    have c5 := sz_a2_lt htx
    rcases LFT h2 with ⟨l1, l2, l3⟩ | ⟨d1, d2, d3, d4⟩
    · rcases hR with ⟨r1, r2⟩ | ⟨r1, r2, r3, r4⟩ | ⟨r1, r2⟩
      · have e1 := congrArg sz r2
        have e2 := congrArg sz l2
        have e3 := sz_a1_lt l1
        omega
      · rw [l2] at r2 r3
        have e1 := sz_a2_lt r2
        have e2 := congrArg sz r3
        omega
      · rw [l2] at r2
        exact NOSELF r2.symm
    · rcases hR with ⟨r1, r2⟩ | ⟨r1, r2, r3, r4⟩ | ⟨r1, r2⟩
      · rcases LFT d1 with ⟨m1, m2, m3⟩ | ⟨-, -, m3, m4⟩
        · rw [← r2] at m1 m3
          rw [← d3] at m3
          have e1 := sz_a2_lt m1
          have e2 := congrArg sz m3
          omega
        · rw [← r2, ← d3] at m4
          omega
      · rcases LFT d1 with ⟨m1, m2, m3⟩ | ⟨-, -, m3, m4⟩
        · rw [← d3] at m3
          have e1 := congrArg sz m3
          have e2 := sz_a2_lt r2
          have e3 := congrArg sz r3
          have e4 := sz_a2_lt m1
          omega
        · rw [← d3] at m3 m4
          have e1 := sz_a2_lt r2
          have e2 := congrArg sz r3
          have e3 := congrArg sz m3
          omega
      · by_cases hfr : op (a2 (a1 x)) (a2 x) = J (a2 (a1 x)) (a2 x)
        · rw [hfr] at r2
          have e0 := congrArg sz r2; simp only [sz_J] at e0
          rcases LFT d1 with ⟨m1, m2, m3⟩ | ⟨-, -, m3, m4⟩
          · rw [← d3] at m3
            have e1 := sz_a2_lt m1
            have e2 := congrArg sz m3
            omega
          · rw [← d3] at m3 m4
            have e2 := congrArg sz m3
            omega
        · exact ih (a2 x) (a2 (a1 x)) (a1 w) (by omega) hfr d1

theorem ONESIDE {u x w : M} (h1 : op u x ≠ J u x) (h2 : op x w ≠ J x w) : False :=
  ONE (sz x) x u w (Nat.le_refl _) h1 h2

theorem Rfree (x y : M) : op (op y x) y = J (op y x) y := by
  rcases TRs y x with hW | ⟨htx, hW, hs⟩
  · -- op y x is free
    rw [hW]
    rcases TR4 (J y x) y with h | ⟨h1, h⟩ | ⟨h2, h⟩ | ⟨h3, hg, h⟩ | ⟨h4, hg, h⟩
    · exact h
    · exfalso
      obtain ⟨-, t2, t3, t4, t5, t6, t7⟩ := h1
      simp only [a1_J_eq, a2_J_eq] at t2 t3 t5 t6 t7
      have hax : a2 y = x := t5.trans t3
      rw [hax] at t6 t7
      exact a1_ne t6 t7.symm
    · exfalso
      obtain ⟨-, t2, t3, t4, t5, t6, t7, t8, t9⟩ := h2
      simp only [a1_J_eq, a2_J_eq] at t2 t3 t5 t6 t7 t8 t9
      have hax : a2 y = x := t5.trans t3
      rw [hax] at t6 t7 t8 t9
      have hs1 := sz_a1_lt t6
      have hs2 := sz_a2_lt t7
      have := congrArg sz t8
      omega
    · exfalso
      obtain ⟨-, t2, t3, t4⟩ := h3
      simp only [a1_J_eq, a2_J_eq] at t2 t3 t4 hg
      rcases TRs x (a1 y) with hd | ⟨htay, hd, hsd⟩
      · rw [hd] at hg
        have hay : a1 y = x := by have := congrArg a1 hg; simpa [a1_J_eq] using this
        have hay2 : a2 y = a1 y := by have := congrArg a2 hg; simpa [a2_J_eq] using this
        rw [hay] at hay2
        rw [hay2] at t3
        rw [hay2, hay] at t4
        exact a1_ne t3 t4.symm
      · rw [hd] at hg
        have hs1 := sz_a1_lt t2
        have hs2 := sz_a1 (a1 y)
        have := congrArg sz hg
        omega
    · exfalso
      obtain ⟨-, t2, t3, t4, t5, t6⟩ := h4
      simp only [a1_J_eq, a2_J_eq] at t2 t3 t5 t6 hg
      have hax : a2 y = x := t5.trans t3
      rw [hax] at t6 hg
      exact core_no_fix x t6 hg
  · -- op y x decodes to a1 x; show `op (a1 x) y` is free
    rw [hW]
    rcases DIG (a1 x) y with hf | ⟨-, hty, hr, hgoal⟩
    · exact hf
    exfalso
    rcases DIG y x with hbad | ⟨hty2, -, -, hhyp⟩
    · rw [hbad] at hW
      have e := congrArg sz hW; simp only [sz_J] at e
      have := sz_a1 x; have := sz_pos y; omega
    have c1 := sz_a1 (a1 x)
    have c2 := sz_a1 x
    have c3 := sz_a1 (a2 y)
    have c4 := sz_a2 y
    rcases hhyp with ⟨p2, p3, p4⟩ | ⟨p2, p3, p4⟩
    · -- y = J (J (a2 y) (a1 x)) (a2 y)
      have s2 := sz_tg (a1 y) p2
      rw [p3, p4] at s2
      rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
      · have e1 := sz_a2_lt g2
        have e3 := congrArg sz g4
        omega
      · rw [← g3] at c3; omega
    · -- op (a2 y) (a1 x) = a1 y
      rcases TRs (a2 y) (a1 x) with hq | ⟨hq1, hq2, hq3⟩
      · rw [hq] at p4
        have s2 := congrArg sz p4; simp only [sz_J] at s2
        rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
        · have e1 := sz_a2_lt g2
          have e3 := congrArg sz g4
          omega
        · rw [← g3] at c3; omega
      · rw [hq2] at p4
        rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
        · have e1 := sz_a2_lt g2
          have e3 := congrArg sz g4
          have e4 := congrArg sz p4
          omega
        · rw [← p4] at g4
          exact NOSELF g4

theorem Ffree (x z : M) : op x (op x z) = J x (op x z) := by
  rcases TRs x z with hr | ⟨htz, hr, hrs⟩
  · -- r free
    rw [hr]
    rcases DIG x (J x z) with hf | ⟨htx, -, -, hgoal⟩
    · exact hf
    exfalso
    simp only [a1_J_eq, a2_J_eq] at hgoal
    rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
    · have e1 := sz_a2_lt g2
      rw [g4] at e1
      have := sz_a1 x; omega
    · exact core_no_fix x htx g4.symm
  · -- r decodes to a1 z
    rw [hr]
    rcases DIG x (a1 z) with hf | ⟨htx, hta, -, hgoal⟩
    · exact hf
    exfalso
    rcases DIG x z with hbad | ⟨-, -, -, hhyp⟩
    · rw [hbad] at hr
      have e := congrArg sz hr; simp only [sz_J] at e
      have := sz_a1 z; have := sz_pos x; omega
    have c1 := sz_a1_lt hta
    have c2 := sz_a1 x
    have c3 := sz_a2 x
    have c4 := sz_pos (a2 x)
    rcases hhyp with ⟨p2, p3, p4⟩ | ⟨p2, p3, p4⟩
    · rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
      · rw [p4] at g4
        have := congrArg sz g4; omega
      · have s1 := sz_tg (a1 x) p2
        rw [p3, p4] at s1
        rcases TRs (a2 x) (a1 (a1 z)) with hq | ⟨hq1, hq2, hq3⟩
        · rw [hq] at g4
          have e := congrArg sz g4; simp only [sz_J] at e
          omega
        · rw [hq2] at g4
          have e := congrArg sz g4
          have e2 := sz_a1 (a1 (a1 z))
          omega
    · rcases hgoal with ⟨g2, g3, g4⟩ | ⟨g2, g3, g4⟩
      · have s1 := sz_tg (a1 x) g2
        rw [g3, g4] at s1
        rcases TRs (a2 x) (a1 z) with hq | ⟨hq1, hq2, hq3⟩
        · rw [hq] at p4
          have e := congrArg sz p4; simp only [sz_J] at e
          omega
        · rw [hq2] at p4
          have e := congrArg sz p4
          have e2 := sz_a1 (a1 (a1 z))
          omega
      · rcases TRs (a2 x) (a1 z) with hq | ⟨hq1, hq2, hq3⟩
        · rw [hq] at p4
          have s1 := congrArg sz p4; simp only [sz_J] at s1
          rcases TRs (a2 x) (a1 (a1 z)) with hw | ⟨hw1, hw2, hw3⟩
          · rw [hw] at g4
            have e := congrArg sz g4; simp only [sz_J] at e
            omega
          · rw [hw2] at g4
            have e := congrArg sz g4
            have e2 := sz_a1 (a1 (a1 z))
            omega
        · rw [hq2] at p4
          rcases TRs (a2 x) (a1 (a1 z)) with hw | ⟨hw1, hw2, hw3⟩
          · rw [hw] at g4
            rw [← p4] at g4
            have e := congrArg sz g4; simp only [sz_J] at e
            omega
          · rw [hw2] at g4
            rw [← p4] at g4
            have e1 := sz_a1_lt hw1
            rw [g4] at e1
            omega

/-- THE LAW: x = ((y * x) * y) * (x * (x * z)) -/
theorem law (x y z : M) : op (op (op (y) (x)) (y)) (op (x) (op (x) (z))) = x := by
  rw [Rfree x y, Ffree x z]
  rcases TRs y x with hp | ⟨htx, hp, hps⟩
  · rw [hp]
    rcases TRs x z with hr | ⟨htz, hr, hrs⟩
    · obtain ⟨p1, p2, -, -, hop⟩ := op_cases (J (J y x) y) (J x (J x z))
      rw [hr, hop, if_pos (show P1 (J (J y x) y) (J x (J x z)) from
        ⟨rfl, rfl, rfl, rfl, rfl, rfl, rfl⟩)]
      rfl
    · rw [hr]
      rcases DIG x z with hbad | ⟨htx2, -, -, hh⟩
      · rw [hbad] at hr
        have e := congrArg sz hr; simp only [sz_J] at e
        have := sz_a1 z; have := sz_pos x; omega
      obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases (J (J y x) y) (J x (a1 z))
      rcases hh with ⟨q2, q3, q4⟩ | ⟨q2, q3, q4⟩
      · by_cases hP1 : P1 (J (J y x) y) (J x (a1 z))
        · rw [hop, if_pos hP1]; rfl
        · rw [hop, if_neg hP1, if_pos (show P2 (J (J y x) y) (J x (a1 z)) from
            ⟨rfl, rfl, rfl, rfl, rfl, htx2, q2, q4.symm, q3⟩)]
          rfl
      · have hgate : msr (a2 (a2 (a1 (J (J y x) y)))) (a2 (J x (a1 z))) <
            msr (J (J y x) y) (J x (a1 z)) := by
          apply msr_lt_of_max_lt
          simp only [a1_J_eq, a2_J_eq, sz_J]
          have := sz_a2 x; have := sz_pos x; have := sz_pos y; have := sz_pos (a1 z); omega
        rw [dif_pos hgate] at hp2
        simp only [a1_J_eq, a2_J_eq] at hp2
        subst hp2
        rw [hop]
        split
        · rename_i h; exact h.2.2.2.2.1
        · split
          · rename_i h; exact h.2.2.2.2.1
          · split
            · rfl
            · split
              · rename_i h; exact h.1.2.2.2.2.1
              · exfalso; rename_i h1 h2 h3 h4
                exact h4 ⟨⟨rfl, rfl, rfl, rfl, rfl, htx2⟩, hgate, q4.symm⟩
  · rw [hp]
    rcases TRs x z with hr | ⟨htz, hr, hrs⟩
    · rw [hr]
      obtain ⟨p1, p2, hp1, hp2, hop⟩ := op_cases (J (a1 x) y) (J x (J x z))
      have hgate : msr (a2 (J (a1 x) y)) (a1 (J x (J x z))) < msr (J (a1 x) y) (J x (J x z)) := by
        apply msr_lt_of_max_lt
        simp only [a1_J_eq, a2_J_eq, sz_J]
        have := sz_a1 x; have := sz_pos x; have := sz_pos y; have := sz_pos z; omega
      rw [dif_pos hgate] at hp1
      simp only [a1_J_eq, a2_J_eq] at hp1
      subst hp1
      rw [hop]
      split
      · rename_i h; exact h.2.2.2.2.1
      · split
        · rename_i h; exact h.2.2.2.2.1
        · split
          · rfl
          · split
            · rename_i h; exact h.1.2.2.2.2.1
            · exfalso; rename_i h1 h2 h3 h4
              exact h3 ⟨⟨rfl, rfl, rfl, rfl⟩, hgate, hp.symm⟩
    · exact absurd (NEFREE hrs) (fun hc => ONESIDE (NEFREE hps) hc)

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
