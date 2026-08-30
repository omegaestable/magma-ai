import JudgeProblem
inductive submission.M : Type where
 | g : Nat→submission.M
 | J : submission.M→submission.M→submission.M
 deriving DecidableEq
namespace submission
open M
def tg : M→Nat
 | .g _ => 1
 | .J _ _ => 2
def a1 : M→M
 | .J x _ => x
 | t => t
def a2 : M→M
 | .J _ x => x
 | t => t
def sz : M→Nat
 | .g _ => 1
 | .J b0 b1 => sz b0+sz b1+1
def T (u : M) : sz (a1 u)≤sz u :=by cases u <;> simp[a1,sz] <;> omega
def E (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def X (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def Z (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=X _ h; simp[sz,a1,a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
def W (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : W a b<W u v :=by
 unfold W
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def L (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a1 (a2 v))=2∧tg (a2 (a2 v))=2∧a2 (a1 (a2 v))=a1 (a2 (a2 v))∧u=a2 (a2 (a2 v))
instance (u v : M) : Decidable (L u v) :=by unfold L; infer_instance
def N (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a1 (a2 v))=2∧tg u=2∧a2 (a1 (a2 v))=a1 u
instance (u v : M) : Decidable (N u v) :=by unfold N; infer_instance
def Q (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a2 (a2 v))=2∧u=a2 (a2 (a2 v))∧tg (a1 (a2 (a2 v)))=2
instance (u v : M) : Decidable (Q u v) :=by unfold Q; infer_instance
def O (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg u=2∧tg (a1 u)=2
instance (u v : M) : Decidable (O u v) :=by unfold O; infer_instance
def R (u v : M) : Prop:=tg v=2∧u=a1 v∧tg u=2
instance (u v : M) : Decidable (R u v) :=by unfold R; infer_instance
def D (u v : M) : Prop:=tg v=2∧u=a1 v∧tg u=2∧tg (a1 u)=2
instance (u v : M) : Decidable (D u v) :=by unfold D; infer_instance
def op (u v : M) : M :=
 let p1:=if hs1 : W (a1 u) (u)<W u v then op (a1 u) (u) else J u v
 let p2:=if hs2 : W (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v)))<W u v then op (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) else J u v
 let p3:=if hs3 : W (a1 (a1 u)) (a1 u)<W u v then op (a1 (a1 u)) (a1 u) else J u v
 let p4:=if hs4 : W (a1 (p1)) (p1)<W u v then op (a1 (p1)) (p1) else J u v
 if L u v then a2 (a1 (a2 v))
 else if N u v∧W (a1 u) (u)<W u v∧a2 (a2 v)=p1 then a1 u
 else if Q u v∧W (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v)))<W u v∧a1 (a2 v)=p2 then a1 (a2 (a2 v))
 else if O u v∧W (a1 (a1 u)) (a1 u)<W u v∧W (a1 u) (u)<W u v∧a1 (a2 v)=p3∧a2 (a2 v)=p1 then a1 u
 else if R u v∧W (a1 u) (u)<W u v∧W (a1 (p1)) (p1)<W u v∧tg (p1)=2∧tg (a1 (p1))=2∧a2 (a1 (p1))=a1 u∧a2 v=p4 then a1 u
 else if D u v∧W (a1 u) (u)<W u v∧W (a1 (a1 u)) (a1 u)<W u v∧W (a1 (p1)) (p1)<W u v∧tg (p1)=2∧a1 (p1)=p3∧a2 v=p4 then a1 u
 else J u v
termination_by W u v
decreasing_by
 ·assumption
 ·assumption
 ·assumption
 ·assumption
def inst : Magma M:={ op:=fun a b => op b a }
def Pre (u v : M) : Prop:=L u v∨N u v∨Q u v∨O u v∨R u v∨D u v
def op_free {u v : M} (h : ¬ Pre u v) : op u v=J u v :=by rw[op.eq_1]; simp only[Pre,not_or] at h; simp[h]
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 0) (g 0) (g 0)
 revert this
 change ¬ g 0=op (op (g 0) (op (g 0) (g 0))) (op (op (g 0) (g 0)) (g 0))
 simp (config:={decide:=true}) [op.eq_1,sz,L,N,Q,O,R,D]
def szJ1 (a b : M) : sz b<sz (J a b) :=by simp only[sz]; omega
def szJ2 (a b : M) : sz a<sz (J a b) :=by simp only[sz]; omega
def U {a t : M} (h : sz a<sz t) : a≠t:=fun e => by rw[e] at h; exact Nat.lt_irrefl _ h
def Y {a b u c : M} (h1 : sz a≤sz u∨sz a≤sz c) (h2 : sz b≤sz u∨sz b≤sz c) : W a b<W u (J u c) :=
 msr_lt_of_max_lt (by simp only[sz]; omega)
def V (u v : M) : ∃ p1 p2 p3 p4 : M,
  p1=(if hs1 : W (a1 u) u<W u v then op (a1 u) u else J u v) ∧
  p2=(if hs2 : W (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v)))<W u v then op (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v))) else J u v) ∧
  p3=(if hs3 : W (a1 (a1 u)) (a1 u)<W u v then op (a1 (a1 u)) (a1 u) else J u v) ∧
  p4=(if hs4 : W (a1 p1) p1<W u v then op (a1 p1) p1 else J u v) ∧
  op u v=(
 if L u v then a2 (a1 (a2 v))
 else if N u v∧W (a1 u) u<W u v∧a2 (a2 v)=p1 then a1 u
 else if Q u v∧W (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v)))<W u v∧a1 (a2 v)=p2 then a1 (a2 (a2 v))
 else if O u v∧W (a1 (a1 u)) (a1 u)<W u v∧W (a1 u) u<W u v∧a1 (a2 v)=p3∧a2 (a2 v)=p1 then a1 u
 else if R u v∧W (a1 u) u<W u v∧W (a1 p1) p1<W u v∧tg p1=2∧tg (a1 p1)=2∧a2 (a1 p1)=a1 u∧a2 v=p4 then a1 u
 else if D u v∧W (a1 u) u<W u v∧W (a1 (a1 u)) (a1 u)<W u v∧W (a1 p1) p1<W u v∧tg p1=2∧a1 p1=p3∧a2 v=p4 then a1 u
 else J u v) :=
 ⟨_,_,_,_,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
