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
/-- Walk the unwrap chain while scanning both the direct payload `a1 T` and the
    reconstruction receipt `J (a1 T) T`.  Measuring this state by
    `sz w + sz T` makes both certification calls decrease without imposing a
    false size bound on the returned receipt. -/
def find (u T w P : M) : M :=
  if tg T = 2 ∧ tg (a1 T) = 2 ∧ tg (a2 (a1 T)) = 2 ∧ a1 (a1 T) = a1 (a2 (a1 T))
     ∧ op u (a1 (a1 T)) = a2 (a2 (a1 T)) ∧ op (a1 T) w = P then a1 T
  else
    let r := J (a1 T) T
    if hq : tg T = 2 ∧ op u (a1 T) = a2 T ∧ op r w = P then r
    else if h : tg T = 2 ∧ tg (a2 T) = 2 then find u (a2 (a2 T)) w P
    else J u u
termination_by (sz w + sz T, 0)
decreasing_by
  · have h1 := sz_a1 T
    have h2 := sz_a1 (a1 T)
    have hw := sz_pos w
    omega
  · have hT := sz_pos T
    omega
  · have h1 := sz_a1 T
    have hw := sz_pos w
    omega
  · have hT := sz_pos T
    omega
  · have e1 := sz_a2_lt h.1
    have e2 := sz_a2_lt h.2
    omega

def op (u v : M) : M :=
  if hc : Cd v then
    if hu : tg u = 2 then
      if op (a2 u) (a1 v) = a2 (a2 v) then a2 u else opTail u v hc
    else opTail u v hc
  else J u v
termination_by (sz v, 2)
decreasing_by
  · apply Prod.Lex.left
    exact sz_a1_lt hc.1
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
termination_by (sz v, 1)
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
    omega
  · have h9 := Cd_sz hc
    omega
end


def inst : Magma M := { op := fun a b => op b a }

theorem rhs : ¬ @EquationRHS M inst := by
  intro h
  have := h (g 0) (g 1) (g 0)
  revert this
  change ¬ g 0 = op (op (g 0) (g 1)) (op (g 0) (op (g 1) (op (g 1) (g 1))))
  simp [op.eq_1, opTail.eq_1, find.eq_1, Cd, tg, a1, a2, sz]
theorem opF {u v : M} (h : ¬ Cd v) : op u v = J u v := by
  rw [op.eq_1, dif_neg h]

/-- "c codes u" -- the relation every decode branch verifies. -/
def cds (u c : M) : Prop :=
  tg c = 2 ∧ tg (a2 c) = 2 ∧ a1 c = a1 (a2 c) ∧ op u (a1 c) = a2 (a2 c)

/-- Every non-sentinel locator result is certified and reproduces the root payload. -/
theorem findN (n : Nat) : ∀ u T w P r : M, sz T ≤ n → find u T w P = r →
    r = J u u ∨ (cds u r ∧ op r w = P) := by
  induction n with
  | zero =>
    intro u T w P r hn
    have hp := sz_pos T
    omega
  | succ n ih =>
    intro u T w P r hn hr
    rw [find.eq_1] at hr
    by_cases h1 : tg T = 2 ∧ tg (a1 T) = 2 ∧ tg (a2 (a1 T)) = 2 ∧
        a1 (a1 T) = a1 (a2 (a1 T)) ∧ op u (a1 (a1 T)) = a2 (a2 (a1 T)) ∧
        op (a1 T) w = P
    · rw [if_pos h1] at hr
      subst hr
      exact Or.inr ⟨⟨h1.2.1, h1.2.2.1, h1.2.2.2.1, h1.2.2.2.2.1⟩,
        h1.2.2.2.2.2⟩
    · rw [if_neg h1] at hr
      let q := J (a1 T) T
      by_cases hq : tg T = 2 ∧ op u (a1 T) = a2 T ∧ op q w = P
      · simp only [q] at hq
        rw [dif_pos hq] at hr
        subst hr
        exact Or.inr ⟨⟨rfl, hq.1, rfl, hq.2.1⟩, hq.2.2⟩
      · simp only [q] at hq
        rw [dif_neg hq] at hr
        by_cases h2 : tg T = 2 ∧ tg (a2 T) = 2
        · rw [dif_pos h2] at hr
          have e1 := sz_a2_lt h2.1
          have e2 := sz_a2_lt h2.2
          exact ih u (a2 (a2 T)) w P r (by omega) hr
        · rw [dif_neg h2] at hr
          exact Or.inl hr.symm

