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
def D (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def I (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def tg_g (t : M) (h : tg t≠2) : ∃ n,t=M.g n :=by cases t <;> simp_all[tg]
def sz_tg (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a1,a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
/-- the recursion measure: lexicographic (max size,total size),packed into one Nat -/
def W (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : W a b<W u v :=by
 unfold W
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b)=max (sz u) (sz v)) (h2 : sz a+sz b<sz u+sz v) : W a b<W u v :=by unfold W; rw[h]; omega
def E (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a1 (a2 v)∧tg (a2 (a2 v))=2∧tg (a1 (a2 (a2 v)))=2∧u=a2 (a1 (a2 (a2 v)))∧u=a2 (a2 (a2 v))
instance (u v : M) : Decidable (E u v) :=by unfold E; infer_instance
def Y (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a1 (a2 v)∧tg (a2 (a2 v))=2∧u=a2 (a2 (a2 v))∧tg u=2∧tg (a2 u)=2
instance (u v : M) : Decidable (Y u v) :=by unfold Y; infer_instance
def L (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a1 (a2 v)∧tg (a2 (a2 v))=2∧u=a2 (a2 (a2 v))
instance (u v : M) : Decidable (L u v) :=by unfold L; infer_instance
def N (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a1 (a2 v)∧tg u=2∧tg (a2 u)=2
instance (u v : M) : Decidable (N u v) :=by unfold N; infer_instance
def Z (u v : M) : Prop:=v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧tg (a2 (a1 u))=2∧tg (a1 (a2 (a1 u)))=2∧a1 (a1 u)=a2 (a1 (a2 (a1 u)))∧a1 (a1 u)=a2 (a2 (a1 u))
instance (u v : M) : Decidable (Z u v) :=by unfold Z; infer_instance
def K (u v : M) : Prop:=v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧tg (a2 (a1 u))=2∧a1 (a1 u)=a2 (a2 (a1 u))∧tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2
instance (u v : M) : Decidable (K u v) :=by unfold K; infer_instance
def V (u v : M) : Prop:=v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧tg (a2 (a1 u))=2∧a1 (a1 u)=a2 (a2 (a1 u))
instance (u v : M) : Decidable (V u v) :=by unfold V; infer_instance
def X (u v : M) : Prop:=v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2
instance (u v : M) : Decidable (X u v) :=by unfold X; infer_instance
def op (u v : M) : M :=
 let p1:=if hs1 : W (a1 (a2 u)) (u)<W u v then op (a1 (a2 u)) (u) else J u v
 let p2:=if hs2 : W (u) (u)<W u v then op (u) (u) else J u v
 let p3:=if hs3 : W (a1 u) (u)<W u v then op (a1 u) (u) else J u v
 let p4:=if hs4 : W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v then op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) else J u v
 let p5:=if hs5 : W (a1 (a1 u)) (a1 (a1 u))<W u v then op (a1 (a1 u)) (a1 (a1 u)) else J u v
 if E u v then a1 v
 else if Y u v∧W (a1 (a2 u)) (u)<W u v∧a1 (a2 (a2 v))=p1 then a1 v
 else if L u v∧W (u) (u)<W u v∧a1 (a2 (a2 v))=p2 then a1 v
 else if N u v∧W (a1 (a2 u)) (u)<W u v∧a2 (a2 v)=p1∧a1 (a2 u)=p1 then a1 v
 else if Z u v∧W (a1 u) (u)<W u v∧a1 u=p3 then a1 (a1 u)
 else if K u v∧W (a1 u) (u)<W u v∧W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v∧a1 u=p3∧a1 (a2 (a1 u))=p4 then a1 (a1 u)
 else if V u v∧W (a1 u) (u)<W u v∧W (a1 (a1 u)) (a1 (a1 u))<W u v∧a1 u=p3∧a1 (a2 (a1 u))=p5 then a1 (a1 u)
 else if X u v∧W (a1 u) (u)<W u v∧W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v∧a1 u=p3∧a2 (a1 u)=p4∧a1 (a2 (a1 (a1 u)))=p4 then a1 (a1 u)
 else J u v
termination_by W u v
decreasing_by
 ·assumption
 ·assumption
 ·assumption
 ·assumption
 ·assumption
def inst : Magma M:={ op:=op }
def Pre (u v : M) : Prop:=E u v∨Y u v∨L u v∨N u v∨Z u v∨K u v∨V u v∨X u v
def op_free {u v : M} (h : ¬ Pre u v) : op u v=J u v :=by rw[op.eq_1]; simp only[Pre,not_or] at h; simp[h]
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 2) (g 0) (g 1)
 revert this
 change ¬ g 2=op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
 simp (config:={decide:=true}) [op.eq_1,sz,E,Y,L,N,Z,K,V,X]
def R (t : M) : 1≤sz t :=by cases t <;> simp[sz] <;> omega
def G (a b : M) : sz (J a b)=sz a+sz b+1:=rfl
def O {t : M} (h : tg t=2) : sz (a1 t)<sz t :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a1]; have:=R b; omega
def H {t : M} (h : tg t=2) : sz (a2 t)<sz t :=by obtain⟨a,b,rfl⟩:=I _ h; simp[sz,a2]; have:=R a; omega
def msr_lt_both {a b u v : M} (ha : sz a<sz v) (hb : sz b<sz v) : W a b<W u v :=
 msr_lt_of_max_lt (by omega)
/-- the unfolding of `op` with the five nested calls packed away as opaque variables -/
def op_cases (u v : M) : ∃ p1 p2 p3 p4 p5 : M,
  p1=(if hs1 : W (a1 (a2 u)) u<W u v then op (a1 (a2 u)) u else J u v) ∧
  p2=(if hs2 : W u u<W u v then op u u else J u v) ∧
  p3=(if hs3 : W (a1 u) u<W u v then op (a1 u) u else J u v) ∧
  p4=(if hs4 : W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v then op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) else J u v) ∧
  p5=(if hs5 : W (a1 (a1 u)) (a1 (a1 u))<W u v then op (a1 (a1 u)) (a1 (a1 u)) else J u v) ∧
  op u v=(
 if E u v then a1 v
 else if Y u v∧W (a1 (a2 u)) u<W u v∧a1 (a2 (a2 v))=p1 then a1 v
 else if L u v∧W u u<W u v∧a1 (a2 (a2 v))=p2 then a1 v
 else if N u v∧W (a1 (a2 u)) u<W u v∧a2 (a2 v)=p1∧a1 (a2 u)=p1 then a1 v
 else if Z u v∧W (a1 u) u<W u v∧a1 u=p3 then a1 (a1 u)
 else if K u v∧W (a1 u) u<W u v∧W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v∧a1 u=p3∧a1 (a2 (a1 u))=p4 then a1 (a1 u)
 else if V u v∧W (a1 u) u<W u v∧W (a1 (a1 u)) (a1 (a1 u))<W u v∧a1 u=p3∧a1 (a2 (a1 u))=p5 then a1 (a1 u)
 else if X u v∧W (a1 u) u<W u v∧W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u v∧a1 u=p3∧a2 (a1 u)=p4∧a1 (a2 (a1 (a1 u)))=p4 then a1 (a1 u)
 else J u v) :=
 ⟨_,_,_,_,_,rfl,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
/-- one unfold of `op`: free,or bucket B (u=a1 (a2 v),value a1 v),or bucket C (v=u,value a1 (a1 u)) -/
def Q (u v : M) : op u v=J u v ∨
  (tg v=2∧tg (a2 v)=2∧u=a1 (a2 v)∧op u v=a1 v∧(
   (tg (a2 (a2 v))=2∧(
     (tg (a1 (a2 (a2 v)))=2∧u=a2 (a1 (a2 (a2 v)))∧u=a2 (a2 (a2 v))) ∨
     (u=a2 (a2 (a2 v))∧tg u=2∧tg (a2 u)=2∧a1 (a2 (a2 v))=op (a1 (a2 u)) u) ∨
     (u=a2 (a2 (a2 v))∧op u u=a1 (a2 (a2 v))))) ∨
   (tg u=2∧tg (a2 u)=2∧a2 (a2 v)=op (a1 (a2 u)) u∧a1 (a2 u)=op (a1 (a2 u)) u))) ∨
  (v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧op (a1 u) u=a1 u∧op u v=a1 (a1 u)∧(
   (tg (a2 (a1 u))=2∧(
     (tg (a1 (a2 (a1 u)))=2∧a1 (a1 u)=a2 (a1 (a2 (a1 u)))∧a1 (a1 u)=a2 (a2 (a1 u))) ∨
     (a1 (a1 u)=a2 (a2 (a1 u))∧tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2∧a1 (a2 (a1 u))=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))) ∨
     (a1 (a1 u)=a2 (a2 (a1 u))∧op (a1 (a1 u)) (a1 (a1 u))=a1 (a2 (a1 u))))) ∨
   (tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2∧a2 (a1 u)=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))∧a1 (a2 (a1 (a1 u)))=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))))) :=by
 obtain⟨p1,p2,p3,p4,p5,hp1,hp2,hp3,hp4,hp5,hop⟩:=op_cases u v
 rw[hop]
 split
 ·rename_i h
  exact Or.inr (Or.inl ⟨h.1,h.2.1,h.2.2.1,rfl,Or.inl ⟨h.2.2.2.1,Or.inl ⟨h.2.2.2.2.1,h.2.2.2.2.2.1,h.2.2.2.2.2.2⟩⟩⟩)
 ·split
  ·rename_i h1 h
   obtain⟨hP2,hs1,he⟩:=h
   rw[dif_pos hs1] at hp1; subst hp1
   exact Or.inr (Or.inl ⟨hP2.1,hP2.2.1,hP2.2.2.1,rfl,Or.inl ⟨hP2.2.2.2.1,Or.inr (Or.inl ⟨hP2.2.2.2.2.1,hP2.2.2.2.2.2.1,hP2.2.2.2.2.2.2,he⟩)⟩⟩)
  ·split
   ·rename_i h1 h2 h
    obtain⟨hP3,hs2,he⟩:=h
    rw[dif_pos hs2] at hp2; subst hp2
    exact Or.inr (Or.inl ⟨hP3.1,hP3.2.1,hP3.2.2.1,rfl,Or.inl ⟨hP3.2.2.2.1,Or.inr (Or.inr ⟨hP3.2.2.2.2,he.symm⟩)⟩⟩)
   ·split
    ·rename_i h1 h2 h3 h
     obtain⟨hP4,hs1,heA,heB⟩:=h
     rw[dif_pos hs1] at hp1; subst hp1
     exact Or.inr (Or.inl ⟨hP4.1,hP4.2.1,hP4.2.2.1,rfl,Or.inr ⟨hP4.2.2.2.1,hP4.2.2.2.2,heA,heB⟩⟩)
    ·split
     ·rename_i h1 h2 h3 h4 h
      obtain⟨hP5,hs3,he⟩:=h
      rw[dif_pos hs3] at hp3; subst hp3
      exact Or.inr (Or.inr ⟨hP5.1,hP5.2.1,hP5.2.2.1,hP5.2.2.2.1,hP5.2.2.2.2.1,he.symm,rfl,
       Or.inl ⟨hP5.2.2.2.2.2.1,Or.inl ⟨hP5.2.2.2.2.2.2.1,hP5.2.2.2.2.2.2.2.1,hP5.2.2.2.2.2.2.2.2⟩⟩⟩)
     ·split
      ·rename_i h1 h2 h3 h4 h5 h
       obtain⟨hP6,hs3,hs4,heA,heB⟩:=h
       rw[dif_pos hs3] at hp3; subst hp3
       rw[dif_pos hs4] at hp4; subst hp4
       exact Or.inr (Or.inr ⟨hP6.1,hP6.2.1,hP6.2.2.1,hP6.2.2.2.1,hP6.2.2.2.2.1,heA.symm,rfl,
        Or.inl ⟨hP6.2.2.2.2.2.1,Or.inr (Or.inl ⟨hP6.2.2.2.2.2.2.1,hP6.2.2.2.2.2.2.2.1,hP6.2.2.2.2.2.2.2.2,heB⟩)⟩⟩)
      ·split
       ·rename_i h1 h2 h3 h4 h5 h6 h
        obtain⟨hP7,hs3,hs5,heA,heB⟩:=h
        rw[dif_pos hs3] at hp3; subst hp3
        rw[dif_pos hs5] at hp5; subst hp5
        exact Or.inr (Or.inr ⟨hP7.1,hP7.2.1,hP7.2.2.1,hP7.2.2.2.1,hP7.2.2.2.2.1,heA.symm,rfl,
         Or.inl ⟨hP7.2.2.2.2.2.1,Or.inr (Or.inr ⟨hP7.2.2.2.2.2.2,heB.symm⟩)⟩⟩)
       ·split
        ·rename_i h1 h2 h3 h4 h5 h6 h7 h
         obtain⟨hP8,hs3,hs4,heA,heB,heC⟩:=h
         rw[dif_pos hs3] at hp3; subst hp3
         rw[dif_pos hs4] at hp4; subst hp4
         exact Or.inr (Or.inr ⟨hP8.1,hP8.2.1,hP8.2.2.1,hP8.2.2.2.1,hP8.2.2.2.2.1,heA.symm,rfl,
          Or.inr ⟨hP8.2.2.2.2.2.1,hP8.2.2.2.2.2.2,heB,heC⟩⟩)
        ·left; rfl