/-- free,or `v=J u _` with a strictly smaller result -/
def K (u v : M) : op u v=J u v∨(tg v=2∧a1 v=u∧sz (op u v)<sz v) :=by
 obtain⟨p1,p2,p3,p4,-,-,-,-,hop⟩:=V u v
 rw[hop]
 split
 ·rename_i h
  have:=Z v h.1; have:=T (a2 v); have:=E (a1 (a2 v))
  exact Or.inr ⟨h.1,h.2.1.symm,by omega⟩
 ·split
  ·rename_i h
   have:=Z v h.1.1; have:=congrArg sz h.1.2.1; have:=T u
   exact Or.inr ⟨h.1.1,h.1.2.1.symm,by omega⟩
  ·split
   ·rename_i h
    have:=Z v h.1.1; have:=E (a2 v); have:=T (a2 (a2 v))
    exact Or.inr ⟨h.1.1,h.1.2.1.symm,by omega⟩
   ·split
    ·rename_i h
     have:=Z v h.1.1; have:=congrArg sz h.1.2.1; have:=T u
     exact Or.inr ⟨h.1.1,h.1.2.1.symm,by omega⟩
    ·split
     ·rename_i h
      have:=Z v h.1.1; have:=congrArg sz h.1.2.1; have:=T u
      exact Or.inr ⟨h.1.1,h.1.2.1.symm,by omega⟩
     ·split
      ·rename_i h
       have:=Z v h.1.1; have:=congrArg sz h.1.2.1; have:=T u
       exact Or.inr ⟨h.1.1,h.1.2.1.symm,by omega⟩
      ·exact Or.inl rfl