theorem findOK (u P w : M) : find u P w P = J u u ∨
    (cds u (find u P w P) ∧ op (find u P w P) w = P) :=
  findN (sz P) u P w P _ (Nat.le_refl _) rfl

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
      rcases findOK u (a2 (a2 v)) (a1 v) with hf | ⟨hc1, hc2⟩
      · rw [hf]; simp only [if_pos rfl]; exact Or.inl rfl
      · by_cases he : find u (a2 (a2 v)) (a1 v) (a2 (a2 v)) = J u u
        · rw [if_pos he]; exact Or.inl rfl
        · rw [if_neg he]; exact Or.inr ⟨hc2, Or.inr hc1⟩
  · rw [dif_neg hr]
    rcases findOK u (a2 (a2 v)) (a1 v) with hf | ⟨hc1, hc2⟩
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

/-- A code strictly below the right child of its producer cannot certify that producer.
    The payload of the code is smaller again; `SND` either gives an impossible free/direct
    reading or another certified code, to which the fuel induction applies. -/
theorem cds_below_a2_N (n : Nat) : ∀ u c : M, sz c ≤ n → sz c < sz (a2 u) → ¬ cds u c := by
  induction n with
  | zero =>
    intro u c hn
    have hp := sz_pos c
    omega
  | succ n ih =>
    intro u c hn hcu hc
    have e1 := sz_a2_lt hc.1
    have e2 := sz_a2_lt hc.2.1
    have hp : sz (a2 (a2 c)) < sz c := by omega
    have hop : op u (a1 c) = a2 (a2 c) := hc.2.2.2
    rcases SND u (a1 c) with hf | ⟨-, -, hu | hd⟩
    · rw [hf] at hop
      have es := congrArg sz hop
      simp only [sz_J] at es
      have eu := sz_a2 u
      have hw := sz_pos (a1 c)
      omega
    · rw [hop] at hu
      have es := congrArg sz hu.2
      omega
    · rw [hop] at hd
      exact ih u (a2 (a2 c)) (by omega) (by omega) hd

theorem cds_below_a2 {u c : M} (h : sz c < sz (a2 u)) : ¬ cds u c :=
  cds_below_a2_N (sz c) u c (Nat.le_refl _) h

/-- The useful descent is to the payload, not merely below the whole code. -/
theorem cds_a2_le_payload_N (n : Nat) : ∀ u c : M, sz c ≤ n → cds u c →
    sz (a2 u) ≤ sz (a2 (a2 c)) := by
  induction n with
  | zero =>
    intro u c hn _
    have hp := sz_pos c
    omega
  | succ n ih =>
    intro u c hn hc
    have e1 := sz_a2_lt hc.1
    have e2 := sz_a2_lt hc.2.1
    have hp : sz (a2 (a2 c)) < sz c := by omega
    have hop : op u (a1 c) = a2 (a2 c) := hc.2.2.2
    rcases SND u (a1 c) with hf | ⟨-, -, hu | hd⟩
    · rw [hf] at hop
      have es := congrArg sz hop
      simp only [sz_J] at es
      have eu := sz_a2 u
      have hw := sz_pos (a1 c)
      omega
    · rw [hop] at hu
      have es := congrArg sz hu.2
      omega
    · rw [hop] at hd
      have hi := ih u (a2 (a2 c)) (by omega) hd
      have e3 := sz_a2 (a2 (a2 c))
      have e4 := sz_a2 (a2 (a2 (a2 c)))
      omega

theorem cds_a2_le_payload {u c : M} (h : cds u c) :
    sz (a2 u) ≤ sz (a2 (a2 c)) :=
  cds_a2_le_payload_N (sz c) u c (Nat.le_refl _) h

theorem cds_a2_lt {u c : M} (h : cds u c) : sz (a2 u) < sz c :=
  by
    have h1 := cds_a2_le_payload h
    have h2 := sz_a2_lt h.1
    have h3 := sz_a2_lt h.2.1
    omega

/-- No term can be a code for itself.  The first payload step lands strictly below `a2 u`,
    where `cds_below_a2` rules out the only recursive `SND` reading. -/
theorem cds_self (u : M) : ¬ cds u u := by
  intro hc
  have e1 := sz_a2_lt hc.1
  have e2 := sz_a2_lt hc.2.1
  have hop : op u (a1 u) = a2 (a2 u) := hc.2.2.2
  rcases SND u (a1 u) with hf | ⟨-, -, hu | hd⟩
  · rw [hf] at hop
    have es := congrArg sz hop
    simp only [sz_J] at es
    have hw := sz_pos (a1 u)
    omega
  · rw [hop] at hu
    have es := congrArg sz hu.2
    omega
  · rw [hop] at hd
    exact cds_below_a2 (by omega) hd