/-- the size bound: free,or a proper accessor of v,or a proper accessor of u -/
def TR2 (u v : M) : op u v=J u v∨(u=a1 (a2 v)∧tg v=2∧tg (a2 v)=2∧sz (op u v)<sz v) ∨
  (v=u∧tg u=2∧tg (a2 u)=2∧a1 u=a1 (a2 u)∧tg (a1 u)=2∧sz (op u v)<sz u) :=by
 rcases Q u v with h | ⟨h1,h2,h3,h4,-⟩ | ⟨h1,h2,h3,h4,h5,h6,h7,-⟩
 ·exact Or.inl h
 ·refine Or.inr (Or.inl ⟨h3,h1,h2,?_⟩)
  rw[h4]; have:=O h1; omega
 ·refine Or.inr (Or.inr ⟨h1,h2,h3,h4,h5,?_⟩)
  rw[h7]; have:=O h5; have s:=T u; omega
/-- `op y (op (op z y) y)` is always free (regardless of how `op z y` and `op (op z y) y` decode) -/
def Tfree_L3 {z y P0 E : M} (hP0 : op z y=P0) (hP1 : op P0 y=E) :
  op y E=J y E :=by
 have tP:=TR2 P0 y; rw[hP1] at tP
 have tZ:=TR2 z y; rw[hP0] at tZ
 rcases Q y E with h | ⟨h1,h2,h3,-,-⟩ | ⟨hC1,hC2,hC3,hC4,hC5,-,-,-⟩
 ·exact h
 ·exfalso
  rcases tP with hPf | ⟨hP0eq,hty,hta2y,hszP1⟩ | ⟨hP0eq2,htP0,hta2P0,ha1eq,htaP0,hszP1⟩
  ·rw[hPf] at h2 h3
   simp only[a2_J_eq] at h2 h3
   have:=congrArg sz h3; have:=O h2; omega
  ·have:=congrArg sz h3
   have:=H h1; have:=O h2
   omega
  ·rcases tZ with hZf | ⟨-,-,-,hszP0⟩ | ⟨hyz,-,-,-,-,hszP0⟩
   ·rw[← hP0eq2] at hZf
    have:=congrArg sz hZf; simp only[G] at this; omega
   ·have:=congrArg sz hP0eq2; omega
   ·have e1:=congrArg sz hP0eq2; have e2:=congrArg sz hyz; omega
 ·exfalso
  rcases tP with hPf | ⟨-,-,-,hszP1⟩ | ⟨hP0eq2,-,-,-,-,hszP1⟩
  ·rw[hC1] at hPf
   have:=congrArg sz hPf; simp only[G] at this; omega
  ·have:=congrArg sz hC1; omega
  ·have e1:=congrArg sz hC1; have e2:=congrArg sz hP0eq2; omega
