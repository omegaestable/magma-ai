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
def K (u : M) : sz (a1 u)≤sz u :=by cases u <;> simp[a1,sz] <;> omega
def Z (u : M) : sz (a2 u)≤sz u :=by cases u <;> simp[a2,sz] <;> omega
def W {a b : M} (h : a=b) : sz a=sz b:=congrArg sz h
def V (t : M) (h : tg t=2) : ∃ b0 b1,t=M.J b0 b1 :=by cases t <;> simp_all[tg]
def tg_g (t : M) (h : tg t≠2) : ∃ n,t=M.g n :=by cases t <;> simp_all[tg]
def E (t : M) (h : tg t=2) : sz t=sz (a1 t)+sz (a2 t)+1 :=by obtain⟨a,b,rfl⟩:=V _ h; simp[sz,a1,a2]
@[simp] theorem tg_g_eq (n : Nat) : tg (M.g n)=1:=rfl
@[simp] theorem tg_J_eq (b0 b1 : M) : tg (M.J b0 b1)=2:=rfl
@[simp] theorem j1 (b0 b1 : M) : a1 (M.J b0 b1)=b0:=rfl
@[simp] theorem j2 (b0 b1 : M) : a2 (M.J b0 b1)=b1:=rfl
@[simp] theorem a1_g_eq (n : Nat) : a1 (M.g n)=M.g n:=rfl
@[simp] theorem a2_g_eq (n : Nat) : a2 (M.g n)=M.g n:=rfl
def T (u v : M) : Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def U {a b u v : M} (h : max (sz a) (sz b)<max (sz u) (sz v)) : T a b<T u v :=by
 unfold T
 have h1 : sz a+sz b≤2*max (sz a) (sz b) :=by omega
 have h2 : (max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def msr_lt_of_max_eq {a b u v : M} (h : max (sz a) (sz b)=max (sz u) (sz v)) (h2 : sz a+sz b<sz u+sz v) : T a b<T u v :=by unfold T; rw[h]; omega
def L (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a1 (a2 v))=2∧u=a2 (a1 (a2 v))∧tg (a2 (a2 v))=2∧u=a2 (a2 (a2 v))
instance (u v : M) : Decidable (L u v) :=by unfold L; infer_instance
def D (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a1 (a2 v))=2∧u=a2 (a1 (a2 v))∧tg u=2
instance (u v : M) : Decidable (D u v) :=by unfold D; infer_instance
def R (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg (a2 (a2 v))=2∧u=a2 (a2 (a2 v))∧tg u=2
instance (u v : M) : Decidable (R u v) :=by unfold R; infer_instance
def Q (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg u=2
instance (u v : M) : Decidable (Q u v) :=by unfold Q; infer_instance
def O (u v : M) : Prop:=tg v=2∧u=a1 v∧tg (a2 v)=2∧tg u=2∧a1 u=a2 u∧a1 u=a1 (a2 v)
instance (u v : M) : Decidable (O u v) :=by unfold O; infer_instance
def op (u v : M) : M :=
 let p1:=if hs1 : T (a1 u) (u)<T u v then op (a1 u) (u) else J u v
 let p2:=if hs2 : T (a1 (a2 v)) (a2 v)<T u v then op (a1 (a2 v)) (a2 v) else J u v
 if L u v then a1 (a2 (a2 v))
 else if D u v∧T (a1 u) (u)<T u v∧a2 (a2 v)=p1 then a1 u
 else if R u v∧T (a1 u) (u)<T u v∧a1 (a2 v)=p1 then a1 (a2 (a2 v))
 else if Q u v∧T (a1 u) (u)<T u v∧a1 (a2 v)=p1∧a2 (a2 v)=p1 then a1 u
 else if O u v∧T (a1 (a2 v)) (a2 v)<T u v∧a1 u=p2 then J (a2 v) (u)
 else J u v
termination_by T u v
decreasing_by
 ·assumption
 ·assumption
def inst : Magma M:={ op:=fun a b => op b a }
def Pre (u v : M) : Prop:=L u v∨D u v∨R u v∨Q u v∨O u v
def op_free {u v : M} (h : ¬ Pre u v) : op u v=J u v :=by rw[op.eq_1]; simp only[Pre,not_or] at h; simp[h]
def rhs : ¬ @EquationRHS M inst :=by
 intro h
 have:=h (g 2) (g 0) (g 1)
 revert this
 change ¬ g 2=op (op (g 0) (op (g 2) (g 2))) (op (op (g 0) (g 1)) (g 0))
 simp (config:={decide:=true}) [op.eq_1,sz,L,D,R,Q,O]
def G (u v : M) : ∃ p1 p2 : M,
  p1=(if hs1 : T (a1 u) u<T u v then op (a1 u) u else J u v) ∧
  p2=(if hs2 : T (a1 (a2 v)) (a2 v)<T u v then op (a1 (a2 v)) (a2 v) else J u v) ∧
  op u v=(
 if L u v then a1 (a2 (a2 v))
 else if D u v∧T (a1 u) u<T u v∧a2 (a2 v)=p1 then a1 u
 else if R u v∧T (a1 u) u<T u v∧a1 (a2 v)=p1 then a1 (a2 (a2 v))
 else if Q u v∧T (a1 u) u<T u v∧a1 (a2 v)=p1∧a2 (a2 v)=p1 then a1 u
 else if O u v∧T (a1 (a2 v)) (a2 v)<T u v∧a1 u=p2 then J (a2 v) u
 else J u v) :=
 ⟨_,_,rfl,rfl,op.eq_1 u v⟩
def X (u v : M) : op u v=J u v∨(tg v=2∧u=a1 v∧tg (a2 v)=2∧(
  (L u v∧op u v=a1 (a2 (a2 v))) ∨
  (D u v∧a2 (a2 v)=op (a1 u) u∧op u v=a1 u) ∨
  (R u v∧a1 (a2 v)=op (a1 u) u∧op u v=a1 (a2 (a2 v))) ∨
  (Q u v∧a1 (a2 v)=op (a1 u) u∧a2 (a2 v)=op (a1 u) u∧op u v=a1 u) ∨
  (O u v∧a1 u=op (a1 (a2 v)) (a2 v)∧op u v=J (a2 v) u))) :=by
 obtain⟨p1,p2,hp1,hp2,hop⟩:=G u v
 rw[hop]
 split
 ·rename_i h; exact Or.inr ⟨h.1,h.2.1,h.2.2.1,Or.inl ⟨h,rfl⟩⟩
 ·split
  ·rename_i h1 h
   obtain⟨h2,hs1,he⟩:=h
   rw[dif_pos hs1] at hp1; subst hp1
   exact Or.inr ⟨h2.1,h2.2.1,h2.2.2.1,Or.inr (Or.inl ⟨h2,he,rfl⟩)⟩
  ·split
   ·rename_i h1 h2 h
    obtain⟨h3,hs1,he⟩:=h
    rw[dif_pos hs1] at hp1; subst hp1
    exact Or.inr ⟨h3.1,h3.2.1,h3.2.2.1,Or.inr (Or.inr (Or.inl ⟨h3,he,rfl⟩))⟩
   ·split
    ·rename_i h1 h2 h3 h
     obtain⟨h4,hs1,he1,he2⟩:=h
     rw[dif_pos hs1] at hp1; subst hp1
     exact Or.inr ⟨h4.1,h4.2.1,h4.2.2.1,Or.inr (Or.inr (Or.inr (Or.inl ⟨h4,he1,he2,rfl⟩)))⟩
    ·split
     ·rename_i h1 h2 h3 h4 h
      obtain⟨h5,hs2,he⟩:=h
      rw[dif_pos hs2] at hp2; subst hp2
      exact Or.inr ⟨h5.1,h5.2.1,h5.2.2.1,Or.inr (Or.inr (Or.inr (Or.inr ⟨h5,he,rfl⟩)))⟩
     ·left; rfl
def TRs (u v : M) : op u v=J u v∨(tg v=2∧u=a1 v∧tg (a2 v)=2 ∧
  (sz (op u v)<sz v∨(tg u=2∧a1 u=a2 u∧a1 u=a1 (a2 v)∧a1 u=op (a1 (a2 v)) (a2 v)∧op u v=J (a2 v) u))) :=by
 rcases X u v with h | ⟨h1,h2,h3,h⟩
 ·exact Or.inl h
 ·right; refine⟨h1,h2,h3,?_⟩
  have s1:=E v h1
  have s2:=E (a2 v) h3
  have s3:=K (a2 (a2 v))
  have s4:=Z (a2 v)
  have s5:=K u
  have s6 : sz u=sz (a1 v) :=by rw[h2]
  rcases h with⟨-,hr⟩ | ⟨-,-,hr⟩ | ⟨-,-,hr⟩ | ⟨-,-,-,hr⟩ | ⟨h5,he,hr⟩
  ·left; rw[hr]; omega
  ·left; rw[hr]; omega
  ·left; rw[hr]; omega
  ·left; rw[hr]; omega
  ·right; exact⟨h5.2.2.2.1,h5.2.2.2.2.1,h5.2.2.2.2.2,he,hr⟩
def H {u v : M} (h : op u v≠J u v) : tg v=2∧u=a1 v∧tg (a2 v)=2 :=by
 rcases X u v with h' | ⟨h1,h2,h3,-⟩
 ·exact absurd h' h
 ·exact⟨h1,h2,h3⟩
def L1 (x y : M) : op x y=J x y∨(tg y=2∧x=a1 y∧tg (a2 y)=2) :=by
 rcases X x y with h | ⟨h1,h2,h3,-⟩
 ·exact Or.inl h
 ·exact Or.inr ⟨h1,h2,h3⟩
def I {c y : M} (hc : a1 c≠y) : op y c=J y c :=by
 apply Classical.byContradiction; intro h
 obtain⟨-,hu,-⟩:=H h
 exact hc hu.symm
def N (q : M) : op q (J q q)≠q :=by
 intro he
 rcases X q (J q q) with h | ⟨-,-,h3,h⟩
 ·rw[h] at he; have:=W he; simp only[sz] at this; omega
 ·simp only[j2] at h3
  obtain⟨q1,q2,rfl⟩:=V q h3
  have s1:=K q1; have s2:=Z q1; have s3:=K q2; have s4:=Z q2
  rcases h with⟨-,hr⟩ | ⟨-,-,hr⟩ | ⟨-,-,hr⟩ | ⟨-,-,-,hr⟩ | ⟨-,-,hr⟩ <;>
   (rw[hr] at he; (try simp only[j1,j2] at he); have:=W he; simp only[sz] at this; omega)
def NE (u v : M) : op u v≠v :=by
 intro he
 rcases TRs u v with h | ⟨h1,h2,h3,h | ⟨h4,h5,h6,h7,h8⟩⟩
 ·rw[h] at he; have:=W he; simp only[sz] at this; omega
 ·have:=W he; omega
 ·rw[h8] at he
  obtain⟨v1,v2,rfl⟩:=V v h1
  simp only[j1,j2] at h2 he h7
  subst h2
  obtain⟨hv,-⟩:=M.J.inj he
  subst hv
  obtain⟨w1,w2,rfl⟩:=V v2 h4
  simp only[j1,j2] at h5 h7
  subst h5
  exact N w1 h7.symm
def NQ2 (q : M) : op q (J q (J q q))≠q :=by
 intro he
 rcases X q (J q (J q q)) with h | ⟨-,-,-,h⟩
 ·rw[h] at he; have:=W he; simp only[sz] at this; omega
 ·rcases h with⟨hP,hr⟩ | ⟨hP,-,hr⟩ | ⟨hP,hg,hr⟩ | ⟨hP,-,-,hr⟩ | ⟨hP,-,hr⟩
  ·obtain⟨-,-,-,h4,h5,-,-⟩:=hP
   simp only[j1,j2] at h4 h5
   have:=W h5; have:=E q h4; have:=Z q; omega
  ·obtain⟨-,-,-,h4,h5,-⟩:=hP
   simp only[j1,j2] at h4 h5
   have:=W h5; have:=E q h4; have:=Z q; omega
  ·simp only[j1,j2] at hg
   exact NE (a1 q) q hg.symm
  ·obtain⟨-,-,-,h4⟩:=hP
   rw[hr] at he; have:=W he; have:=E q h4; omega
  ·obtain⟨-,-,-,h4,-,h6⟩:=hP
   simp only[j1,j2] at h6
   have:=W h6; have:=E q h4; omega
def op_R1 (y z x : M) : op y (J y (J (J z y) (J x y)))=x :=by
 obtain⟨p1,p2,-,-,hop⟩:=G y (J y (J (J z y) (J x y)))
 have h1 : L y (J y (J (J z y) (J x y))):=⟨rfl,rfl,rfl,rfl,rfl,rfl,rfl⟩
 rw[hop,if_pos h1]
 rfl
def CFF (x y z : M) : op (J z y) (J x y)=J (J z y) (J x y) ∨
  (x=J z y∧tg y=2∧a1 y=op z (J z y)∧a2 y=op z (J z y)∧op (J z y) (J x y)=z) :=by
 rcases X (J z y) (J x y) with h | ⟨-,hu,hty,h⟩
 ·exact Or.inl h
 ·simp only[j1,j2] at hu hty
  subst hu
  have s1:=E y hty
  have s2:=K y
  have s3:=Z y
  have s4:=Z (a1 y)
  have s5:=Z (a2 y)
  rcases h with⟨hP,-⟩ | ⟨hP,-,-⟩ | ⟨hP,-,-⟩ | ⟨hP,he1,he2,hr⟩ | ⟨hP,-,-⟩
  ·obtain⟨-,-,-,-,h5,-,-⟩:=hP
   simp only[j1,j2] at h5
   have:=W h5; simp only[sz] at this; omega
  ·obtain⟨-,-,-,-,h5,-⟩:=hP
   simp only[j1,j2] at h5
   have:=W h5; simp only[sz] at this; omega
  ·obtain⟨-,-,-,-,h5,-⟩:=hP
   simp only[j1,j2] at h5
   have:=W h5; simp only[sz] at this; omega
  ·simp only[j1,j2] at he1 he2 hr
   exact Or.inr ⟨rfl,hty,he1,he2,hr⟩
  ·obtain⟨-,-,-,-,h5,h6⟩:=hP
   simp only[j1,j2] at h5 h6
   subst h5
   have:=W h6; omega
def TZ {y z : M} (hty : tg y=2) (h1 : a1 y=op z (J z y)) (h2 : a2 y=op z (J z y)) :
  tg z=2∧a1 z=a1 y∧op (a1 y) z=a1 y :=by
 have s1:=E y hty
 have s2:=K y
 have s3:=Z y
 have s4:=K (a2 y)
 have s5:=Z (a1 z)
 have s6:=K z
 rcases X z (J z y) with h | ⟨-,-,-,h⟩
 ·rw[h] at h1; have:=W h1; simp only[sz] at this; omega
 ·rcases h with⟨hP,hr⟩ | ⟨hP,-,hr⟩ | ⟨hP,-,hr⟩ | ⟨hP,he1,he2,hr⟩ | ⟨hP,-,hr⟩
  ·obtain⟨-,-,-,-,-,h6,-⟩:=hP
   simp only[j1,j2] at h6 hr
   rw[hr] at h2; have:=W h2; have:=E (a2 y) h6; omega
  ·obtain⟨-,-,-,-,h5,h6⟩:=hP
   simp only[j1,j2] at h5 hr
   rw[hr] at h1; rw[h1] at h5
   have:=W h5; have:=E z h6; omega
  ·obtain⟨-,-,-,h4,-,-⟩:=hP
   simp only[j1,j2] at h4 hr
   rw[hr] at h2; have:=W h2; have:=E (a2 y) h4; omega
  ·obtain⟨-,-,-,h4⟩:=hP
   simp only[j1,j2] at he1 hr
   rw[hr] at h1
   refine⟨h4,h1.symm,?_⟩
   rw[h1] at he1 ⊢
   exact he1.symm
  ·simp only[j1,j2] at hr
   rw[hr] at h1; have:=W h1; simp only[sz] at this; omega
def op_R5 {y z : M} (hty : tg y=2) (hyq : a1 y=a2 y) (htz : tg z=2) (hz : a1 z=a1 y)
  (hq : op (a1 y) z=a1 y) : op y (J y z)=J z y :=by
 obtain⟨y1,y2,rfl⟩:=V y hty
 simp only[j1,j2] at hyq hz hq
 subst hyq
 obtain⟨p1,p2,hp1,hp2,hop⟩:=G (J y1 y1) (J (J y1 y1) z)
 have hs1 : T (a1 (J y1 y1)) (J y1 y1)<T (J y1 y1) (J (J y1 y1) z) :=
  U (by simp only[j1,sz]; omega)
 have hs2 : T (a1 (a2 (J (J y1 y1) z))) (a2 (J (J y1 y1) z))<T (J y1 y1) (J (J y1 y1) z) :=
  U (by simp only[j2,sz]; have:=K z; omega)
 rw[dif_pos hs1] at hp1; subst hp1; rw[dif_pos hs2] at hp2; subst hp2
 have s1:=Z y1
 rw[hop]
 split
 ·rename_i h
  obtain⟨-,-,-,-,h5,-,-⟩:=h
  simp only[j1,j2] at h5
  rw[hz] at h5; have:=W h5; simp only[sz] at this; omega
 ·split
  ·rename_i h1 h
   obtain⟨⟨-,-,-,-,h5,-⟩,-,-⟩:=h
   simp only[j1,j2] at h5
   rw[hz] at h5; have:=W h5; simp only[sz] at this; omega
  ·split
   ·rename_i h1 h2 h
    obtain⟨-,-,he⟩:=h
    simp only[j1,j2] at he
    rw[hz] at he
    exact absurd he.symm (N y1)
   ·split
    ·rename_i h1 h2 h3 h
     obtain⟨-,-,he,-⟩:=h
     simp only[j1,j2] at he
     rw[hz] at he
     exact absurd he.symm (N y1)
    ·split
     ·rfl
     ·rename_i h1 h2 h3 h4 h5
      exfalso; apply h5
      refine⟨⟨rfl,rfl,htz,rfl,rfl,hz.symm⟩,hs2,?_⟩
      show y1=op (a1 z) z
      rw[hz]; exact hq.symm
def R24case {y : M} (hty : tg y=2) (h7 : y=a2 (op (a1 y) y)) : a1 (op (a1 y) y)=a1 y :=by
 have s1:=E y hty
 have s2:=Z (op (a1 y) y)
 rcases TRs (a1 y) y with hf | ⟨-,-,-,hs | ⟨-,-,-,-,hr⟩⟩
 ·rw[hf]; rfl
 ·have:=W h7; omega
 ·rw[hr] at h7; simp only[j2] at h7; have:=W h7; have:=K y; omega
def op_R2 {y : M} (hty : tg y=2) (z : M) : op y (J y (J (J z y) (op (a1 y) y)))=a1 y :=by
 obtain⟨p1,p2,hp1,hp2,hop⟩:=G y (J y (J (J z y) (op (a1 y) y)))
 have hs1 : T (a1 y) y<T y (J y (J (J z y) (op (a1 y) y))) :=
  U (by simp only[sz]; have:=K y; omega)
 rw[dif_pos hs1] at hp1; subst hp1
 have s1:=E y hty
 have s2:=Z (op (a1 y) y)
 rw[hop]
 split
 ·rename_i h
  obtain⟨-,-,-,-,-,-,h7⟩:=h
  simp only[j1,j2] at h7
  exact R24case hty h7
 ·split
  ·rfl
  ·rename_i h1 h2
   exfalso; apply h2
   exact⟨⟨rfl,rfl,rfl,rfl,rfl,hty⟩,hs1,rfl⟩
def CNF {y : M} (hty : tg y=2) (z : M) : op (J z y) (op (a1 y) y)=J (J z y) (op (a1 y) y) :=by
 apply Classical.byContradiction; intro h
 obtain⟨-,hu,-⟩:=H h
 have s1:=E y hty
 have s2:=K y
 have s3:=Z y
 have s4:=K (op (a1 y) y)
 rcases TRs (a1 y) y with hf | ⟨-,-,-,hs | ⟨-,-,-,-,hr⟩⟩
 ·rw[hf] at hu; simp only[j1] at hu; have:=W hu; simp only[sz] at this; omega
 ·have:=W hu; simp only[sz] at this; omega
 ·rw[hr] at hu; simp only[j1] at hu; have:=W hu; simp only[sz] at this; omega
def op_R3 {y : M} (hty : tg y=2) (x : M) : op y (J y (J (op (a1 y) y) (J x y)))=x :=by
 obtain⟨p1,p2,hp1,hp2,hop⟩:=G y (J y (J (op (a1 y) y) (J x y)))
 have hs1 : T (a1 y) y<T y (J y (J (op (a1 y) y) (J x y))) :=
  U (by simp only[sz]; have:=K y; omega)
 rw[dif_pos hs1] at hp1; subst hp1
 rw[hop]
 split
 ·rfl
 ·split
  ·rename_i h1 h
   exfalso; apply h1
   obtain⟨⟨-,-,-,h4,h5,-⟩,-,-⟩:=h
   exact⟨rfl,rfl,rfl,h4,h5,rfl,rfl⟩
  ·split
   ·rfl
   ·rename_i h1 h2 h3
    exfalso; apply h3
    exact⟨⟨rfl,rfl,rfl,rfl,rfl,hty⟩,hs1,rfl⟩
def op_R4 {y : M} (hty : tg y=2) : op y (J y (J (op (a1 y) y) (op (a1 y) y)))=a1 y :=by
 obtain⟨p1,p2,hp1,hp2,hop⟩:=G y (J y (J (op (a1 y) y) (op (a1 y) y)))
 have hs1 : T (a1 y) y<T y (J y (J (op (a1 y) y) (op (a1 y) y))) :=
  U (by simp only[sz]; have:=K y; omega)
 rw[dif_pos hs1] at hp1; subst hp1
 have s1:=E y hty
 have s2:=Z (op (a1 y) y)
 rw[hop]
 split
 ·rename_i h
  obtain⟨-,-,-,-,h5,-,-⟩:=h
  simp only[j1,j2] at h5
  exact R24case hty h5
 ·split
  ·rfl
  ·split
   ·rename_i h1 h2 h
    exfalso; apply h2
    obtain⟨⟨-,-,-,h4,h5,h6⟩,hs,he⟩:=h
    exact⟨⟨rfl,rfl,rfl,h4,h5,h6⟩,hs,he⟩
   ·split
    ·rfl
    ·rename_i h1 h2 h3 h4
     exfalso; apply h4
     exact⟨⟨rfl,rfl,rfl,hty⟩,hs1,rfl,rfl⟩
def Tsplit3 {A B P : M} (hg : M.J A B=op (a1 P) P) :
  (sz A=sz (a1 P)∧sz B=sz P)∨(sz A+sz B+1<sz P)∨(sz A=sz (a2 P)∧sz B=sz (a1 P)) :=by
 rcases TRs (a1 P) P with hgf | ⟨-,-,-,hs | ⟨-,-,-,-,hr5⟩⟩
 ·rw[hgf] at hg; obtain⟨e1,e2⟩:=M.J.inj hg
  exact Or.inl ⟨by rw[e1],by rw[e2]⟩
 ·right; left; have:=W hg; simp only[sz] at this; omega
 ·rw[hr5] at hg; obtain⟨e1,e2⟩:=M.J.inj hg
  exact Or.inr (Or.inr ⟨by rw[e1],by rw[e2]⟩)
def PPfree {p : M} (hp2 : tg p=2) : op p (J p p)=J p (J p p) ∨
  (a1 p=op (a1 p) p∧op p (J p p)=a1 p)∨op p (J p p)=J p p :=by
 have sp:=E p hp2
 rcases X p (J p p) with hqf | ⟨-,-,-,⟨hP',-⟩ | ⟨hP',-,-⟩ | ⟨hP',-,-⟩ | ⟨-,he1,-,hr'⟩ | ⟨-,-,hr'⟩⟩
 ·exact Or.inl hqf
 ·exfalso; obtain⟨-,-,-,-,h5,-,-⟩:=hP'; simp only[j1,j2] at h5
  have:=W h5; have:=Z (a1 p); omega
 ·exfalso; obtain⟨-,-,-,-,h5,-⟩:=hP'; simp only[j1,j2] at h5
  have:=W h5; have:=Z (a1 p); omega
 ·exfalso; obtain⟨-,-,-,-,h5,-⟩:=hP'; simp only[j1,j2] at h5
  have:=W h5; have:=Z (a2 p); omega
 ·right; left; simp only[j1,j2] at he1; exact⟨he1,hr'⟩
 ·right; right; simp only[j1,j2] at hr'; exact hr'
def CFN {y : M} (hty : tg y=2) (hta : tg (a2 y)=2) (x : M) :
  op (op (a1 y) y) (J x y)=J (op (a1 y) y) (J x y) :=by
 apply Classical.byContradiction; intro h
 obtain⟨-,hu,-⟩:=H h
 simp only[j1] at hu
 subst hu
 obtain⟨y1,y2,rfl⟩:=V y hty
 simp only[j2] at hta
 obtain⟨y21,y22,rfl⟩:=V y2 hta
 simp only[j1,j2] at h
 have tp:=X y1 (J y1 (J y21 y22))
 generalize hp : op y1 (J y1 (J y21 y22))=p at *
 have s1:=K y1; have s2:=Z y1; have s3:=K y21; have s4:=Z y21
 have s5:=K y22; have s6:=Z y22; have s7:=K p; have s8:=Z p
 rcases X p (J p (J y1 (J y21 y22))) with hf | ⟨-,-,-,hc⟩
 ·exact h hf
 have t:=TRs (a1 p) p
 rcases hc with⟨hP,-⟩ | ⟨hP,hg,-⟩ | ⟨hP,hg,-⟩ | ⟨hP,hg1,hg2,-⟩ | ⟨hP,hg,-⟩
 ·-- C1: p=a2 y1,p=y22,tg y1=2
  obtain⟨-,-,-,c4,c5,-,c7⟩:=hP
  simp only[j1,j2] at c4 c5 c7
  have C1dup : p=a1 y1→a2 (a2 (J y1 (J y21 y22)))=op (a1 y1) y1→False :=by
   intro hr hg2
   simp only[j1,j2] at hr hg2
   obtain⟨c,d,rfl⟩:=V y1 c4
   simp only[j1,j2] at hr c5 hg2
   subst hr; subst c5
   rw[← c7] at hg2
   exact N p hg2.symm
  rcases tp with hpf | ⟨-,-,-,⟨hQ,hr⟩ | ⟨hQ,hg2,hr⟩ | ⟨hQ,hg3,hr⟩ | ⟨hQ,hg1,hg2,hr⟩ | ⟨hQ,hg5,hr⟩⟩
  ·have:=W c7; have:=W hpf; simp only[sz] at *; omega
  ·obtain⟨-,-,-,-,-,q6,-⟩:=hQ
   simp only[j1,j2] at q6 hr
   have:=W c7; have:=W hr; have:=E y22 q6; omega
  ·exact C1dup hr hg2
  ·obtain⟨-,-,-,q4,-,-⟩:=hQ
   simp only[j1,j2] at q4 hr
   have:=W c7; have:=W hr; have:=E y22 q4; omega
  ·exact C1dup hr hg2
  ·simp only[j1,j2] at hr
   have:=W c7; have:=W hr; simp only[sz] at *; omega
 ·-- C2: tg y1=2,p=a2 y1,tg p=2,guard J y21 y22=op (a1 p) p
  obtain⟨-,-,-,c4,c5,c6⟩:=hP
  simp only[j1,j2] at c4 c5 c6 hg
  have sp:=E p c6
  rcases tp with hpf | ⟨-,-,-,⟨hQ,hr⟩ | ⟨hQ,hg2,hr⟩ | ⟨hQ,hg3,hr⟩ | ⟨hQ,hq1,hq2,hr⟩ | ⟨hQ,hg5,hr⟩⟩
  ·have:=W c5; have:=W hpf; simp only[sz] at *; omega
  ·obtain⟨-,-,-,-,-,q6,q7⟩:=hQ
   simp only[j1,j2] at q6 q7 hr
   have e1:=E y22 q6
   have e2:=W hr; have e3:=W q7
   rcases Tsplit3 hg with⟨k1,k2⟩ | hk | ⟨k1,k2⟩ <;> omega
  ·obtain⟨-,-,-,q4,q5,q6⟩:=hQ
   simp only[j1,j2] at q4 q5 q6 hr hg2
   have e1:=E y21 q4
   have e2:=E y1 q6
   have e3:=W hr; have e4:=W q5; have e5:=W c5
   rcases Tsplit3 hg with⟨k1,k2⟩ | hk | ⟨k1,k2⟩ <;> omega
  ·obtain⟨-,-,-,q4,q5,q6⟩:=hQ
   simp only[j1,j2] at q4 q5 q6 hr hg3
   have e1:=E y22 q4
   have e2:=W hr; have e3:=W q5
   rcases Tsplit3 hg with⟨k1,k2⟩ | hk | ⟨k1,k2⟩ <;> omega
  ·obtain⟨-,-,-,q4⟩:=hQ
   simp only[j1,j2] at hr hq1 hq2
   obtain⟨c,d,rfl⟩:=V y1 q4
   simp only[j1,j2] at hr c5 hq1 hq2
   subst hr; subst c5
   subst hq1; subst hq2
   rcases t with hgf | ⟨-,-,-,hs | ⟨t4,t5,t6,t7,hr5⟩⟩
   ·rw[hgf] at hg; obtain⟨e1,e2⟩:=M.J.inj hg; rw[e2] at e1; have:=W e1; omega
   ·have hsq:=W hg; simp only[sz] at hsq
    rcases PPfree c6 with hqf | ⟨he1,hr'⟩ | hr'
    ·rw[hqf] at hsq; simp only[sz] at hsq; omega
    ·rw[hr',← he1] at hg
     have:=W hg; simp only[sz] at this; omega
    ·rw[hr'] at hsq; simp only[sz] at hsq; omega
   ·rw[hr5] at hg; obtain⟨e1,e2⟩:=M.J.inj hg
    rcases PPfree c6 with hqf | ⟨he1,hr'⟩ | hr'
    ·rw[hqf] at e2; have:=W e2; simp only[sz] at this; omega
    ·rw[hr5] at he1; have:=W he1; simp only[sz] at this; omega
    ·rw[hr'] at e2; have:=W e2; simp only[sz] at this; omega
  ·simp only[j1,j2] at hr
   have:=W c5; have:=W hr; simp only[sz] at *; omega
 ·-- C3: tg y22=2,p=y22,tg p=2,guard y1=op (a1 p) p
  obtain⟨-,-,-,c4,c5,c6⟩:=hP
  simp only[j1,j2] at c4 c5 c6 hg
  have sp:=E p c6
  have C3dup2 : p=a1 (a2 (a2 (J y1 (J y21 y22))))→False :=by
   intro hr
   simp only[j1,j2] at hr
   have hty22 : tg y22=2 :=by rw[← c5]; exact c6
   have:=W c5; have:=W hr; have:=E y22 hty22; omega
  have C3dup3 : tg y1=2→p=a1 y1→False :=by
   intro q hr
   obtain⟨c,d,rfl⟩:=V y1 q
   simp only[j1,j2] at hr hg
   subst hr
   rcases Tsplit3 hg with⟨k1,k2⟩ | hk | ⟨k1,k2⟩ <;> omega
  rcases tp with hpf | ⟨-,-,-,⟨hQ,hr⟩ | ⟨hQ,hg2,hr⟩ | ⟨hQ,hg3,hr⟩ | ⟨hQ,hq1,hq2,hr⟩ | ⟨hQ,hg5,hr⟩⟩
  ·have:=W c5; have:=W hpf; simp only[sz] at *; omega
  ·exact C3dup2 hr
  ·obtain⟨-,-,-,-,-,q6⟩:=hQ
   exact C3dup3 q6 hr
  ·exact C3dup2 hr
  ·obtain⟨-,-,-,q4⟩:=hQ
   exact C3dup3 q4 hr
  ·simp only[j1,j2] at hr
   have:=W c5; have:=W hr; simp only[sz] at *; omega
 ·-- C4: tg p=2,guards y1=op (a1 p) p=J y21 y22
  obtain⟨-,-,-,c4⟩:=hP
  simp only[j1,j2] at hg1 hg2
  have hy : y1=J y21 y22:=hg1.trans hg2.symm
  subst hy
  rcases tp with hpf | ⟨-,-,-,⟨hQ,hr⟩ | ⟨hQ,hg2',hr⟩ | ⟨hQ,hg3,hr⟩ | ⟨-,hq1,hq2,hr⟩ | ⟨hQ,hg5,hr⟩⟩
  ·rw[hpf] at hg1; simp only[j1,j2] at hg1
   exact NQ2 (J y21 y22) hg1.symm
  ·obtain⟨-,-,-,-,q5,-,-⟩:=hQ
   simp only[j1,j2] at q5
   have:=W q5; simp only[sz] at this; omega
  ·obtain⟨-,-,-,-,q5,-⟩:=hQ
   simp only[j1,j2] at q5
   have:=W q5; simp only[sz] at this; omega
  ·obtain⟨-,-,-,-,q5,-⟩:=hQ
   simp only[j1,j2] at q5
   have:=W q5; simp only[sz] at this; omega
  ·simp only[j1,j2] at hq1 hq2 hr
   have e : y21=y22:=hq1.trans hq2.symm
   subst e
   exact N y21 hq1.symm
  ·obtain⟨-,-,-,-,q5,-⟩:=hQ
   simp only[j1,j2] at q5 hg5
   subst q5
   exact N y21 hg5.symm
 ·-- C5: a1 p=op (a1 Y) Y=p
  obtain⟨-,-,-,c4,-,-⟩:=hP
  simp only[j1,j2] at hg
  rw[hp] at hg
  have:=W hg; have:=E p c4; omega
def law (x y z : M) : op (y) (op (y) (op (op (z) (y)) (op (x) (y))))=x :=by
 rcases L1 x y with hA | ⟨hty,hx,hta⟩
 ·rcases L1 z y with hB | ⟨hty,hz,hta⟩
  ·rw[hA,hB]
   rcases CFF x y z with hC | ⟨hxe,hty,he1,he2,hC⟩
   ·have hD : op y (J (J z y) (J x y))=J y (J (J z y) (J x y)) :=by apply I; intro he; have:=W he; simp only[j1,sz] at this; omega
    rw[hC,hD,op_R1]
   ·subst hxe
    obtain⟨htz,hz1,hq⟩:=TZ hty he1 he2
    have hyq : a1 y=a2 y:=he1.trans he2.symm
    have hc : a1 z≠y :=by rw[hz1]; intro he; have:=W he; have:=E y hty; omega
    rw[hC,I hc,op_R5 hty hyq htz hz1 hq]
  ·subst hz
   have hD : op y (J (op (a1 y) y) (J x y))=J y (J (op (a1 y) y) (J x y)):=I (NE (a1 y) y)
   rw[hA,CFN hty hta x,hD,op_R3 hty x]
 ·rcases L1 z y with hB | ⟨-,hz,-⟩
  ·subst hx
   have hD : op y (J (J z y) (op (a1 y) y))=J y (J (J z y) (op (a1 y) y)) :=by apply I; intro he; have:=W he; simp only[j1,sz] at this; omega
   rw[hB,CNF hty z,hD,op_R2 hty z]
  ·subst hx; subst hz
   have hpp : op (op (a1 y) y) (op (a1 y) y)=J (op (a1 y) y) (op (a1 y) y) :=by
    apply Classical.byContradiction; intro h
    obtain⟨htp,hu,-⟩:=H h
    have:=W hu; have:=E _ htp; omega
   have hD : op y (J (op (a1 y) y) (op (a1 y) y))=J y (J (op (a1 y) y) (op (a1 y) y)):=I (NE (a1 y) y)
   rw[hpp,hD,op_R4 hty]
def lhs : @EquationLHS M inst :=by
 intro x y z
 exact (law x y z).symm
end submission
def submission : Goal :=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))