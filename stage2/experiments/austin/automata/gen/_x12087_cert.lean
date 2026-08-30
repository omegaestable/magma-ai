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

def P1 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v)) ∧ tg (a2 v) = 2 ∧ a2 (a1 (a1 v)) = a1 (a2 v) ∧ a2 (a1 v) = a2 (a2 v)
instance (u v : M) : Decidable (P1 u v) := by unfold P1; infer_instance
def P2 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a1 (a1 v)) = 2 ∧ u = a1 (a1 (a1 v))
instance (u v : M) : Decidable (P2 u v) := by unfold P2; infer_instance
def P3 (u v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2
instance (u v : M) : Decidable (P3 u v) := by unfold P3; infer_instance
def P4 (u v : M) : Prop := tg v = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2 ∧ tg (a1 (a2 (a1 v))) = 2 ∧ tg (a1 (a1 (a2 (a1 v)))) = 2
instance (u v : M) : Decidable (P4 u v) := by unfold P4; infer_instance
def op (u v : M) : M :=
  let p1 := if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v
  let p2 := if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v
  let p3 := if hs3 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v
  let p4 := if hs4 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v
  let p5 := if hs5 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p3 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p4 ∧ a1 (a1 v) = p5 then a1 (a1 (a1 (a2 (a1 v))))
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
  change ¬ g 1 = op (op (op (op (g 0) (g 0)) (g 0)) (g 1)) (op (g 0) (g 2))
  simp (config := {decide := true}) [op.eq_1, sz, P1, P2, P3, P4]


theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega
theorem tgJ2 {t : M} (h : tg t = 2) : t = J (a1 t) (a2 t) := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp only [a1_J_eq, a2_J_eq]
theorem Jinj {a b c d : M} (h : J a b = J c d) : a = c ∧ b = d := by
  injection h with h1 h2; exact ⟨h1, h2⟩

/-- the unfolding of `op` with the five nested calls packed away as opaque variables -/
theorem op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
    p1 = (if hs1 : msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v then op (a2 (a1 (a1 v))) (a2 (a1 v)) else J u v) ∧
    p2 = (if hs2 : msr (u) (a1 (a2 v)) < msr u v then op (u) (a1 (a2 v)) else J u v) ∧
    p3 = (if hs3 : msr (p2) (a2 (a2 v)) < msr u v then op (p2) (a2 (a2 v)) else J u v) ∧
    p4 = (if hs4 : msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v then op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) else J u v) ∧
    p5 = (if hs5 : msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v then op (u) (a1 (a1 (a1 (a2 (a1 v))))) else J u v) ∧
    op u v = (
  if P1 u v then a2 (a1 (a1 v))
  else if P2 u v ∧ msr (a2 (a1 (a1 v))) (a2 (a1 v)) < msr u v ∧ a2 v = p1 then a2 (a1 (a1 v))
  else if P3 u v ∧ msr (u) (a1 (a2 v)) < msr u v ∧ msr (p2) (a2 (a2 v)) < msr u v ∧ a1 v = p3 then a1 (a2 v)
  else if P4 u v ∧ msr (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) < msr u v ∧ msr (u) (a1 (a1 (a1 (a2 (a1 v))))) < msr u v ∧ a2 v = p4 ∧ a1 (a1 v) = p5 then a1 (a1 (a1 (a2 (a1 v))))
  else J u v) :=
  ⟨_, _, _, _, _, rfl, rfl, rfl, rfl, rfl, op.eq_1 u v⟩