def noFix (a b : M) : op a b≠b :=by
 intro he
 rcases TR2 a b with h | ⟨-,-,-,hs⟩ | ⟨hv,-,-,-,-,hs⟩
 ·rw[h] at he; have:=congrArg sz he; simp only[G] at this; have:=R a; omega
 ·rw[he] at hs; omega
 ·rw[he] at hs; have:=congrArg sz hv; omega
/-- the second chain product is free,or the whole chain collapses onto `a1 y` -/
def Wdig (z y : M) : op (op z y) y=J (op z y) y ∨
  (tg y=2∧tg (a2 y)=2∧a1 y=a1 (a2 y)∧op z y=a1 y∧op (op z y) y=a1 y) :=by
 rcases Q (op z y) y with h | ⟨h1,h2,h3,h4,-⟩ | ⟨h1,-,-,-,-,-,-,-⟩
 ·exact Or.inl h
 ·rcases Q z y with g | ⟨-,-,-,g4,-⟩ | ⟨g1,-,-,g4,g5,-,g7,-⟩
  ·exfalso
   rw[g] at h3
   have e1:=congrArg sz h3
   simp only[G] at e1
   have:=T (a2 y); have:=D y; have:=R z; omega
  ·exact Or.inr ⟨h1,h2,g4.symm.trans h3,g4,h4⟩
  ·exfalso
   rw[← g1] at g4 g5 g7 h3
   have e1 : a1 (a1 y)=a1 (a2 y):=g7.symm.trans h3
   rw[← g4] at e1
   have:=O g5
   have:=congrArg sz e1
   omega
 ·exact absurd h1.symm (noFix z y)
