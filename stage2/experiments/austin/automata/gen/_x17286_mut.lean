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
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1) = 2 := rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1) = b0 := rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1) = b1 := rfl
@[simp] theorem sz_J (a b : M) : sz (J a b) = sz a + sz b + 1 := rfl
theorem sz_pos (t : M) : 1 ≤ sz t := by cases t <;> simp [sz] <;> omega
theorem tg_J (t : M) (h : tg t = 2) : ∃ b0 b1, t = M.J b0 b1 := by cases t <;> simp_all [tg]
theorem sz_a1 (u : M) : sz (a1 u) ≤ sz u := by cases u <;> simp [a1, sz] <;> omega
theorem sz_a2 (u : M) : sz (a2 u) ≤ sz u := by cases u <;> simp [a2, sz] <;> omega
theorem sz_a1_lt {t : M} (h : tg t = 2) : sz (a1 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a1]; have := sz_pos b; omega
theorem sz_a2_lt {t : M} (h : tg t = 2) : sz (a2 t) < sz t := by
  obtain ⟨a, b, rfl⟩ := tg_J _ h; simp [sz, a2]; have := sz_pos a; omega

/-- `v` is a code against `w = a1 v`, with payload slot `P = a2 (a2 v)`. -/
def Cd (v : M) : Prop := tg v = 2 ∧ tg (a2 v) = 2 ∧ a1 v = a1 (a2 v)
instance (v : M) : Decidable (Cd v) := by unfold Cd; infer_instance

/-- the size identity that makes every gate arithmetic: `sz v = 2*sz w + sz P + 2`. -/
theorem Cd_sz {v : M} (h : Cd v) : sz v = 2 * sz (a1 v) + sz (a2 (a2 v)) + 2 := by
  obtain ⟨h1, h2, h3⟩ := h
  obtain ⟨a, b, rfl⟩ := tg_J _ h1
  simp only [a1_J_eq, a2_J_eq] at h2 h3
  obtain ⟨c, d, rfl⟩ := tg_J _ h2
  simp only [a1_J_eq, a2_J_eq] at h3
  subst h3
  simp only [sz_J, a1_J_eq, a2_J_eq]
  omega

mutual
/-- walk the unwrap chain `T := a2 (a2 T)` looking for a payload `a1 T` that codes `u` and
    reproduces the ORIGINAL `P` against `w`.  `J u u` is the "not found" sentinel. -/
def find (u T w P : M) : M :=
  if tg T = 2 ∧ tg (a1 T) = 2 ∧ tg (a2 (a1 T)) = 2 ∧ a1 (a1 T) = a1 (a2 (a1 T))
     ∧ op u (a1 (a1 T)) = a2 (a2 (a1 T)) ∧ op (a1 T) w = P then a1 T
  else if h : tg T = 2 ∧ tg (a2 T) = 2 then find u (a2 (a2 T)) w P
  else J u u
termination_by (sz u + 2 * sz w + sz T + 2, 0)
decreasing_by
  · have := sz_a1 T; have := sz_a1 (a1 T); omega
  · have := sz_a1 T; omega
  · have e1 := sz_a2_lt h.1
    have e2 := sz_a2_lt h.2
    omega

def op (u v : M) : M :=
  if hc : Cd v then
    if hu : tg u = 2 then
      if op (a2 u) (a1 v) = a2 (a2 v) then a2 u else opTail u v hc
    else opTail u v hc
  else J u v
termination_by (sz u + sz v, 2)
decreasing_by
  · have e1 := sz_a2_lt hu
    have e2 := sz_a1_lt hc.1
    omega
  · exact Prod.Lex.right _ (by omega)
  · exact Prod.Lex.right _ (by omega)

/-- the non-`U` half of `op`: branch R (reconstruction), then the unwrap search. -/
def opTail (u v : M) (hc : Cd v) : M :=
  if hr : tg (a2 (a2 v)) = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
          ∧ a1 (a1 v) = a1 (a2 (a1 v)) then
    if op u (a1 (a2 (a2 v))) = a2 (a2 (a2 v))
       ∧ op (a2 (a2 v)) (a1 (a1 v)) = a2 (a2 (a1 v)) then
      J (a1 (a2 (a2 v))) (a2 (a2 v))
    else
      let r := find u (a2 (a2 v)) (a1 v) (a2 (a2 v))
      if r = J u u then J u v else r
  else
    let r := find u (a2 (a2 v)) (a1 v) (a2 (a2 v))
    if r = J u u then J u v else r