/-- The decoder has no left fixed point. -/
theorem op_ne_left (u v : M) : op u v ≠ u := by
  intro h
  rcases SND u v with hf | ⟨-, -, hu | hd⟩
  · rw [hf] at h
    have es := congrArg sz h
    simp only [sz_J] at es
    have hv := sz_pos v
    omega
  · rw [h] at hu
    have es := congrArg sz hu.2
    have eu := sz_a2_lt hu.1
    omega
  · rw [h] at hd
    exact cds_self u hd

/-- The decoder has no right fixed point either. -/
theorem op_ne_right (u v : M) : op u v ≠ v := by
  intro h
  rcases SND u v with hf | ⟨hc, hr, -⟩
  · rw [hf] at h
    have es := congrArg sz h
    simp only [sz_J] at es
    have hu := sz_pos u
    omega
  · rw [h] at hr
    exact cds_self v ⟨hc.1, hc.2.1, hc.2.2, hr⟩

/-- If a coded left argument produces `T`, its own payload lies strictly below `T`. -/
theorem code_payload_lt_result {c w T : M} (hc : Cd c) (hop : op c w = T) :
    sz (a2 (a2 c)) < sz T := by
  rcases SND c w with hf | ⟨-, -, hu | hd⟩
  · rw [hf] at hop
    have es := congrArg sz hop
    simp only [sz_J] at es
    have ec := sz_a2 c
    have ec2 := sz_a2 (a2 c)
    have hw := sz_pos w
    omega
  · rw [hop] at hu
    have ec := sz_a2_lt hc.2.1
    have es := congrArg sz hu.2
    omega
  · rw [hop] at hd
    have hh := cds_a2_lt hd
    have ec := sz_a2 (a2 c)
    omega

theorem out_cases {u z P : M} (h : op u z = P) :
    P = J u z ∨ (cds P z ∧ ((tg u = 2 ∧ a2 u = P) ∨ cds u P)) := by
  rcases SND u z with hf | ⟨hc, hr, hs⟩
  · exact Or.inl (h.symm.trans hf)
  · rw [h] at hr hs
    exact Or.inr ⟨⟨hc.1, hc.2.1, hc.2.2, hr⟩, hs⟩

theorem code_eq_recon {c P : M} (hc : Cd c) (h : a2 c = P) :
    c = J (a1 P) P := by
  obtain ⟨a, b, rfl⟩ := tg_J _ hc.1
  unfold Cd at hc
  simp only [a1_J_eq, a2_J_eq] at hc h ⊢
  subst b
  rw [hc.2.2]

theorem code_direct_recursive_absurd {A c x P : M}
    (hAc : cds A c) (hAx : cds A x) (hcP : a2 c = P) (hxP : cds x P) : False := by
  have hcEq := code_eq_recon (⟨hAc.1, hAc.2.1, hAc.2.2.1⟩ : Cd c) hcP
  have hpay := code_payload_lt_result
    (⟨hAx.1, hAx.2.1, hAx.2.2.1⟩ : Cd x) hxP.2.2.2
  have hA := cds_a2_le_payload hAx
  have hp := sz_a2_lt hxP.2.1
  have hlt : sz (a2 A) < sz (a2 P) := by omega
  have hopA : op A (a1 P) = a2 P := by
    have h := hAc.2.2.2
    rw [hcEq] at h
    simpa only [a1_J_eq, a2_J_eq] using h
  rcases SND A (a1 P) with hf | ⟨-, -, hu | hd⟩
  · have e : J A (a1 P) = a2 P := hf.symm.trans hopA
    have e2 := congrArg a2 e
    simp only [a2_J_eq] at e2
    exact op_ne_right x (a1 P) (hxP.2.2.2.trans e2.symm)
  · rw [hopA] at hu
    have es := congrArg sz hu.2
    omega
  · rw [hopA] at hd
    have hs : op A (a1 (a2 P)) = a2 P := by
      rw [← hxP.2.2.1]
      exact hopA
    have he := congrArg sz (hs.symm.trans hd.2.2.2)
    have ep := sz_a2_lt hd.1
    have ep2 := sz_a2 (a2 (a2 P))
    omega