/-- one of the four `a1 v` branches fires -/
def U {u v w : M} (hw : a1 v=w) (h : E u v ∨
  (Y u v∧W (a1 (a2 u)) u<W u v∧a1 (a2 (a2 v))=op (a1 (a2 u)) u) ∨
  (L u v∧W u u<W u v∧a1 (a2 (a2 v))=op u u) ∨
  (N u v∧W (a1 (a2 u)) u<W u v∧a2 (a2 v)=op (a1 (a2 u)) u ∧
   a1 (a2 u)=op (a1 (a2 u)) u)) : op u v=w :=by
 obtain⟨p1,p2,p3,p4,p5,hp1,hp2,hp3,hp4,hp5,hop⟩:=op_cases u v
 rw[hop]
 split
 ·exact hw
 split
 ·exact hw
 split
 ·exact hw
 split
 ·exact hw
 exfalso
 rename_i n1 n2 n3 n4
 rcases h with c | c | c | c
 ·exact n1 c
 ·rw[dif_pos c.2.1] at hp1
  exact n2 ⟨c.1,c.2.1,by rw[hp1]; exact c.2.2⟩
 ·rw[dif_pos c.2.1] at hp2
  exact n3 ⟨c.1,c.2.1,by rw[hp2]; exact c.2.2⟩
 ·rw[dif_pos c.2.1] at hp1
  exact n4 ⟨c.1,c.2.1,by rw[hp1]; exact c.2.2.1,by rw[hp1]; exact c.2.2.2⟩
