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
def sz_a1 (u : M) : sz (a1 u)≤sz u :=by cases u <;> simp[a1,sz] <;> omega
def E (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def Z (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def tg_g (t : M) (h : tg t≠2) : ∃ n,t=M.g n :=by cases t <;> simp_all[tg]
def sz_tg (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=Z _ h; simp[sz,a1,a2]
def tg_of_sz (t : M) (h : 1<sz t) : tg t=2 :=by cases t <;> simp_all[tg,sz]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem a1_J_eq (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem a2_J_eq (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
@[simp] theorem sz_J (b0 b1 : M) : sz (M.J b0 b1)=sz b0+sz b1+1:=rfl
/-- the recursion measure: lexicographic (max size,total size),packed into one Nat -/
def T (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def msr_lt_of_max_lt {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : T a b<T u v :=by
 unfold T
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
/-- the encoder of an encoding `t=J B C`: the free half is the big one (`u=B.2` if B is free,else `u=C.2`) -/
def W (t : M) : M:=if sz (a1 t)<sz (a2 (a2 t)) then a2 (a2 t) else a2 (a1 t)
def D (t : M) : sz (W t)≤sz t :=by unfold W; have:=E (a2 t); have:=E t; have:=E (a1 t); have:=sz_a1 t; split <;> omega
def sz_oc_lt (t : M) (h : tg t=2) : sz (W t)<sz t :=by
 obtain⟨a,b,rfl⟩:=Z _ h
 have:=E b; have:=E a
 unfold W; split <;> simp only[a1_J_eq,a2_J_eq,sz_J] <;> omega
def Y (u v : M) : Prop:=tg v=2∧tg (a1 v)=2∧tg (a1 (a1 v))=2∧u=a2 (a1 v)∧tg (a2 v)=2∧a2 (a1 (a1 v))=a1 (a2 v)∧u=a2 (a2 v)
instance (u v : M) : Decidable (Y u v) :=by unfold Y; infer_instance
def O (u v : M) : Prop:=tg v=2∧tg (a1 v)=2∧tg (a1 (a1 v))=2∧u=a2 (a1 v)
instance (u v : M) : Decidable (O u v) :=by unfold O; infer_instance
def X (u v : M) : Prop:=tg v=2∧tg (a1 v)=2∧u=a2 (a1 v)∧tg (a2 v)=2∧u=a2 (a2 v)
instance (u v : M) : Decidable (X u v) :=by unfold X; infer_instance
def L (u v : M) : Prop:=tg v=2∧tg (a1 v)=2∧u=a2 (a1 v)∧tg u=2
instance (u v : M) : Decidable (L u v) :=by unfold L; infer_instance
def N (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a2 (a2 v)∧tg u=2∧tg (W u)=2∧a1 (a2 v)=a2 (W u)
instance (u v : M) : Decidable (N u v) :=by unfold N; infer_instance
def V (u v : M) : Prop:=tg v=2∧tg (a2 v)=2∧u=a2 (a2 v)∧tg u=2
instance (u v : M) : Decidable (V u v) :=by unfold V; infer_instance
/-- op u v=x  iff  v=((z*x)*u)*(x*u) evaluated in the model,for some z; the six rules are the
  six combinations of free/decoded inner products (both B and C decoded is impossible); nested products are
  recomputed,the encoder of a decoded product is recovered by `W`. -/
def op (u v : M) : M :=
 let p1:=if hs1 : T (a2 (a1 (a1 v))) u<T u v then op (a2 (a1 (a1 v))) u else J u v
 let p2:=if hs2 : T (W (a1 (a2 v))) (a1 (a2 v))<T u v then op (W (a1 (a2 v))) (a1 (a2 v)) else J u v
 let p3:=if hs3 : T (W u) u<T u v then op (W u) u else J u v
 let p4:=if hs4 : T (W (W u)) (W u)<T u v then op (W (W u)) (W u) else J u v
 if Y u v then a2 (a1 (a1 v))
 else if O u v∧T (a2 (a1 (a1 v))) u<T u v∧a2 v=p1 then a2 (a1 (a1 v))
 else if X u v∧T (W (a1 (a2 v))) (a1 (a2 v))<T u v∧a1 (a1 v)=p2 then a1 (a2 v)
 else if L u v∧T (W u) u<T u v∧T (W (W u)) (W u)<T u v∧a2 v=p3∧a1 (a1 v)=p4 then W u
 else if N u v∧T (W u) u<T u v∧a1 v=p3 then a1 (a2 v)
 else if V u v∧T (W u) u<T u v∧T (W (a1 (a2 v))) (a1 (a2 v))<T u v∧a1 v=p3∧W u=p2 then a1 (a2 v)
 else J u v
termination_by T u v
decreasing_by all_goals assumption
def inst : Magma M:={ op:=op }
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 2) (g 0) (g 1)
 revert this
 change ¬ g 2=op (op (g 0) (op (g 1) (g 0))) (op (op (g 2) (g 2)) (g 0))
 simp (config:={decide:=true}) [op.eq_1,sz,W,Y,O,X,L,N,V]
/-- the unfolding of `op` with the four nested calls packed away as opaque variables -/
def G (u v : M) : ∃ p1 p2 p3 p4 : M,
  p1=(if hs1 : T (a2 (a1 (a1 v))) u<T u v then op (a2 (a1 (a1 v))) u else J u v) ∧
  p2=(if hs2 : T (W (a1 (a2 v))) (a1 (a2 v))<T u v then op (W (a1 (a2 v))) (a1 (a2 v)) else J u v) ∧
  p3=(if hs3 : T (W u) u<T u v then op (W u) u else J u v) ∧
  p4=(if hs4 : T (W (W u)) (W u)<T u v then op (W (W u)) (W u) else J u v) ∧
  op u v=(
 if Y u v then a2 (a1 (a1 v))
 else if O u v∧T (a2 (a1 (a1 v))) u<T u v∧a2 v=p1 then a2 (a1 (a1 v))
 else if X u v∧T (W (a1 (a2 v))) (a1 (a2 v))<T u v∧a1 (a1 v)=p2 then a1 (a2 v)
 else if L u v∧T (W u) u<T u v∧T (W (W u)) (W u)<T u v∧a2 v=p3∧a1 (a1 v)=p4 then W u
 else if N u v∧T (W u) u<T u v∧a1 v=p3 then a1 (a2 v)
 else if V u v∧T (W u) u<T u v∧T (W (a1 (a2 v))) (a1 (a2 v))<T u v∧a1 v=p3∧W u=p2 then a1 (a2 v)
 else J u v) :=
 ⟨_,_,_,_,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
/-- one unfold of `op`: free,or one of the six rules with its recomputed guards -/
def K (u v : M) : op u v=J u v ∨
  (Y u v∧op u v=a2 (a1 (a1 v))) ∨
  (O u v∧a2 v=op (a2 (a1 (a1 v))) u∧op u v=a2 (a1 (a1 v))) ∨
  (X u v∧a1 (a1 v)=op (W (a1 (a2 v))) (a1 (a2 v))∧op u v=a1 (a2 v)) ∨
  (L u v∧a2 v=op (W u) u∧a1 (a1 v)=op (W (W u)) (W u)∧op u v=W u) ∨
  (N u v∧a1 v=op (W u) u∧op u v=a1 (a2 v)) ∨
  (V u v∧a1 v=op (W u) u∧W u=op (W (a1 (a2 v))) (a1 (a2 v))∧op u v=a1 (a2 v)) :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u v
 rw[hop]
 split
 ·rename_i h; exact Or.inr (Or.inl ⟨h,rfl⟩)
 ·split
  ·rename_i h1 h
   obtain⟨h2,hs1,he⟩:=h
   rw[dif_pos hs1] at hp1; subst hp1
   exact Or.inr (Or.inr (Or.inl ⟨h2,he,rfl⟩))
  ·split
   ·rename_i h1 h2 h
    obtain⟨h3,hs2,he⟩:=h
    rw[dif_pos hs2] at hp2; subst hp2
    exact Or.inr (Or.inr (Or.inr (Or.inl ⟨h3,he,rfl⟩)))
   ·split
    ·rename_i h1 h2 h3 h
     obtain⟨h4,hs3,hs4,he1,he2⟩:=h
     rw[dif_pos hs3] at hp3; subst hp3
     rw[dif_pos hs4] at hp4; subst hp4
     exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h4,he1,he2,rfl⟩))))
    ·split
     ·rename_i h1 h2 h3 h4 h
      obtain⟨h5,hs3,he⟩:=h
      rw[dif_pos hs3] at hp3; subst hp3
      exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨h5,he,rfl⟩)))))
     ·split
      ·rename_i h1 h2 h3 h4 h5 h
       obtain⟨h6,hs3,hs2,he1,he2⟩:=h
       rw[dif_pos hs3] at hp3; subst hp3
       rw[dif_pos hs2] at hp2; subst hp2
       exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr (Or.inr ⟨h6,he1,he2,rfl⟩)))))
      ·left; rfl