/-- Two code candidates for the same source cannot reproduce the same chain payload. -/
theorem code_fiber_unique_N (n : Nat) : ∀ A c x z P : M, sz P ≤ n →
    cds A c → cds A x → op c z = P → op x z = P → c = x := by
  induction n with
  | zero =>
    intro A c x z P hn
    have hp := sz_pos P
    omega
  | succ n ih =>
    intro A c x z P hn hAc hAx hcP hxP
    rcases out_cases hcP with hcf | ⟨hPz, hc⟩
    · rcases out_cases hxP with hxf | ⟨hPz', hx⟩
      · have e : J c z = J x z := hcf.symm.trans hxf
        injection e
      · rw [hcf] at hPz'
        have hh := cds_a2_lt hPz'
        simp only [a2_J_eq] at hh
        omega
    · rcases out_cases hxP with hxf | ⟨hPz', hx⟩
      · rw [hxf] at hPz
        have hh := cds_a2_lt hPz
        simp only [a2_J_eq] at hh
        omega
      · rcases hc with hc | hc <;> rcases hx with hx | hx
        · exact (code_eq_recon ⟨hAc.1, hAc.2.1, hAc.2.2.1⟩ hc.2).trans
            (code_eq_recon ⟨hAx.1, hAx.2.1, hAx.2.2.1⟩ hx.2).symm
        · exact (code_direct_recursive_absurd hAc hAx hc.2 hx).elim
        · exact (code_direct_recursive_absurd hAx hAc hx.2 hc).elim
        · have e1 := sz_a2_lt hc.1
          have e2 := sz_a2_lt hc.2.1
          exact ih A c x (a1 P) (a2 (a2 P)) (by omega) hAc hAx
            hc.2.2.2 hx.2.2.2

theorem code_fiber_unique {A c x z P : M} (hAc : cds A c) (hAx : cds A x)
    (hcP : op c z = P) (hxP : op x z = P) : c = x :=
  code_fiber_unique_N (sz P) A c x z P (Nat.le_refl _) hAc hAx hcP hxP

/-- Completeness of the unbounded locator.  A free transition exposes `x` as
    `a1 T`, a direct transition exposes it as the receipt `J (a1 T) T`, and a
    recursive transition descends to `a2 (a2 T)`.  Any candidate accepted
    earlier is `x` by `code_fiber_unique`. -/
theorem find_complete_N (n : Nat) : ∀ A x z P T w : M, sz T ≤ n →
    cds A x → op x z = P → op x w = T → find A T z P = x := by
  induction n with
  | zero =>
    intro A x z P T w hn
    have hp := sz_pos T
    omega
  | succ n ih =>
    intro A x z P T w hn hAx hxP hxT
    rw [find.eq_1]
    by_cases h1 : tg T = 2 ∧ tg (a1 T) = 2 ∧ tg (a2 (a1 T)) = 2 ∧
        a1 (a1 T) = a1 (a2 (a1 T)) ∧
        op A (a1 (a1 T)) = a2 (a2 (a1 T)) ∧ op (a1 T) z = P
    · rw [if_pos h1]
      exact code_fiber_unique
        ⟨h1.2.1, h1.2.2.1, h1.2.2.2.1, h1.2.2.2.2.1⟩ hAx
        h1.2.2.2.2.2 hxP
    · rw [if_neg h1]
      let q := J (a1 T) T
      by_cases hq : tg T = 2 ∧ op A (a1 T) = a2 T ∧ op q z = P
      · simp only [q] at hq
        rw [dif_pos hq]
        exact code_fiber_unique ⟨rfl, hq.1, rfl, hq.2.1⟩ hAx hq.2.2 hxP
      · simp only [q] at hq
        rw [dif_neg hq]
        rcases out_cases hxT with hf | ⟨hTw, hd | hr⟩
        · exfalso
          apply h1
          rw [hf]
          simp only [tg_J_eq, a1_J_eq, a2_J_eq]
          exact ⟨True.intro, hAx.1, hAx.2.1, hAx.2.2.1, hAx.2.2.2, hxP⟩
        · exfalso
          apply hq
          have hxEq := code_eq_recon
            (⟨hAx.1, hAx.2.1, hAx.2.2.1⟩ : Cd x) hd.2
          refine ⟨?_, ?_, ?_⟩
          · rw [← hd.2]
            exact hAx.2.1
          · rw [← hd.2, ← hAx.2.2.1]
            exact hAx.2.2.2
          · rw [← hxEq]
            exact hxP
        · have h2 : tg T = 2 ∧ tg (a2 T) = 2 := ⟨hr.1, hr.2.1⟩
          rw [dif_pos h2]
          have e1 := sz_a2_lt h2.1
          have e2 := sz_a2_lt h2.2
          exact ih A x z P (a2 (a2 T)) (a1 T) (by omega) hAx hxP hr.2.2.2