/-- one unfold of `op`: free, or one of the four rules fired (with its op-guards) -/
theorem TR4 (u v : M) : op u v = J u v ∨
    (P1 u v ∧ op u v = a2 (a1 (a1 v))) ∨
    (P2 u v ∧ a2 v = op (a2 (a1 (a1 v))) (a2 (a1 v)) ∧ op u v = a2 (a1 (a1 v))) ∨
    (P3 u v ∧ a1 v = op (op u (a1 (a2 v))) (a2 (a2 v)) ∧ op u v = a1 (a2 v)) ∨
    (P4 u v ∧ a2 v = op (a1 (a1 (a1 (a2 (a1 v))))) (a2 (a1 v)) ∧ a1 (a1 v) = op u (a1 (a1 (a1 (a2 (a1 v))))) ∧ op u v = a1 (a1 (a1 (a2 (a1 v))))) := by
  obtain ⟨p1, p2, p3, p4, p5, hp1, hp2, hp3, hp4, hp5, hop⟩ := op_cases u v
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
        obtain ⟨h3, hs2, hs3, he⟩ := h
        rw [dif_pos hs2] at hp2; subst hp2
        rw [dif_pos hs3] at hp3; subst hp3
        exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3, he, rfl⟩)))
      · split
        · rename_i h1 h2 h3 h
          obtain ⟨h4, hs4, hs5, he4, he5⟩ := h
          rw [dif_pos hs4] at hp4; subst hp4
          rw [dif_pos hs5] at hp5; subst hp5
          exact Or.inr (Or.inr (Or.inr (Or.inr ⟨h4, he4, he5, rfl⟩)))
        · left; rfl

/-- every rule returns a proper subterm of `v` -/
theorem SZV (u v : M) : op u v = J u v ∨ sz (op u v) < sz v := by
  rcases TR4 u v with h | ⟨h1, h⟩ | ⟨h2, -, h⟩ | ⟨h3, -, h⟩ | ⟨h4, -, -, h⟩
  · exact Or.inl h
  · right; rw [h]
    obtain ⟨hv, hav, haav, -, -, -, -⟩ := h1
    have := sz_a2_lt haav; have := sz_a1_lt hav; have := sz_a1_lt hv; have := sz_a1 (a1 v); omega
  · right; rw [h]
    obtain ⟨hv, hav, haav, -⟩ := h2
    have := sz_a2_lt haav; have := sz_a1_lt hav; have := sz_a1_lt hv; have := sz_a1 (a1 v); omega
  · right; rw [h]
    obtain ⟨hv, ha2v⟩ := h3
    have := sz_a1_lt ha2v; have := sz_a2_lt hv; omega
  · right; rw [h]
    obtain ⟨hv, hav, ha2av, -, -⟩ := h4
    have := sz_a1 (a1 (a1 (a2 (a1 v)))); have := sz_a1 (a1 (a2 (a1 v)))
    have := sz_a1 (a2 (a1 v)); have := sz_a2_lt hav; have := sz_a1_lt hv; omega

/-- a `J`-shaped value at least as big as `w` can only be the free product -/
theorem noBig {p w a b : M} (h : op p w = J a b) (hb : sz w ≤ sz a + sz b) : p = a ∧ w = b := by
  rcases SZV p w with hf | hs
  · rw [hf] at h; exact Jinj h
  · rw [h] at hs; simp only [sz_J] at hs; omega

/-- a decoded product has a strictly smaller left argument -/
theorem SUn (n : Nat) : ∀ u v : M, sz v ≤ n → op u v ≠ J u v → sz u < sz v := by
  induction n with
  | zero => intro u v hn _; have := sz_pos v; omega
  | succ n ih =>
    intro u v hn hd
    rcases TR4 u v with h | ⟨h1, -⟩ | ⟨h2, -, -⟩ | ⟨h3, hg, -⟩ | ⟨h4, -, hg2, -⟩
    · exact absurd h hd
    · obtain ⟨hv, hav, haav, hu, -, -, -⟩ := h1
      have := sz_a1 (a1 (a1 v)); have := sz_a1_lt haav; have := sz_a1_lt hav; have := sz_a1_lt hv
      rw [hu]; omega
    · obtain ⟨hv, hav, haav, hu⟩ := h2
      have := sz_a1 (a1 (a1 v)); have := sz_a1_lt haav; have := sz_a1_lt hav; have := sz_a1_lt hv
      rw [hu]; omega
    · obtain ⟨hv, ha2v⟩ := h3
      have hX : sz (a1 (a2 v)) < sz v := by
        have := sz_a1_lt ha2v; have := sz_a2_lt hv; omega
      have hZ : sz (a2 (a2 v)) < sz v := by
        have := sz_a2_lt ha2v; have := sz_a2_lt hv; omega
      have hA : sz (a1 v) < sz v := sz_a1_lt hv
      by_cases hW : op u (a1 (a2 v)) = J u (a1 (a2 v))
      · by_cases hR : op (op u (a1 (a2 v))) (a2 (a2 v)) = J (op u (a1 (a2 v))) (a2 (a2 v))
        · rw [hR, hW] at hg
          have := congrArg sz hg; simp only [sz_J] at this; omega
        · have h5 := ih (op u (a1 (a2 v))) (a2 (a2 v)) (by omega) hR
          rw [hW] at h5; simp only [sz_J] at h5; omega
      · have h5 := ih u (a1 (a2 v)) (by omega) hW; omega
    · obtain ⟨hv, hav, ha2av, -, -⟩ := h4
      have hX : sz (a1 (a1 (a1 (a2 (a1 v))))) < sz v := by
        have := sz_a1 (a1 (a1 (a2 (a1 v)))); have := sz_a1 (a1 (a2 (a1 v)))
        have := sz_a1 (a2 (a1 v)); have := sz_a2_lt hav; have := sz_a1_lt hv; omega
      by_cases hW : op u (a1 (a1 (a1 (a2 (a1 v))))) = J u (a1 (a1 (a1 (a2 (a1 v)))))
      · rw [hW] at hg2
        have := congrArg sz hg2; simp only [sz_J] at this
        have := sz_a1 (a1 v); have := sz_a1_lt hv; omega
      · have h5 := ih u (a1 (a1 (a1 (a2 (a1 v))))) (by omega) hW; omega