/-- shapes -/
def P1_ex {u v : M} (h : Y u v) : ∃ z x,v=J (J (J z x) u) (J x u) :=by
 obtain⟨h1,h2,h3,h4,h5,h6,h7⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 obtain⟨d0,d1,rfl⟩:=Z _ h3
 obtain⟨e0,e1,rfl⟩:=Z _ h5
 simp only[a1_J_eq,a2_J_eq] at h4 h6 h7
 subst h4 h6 h7; exact⟨d0,d1,rfl⟩
def P2_ex {u v : M} (h : O u v) : ∃ z x C,v=J (J (J z x) u) C :=by
 obtain⟨h1,h2,h3,h4⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 obtain⟨d0,d1,rfl⟩:=Z _ h3
 simp only[a1_J_eq,a2_J_eq] at h4
 subst h4; exact⟨d0,d1,b1,rfl⟩
def P3_ex {u v : M} (h : X u v) : ∃ A x,v=J (J A u) (J x u) :=by
 obtain⟨h1,h2,h3,h4,h5⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 obtain⟨e0,e1,rfl⟩:=Z _ h4
 simp only[a1_J_eq,a2_J_eq] at h3 h5
 subst h3 h5; exact⟨c0,e0,rfl⟩
def P4_ex {u v : M} (h : L u v) : tg u=2∧∃ A C,v=J (J A u) C :=by
 obtain⟨h1,h2,h3,h4⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 simp only[a1_J_eq,a2_J_eq] at h3
 subst h3; exact⟨h4,c0,b1,rfl⟩