termination_by (sz u + sz v, 1)
decreasing_by
  · have e1 := sz_a2_lt hc.1
    have e2 := sz_a2_lt hc.2.1
    have e3 := sz_a1 (a2 (a2 v))
    omega
  · have e1 := sz_a2_lt hc.1
    have e2 := sz_a2_lt hc.2.1
    have e3 := sz_a1 (a1 v)
    have e4 := sz_a1 v
    have := Cd_sz hc
    omega
  · have h9 := Cd_sz hc
    have h8 : sz u + sz v = sz u + 2 * sz (a1 v) + sz (a2 (a2 v)) + 2 := by omega
    rw [h8]; exact Prod.Lex.right _ (by omega)
  · have h9 := Cd_sz hc
    have h8 : sz u + sz v = sz u + 2 * sz (a1 v) + sz (a2 (a2 v)) + 2 := by omega
    rw [h8]; exact Prod.Lex.right _ (by omega)
end


def inst : Magma M := { op := op }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 0) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (g 0)) (op (op (g 0) (op (g 0) (g 0))) (g 0))
  simp [op.eq_1, opTail.eq_1, find.eq_1, Cd, tg, a1, a2, sz]

theorem opF {u v : M} (h : ¬ Cd v) : op u v = J u v := by
  rw [op.eq_1, dif_neg h]

/-- "c codes u" -- the relation every decode branch verifies. -/
def cds (u c : M) : Prop :=
  tg c = 2 ∧ tg (a2 c) = 2 ∧ a1 c = a1 (a2 c) ∧ op u (a1 c) = a2 (a2 c)

/-- what `find` returns: either the sentinel, or a genuine payload. Fuel induction on `sz T`
    (the mutual `find.induct` carries three motives and is unusable for a single statement). -/
theorem findN (n : Nat) : ∀ u T w P r : M, sz T ≤ n → find u T w P = r →
    r = J u u ∨ (cds u r ∧ op r w = P) := by
  induction n with
  | zero => intro u T w P r hn _; have := sz_pos T; omega
  | succ n ih =>
    intro u T w P r hn hr
    rw [find.eq_1] at hr
    by_cases h1 : tg T = 2 ∧ tg (a1 T) = 2 ∧ tg (a2 (a1 T)) = 2 ∧ a1 (a1 T) = a1 (a2 (a1 T))
       ∧ op u (a1 (a1 T)) = a2 (a2 (a1 T)) ∧ op (a1 T) w = P
    · rw [if_pos h1] at hr
      subst hr
      exact Or.inr ⟨⟨h1.2.1, h1.2.2.1, h1.2.2.2.1, h1.2.2.2.2.1⟩, h1.2.2.2.2.2⟩
    · rw [if_neg h1] at hr
      by_cases h2 : tg T = 2 ∧ tg (a2 T) = 2
      · rw [dif_pos h2] at hr
        have e1 := sz_a2_lt h2.1
        have e2 := sz_a2_lt h2.2
        exact ih u (a2 (a2 T)) w P r (by omega) hr
      · rw [dif_neg h2] at hr; exact Or.inl hr.symm

theorem findOK (u T w P : M) :
    find u T w P = J u u ∨ (cds u (find u T w P) ∧ op (find u T w P) w = P) :=
  findN (sz T) u T w P _ (Nat.le_refl _) rfl

/-- the digest, for `opTail`. -/
theorem SNDtail (u v : M) (hc : Cd v) : opTail u v hc = J u v ∨
    (op (opTail u v hc) (a1 v) = a2 (a2 v)
     ∧ ((tg u = 2 ∧ a2 u = opTail u v hc) ∨ cds u (opTail u v hc))) := by
  rw [opTail.eq_1]
  by_cases hr : tg (a2 (a2 v)) = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
                ∧ a1 (a1 v) = a1 (a2 (a1 v))
  · rw [dif_pos hr]
    by_cases hg : op u (a1 (a2 (a2 v))) = a2 (a2 (a2 v))
                  ∧ op (a2 (a2 v)) (a1 (a1 v)) = a2 (a2 (a1 v))
    · rw [if_pos hg]
      have hcw : Cd (a1 v) := ⟨hr.2.1, hr.2.2.1, hr.2.2.2⟩
      have hU : op (J (a1 (a2 (a2 v))) (a2 (a2 v))) (a1 v) = a2 (a2 v) := by
        rw [op.eq_1, dif_pos hcw, dif_pos (show tg (J (a1 (a2 (a2 v))) (a2 (a2 v))) = 2 from rfl)]
        rw [if_pos (by simp only [a2_J_eq]; exact hg.2)]
        simp only [a2_J_eq]
      refine Or.inr ⟨hU, Or.inr ⟨rfl, ?_, ?_, ?_⟩⟩
      · simp only [a2_J_eq]; exact hr.1
      · simp only [a1_J_eq, a2_J_eq]
      · simp only [a1_J_eq, a2_J_eq]; exact hg.1
    · rw [if_neg hg]
      rcases findOK u (a2 (a2 v)) (a1 v) (a2 (a2 v)) with hf | ⟨hc1, hc2⟩
      · rw [hf]; simp only [if_pos rfl]; exact Or.inl rfl
      · by_cases he : find u (a2 (a2 v)) (a1 v) (a2 (a2 v)) = J u u
        · rw [if_pos he]; exact Or.inl rfl
        · rw [if_neg he]; exact Or.inr ⟨hc2, Or.inr hc1⟩
  · rw [dif_neg hr]
    rcases findOK u (a2 (a2 v)) (a1 v) (a2 (a2 v)) with hf | ⟨hc1, hc2⟩
    · rw [hf]; simp only [if_pos rfl]; exact Or.inl rfl
    · by_cases he : find u (a2 (a2 v)) (a1 v) (a2 (a2 v)) = J u u
      · rw [if_pos he]; exact Or.inl rfl
      · rw [if_neg he]; exact Or.inr ⟨hc2, Or.inr hc1⟩