theorem find_complete {A x z P : M} (hAx : cds A x) (hxP : op x z = P) :
    find A P z P = x :=
  find_complete_N (sz P) A x z P P z (Nat.le_refl _) hAx hxP hxP

theorem cds_ne_sentinel {A x : M} (hAx : cds A x) : x ≠ J A A := by
  intro he
  have ht : tg A = 2 := by rw [he] at hAx; exact hAx.2.1
  have ha : A = a1 A := by rw [he] at hAx; simpa only [a1_J_eq, a2_J_eq] using hAx.2.2.1
  have hs := sz_a1_lt ht
  have hz := congrArg sz ha
  omega

theorem receipt_reproduces {P z : M} (hz : Cd z)
    (h : op P (a1 z) = a2 (a2 z)) :
    op (J (a1 P) P) z = P := by
  rw [op.eq_1, dif_pos hz]
  rw [dif_pos (show tg (J (a1 P) P) = 2 from rfl)]
  rw [if_pos (by simpa only [a2_J_eq] using h)]
  rfl

/-- Once branch U is bypassed, the concrete top decoder returns the unique
    certified reproducer.  Reconstruction is unique by `code_fiber_unique`;
    every other branch reaches the complete locator. -/
theorem opTail_complete {A x z P : M} (hAx : cds A x) (hxP : op x z = P) :
    opTail A (J z (J z P)) (show Cd (J z (J z P)) from ⟨rfl, rfl, rfl⟩) = x := by
  rw [opTail.eq_1]
  by_cases hr : tg P = 2 ∧ tg z = 2 ∧ tg (a2 z) = 2 ∧ a1 z = a1 (a2 z)
  · rw [dif_pos (by simpa only [a1_J_eq, a2_J_eq] using hr)]
    by_cases hg : op A (a1 P) = a2 P ∧ op P (a1 z) = a2 (a2 z)
    · rw [if_pos (by simpa only [a1_J_eq, a2_J_eq] using hg)]
      apply code_fiber_unique
        (show cds A (J (a1 P) P) from ⟨rfl, hr.1, rfl, hg.1⟩) hAx
        (receipt_reproduces ⟨hr.2.1, hr.2.2.1, hr.2.2.2⟩ hg.2) hxP
    · rw [if_neg (by simpa only [a1_J_eq, a2_J_eq] using hg)]
      simp only [a1_J_eq, a2_J_eq]
      simp only [find_complete hAx hxP, if_neg (cds_ne_sentinel hAx)]
  · rw [dif_neg (by simpa only [a1_J_eq, a2_J_eq] using hr)]
    simp only [a1_J_eq, a2_J_eq]
    simp only [find_complete hAx hxP, if_neg (cds_ne_sentinel hAx)]

theorem TOPD_noU {A x z P : M} (hAx : cds A x) (hxP : op x z = P)
    (hU : ¬ (tg A = 2 ∧ op (a2 A) z = P)) :
    op A (J z (J z P)) = x := by
  rw [op.eq_1, dif_pos (show Cd (J z (J z P)) from ⟨rfl, rfl, rfl⟩)]
  by_cases hA : tg A = 2
  · rw [dif_pos hA]
    rw [if_neg (by
      intro h
      apply hU
      refine ⟨hA, ?_⟩
      simpa only [a1_J_eq, a2_J_eq] using h)]
    exact opTail_complete hAx hxP
  · rw [dif_neg hA]
    exact opTail_complete hAx hxP

/-- the A-free top product: branch U fires and returns `a2 (J y x) = x`. -/
theorem TOPU (x y z Q : M) (hP : op x z = Q) : op (J y x) (J z (J z Q)) = x := by
  rw [op.eq_1]
  rw [dif_pos (show Cd (J z (J z Q)) from ⟨rfl, rfl, rfl⟩)]
  rw [dif_pos (show tg (J y x) = 2 from rfl)]
  rw [if_pos (show op (a2 (J y x)) (a1 (J z (J z Q))) = a2 (a2 (J z (J z Q))) by
    simp only [a1_J_eq, a2_J_eq]; exact hP)]
  rfl