def P5_ex {u v : M} (h : N u v) : tg u=2∧tg (W u)=2∧∃ B x,v=J B (J x u)∧x=a2 (W u) :=by
 obtain⟨h1,h2,h3,h4,h5,h6⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 simp only[a1_J_eq,a2_J_eq] at h3 h6
 subst h3; exact⟨h4,h5,b0,c0,rfl,h6⟩
def P6_ex {u v : M} (h : V u v) : tg u=2∧∃ B x,v=J B (J x u) :=by
 obtain⟨h1,h2,h3,h4⟩:=h
 obtain⟨b0,b1,rfl⟩:=Z _ h1
 obtain⟨c0,c1,rfl⟩:=Z _ h2
 simp only[a1_J_eq,a2_J_eq] at h3
 subst h3; exact⟨h4,b0,c0,rfl⟩
/-- a decoded product: the encoder and the result are strictly smaller than the encoding -/
def R (u v : M) : op u v=J u v∨(tg v=2∧sz u<sz v∧sz (op u v)<sz v) :=by
 rcases K u v with h | ⟨h1,h⟩ | ⟨h1,-,h⟩ | ⟨h1,-,h⟩ | ⟨h1,-,-,h⟩ | ⟨h1,-,h⟩ | ⟨h1,-,-,h⟩
 ·exact Or.inl h
 ·obtain⟨z,x,rfl⟩:=P1_ex h1; right; rw[h]; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
 ·obtain⟨z,x,C,rfl⟩:=P2_ex h1; right; rw[h]; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
 ·obtain⟨A,x,rfl⟩:=P3_ex h1; right; rw[h]; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
 ·obtain⟨hu,A,C,rfl⟩:=P4_ex h1; right; rw[h]; have:=sz_oc_lt u hu; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
 ·obtain⟨hu,-,B,x,rfl,-⟩:=P5_ex h1; right; rw[h]; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
 ·obtain⟨hu,B,x,rfl⟩:=P6_ex h1; right; rw[h]; simp only[a1_J_eq,a2_J_eq,sz_J]; exact⟨rfl,by omega,by omega⟩