/-- the digest: a decoded product reproduces the payload slot, and codes `u`. -/
theorem SND (u v : M) : op u v = J u v ∨
    (Cd v ∧ op (op u v) (a1 v) = a2 (a2 v)
     ∧ ((tg u = 2 ∧ a2 u = op u v) ∨ cds u (op u v))) := by
  by_cases hc : Cd v
  · by_cases hu : tg u = 2
    · by_cases hb : op (a2 u) (a1 v) = a2 (a2 v)
      · have hop : op u v = a2 u := by rw [op.eq_1, dif_pos hc, dif_pos hu, if_pos hb]
        exact Or.inr ⟨hc, by rw [hop]; exact hb, Or.inl ⟨hu, hop.symm⟩⟩
      · have hop : op u v = opTail u v hc := by rw [op.eq_1, dif_pos hc, dif_pos hu, if_neg hb]
        rw [hop]
        rcases SNDtail u v hc with h | ⟨h1, h2⟩
        · exact Or.inl h
        · exact Or.inr ⟨hc, h1, h2⟩
    · have hop : op u v = opTail u v hc := by rw [op.eq_1, dif_pos hc, dif_neg hu]
      rw [hop]
      rcases SNDtail u v hc with h | ⟨h1, h2⟩
      · exact Or.inl h
      · exact Or.inr ⟨hc, h1, h2⟩
  · exact Or.inl (opF hc)

/-- the A-free top product: branch U fires and returns `a2 (J y x) = x`. -/
theorem TOPU (x y z Q : M) (hP : op x z = Q) : op (J y x) (J z (J z Q)) = x := by
  rw [op.eq_1]
  rw [dif_pos (show Cd (J z (J z Q)) from ⟨rfl, rfl, rfl⟩)]
  rw [dif_pos (show tg (J y x) = 2 from rfl)]
  rw [if_pos (show op (a2 (J y x)) (a1 (J z (J z Q))) = a2 (a2 (J z (J z Q))) by
    simp only [a1_J_eq, a2_J_eq]; exact hP)]
  rfl

/-- F2 : the outer chain product is free.  `Cd (J z P)` reduces to `tg P = 2 ∧ z = a1 P`. -/
theorem F2 (x z : M) : op z (J z (op x z)) = J z (J z (op x z)) := by
  by_cases hc : Cd (J z (op x z))
  · obtain ⟨-, h2, h3⟩ := hc
    simp only [a1_J_eq, a2_J_eq] at h2 h3
    -- h2 : tg (op x z) = 2 ,  h3 : z = a1 (op x z)
    rw [op.eq_1, dif_pos (show Cd (J z (op x z)) from ⟨rfl, h2, by simp only [a1_J_eq, a2_J_eq]; exact h3⟩)]
    by_cases hu : tg z = 2
    · rw [dif_pos hu]
      by_cases hb : op (a2 z) (a1 (J z (op x z))) = a2 (a2 (J z (op x z)))
      · exfalso; sorry   -- L-U : refute branch U
      · rw [if_neg hb]; sorry  -- L-T1 : opTail = J z (J z P)
    · rw [dif_neg hu]; sorry   -- L-T2 : opTail = J z (J z P)
  · exact opF hc

theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (z) (op (x) (z)))) = x := by
  sorry

theorem lhs : @EquationLHS M inst := by
  intro x y z
  exact (law x y z).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