/-- A product can never equal its own right argument. -/
theorem NZ {c t : M} (hs : sz c < sz t) (h : op c t = t) : False := by
  exact op_ne_right c t h

/-- `find` returns the sentinel once every reproducing candidate is refuted. -/
theorem findSent {u P w : M} (h : ∀ r : M, op r w = P → False) :
    find u P w P = J u u := by
  rcases findOK u P w with hf | ⟨-, hc2⟩
  · exact hf
  · exact (h _ hc2).elim

/-- `opTail` is free when branch R's inner pair fails (under its own guard) and `find` bails. -/
theorem opTailF {u v : M} (hc : Cd v)
    (hg : tg (a2 (a2 v)) = 2 → tg (a1 v) = 2 → tg (a2 (a1 v)) = 2 → a1 (a1 v) = a1 (a2 (a1 v)) →
          ¬ (op u (a1 (a2 (a2 v))) = a2 (a2 (a2 v))
             ∧ op (a2 (a2 v)) (a1 (a1 v)) = a2 (a2 (a1 v))))
    (hf : find u (a2 (a2 v)) (a1 v) (a2 (a2 v)) = J u u) : opTail u v hc = J u v := by
  rw [opTail.eq_1]
  by_cases hr : tg (a2 (a2 v)) = 2 ∧ tg (a1 v) = 2 ∧ tg (a2 (a1 v)) = 2
                ∧ a1 (a1 v) = a1 (a2 (a1 v))
  · rw [dif_pos hr, if_neg (hg hr.1 hr.2.1 hr.2.2.1 hr.2.2.2), hf]; simp
  · rw [dif_neg hr, hf]; simp

/-- `op` is free when branch U's guard fails and `opTail` is free. -/
theorem opFree {u v : M} (hc : Cd v)
    (hb : ¬ (tg u = 2 ∧ op (a2 u) (a1 v) = a2 (a2 v)))
    (ht : opTail u v hc = J u v) : op u v = J u v := by
  rw [op.eq_1, dif_pos hc]
  by_cases hu : tg u = 2
  · rw [dif_pos hu, if_neg (fun h => hb ⟨hu, h⟩)]; exact ht
  · rw [dif_neg hu]; exact ht

/-- The first chain product is free.  A hypothetical decode makes the
    `a2`-payload sizes run around a strict two- or three-code cycle. -/
theorem F1 (x z : M) : op z (op x z) = J z (op x z) := by
  rcases out_cases (show op z (op x z) = op z (op x z) from rfl) with hf | ⟨hQP, hQ⟩
  · exact hf
  · rcases out_cases (show op x z = op x z from rfl) with hP | ⟨hPz, hPsrc⟩
    · rw [hP] at hQP hQ
      rcases hQ with ⟨-, hQ⟩ | hzQ
      · exfalso
        have he := hQP.2.2.2
        simp only [a1_J_eq, a2_J_eq] at he
        rw [hQ] at he
        exact op_ne_left (op z (J x z)) x he
      · exfalso
        have e1 := cds_a2_le_payload hQP
        have e2 := cds_a2_le_payload hzQ
        have e3 := sz_a2_lt hzQ.2.1
        simp only [a2_J_eq] at e1
        omega
    · rcases hQ with ⟨-, hQ⟩ | hzQ
      · exfalso
        have e1 := cds_a2_le_payload hPz
        have e2 := cds_a2_le_payload hQP
        have e3 := sz_a2_lt hQP.2.1
        rw [← hQ] at e2
        omega
      · exfalso
        have e1 := cds_a2_le_payload hPz
        have e2 := sz_a2_lt hPz.2.1
        have e3 := cds_a2_le_payload hzQ
        have e4 := sz_a2_lt hzQ.2.1
        have e5 := cds_a2_le_payload hQP
        have e6 := sz_a2_lt hQP.2.1
        omega

/-- the diagonal cell of F2 (`x = z`, the payload slot is `z` itself).  Every branch dies:
    U and the search by `NZ`, and branch R by its OWN two inner conditions, which both become
    statements about `op z (a1 z)`. -/
theorem FDiag (z : M) : op z (J z (J z z)) = J z (J z (J z z)) := by
  refine opFree (⟨rfl, rfl, rfl⟩ : Cd (J z (J z z))) ?_ (opTailF _ ?_ ?_)
  · rintro ⟨hu, h⟩
    exact op_ne_right (a2 z) z h
  · intro _ _ h3 _
    rintro ⟨g1, g2⟩
    simp only [a1_J_eq, a2_J_eq] at g1 g2 h3
    have e := g1.symm.trans g2
    have := sz_a2_lt h3
    have := congrArg sz e
    omega
  · exact findSent (fun r hq => op_ne_right r z hq)