def H (u v : M) : op u v≠v :=by
 intro h
 rcases K u v with h' | ⟨-,-,h'⟩
 ·rw[h] at h'; have:=congrArg sz h'; simp only[sz] at this; omega
 ·rw[h] at h'; exact Nat.lt_irrefl _ h'
def G {u a : M} (b : M) (h : a≠u) : op u (J a b)=J u (J a b) :=
 op_free (fun hp => by
  rcases hp with h1 | h1 | h1 | h1 | h1 | h1 <;>
   exact h (by have e:=h1.2.1; simp only[a1_J_eq] at e; exact e.symm))
def Wsz {u c : M} (h : sz c≤sz u) : op u c=J u c :=by
 rcases K u c with h' | ⟨hct,hcu,-⟩
 ·exact h'
 ·exfalso; have:=Z c hct; rw[hcu] at this; omega
def red1 (u : M) (h2 : tg (a1 (op (a1 u) u))=2) (h3 : a2 (a1 (op (a1 u) u))=a1 u) : sz (op (a1 u) u)<sz u :=by
 rcases K (a1 u) u with h | ⟨-,-,h⟩
 ·rw[h] at h2 h3; simp only[a1_J_eq] at h2 h3
  have:=Z _ h2; have:=congrArg sz h3; omega
 ·exact h
def red2 (u : M) (h3 : a1 (op (a1 u) u)=op (a1 (a1 u)) (a1 u)) : sz (op (a1 u) u)<sz u :=by
 rcases K (a1 u) u with h | ⟨-,-,h⟩
 ·rw[h] at h3; simp only[a1_J_eq] at h3; exact absurd h3.symm (H _ _)
 ·exact h