def sz_op_le (u v : M) : sz (op u v)≤sz u+sz v+1 :=by
 rcases R u v with h | ⟨-,-,h⟩
 ·rw[h]; simp only[sz_J]; omega
 ·omega
/-- the encoder of a decoded product is `W` of the encoding -/
def H (u v : M) : op u v=J u v∨(tg v=2∧sz u<sz v∧sz (op u v)<sz v∧u=W v) :=by
 rcases R u v with h | ⟨htv,hsu,hsr⟩
 ·exact Or.inl h
 right; refine⟨htv,hsu,hsr,?_⟩
 rcases K u v with h | ⟨h1,-⟩ | ⟨h1,he,-⟩ | ⟨h1,-⟩ | ⟨h1,he,-,-⟩ | ⟨h1,he,-⟩ | ⟨h1,he,-,-⟩
 ·rw[h] at hsr; simp only[sz_J] at hsr; omega
 ·obtain⟨z,x,rfl⟩:=P1_ex h1; unfold W; split <;> rfl
 ·obtain⟨z,x,C,rfl⟩:=P2_ex h1; simp only[a1_J_eq,a2_J_eq] at he
  unfold W; split
  ·rename_i hh; exfalso; simp only[a1_J_eq,a2_J_eq,sz_J] at hh
   rcases R x u with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; subst he; simp only[a2_J_eq] at hh; omega
   ·rw[← he] at h'; have:=E C; omega
  ·rfl
 ·obtain⟨A,x,rfl⟩:=P3_ex h1; unfold W; split <;> rfl
 ·obtain⟨hu,A,C,rfl⟩:=P4_ex h1; simp only[a1_J_eq,a2_J_eq] at he
  unfold W; split
  ·rename_i hh; exfalso; simp only[a1_J_eq,a2_J_eq,sz_J] at hh
   rcases R (W u) u with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; subst he; simp only[a2_J_eq] at hh; omega
   ·rw[← he] at h'; have:=E C; omega
  ·rfl
 ·obtain⟨hu,-,B,x,rfl,-⟩:=P5_ex h1; simp only[a1_J_eq,a2_J_eq] at he
  unfold W; split
  ·rfl
  ·rename_i hh; simp only[a1_J_eq,a2_J_eq,sz_J] at hh
   rcases R (W u) u with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; subst he; rfl
   ·rw[← he] at h'; omega
 ·obtain⟨hu,B,x,rfl⟩:=P6_ex h1; simp only[a1_J_eq,a2_J_eq] at he
  unfold W; split
  ·rfl
  ·rename_i hh; simp only[a1_J_eq,a2_J_eq,sz_J] at hh
   rcases R (W u) u with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; subst he; rfl
   ·rw[← he] at h'; omega
def Q {a b u v : M} (ha : sz a<sz v) (hb : sz b<sz v) : T a b<T u v :=
 msr_lt_of_max_lt (by omega)
/-- rule lemmas: each rule fires on its own shape (earlier rules refuted by size) -/
def op_R1 (u z x : M) : op u (J (J (J z x) u) (J x u))=x :=by
 obtain⟨p1,p2,p3,p4,-,-,-,-,hop⟩:=G u (J (J (J z x) u) (J x u))
 have h1 : Y u (J (J (J z x) u) (J x u)):=⟨rfl,rfl,rfl,rfl,rfl,rfl,rfl⟩
 rw[hop,if_pos h1]; rfl