/-- F2 : the outer chain product is free.  `Cd (J z P)` reduces to `tg P = 2 ∧ z = a1 P`;
    `RS x z` then kills the reconstruction and the search readings of `P` by size, leaving
    the free reading (the diagonal, `FDiag`) and the `a2 x` reading. -/
theorem F2 (x z : M) : op z (J z (op x z)) = J z (J z (op x z)) := by
  rcases out_cases
      (show op z (J z (op x z)) = op z (J z (op x z)) from rfl) with hf | ⟨hQV, hQ⟩
  · exact hf
  · have hza : z = a1 (op x z) := by
      simpa only [a1_J_eq, a2_J_eq] using hQV.2.2.1
    rcases out_cases (show op x z = op x z from rfl) with hP | ⟨hPz, hPsrc⟩
    · have hzx : z = x := by
        rw [hP] at hza
        simpa only [a1_J_eq] using hza
      subst x
      rw [hP]
      exact FDiag z
    · rcases hPsrc with hd | hxP
      · rcases hQ with ⟨-, hQ⟩ | hzQ
        · have hRT : op (a2 z) z = a2 (op x z) := by
            have he := hQV.2.2.2
            simpa only [a1_J_eq, a2_J_eq, ← hQ] using he
          rcases out_cases hRT with hfree | ⟨hTz, hsrc⟩
          · exfalso
            have e1 := cds_a2_le_payload hPz
            have e2 := sz_a2_lt hPz.2.1
            have e3 := congrArg sz hfree
            simp only [sz_J] at e3
            have hzpos := sz_pos z
            omega
          · rcases hsrc with ⟨-, hdir⟩ | hRTc
            · exfalso
              have he := hTz.2.2.2
              rw [hdir] at he
              exact op_ne_left (a2 (op x z)) (a1 z) he
            · exfalso
              have e1 := cds_a2_le_payload hPz
              have e2 := cds_a2_le_payload hRTc
              have e3 := sz_a2_lt hRTc.2.1
              have e4 := sz_a2_lt hRTc.1
              omega
        · exfalso
          have e1 := cds_a2_le_payload hPz
          have e2 := sz_a2_lt hPz.2.1
          have e3 := cds_a2_le_payload hzQ
          have e4 := sz_a2_lt hzQ.2.1
          have e5 : sz (a2 (op z (J z (op x z)))) ≤ sz (a2 (op x z)) := by
            simpa only [a2_J_eq] using cds_a2_le_payload hQV
          omega
      · exfalso
        have e1 := cds_a2_lt hPz
        have e2 := sz_a1_lt hxP.2.1
        have e3 := congrArg sz hza
        have e4 := congrArg sz hxP.2.2.1
        omega

/-- Adjacent right children never have the same value at one argument. -/
theorem a2_fiber_N (n : Nat) : ∀ u v P : M, sz P ≤ n → tg u = 2 →
    op u v = P → op (a2 u) v = P → False := by
  induction n with
  | zero =>
    intro u v P hn
    have hp := sz_pos P
    omega
  | succ n ih =>
    intro u v P hn hu h1 h2
    rcases out_cases h1 with h1f | ⟨hPv1, h1s⟩
    · rcases out_cases h2 with h2f | ⟨hPv2, -⟩
      · have he : u = a2 u := by
          have h := h1f.symm.trans h2f
          injection h
        have hs := sz_a2_lt hu
        rw [← he] at hs
        omega
      · have hs := cds_a2_lt hPv2
        rw [h1f] at hs
        simp only [a2_J_eq] at hs
        omega
    · rcases out_cases h2 with h2f | ⟨hPv2, h2s⟩
      · have hs := cds_a2_lt hPv1
        rw [h2f] at hs
        simp only [a2_J_eq] at hs
        omega
      · rcases h1s with h1d | h1r <;> rcases h2s with h2d | h2r
        · rw [h1d.2] at h2d
          have hs := sz_a2_lt h2d.1
          have he := congrArg sz h2d.2
          omega
        · rw [h1d.2] at h2r
          exact cds_self P h2r
        · have e1 := cds_a2_le_payload h1r
          have e2 := sz_a2_lt h1r.1
          have e3 := sz_a2 (a2 P)
          have e4 := sz_a2 (a2 u)
          have es := congrArg sz h2d.2
          omega
        · have ep1 := sz_a2_lt h1r.1
          have ep2 := sz_a2 (a2 P)
          exact ih u (a1 P) (a2 (a2 P)) (by omega) hu
            h1r.2.2.2 h2r.2.2.2