/-- no rule fires on `(y,J y (J x y))` -/
def I (x y : M) : op y (J y (J x y))=J y (J y (J x y)) :=by
 obtain⟨p1,p2,p3,p4,hp1,-,hp3,hp4,hop⟩:=V y (J y (J x y))
 have hs1 : W (a1 y) y<W y (J y (J x y)):=Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 have hs3 : W (a1 (a1 y)) (a1 y)<W y (J y (J x y)):=Y (Or.inl (Nat.le_trans (T _) (T _))) (Or.inl (T _))
 rw[dif_pos hs1] at hp1; subst hp1
 rw[dif_pos hs3] at hp3; subst hp3
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,h5,-,h7⟩:=h
  simp only[a2_J_eq] at h5 h7
  have:=Z y h5; have:=congrArg sz h7; omega
 ·split
  ·rename_i h; exfalso
   obtain⟨-,-,he⟩:=h
   simp only[a2_J_eq] at he
   exact H _ _ he.symm
  ·split
   ·rename_i h; exfalso
    obtain⟨⟨-,-,-,h4,h5,-⟩,-,-⟩:=h
    simp only[a2_J_eq] at h4 h5
    have:=Z y h4; have:=congrArg sz h5; omega
   ·split
    ·rename_i h; exfalso
     obtain⟨-,-,-,-,he⟩:=h
     simp only[a2_J_eq] at he
     exact H _ _ he.symm
    ·split
     ·rename_i h; exfalso
      obtain⟨-,-,hs4,-,h5,h6,he⟩:=h
      rw[dif_pos hs4] at hp4; subst hp4
      simp only[a2_J_eq] at he
      have hr:=red1 y h5 h6
      rcases K (a1 (op (a1 y) y)) (op (a1 y) y) with h' | ⟨-,-,h'⟩
      ·rw[h'] at he; rw[← (M.J.inj he).2] at hr; exact Nat.lt_irrefl _ hr
      ·rw[← he] at h'; simp only[sz] at h'; omega
     ·split
      ·rename_i h; exfalso
       obtain⟨-,-,-,hs4,-,h5,he⟩:=h
       rw[dif_pos hs4] at hp4; subst hp4
       simp only[a2_J_eq] at he
       have hr:=red2 y h5
       rcases K (a1 (op (a1 y) y)) (op (a1 y) y) with h' | ⟨-,-,h'⟩
       ·rw[h'] at he; rw[← (M.J.inj he).2] at hr; exact Nat.lt_irrefl _ hr
       ·rw[← he] at h'; simp only[sz] at h'; omega
      ·rfl
/-- no rule fires on `(x,J x x)` -/
def SELF (x : M) : op x (J x x)=J x (J x x) :=by
 obtain⟨p1,p2,p3,p4,hp1,-,hp3,hp4,hop⟩:=V x (J x x)
 have hs1 : W (a1 x) x<W x (J x x):=Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 have hs3 : W (a1 (a1 x)) (a1 x)<W x (J x x):=Y (Or.inl (Nat.le_trans (T _) (T _))) (Or.inl (T _))
 rw[dif_pos hs1] at hp1; subst hp1
 rw[dif_pos hs3] at hp3; subst hp3
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,h3,-,h5,-,h7⟩:=h
  simp only[a2_J_eq] at h3 h5 h7
  have:=Z x h3; have:=Z _ h5; have:=congrArg sz h7; omega
 ·split
  ·rename_i h; exfalso
   obtain⟨⟨-,-,-,h4,-,h6⟩,-,-⟩:=h
   simp only[a1_J_eq,a2_J_eq] at h4 h6
   have:=Z _ h4; have:=congrArg sz h6; omega
  ·split
   ·rename_i h; exfalso
    obtain⟨⟨-,-,h3,h4,h5,-⟩,-,-⟩:=h
    simp only[a2_J_eq] at h3 h4 h5
    have:=Z x h3; have:=Z _ h4; have:=congrArg sz h5; omega
   ·split
    ·rename_i h; exfalso
     obtain⟨-,-,-,he,-⟩:=h
     simp only[a1_J_eq,a2_J_eq] at he
     exact H _ _ he.symm
    ·split
     ·rename_i h; exfalso
      obtain⟨-,-,hs4,-,h5,h6,he⟩:=h
      rw[dif_pos hs4] at hp4; subst hp4
      simp only[a2_J_eq] at he
      have hr:=red1 x h5 h6
      rcases K (a1 (op (a1 x) x)) (op (a1 x) x) with h' | ⟨-,-,h'⟩
      ·rw[h'] at he
       have e:=congrArg a1 he; simp only[a1_J_eq] at e
       have:=Z _ h5; have:=congrArg sz (h6.trans e); omega
      ·rw[← he] at h'; omega
     ·split
      ·rename_i h; exfalso
       obtain⟨-,-,-,hs4,-,h5,he⟩:=h
       rw[dif_pos hs4] at hp4; subst hp4
       simp only[a2_J_eq] at he
       have hr:=red2 x h5
       rcases K (a1 (op (a1 x) x)) (op (a1 x) x) with h' | ⟨-,-,h'⟩
       ·rw[h'] at he
        have e:=congrArg a1 he; simp only[a1_J_eq] at e
        exact H _ _ (h5.symm.trans e.symm)
       ·rw[← he] at h'; omega
      ·rfl
def L1' (x y a : M) : op y (J a (J x y))=J y (J a (J x y)) :=by
 by_cases h : a=y
 ·rw[h]; exact I x y
 ·exact G _ h
/-- R1: a,b free -/
def op_R1 (x y z : M) : op y (op y (J (J z x) (J x y)))=x :=by
 rw[L1']
 obtain⟨p1,p2,p3,p4,-,-,-,-,hop⟩:=V y (J y (J (J z x) (J x y)))
 rw[hop,if_pos (show L y (J y (J (J z x) (J x y))) from ⟨rfl,rfl,rfl,rfl,rfl,rfl,rfl⟩)]
 rfl
/-- R2: b decoded,a free -/
def op_R2 (x y2 z u : M) (hu : u=J x y2) (hsb : sz (op x u)<sz u) : op u (op u (J (J z x) (op x u)))=x :=by
 have hw : op u (J (J z x) (op x u))=J u (J (J z x) (op x u)) :=by
  by_cases h : J z x=u
  ·exfalso; subst hu; obtain⟨rfl,rfl⟩:=M.J.inj h
   rw[SELF] at hsb; simp only[sz] at hsb; omega
  ·exact G _ h
 rw[hw]
 obtain⟨p1,p2,p3,p4,hp1,-,-,-,hop⟩:=V u (J u (J (J z x) (op x u)))
 have hs1 : W (a1 u) u<W u (J u (J (J z x) (op x u))):=Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 rw[dif_pos hs1] at hp1; subst hu
 simp only[a1_J_eq] at hp1; subst hp1
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[a2_J_eq] at h7
  have:=congrArg sz h7; have:=E (op x (J x y2)); omega
 ·split
  ·rfl
  ·rename_i h; exact absurd ⟨⟨rfl,rfl,rfl,rfl,rfl,rfl⟩,hs1,rfl⟩ h
/-- R3: a decoded,b free -/
def op_R3 (x2 y z u : M) (hu : u=J z x2) (hsa : sz (op z u)<sz u) : op y (op y (J (op z u) (J u y)))=u :=by
 rw[L1']
 generalize hv : J y (J (op z u) (J u y))=v
 obtain⟨p1,p2,p3,p4,hp1,hp2,-,-,hop⟩:=V y v
 have hs1 : W (a1 y) y<W y v :=by subst hv; exact Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 have hs2 : W (a1 (a1 (a2 (a2 v)))) (a1 (a2 (a2 v)))<W y v :=by
  subst hv; simp only[a1_J_eq,a2_J_eq]
  exact Y (Or.inr (by simp only[sz]; have:=T u; omega)) (Or.inr (by simp only[sz]; omega))
 rw[dif_pos hs1] at hp1; subst hp1
 rw[dif_pos hs2] at hp2; subst hv; subst hu
 simp only[a1_J_eq,a2_J_eq] at hp2; subst hp2
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,-,h6,-⟩:=h
  simp only[a1_J_eq,a2_J_eq] at h6
  have:=congrArg sz h6; have:=E (op z (J z x2)); omega
 ·split
  ·rename_i h; exfalso
   obtain⟨⟨-,-,-,-,-,h6⟩,-,he⟩:=h
   simp only[a1_J_eq,a2_J_eq] at h6 he
   rcases K (a1 y) y with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; rw[← (M.J.inj he).1] at h6
    have:=congrArg sz h6; have:=E (op z (J z x2)); omega
   ·rw[← he] at h'; simp only[sz] at h'; omega
  ·split
   ·rfl
   ·rename_i h; exact absurd ⟨⟨rfl,rfl,rfl,rfl,rfl,rfl⟩,hs2,rfl⟩ h
/-- R4: a and b decoded -/
def op_R4 (x2 y2 z x u : M) (hx : x=J z x2) (hu : u=J x y2) (hsa : sz (op z x)<sz x) (hsb : sz (op x u)<sz u) : op u (op u (J (op z x) (op x u)))=x :=by
 have hw : op u (J (op z x) (op x u))=J u (J (op z x) (op x u)) :=
  G _ (U (Nat.lt_trans hsa (by subst hu; exact szJ2 _ _)))
 rw[hw]
 generalize hv : J u (J (op z x) (op x u))=v
 obtain⟨p1,p2,p3,p4,hp1,-,hp3,-,hop⟩:=V u v
 have hs1 : W (a1 u) u<W u v :=by subst hv; exact Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 have hs3 : W (a1 (a1 u)) (a1 u)<W u v :=by subst hv; exact Y (Or.inl (Nat.le_trans (T _) (T _))) (Or.inl (T _))
 rw[dif_pos hs1] at hp1; rw[dif_pos hs3] at hp3
 subst hv; subst hu; subst hx
 simp only[a1_J_eq] at hp1 hp3; subst hp1; subst hp3
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[a2_J_eq] at h7
  have:=congrArg sz h7; have:=E (op (J z x2) (J (J z x2) y2)); omega
 ·split
  ·rename_i h; exfalso
   obtain⟨⟨-,-,-,-,-,h6⟩,-,-⟩:=h
   simp only[a1_J_eq,a2_J_eq] at h6
   have:=congrArg sz h6; have:=E (op z (J z x2)); omega
  ·split
   ·rename_i h; exfalso
    obtain⟨⟨-,-,-,-,h5,-⟩,-,-⟩:=h
    simp only[a2_J_eq] at h5
    have:=congrArg sz h5; have:=E (op (J z x2) (J (J z x2) y2)); omega
   ·split
    ·rfl
    ·rename_i h; exact absurd ⟨⟨rfl,rfl,rfl,rfl,rfl⟩,hs3,hs1,rfl,rfl⟩ h
/-- R5: c decoded,a free -/
def op_R5 (x y2 z b2 u c : M) (hu : u=J x y2) (hb : op x u=J (J z x) b2) (hc : op (J z x) (J (J z x) b2)=c) (hsb : sz (J (J z x) b2)<sz u) (hsc : sz c<sz (J (J z x) b2)) : op u (op u c)=x :=by
 have hw : op u c=J u c:=Wsz (by omega)
 rw[hw]
 obtain⟨p1,p2,p3,p4,hp1,-,-,hp4,hop⟩:=V u (J u c)
 have hs1 : W (a1 u) u<W u (J u c):=Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 rw[dif_pos hs1] at hp1; subst hu
 simp only[a1_J_eq] at hp1; rw[hb] at hp1; subst hp1
 have hs4 : W (a1 (J (J z x) b2)) (J (J z x) b2)<W (J x y2) (J (J x y2) c):=Y (Or.inl (Nat.le_trans (T _) (Nat.le_of_lt hsb))) (Or.inl (Nat.le_of_lt hsb))
 rw[dif_pos hs4] at hp4; subst hp4
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[a2_J_eq] at h7
  have:=congrArg sz h7; have:=E (a2 c); have:=E c; omega
 ·split
  ·rename_i h; exfalso
   obtain⟨-,-,he⟩:=h
   simp only[a2_J_eq] at he
   have:=congrArg sz he; have:=E c; omega
  ·split
   ·rename_i h; exfalso
    obtain⟨⟨-,-,-,-,h5,-⟩,-,-⟩:=h
    simp only[a2_J_eq] at h5
    have:=congrArg sz h5; have:=E (a2 c); have:=E c; omega
   ·split
    ·rename_i h; exfalso
     obtain⟨-,-,-,-,he⟩:=h
     simp only[a2_J_eq] at he
     have:=congrArg sz he; have:=E c; omega
    ·split
     ·rfl
     ·rename_i h; exact absurd ⟨⟨rfl,rfl,rfl⟩,hs1,hs4,rfl,rfl,rfl,hc.symm⟩ h
/-- R6: c decoded,a decoded -/
def op_R6 (x2 y2 z b2 x u c : M) (hx : x=J z x2) (hu : u=J x y2) (hsa : sz (op z x)<sz x) (hb : op x u=J (op z x) b2) (hc : op (op z x) (J (op z x) b2)=c) (hsb : sz (J (op z x) b2)<sz u) (hsc : sz c<sz (J (op z x) b2)) : op u (op u c)=x :=by
 have hw : op u c=J u c:=Wsz (by omega)
 rw[hw]
 obtain⟨p1,p2,p3,p4,hp1,-,hp3,hp4,hop⟩:=V u (J u c)
 have hs1 : W (a1 u) u<W u (J u c):=Y (Or.inl (T _)) (Or.inl (Nat.le_refl _))
 have hs3 : W (a1 (a1 u)) (a1 u)<W u (J u c):=Y (Or.inl (Nat.le_trans (T _) (T _))) (Or.inl (T _))
 rw[dif_pos hs1] at hp1; rw[dif_pos hs3] at hp3; subst hu
 simp only[a1_J_eq] at hp1 hp3; rw[hb] at hp1; subst hp1; subst hx
 simp only[a1_J_eq] at hp3; subst hp3
 have hs4 : W (a1 (J (op z (J z x2)) b2)) (J (op z (J z x2)) b2)<W (J (J z x2) y2) (J (J (J z x2) y2) c):=Y (Or.inl (Nat.le_trans (T _) (Nat.le_of_lt hsb))) (Or.inl (Nat.le_of_lt hsb))
 rw[dif_pos hs4] at hp4; subst hp4
 rw[hop]; split
 ·rename_i h; exfalso
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[a2_J_eq] at h7
  have:=congrArg sz h7; have:=E (a2 c); have:=E c; omega
 ·split
  ·rename_i h; exfalso
   obtain⟨-,-,he⟩:=h
   simp only[a2_J_eq] at he
   have:=congrArg sz he; have:=E c; omega
  ·split
   ·rename_i h; exfalso
    obtain⟨⟨-,-,-,-,h5,-⟩,-,-⟩:=h
    simp only[a2_J_eq] at h5
    have:=congrArg sz h5; have:=E (a2 c); have:=E c; omega
   ·split
    ·rename_i h; exfalso
     obtain⟨-,-,-,-,he⟩:=h
     simp only[a2_J_eq] at he
     have:=congrArg sz he; have:=E c; omega
    ·split
     ·rename_i h; exfalso
      obtain⟨-,-,-,-,h5,h6,-⟩:=h
      simp only[a1_J_eq,a2_J_eq] at h5 h6
      have:=Z _ h5; have:=congrArg sz h6; omega
     ·split
      ·rfl
      ·rename_i h; exact absurd ⟨⟨rfl,rfl,rfl,rfl⟩,hs1,hs3,hs4,rfl,rfl,hc.symm⟩ h
/-- THE LAW: x=y*(y*((z*x)*(x*y))) -/
def law (x y z : M) : op (y) (op (y) (op (op (z) (x)) (op (x) (y))))=x :=by
 rcases K z x with ha | ⟨hxt,hxz,hsa⟩
 ·rw[ha]
  rcases K x y with hb | ⟨hyt,hyx,hsb⟩
  ·rw[hb,G _ (U (szJ1 z x))]; exact op_R1 x y z
  ·obtain⟨x',y2,rfl⟩:=X y hyt
   simp only[a1_J_eq] at hyx; subst x'
   rcases K (J z x) (op x (J x y2)) with hc | ⟨hbt,hba,hsc⟩
   ·rw[hc]; exact op_R2 _ _ _ _ rfl hsb
   ·obtain⟨a',b2,hb'⟩:=X _ hbt
    rw[hb'] at hba; simp only[a1_J_eq] at hba; subst a'
    rw[hb'] at hsb hsc ⊢
    exact op_R5 _ _ _ _ _ _ rfl hb' rfl hsb hsc
 ·obtain⟨z',x2,rfl⟩:=X x hxt
  simp only[a1_J_eq] at hxz; subst z'
  rcases K (J z x2) y with hb | ⟨hyt,hyx,hsb⟩
  ·rw[hb,G _ (U hsa).symm]; exact op_R3 _ _ _ _ rfl hsa
  ·obtain⟨x',y2,rfl⟩:=X y hyt
   simp only[a1_J_eq] at hyx; subst x'
   rcases K (op z (J z x2)) (op (J z x2) (J (J z x2) y2)) with hc | ⟨hbt,hba,hsc⟩
   ·rw[hc]; exact op_R4 _ _ _ _ _ rfl rfl hsa hsb
   ·obtain⟨a',b2,hb'⟩:=X _ hbt
    rw[hb'] at hba; simp only[a1_J_eq] at hba; subst a'
    rw[hb'] at hsb hsc ⊢
    exact op_R6 _ _ _ _ _ _ _ rfl rfl hsa hb' rfl hsb hsc
def lhs : @EquationLHS M inst :=by
 intro x y z
 first | exact (law x y z).symm | exact (law x z y).symm | exact (law y x z).symm | exact (law y z x).symm | exact (law z x y).symm | exact (law z y x).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))