def op_R2 (u z x C : M) (hC : C=op x u) (hs : sz C<sz u) : op u (J (J (J z x) u) C)=x :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u (J (J (J z x) u) C)
 have g1 : T (a2 (a1 (a1 (J (J (J z x) u) C)))) u<T u (J (J (J z x) u) C) :=
  Q (by simp only[a1_J_eq,a2_J_eq,sz_J]; omega) (by simp only[sz_J]; omega)
 rw[dif_pos g1] at hp1; subst hp1
 rw[hop]
 split
 ·rename_i h; exfalso; obtain⟨-,-,-,-,-,-,h7⟩:=h; simp only[a2_J_eq] at h7
  have:=E C; rw[← h7] at this; omega
 ·split
  ·rfl
  ·rename_i h1 h; exfalso; apply h; exact⟨⟨rfl,rfl,rfl,rfl⟩,g1,by simp only[a1_J_eq,a2_J_eq]; exact hC⟩
def op_R3 (u A x : M) (hA : A=op (W x) x) (hs : sz A<sz x) : op u (J (J A u) (J x u))=x :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u (J (J A u) (J x u))
 have g2 : T (W (a1 (a2 (J (J A u) (J x u))))) (a1 (a2 (J (J A u) (J x u))))<T u (J (J A u) (J x u)) :=
  Q (by simp only[a1_J_eq,a2_J_eq,sz_J]; have:=D x; omega) (by simp only[a1_J_eq,a2_J_eq,sz_J]; omega)
 have g1 : T (a2 (a1 (a1 (J (J A u) (J x u))))) u<T u (J (J A u) (J x u)) :=
  Q (by simp only[a1_J_eq,a2_J_eq,sz_J]; have:=E A; omega) (by simp only[sz_J]; omega)
 rw[dif_pos g1] at hp1; subst hp1
 rw[dif_pos g2] at hp2; subst hp2
 rw[hop]
 split
 ·rename_i h; exfalso; obtain⟨-,-,-,-,-,h6,-⟩:=h; simp only[a1_J_eq,a2_J_eq] at h6
  have:=E A; rw[h6] at this; omega
 ·split
  ·rename_i h1 h; exfalso; obtain⟨-,-,he⟩:=h; simp only[a1_J_eq,a2_J_eq] at he
   rcases R (a2 A) u with h' | ⟨-,-,h'⟩
   ·rw[h'] at he; injection he with he1 he2; have:=E A; rw[← he1] at this; omega
   ·rw[← he] at h'; simp only[sz_J] at h'; omega
  ·split
   ·rfl
   ·rename_i h1 h2 h; exfalso; apply h; exact⟨⟨rfl,rfl,rfl,rfl,rfl⟩,g2,by simp only[a1_J_eq,a2_J_eq]; exact hA⟩
def op_R4 (u A x C : M) (hu : tg u=2) (hx : x=W u) (hC : C=op x u) (hsC : sz C<sz u)
  (hA : A=op (W x) x) (hsA : sz A<sz x) : op u (J (J A u) C)=x :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u (J (J A u) C)
 have hxu : sz x<sz u :=by rw[hx]; exact sz_oc_lt u hu
 have g3 : T (W u) u<T u (J (J A u) C):=Q (by rw[← hx]; simp only[sz_J]; omega) (by simp only[sz_J]; omega)
 have g4 : T (W (W u)) (W u)<T u (J (J A u) C) :=
  Q (by rw[← hx]; have:=D x; simp only[sz_J]; omega) (by rw[← hx]; simp only[sz_J]; omega)
 have g1 : T (a2 (a1 (a1 (J (J A u) C)))) u<T u (J (J A u) C) :=
  Q (by simp only[a1_J_eq,a2_J_eq,sz_J]; have:=E A; omega) (by simp only[sz_J]; omega)
 rw[dif_pos g1] at hp1; subst hp1
 rw[dif_pos g3] at hp3; subst hp3
 rw[dif_pos g4] at hp4; subst hp4
 rw[hop]
 split
 ·rename_i h; exfalso; obtain⟨-,-,-,-,-,-,h7⟩:=h; simp only[a2_J_eq] at h7
  have:=E C; rw[← h7] at this; omega
 ·split
  ·rename_i h1 h; exfalso; obtain⟨-,-,he⟩:=h; simp only[a1_J_eq,a2_J_eq] at he
   rcases H (a2 A) u with h' | ⟨-,-,-,h'⟩
   ·rw[h'] at he; rw[he] at hsC; simp only[sz_J] at hsC; omega
   ·rw[← hx] at h'; have:=E A; rw[h'] at this; omega
  ·split
   ·rename_i h1 h2 h; exfalso; obtain⟨⟨-,-,-,-,h5⟩,-⟩:=h; simp only[a2_J_eq] at h5
    have:=E C; rw[← h5] at this; omega
   ·split
    ·rw[hx]
    ·rename_i h1 h2 h3 h; exfalso; apply h
     exact⟨⟨rfl,rfl,rfl,hu⟩,g3,g4,by simp only[a2_J_eq]; rw[hC,hx],by simp only[a1_J_eq]; rw[hA,hx]⟩
def op_R5 (u B z x : M) (hu : tg u=2) (hoc : W u=J z x) (hB : B=op (W u) u) (hs : sz B<sz u) :
  op u (J B (J x u))=x :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u (J B (J x u))
 have g3 : T (W u) u<T u (J B (J x u)):=Q (by have:=D u; simp only[sz_J]; omega) (by simp only[sz_J]; omega)
 rw[dif_pos g3] at hp3; subst hp3
 have nB : ¬ (tg (a1 (J B (J x u)))=2∧u=a2 (a1 (J B (J x u)))) :=by intro hh; obtain⟨-,h⟩:=hh; simp only[a1_J_eq] at h; have:=E B; rw[← h] at this; omega
 rw[hop]
 split
 ·rename_i h; exact absurd ⟨h.2.1,h.2.2.2.1⟩ nB
 ·split
  ·rename_i h1 h; exact absurd ⟨h.1.2.1,h.1.2.2.2⟩ nB
  ·split
   ·rename_i h1 h2 h; exact absurd ⟨h.1.2.1,h.1.2.2.1⟩ nB
   ·split
    ·rename_i h1 h2 h3 h; exact absurd ⟨h.1.2.1,h.1.2.2.1⟩ nB
    ·split
     ·rfl
     ·rename_i h1 h2 h3 h4 h; exfalso; apply h
      exact⟨⟨rfl,rfl,rfl,hu,by simp[hoc],by simp[hoc]⟩,g3,by simp only[a1_J_eq]; exact hB⟩
def op_R6 (u B A x : M) (hu : tg u=2) (hoc : W u=A) (hB : B=op A u) (hs : sz B<sz u)
  (hA : A=op (W x) x) (hsA : sz A<sz x) : op u (J B (J x u))=x :=by
 obtain⟨p1,p2,p3,p4,hp1,hp2,hp3,hp4,hop⟩:=G u (J B (J x u))
 have g3 : T (W u) u<T u (J B (J x u)):=Q (by have:=D u; simp only[sz_J]; omega) (by simp only[sz_J]; omega)
 have g2 : T (W (a1 (a2 (J B (J x u))))) (a1 (a2 (J B (J x u))))<T u (J B (J x u)) :=
  Q (by simp only[a1_J_eq,a2_J_eq,sz_J]; have:=D x; omega) (by simp only[a1_J_eq,a2_J_eq,sz_J]; omega)
 rw[dif_pos g3] at hp3; subst hp3
 rw[dif_pos g2] at hp2; subst hp2
 have nB : ¬ (tg (a1 (J B (J x u)))=2∧u=a2 (a1 (J B (J x u)))) :=by intro hh; obtain⟨-,h⟩:=hh; simp only[a1_J_eq] at h; have:=E B; rw[← h] at this; omega
 rw[hop]
 split
 ·rename_i h; exact absurd ⟨h.2.1,h.2.2.2.1⟩ nB
 ·split
  ·rename_i h1 h; exact absurd ⟨h.1.2.1,h.1.2.2.2⟩ nB
  ·split
   ·rename_i h1 h2 h; exact absurd ⟨h.1.2.1,h.1.2.2.1⟩ nB
   ·split
    ·rename_i h1 h2 h3 h; exact absurd ⟨h.1.2.1,h.1.2.2.1⟩ nB
    ·split
     ·rename_i h1 h2 h3 h4 h; exfalso; obtain⟨⟨-,-,-,-,-,h6⟩,-⟩:=h
      simp only[a1_J_eq,a2_J_eq] at h6; rw[hoc] at h6; have:=E A; rw[← h6] at this; omega
     ·split
      ·rfl
      ·rename_i h1 h2 h3 h4 h5 h; exfalso; apply h
       exact⟨⟨rfl,rfl,rfl,hu⟩,g3,g2,by simp only[a1_J_eq]; rw[hB,hoc],by simp only[a1_J_eq,a2_J_eq]; rw[hoc,hA]⟩
def sz_pos (t : M) : 1≤sz t :=by cases t <;> simp[sz] <;> omega
def I (x z : M) : op z x≠x :=by
 intro h
 rcases R z x with hf | ⟨-,-,hsr⟩
 ·rw[hf] at h
  have:=congrArg sz h; simp only[sz_J] at this; have:=sz_pos z; omega
 ·rw[h] at hsr; omega
def op_self (t : M) : op t t=J t t :=by
 rcases R t t with h | ⟨-,hlt,-⟩
 ·exact h
 ·omega
def no_core_CD (x y z t : M) (hBf : op (op z x) y=J (op z x) y)
  (hBeq : op (op z x) y=t) (ht : sz t≤sz (op x y))
  (hCty : tg y=2) (hCsx : sz x<sz y) (hCsC : sz (op x y)<sz y) : False :=by
 have hBsize : sz y+2≤sz (op (op z x) y) :=by rw[hBf]; simp only[sz_J]; have:=sz_pos (op z x); omega
 rw[hBeq] at hBsize
 omega
def U (x y z : M) (hBf : op (op z x) y=J (op z x) y)
  (hEq : op (op z x) y=a2 (a2 (op x y))) : False :=by
 have hBsize : sz y+2≤sz (op (op z x) y) :=by rw[hBf]; simp only[sz_J]; have:=sz_pos (op z x); omega
 rw[hEq] at hBsize
 rcases H x y with hCf | ⟨-,-,hCsC,-⟩
 ·rw[hCf] at hBsize; simp only[a2_J_eq] at hBsize
  have:=E y; omega
 ·have:=E (a2 (op x y)); have:=E (op x y); omega
/-- the outer product ((z*x)*y)*(x*y) is always free -/
def Dfree (x y z : M) : op (op (op z x) y) (op x y)=J (op (op z x) y) (op x y) :=by
 have hB:=H (op z x) y
 have hC:=H x y
 rcases K (op (op z x) y) (op x y) with h | h1 | h2 | h3 | h4 | h5 | h6
 ·exact h
 ·exfalso
  obtain⟨hP1,hRes⟩:=h1
  obtain⟨_,_,_,_,_,_,hBeq⟩:=hP1
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·exact U x y z hBf hBeq
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact I x z (hBoc.trans hCoc.symm)
 ·obtain⟨hP2,hExtra,hRes⟩:=h2
  obtain⟨_,_,_,hBeq⟩:=hP2
  have htC : sz (a2 (a1 (op x y)))≤sz (op x y) :=by have:=E (a1 (op x y)); have:=sz_a1 (op x y); omega
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact (no_core_CD x y z _ hBf hBeq htC hCty hCsx hCsC).elim
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact (I x z (hBoc.trans hCoc.symm)).elim
 ·exfalso
  obtain⟨hP3,hRes⟩:=h3
  obtain⟨_,_,_,_,hBeq⟩:=hP3
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·exact U x y z hBf hBeq
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact I x z (hBoc.trans hCoc.symm)
 ·obtain⟨hP4,hE1,hE2,hRes⟩:=h4
  obtain⟨_,_,hBeq,_⟩:=hP4
  have htC : sz (a2 (a1 (op x y)))≤sz (op x y) :=by have:=E (a1 (op x y)); have:=sz_a1 (op x y); omega
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact (no_core_CD x y z _ hBf hBeq htC hCty hCsx hCsC).elim
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact (I x z (hBoc.trans hCoc.symm)).elim
 ·exfalso
  obtain⟨hP5,hRes⟩:=h5
  obtain⟨_,_,hBeq,_,_,_⟩:=hP5
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·exact U x y z hBf hBeq
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·sorry
   ·exact I x z (hBoc.trans hCoc.symm)
 ·exfalso
  obtain⟨hP6,hRes⟩:=h6
  obtain⟨_,_,hBeq,_⟩:=hP6
  rcases hB with hBf | ⟨hBty,hBsA,hBsB,hBoc⟩
  ·exact U x y z hBf hBeq
  ·rcases hC with hCf | ⟨hCty,hCsx,hCsC,hCoc⟩
   ·rw[hCf] at hBeq; simp only[a2_J_eq] at hBeq
    -- REMAINING: B (= op (op z x) y) decoded,C free,B=a2 y.
    -- op z x=W y (subterm of y); B=op (W y) y is forced to fire one of TR's
    -- own rules (its "free" case contradicts sz B<sz y directly),landing B on
    -- a1(a2y)/a2(a1(a1y))/W(W y) -- all deeper subterms of y than a2 y itself,
    -- but no pure size argument found separates that value from a2 y; would need a
    -- genuine strong induction (see REMAINING in the session report).
    sorry
   ·exact I x z (hBoc.trans hCoc.symm)
/-- THE LAW: x=y*(((z*x)*y)*(x*y)) -/
def law (x y z : M) : op (y) (op (op (op (z) (x)) (y)) (op (x) (y)))=x :=by
 rw[Dfree]
 have hA:=H z x
 have hC:=H x y
 have hB:=H (op z x) y
 generalize hAe : op z x=A at *
 generalize hCe : op x y=C at *
 generalize hBe : op A y=B at *
 rcases hB with hB | ⟨hty,hAy,hB,hAoc⟩
 ·rcases hC with hC | ⟨hty,hxy,hC,hxoc⟩
  ·rcases hA with hA | ⟨htx,hzx,hA,hzoc⟩
   ·subst hA hB hC; exact op_R1 y z x
   ·subst hB hC; exact op_R3 y A x (by rw[← hAe,hzoc]) hA
  ·rcases hA with hA | ⟨htx,hzx,hA,hzoc⟩
   ·subst hA hB; exact op_R2 y z x C hCe.symm hC
   ·subst hB; exact op_R4 y A x C hty hxoc hCe.symm hC (by rw[← hAe,hzoc]) hA
 ·rcases hC with hC | ⟨hty',hxy,hC,hxoc⟩
  ·rcases hA with hA | ⟨htx,hzx,hA,hzoc⟩
   ·subst hC; exact op_R5 y B z x hty (by rw[← hAoc,hA]) (by rw[← hAoc,hBe]) hB
   ·subst hC; exact op_R6 y B A x hty hAoc.symm hBe.symm hB (by rw[← hAe,hzoc]) hA
  ·exfalso
   have hAx : A=x :=by rw[hAoc,hxoc]
   rcases hA with hA | ⟨-,-,hA,-⟩
   ·rw[hAx] at hA; have:=congrArg sz hA; simp only[sz_J] at this; omega
   ·rw[hAx] at hA; omega
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))