theorem SU {u v : M} (h : op u v ≠ J u v) : sz u < sz v := SUn (sz v) u v (Nat.le_refl _) h
theorem SZ {u v : M} (h : op u v ≠ J u v) : sz (op u v) < sz v := by
  rcases SZV u v with hf | hs
  · exact absurd hf h
  · exact hs

/-- the shape of `v` when it decodes for `u`: the chain form (rules 1,2,4) or the third-product
    form (rule 3). -/
theorem SH_of {u v : M} (hd : op u v ≠ J u v) :
    tg v = 2 ∧ (
      (tg (a1 v) = 2 ∧ (a1 (a1 v) = J u (op u v) ∨ a1 (a1 v) = op u (op u v))
        ∧ (a2 v = J (op u v) (a2 (a1 v)) ∨ a2 v = op (op u v) (a2 (a1 v))))
      ∨ (a2 v = J (op u v) (a2 (a2 v)) ∧ a1 v = op (op u (op u v)) (a2 (a2 v)))) := by
  rcases TR4 u v with h | ⟨h1, he⟩ | ⟨h2, hg, he⟩ | ⟨h3, hg, he⟩ | ⟨h4, hg1, hg2, he⟩
  · exact absurd h hd
  · obtain ⟨hv, hav, haav, hu, ha2v, e1, e2⟩ := h1
    refine ⟨hv, Or.inl ⟨hav, Or.inl ?_, Or.inl ?_⟩⟩
    · rw [he, hu]; exact tgJ2 haav
    · rw [he, e1, e2]; exact tgJ2 ha2v
  · obtain ⟨hv, hav, haav, hu⟩ := h2
    refine ⟨hv, Or.inl ⟨hav, Or.inl ?_, Or.inr ?_⟩⟩
    · rw [he, hu]; exact tgJ2 haav
    · rw [he]; exact hg
  · obtain ⟨hv, ha2v⟩ := h3
    refine ⟨hv, Or.inr ⟨?_, ?_⟩⟩
    · rw [he]; exact tgJ2 ha2v
    · rw [he]; exact hg
  · obtain ⟨hv, hav, ha2av, hb1, hb2⟩ := h4
    refine ⟨hv, Or.inl ⟨hav, Or.inr ?_, Or.inr ?_⟩⟩
    · rw [he]; exact hg2
    · rw [he]; exact hg1