/-- the diagonal pair: one of the four `a1 (a1 u)` branches fires -/
def opC {u w : M} (hw : a1 (a1 u)=w) (h1 : tg u=2) (h2 : tg (a2 u)=2)
  (h3 : a1 u=a1 (a2 u)) (h4 : tg (a1 u)=2) (h5 : op (a1 u) u=a1 u)
  (h6 : (tg (a2 (a1 u))=2∧(
     (tg (a1 (a2 (a1 u)))=2∧a1 (a1 u)=a2 (a1 (a2 (a1 u)))∧a1 (a1 u)=a2 (a2 (a1 u))) ∨
     (a1 (a1 u)=a2 (a2 (a1 u))∧tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2 ∧
      a1 (a2 (a1 u))=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))) ∨
     (a1 (a1 u)=a2 (a2 (a1 u))∧op (a1 (a1 u)) (a1 (a1 u))=a1 (a2 (a1 u))))) ∨
   (tg (a1 (a1 u))=2∧tg (a2 (a1 (a1 u)))=2 ∧
     a2 (a1 u)=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)) ∧
     a1 (a2 (a1 (a1 u)))=op (a1 (a2 (a1 (a1 u)))) (a1 (a1 u)))) : op u u=w :=by
 have hne : ¬ (u=a1 (a2 u)) :=by rw[← h3]; intro he; have:=O h1; have:=congrArg sz he; omega
 have g3 : W (a1 u) u<W u u :=
  msr_lt_of_max_eq (by have:=T u; omega) (by have:=O h1; omega)
 have s1:=O h1
 have s2:=T (a1 u)
 have s3:=T (a2 (a1 (a1 u)))
 have s4:=D (a1 (a1 u))
 have g4 : W (a1 (a2 (a1 (a1 u)))) (a1 (a1 u))<W u u :=
  msr_lt_both (by omega) (by omega)
 have g5 : W (a1 (a1 u)) (a1 (a1 u))<W u u:=msr_lt_both (by omega) (by omega)
 obtain⟨p1,p2,p3,p4,p5,hp1,hp2,hp3,hp4,hp5,hop⟩:=op_cases u u
 rw[dif_pos g3] at hp3
 rw[dif_pos g4] at hp4
 rw[dif_pos g5] at hp5
 rw[hop]
 split
 ·rename_i c; exact absurd c.2.2.1 hne
 split
 ·rename_i c; exact absurd c.1.2.2.1 hne
 split
 ·rename_i c; exact absurd c.1.2.2.1 hne
 split
 ·rename_i c; exact absurd c.1.2.2.1 hne
 split
 ·exact hw
 split
 ·exact hw
 split
 ·exact hw
 split
 ·exact hw
 exfalso
 rename_i n5 n6 n7 n8
 rcases h6 with⟨ha,hb | hb | hb⟩ | hb
 ·exact n5 ⟨⟨rfl,h1,h2,h3,h4,ha,hb.1,hb.2.1,hb.2.2⟩,g3,by rw[hp3]; exact h5.symm⟩
 ·exact n6 ⟨⟨rfl,h1,h2,h3,h4,ha,hb.1,hb.2.1,hb.2.2.1⟩,g3,g4,
   by rw[hp3]; exact h5.symm,by rw[hp4]; exact hb.2.2.2⟩
 ·exact n7 ⟨⟨rfl,h1,h2,h3,h4,ha,hb.1⟩,g3,g5,
   by rw[hp3]; exact h5.symm,by rw[hp5]; exact hb.2.symm⟩
 ·exact n8 ⟨⟨rfl,h1,h2,h3,h4,hb.1,hb.2.1⟩,g3,g4,
   by rw[hp3]; exact h5.symm,by rw[hp4]; exact hb.2.2.1,by rw[hp4]; exact hb.2.2.2⟩