theorem a2_fiber {u v : M} (hu : tg u = 2) : op u v ≠ op (a2 u) v := by
  intro h
  exact a2_fiber_N (sz (op u v)) u v (op u v) (Nat.le_refl _) hu rfl h.symm

/-- Adjacent inputs cannot send one argument to adjacent outputs. -/
theorem a2_square {u v P : M} (hu : tg u = 2) (hP : tg P = 2)
    (h1 : op u v = P) (h2 : op (a2 u) v = a2 P) : False := by
  rcases out_cases h1 with h1f | ⟨hPv1, -⟩
  · rw [h1f] at h2
    simp only [a2_J_eq] at h2
    exact op_ne_right (a2 u) v h2
  · rcases out_cases h2 with h2f | ⟨hPv2, -⟩
    · have e1 := cds_a2_lt hPv1
      have es := congrArg sz h2f
      simp only [sz_J] at es
      omega
    · apply a2_fiber hP
      exact hPv1.2.2.2.trans hPv2.2.2.2.symm

/-- A code and the right child of its source cannot share an output. -/
theorem code_a2_fiber_N (n : Nat) : ∀ A x z P : M, sz P ≤ n → tg A = 2 →
    cds A x → op (a2 A) z = P → op x z = P → False := by
  induction n with
  | zero =>
    intro A x z P hn
    have hp := sz_pos P
    omega
  | succ n ih =>
    intro A x z P hn hA hAx h1 h2
    rcases out_cases h1 with h1f | ⟨hPz1, h1s⟩
    · rcases out_cases h2 with h2f | ⟨hPz2, -⟩
      · have he : a2 A = x := by
          have h := h1f.symm.trans h2f
          injection h
        have hs := cds_a2_lt hAx
        rw [he] at hs
        omega
      · have hs := cds_a2_lt hPz2
        rw [h1f] at hs
        simp only [a2_J_eq] at hs
        omega
    · rcases out_cases h2 with h2f | ⟨hPz2, h2s⟩
      · have hs := cds_a2_lt hPz1
        rw [h2f] at hs
        simp only [a2_J_eq] at hs
        omega
      · rcases h1s with h1d | h1r <;> rcases h2s with h2d | h2r
        · have e1 := cds_a2_le_payload hAx
          have e2 := sz_a2_lt hAx.2.1
          have e3 := sz_a2 (a2 A)
          have es1 := congrArg sz h1d.2
          have es2 := congrArg sz h2d.2
          omega
        · have e1 := cds_a2_le_payload hAx
          have e2 := sz_a2_lt hAx.2.1
          have e3 := cds_a2_le_payload h2r
          have e4 := sz_a2_lt h2r.1
          have e5 := sz_a2 (a2 P)
          have e6 := sz_a2 (a2 A)
          have es := congrArg sz h1d.2
          omega
        · have hxEq := code_eq_recon
            (⟨hAx.1, hAx.2.1, hAx.2.2.1⟩) h2d.2
          have hp1 : op A (a1 P) = a2 P := by
            have h := hAx.2.2.2
            rw [hxEq] at h
            simpa only [a1_J_eq, a2_J_eq] using h
          exact a2_square hA h1r.2.1 hp1 h1r.2.2.2
        · have ep1 := sz_a2_lt h1r.1
          have ep2 := sz_a2 (a2 P)
          exact ih A x (a1 P) (a2 (a2 P)) (by omega) hA hAx
            h1r.2.2.2 h2r.2.2.2

theorem law (x y z : M) : op (op (y) (x)) (op (z) (op (z) (op (x) (z)))) = x := by
  rw [F1 x z, F2 x z]
  rcases out_cases (show op y x = op y x from rfl) with hf | ⟨hAx, -⟩
  · rw [hf]
    exact TOPU x y z (op x z) rfl
  · apply TOPD_noU hAx rfl
    rintro ⟨hA, hU⟩
    exact code_a2_fiber_N (sz (op x z)) (op y x) x z (op x z)
      (Nat.le_refl _) hA hAx hU rfl

theorem lhs : @EquationLHS M inst := by
  intro x y z
  first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm

end submission

def submission : Goal :=
  Exists.intro submission.M (Exists.intro submission.inst
    (And.intro submission.lhs submission.rhs))