/-- injectivity of a decoded product in its left argument (fuel induction on `sz v`) -/
theorem INJn (n : Nat) : ∀ v u u' : M, sz v ≤ n → op u v ≠ J u v → op u' v = op u v → u = u' := by
  induction n with
  | zero => intro v u u' hn _ _; have := sz_pos v; omega
  | succ n ih =>
    intro v u u' hn hd he
    have hr : sz (op u v) < sz v := SZ hd
    have hd' : op u' v ≠ J u' v := by
      intro hf; rw [hf] at he; have := congrArg sz he; simp only [sz_J] at this
      have := sz_pos u'; omega
    have same : ∀ a b w : M, sz w ≤ n → op a w = op b w → a = b := by
      intro a b w hw hab
      by_cases hf : op a w = J a w
      · rw [hf] at hab
        exact (noBig hab.symm (by omega)).1.symm
      · exact ih w a b hw hf hab.symm
    have hZv : sz (op u v) ≤ n := by omega
    obtain ⟨hv, hs⟩ := SH_of hd
    obtain ⟨-, hs'⟩ := SH_of hd'
    rw [he] at hs'
    -- the mixed case: `a` decodes by the chain form, `b` by the third-product form
    have mixed : ∀ a b : M,
        (a1 (a1 v) = J a (op u v) ∨ a1 (a1 v) = op a (op u v)) →
        (a2 v = J (op u v) (a2 (a1 v)) ∨ a2 v = op (op u v) (a2 (a1 v))) →
        tg (a1 v) = 2 →
        a2 v = J (op u v) (a2 (a2 v)) →
        a1 v = op (op b (op u v)) (a2 (a2 v)) → a = b := by
      intro a b hk hq hav hq' hk'
      by_cases hf : op (op b (op u v)) (a2 (a2 v)) = J (op b (op u v)) (a2 (a2 v))
      · rw [hf] at hk'
        obtain ⟨e1, -⟩ := Jinj ((tgJ2 hav).symm.trans hk')
        rcases hk with hL | hQ
        · exact (noBig ((hL.symm.trans e1).symm) (by omega)).1.symm
        · exact same a b (op u v) hZv (hQ.symm.trans e1)
      · exfalso
        have hlt : sz (a1 v) < sz (a2 (a2 v)) := by rw [hk']; exact SZ hf
        have hs1 : sz (a1 v) = sz (a1 (a1 v)) + sz (a2 (a1 v)) + 1 := sz_tg _ hav
        rcases hq with hJ | hO
        · have := congrArg sz (Jinj (hJ.symm.trans hq')).2; omega
        · by_cases hf2 : op (op u v) (a2 (a1 v)) = J (op u v) (a2 (a1 v))
          · rw [hf2] at hO
            have := congrArg sz (Jinj (hO.symm.trans hq')).2; omega
          · have hb := SZ hf2
            rw [hO.symm.trans hq'] at hb; simp only [sz_J] at hb; omega
    rcases hs with ⟨hav, hk, hq⟩ | ⟨hq, hk⟩
    · rcases hs' with ⟨-, hk', -⟩ | ⟨hq', hk'⟩
      · rcases hk with hL | hQ <;> rcases hk' with hL' | hQ'
        · exact (Jinj (hL.symm.trans hL')).1
        · exact ((noBig (hQ'.symm.trans hL) (by omega)).1).symm
        · exact (noBig (hQ.symm.trans hL') (by omega)).1
        · exact same u u' (op u v) hZv (hQ.symm.trans hQ')
      · exact mixed u u' hk hq hav hq' hk'
    · rcases hs' with ⟨hav', hk', hq'⟩ | ⟨hq', hk'⟩
      · exact (mixed u' u hk' hq' hav' hq hk).symm
      · by_cases hf : op (op u (op u v)) (a2 (a2 v)) = J (op u (op u v)) (a2 (a2 v))
        · rw [hf] at hk
          exact (same u' u (op u v) hZv (noBig (hk'.symm.trans hk) (by omega)).1).symm
        · have hlt : sz (a1 v) < sz (a2 (a2 v)) := by rw [hk]; exact SZ hf
          have ht : tg (a2 v) = 2 := by rw [hq]; rfl
          have hd2 : sz (a2 (a2 v)) ≤ n := by
            have := sz_a2_lt hv; have := sz_a2_lt ht; omega
          have hq2 := ih (a2 (a2 v)) (op u (op u v)) (op u' (op u v)) hd2 hf (hk'.symm.trans hk)
          exact same u u' (op u v) hZv hq2

theorem INJ {v u u' : M} (hd : op u v ≠ J u v) (he : op u' v = op u v) : u = u' :=
  INJn (sz v) v u u' (Nat.le_refl _) hd he

theorem law (x y z : M) : op (y) (op (op (op (y) (x)) (z)) (op (x) (z))) = x := by
  sorry


theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