/-- the gate of a nested call whose arguments are bounded by `b`,against `(b,J x (J b t))` -/
def gL {a b x t : M} (h : sz a≤sz b) : W a b<W b (J x (J b t)) :=
 msr_lt_both (by simp only[G]; have:=R x; have:=R t; omega)
  (by simp only[G]; have:=R x; have:=R t; omega)
def main (x y z : M) : op y (op x (J y (op (op z y) y)))=x :=by
 rcases Q x (J y (op (op z y) y)) with hE | ⟨-,hEt,hEx,hEv,hEs⟩ |
  ⟨hC1,-,hC3,hC4,-,-,-,-⟩
 ·rw[hE]
  rcases Wdig z y with hW | ⟨hy1,hy2,hy3,hZ,hWv⟩
  ·rw[hW]
   rcases Q z y with hz | ⟨hz1,hz2,hz3,-,-⟩ | ⟨hz1,-,-,-,-,-,-,-⟩
   ·rw[hz]
    exact U rfl (Or.inl ⟨rfl,rfl,rfl,rfl,rfl,rfl,rfl⟩)
   ·exact U rfl (Or.inr (Or.inl ⟨⟨rfl,rfl,rfl,rfl,rfl,hz1,hz2⟩,
     gL (by have:=T (a2 y); have:=D y; omega),
     by simp only[a1_J_eq,a2_J_eq]; rw[← hz3]⟩))
   ·rw[← hz1]
    exact U rfl (Or.inr (Or.inr (Or.inl ⟨⟨rfl,rfl,rfl,rfl,rfl⟩,gL (Nat.le_refl _),
     by simp only[a1_J_eq,a2_J_eq]⟩)))
  ·have h5 : op (a1 y) y=a1 y :=by rw[← hZ]; exact hWv.trans hZ.symm
   rw[hWv]
   exact U rfl (Or.inr (Or.inr (Or.inr ⟨⟨rfl,rfl,rfl,hy1,hy2⟩,
    gL (by have:=T (a2 y); have:=D y; omega),
    by simp only[a2_J_eq]; rw[← hy3]; exact h5.symm,
    by rw[← hy3]; exact h5.symm⟩)))
 ·simp only[a1_J_eq,a2_J_eq] at hEt hEx hEv hEs
  rw[hEv]
  rcases Wdig z y with hW | ⟨hy1,hy2,hy3,hZ,hWv⟩
  ·rw[hW] at hEt hEx hEs
   simp only[a1_J_eq,a2_J_eq] at hEt hEx hEs
   rcases Q z y with hz | ⟨hz1,-,-,hz4,-⟩ | ⟨hz1,-,-,-,-,-,-,-⟩
   ·exfalso
    rw[hz] at hEx
    subst hEx
    simp only[a1_J_eq,a2_J_eq] at hEs
    rcases hEs with⟨ht,⟨-,-,h⟩ | ⟨h,-,-,-⟩ | ⟨h,-⟩⟩ | ⟨-,hb2,hb3,hb4⟩
    ·have:=congrArg sz h; simp only[G] at this
     have:=H ht; have:=R z; omega
    ·have:=congrArg sz h; simp only[G] at this
     have:=H ht; have:=R z; omega
    ·have:=congrArg sz h; simp only[G] at this
     have:=H ht; have:=R z; omega
    ·have hy : y=a1 (a2 (J z y)):=hb3.trans hb4.symm
     simp only[a1_J_eq,a2_J_eq] at hy hb2
     have:=O hb2; have:=congrArg sz hy; omega
   ·exfalso
    rw[hz4] at hEx
    subst hEx
    rcases hEs with⟨-,⟨h1,h2,-⟩ | ⟨-,-,-,h4⟩ | ⟨-,h2⟩⟩ | ⟨hb1,-,hb3,hb4⟩
    ·have:=H h1; have:=congrArg sz h2; omega
    ·exact noFix _ _ h4.symm
    ·exact noFix _ _ h2
    ·have hy : y=a1 (a2 (a1 y)):=hb3.trans hb4.symm
     have:=T (a2 (a1 y)); have:=H hb1; have:=O hz1
     have:=congrArg sz hy; omega
   ·rw[← hz1] at hEx
    exact hEx.symm
  ·rw[hWv] at hEt hEx hEs
   subst hEx
   have h5 : op (a1 y) y=a1 y :=by rw[← hZ]; exact hWv.trans hZ.symm
   exact opC rfl hy1 hy2 hy3 hEt h5 hEs
 ·exfalso
  subst hC1
  simp only[a1_J_eq,a2_J_eq] at hC3 hC4
  rcases Wdig z y with hW | ⟨hy1,-,-,-,hWv⟩
  ·rw[hW] at hC4
   simp only[a1_J_eq] at hC4
   exact noFix z y hC4.symm
  ·rw[hWv] at hC3 hC4
   have:=O hy1; have:=O hC3; have:=congrArg sz hC4; omega
/-- THE LAW: x=y*(x*(y*((z*y)*y))) -/
def law (x y z : M) : op (y) (op (x) (op (y) (op (op (z) (y)) (y))))=x :=by
 have h1 : op y (op (op z y) y)=J y (op (op z y) y):=Tfree_L3 rfl rfl
 rw[h1]
 exact main x y z
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))