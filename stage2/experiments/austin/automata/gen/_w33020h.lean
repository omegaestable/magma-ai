import JudgeProblem
inductive submission.M:Type where
 | g:Nat→submission.M
 | J:submission.M→submission.M→submission.M
 deriving DecidableEq
namespace submission
open M
def tg:M→Nat
 | .g _=>1
 | .J _ _=>2
def a1:M→M
 | .J x _=>x
 | t=>t
def a2:M→M
 | .J _ x=>x
 | t=>t
def sz:M→Nat
 | .g _=>1
 | .J b0 b1=>sz b0+sz b1+1
def Z (u:M):sz (a1 u)≤sz u:=by cases u<;>simp[a1,sz]<;>omega
def T (u:M):sz (a2 u)≤sz u:=by cases u<;>simp[a2,sz]<;>omega
def H (t:M) (h:tg t=2):∃ b0 b1,t=M.J b0 b1:=by cases t<;>simp_all[tg]
def U (t:M) (h:tg t=2):sz t=sz (a1 t)+sz (a2 t)+1:=by obtain⟨a,b,rfl⟩:=H _ h;simp[sz,a1,a2]
@[simp] def tg_g_eq (n:Nat):tg (M.g n)=1:=rfl
@[simp] def tg_J_eq (b0 b1:M):tg (M.J b0 b1)=2:=rfl
@[simp] def a1_J_eq (b0 b1:M):a1 (M.J b0 b1)=b0:=rfl
@[simp] def a2_J_eq (b0 b1:M):a2 (M.J b0 b1)=b1:=rfl
@[simp] def a1_g_eq (n:Nat):a1 (M.g n)=M.g n:=rfl
@[simp] def a2_g_eq (n:Nat):a2 (M.g n)=M.g n:=rfl
def W (u v:M):Nat:=max (sz u) (sz v)*max (sz u) (sz v)+sz u+sz v
def K {a b u v:M} (h:max (sz a) (sz b)<max (sz u) (sz v)):W a b<W u v:=by
 unfold W
 have h1:sz a+sz b≤2*max (sz a) (sz b):=by omega
 have h2:(max (sz a) (sz b)+1)*(max (sz a) (sz b)+1)≤max (sz u) (sz v)*max (sz u) (sz v):=Nat.mul_le_mul h h
 simp only[Nat.mul_succ,Nat.succ_mul] at h2
 omega
def O (u v:M):Prop:=tg v=2∧tg (a1 v)=2∧tg (a2 (a1 v))=2∧u=a2 v
instance (u v:M):Decidable (O u v):=by unfold O;infer_instance
def R (u v:M):Prop:=tg v=2∧tg (a1 v)=2∧u=a2 v
instance (u v:M):Decidable (R u v):=by unfold R;infer_instance
def D (u v:M):Prop:=tg v=2∧u=a2 v∧tg u=2∧tg (a1 u)=2∧tg (a2 u)=2
instance (u v:M):Decidable (D u v):=by unfold D;infer_instance
def Q (u v:M):Prop:=tg v=2∧u=a2 v∧tg u=2∧tg (a1 u)=2
instance (u v:M):Decidable (Q u v):=by unfold Q;infer_instance
def op (u v:M):M:=
 let p1:=if _:W (u) (a1 (a1 v))<W u v then op (u) (a1 (a1 v)) else J u v
 let p2:=if _:W (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))<W u v then op (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) else J u v
 let p3:=if _:W (a1 (a1 v)) (a2 (a1 v))<W u v then op (a1 (a1 v)) (a2 (a1 v)) else J u v
 let p4:=if _:W (a1 v) (u)<W u v then op (a1 v) (u) else J u v
 let p5:=if _:W (a2 (p1)) (p1)<W u v then op (a2 (p1)) (p1) else J u v
 let p6:=if _:W (u) (a2 (a1 u))<W u v then op (u) (a2 (a1 u)) else J u v
 let p7:=if _:W (a2 (a1 u)) (a1 u)<W u v then op (a2 (a1 u)) (a1 u) else J u v
 let p8:=if _:W (a1 (a2 u)) (a2 (a2 u))<W u v then op (a1 (a2 u)) (a2 (a2 u)) else J u v
 let p9:=if _:W (a1 u) (a2 u)<W u v then op (a1 u) (a2 u) else J u v
 let p10:=if _:W (a2 (p7)) (p7)<W u v then op (a2 (p7)) (p7) else J u v
 if O u v∧W (u) (a1 (a1 v))<W u v∧W (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))<W u v∧W (a1 (a1 v)) (a2 (a1 v))<W u v∧W (a1 v) (u)<W u v∧a2 (a2 (a1 v))=p1∧a2 (a1 v)=p2∧a1 v=p3∧v=p4 then a1 (a1 v)
 else if R u v∧W (u) (a1 (a1 v))<W u v∧W (a2 (p1)) (p1)<W u v∧W (a1 (a1 v)) (a2 (a1 v))<W u v∧W (a1 v) (u)<W u v∧tg (p1)=2∧a2 (a1 v)=p5∧a1 v=p3∧v=p4 then a1 (a1 v)
 else if D u v∧W (u) (a2 (a1 u))<W u v∧W (a2 (a1 u)) (a1 u)<W u v∧W (a1 (a2 u)) (a2 (a2 u))<W u v∧W (a1 u) (a2 u)<W u v∧W (a1 v) (u)<W u v∧J (u) (a2 (a1 u))=p6∧a2 (a2 u)=p7∧a2 u=p8∧u=p9∧a1 v=p7∧v=p4 then a2 (a1 u)
 else if Q u v∧W (u) (a2 (a1 u))<W u v∧W (a2 (a1 u)) (a1 u)<W u v∧W (a2 (p7)) (p7)<W u v∧W (a1 u) (a2 u)<W u v∧W (a1 v) (u)<W u v∧J (u) (a2 (a1 u))=p6∧tg (p7)=2∧a2 u=p10∧u=p9∧a1 v=p7∧v=p4 then a2 (a1 u)
 else J u v
termination_by W u v
decreasing_by all_goals assumption
def inst:Magma M:={ op:=fun a b=>op b a }
def rhs:¬ @EquationRHS M inst:=by
 intro h
 have:=h (g 1) (g 0) (g 2)
 revert this
 change ¬ g 1=op (op (g 2) (g 0)) (op (g 1) (op (g 0) (op (g 0) (g 0))))
 simp (config:={decide:=true}) [op.eq_1,sz,O,R,D,Q]
def V (t:M):1≤sz t:=by cases t<;>simp[sz]<;>omega
@[simp] def szJ (a b:M):sz (M.J a b)=sz a+sz b+1:=rfl
def Y {t:M} (h:tg t=2):sz (a1 t)<sz t:=by obtain⟨a,b,rfl⟩:=H _ h;simp only[a1_J_eq,szJ];have:=V b;omega
def E {t:M} (h:tg t=2):sz (a2 t)<sz t:=by obtain⟨a,b,rfl⟩:=H _ h;simp only[a2_J_eq,szJ];have:=V a;omega
def G (u v:M):∃ p1 p2 p3 p4 p5 p6 p7 p8 p9 p10:M,
  p1=(if _:W (u) (a1 (a1 v))<W u v then op (u) (a1 (a1 v)) else J u v) ∧
  p2=(if _:W (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))<W u v then op (a1 (a2 (a1 v))) (a2 (a2 (a1 v))) else J u v) ∧
  p3=(if _:W (a1 (a1 v)) (a2 (a1 v))<W u v then op (a1 (a1 v)) (a2 (a1 v)) else J u v) ∧
  p4=(if _:W (a1 v) (u)<W u v then op (a1 v) (u) else J u v) ∧
  p5=(if _:W (a2 (p1)) (p1)<W u v then op (a2 (p1)) (p1) else J u v) ∧
  p6=(if _:W (u) (a2 (a1 u))<W u v then op (u) (a2 (a1 u)) else J u v) ∧
  p7=(if _:W (a2 (a1 u)) (a1 u)<W u v then op (a2 (a1 u)) (a1 u) else J u v) ∧
  p8=(if _:W (a1 (a2 u)) (a2 (a2 u))<W u v then op (a1 (a2 u)) (a2 (a2 u)) else J u v) ∧
  p9=(if _:W (a1 u) (a2 u)<W u v then op (a1 u) (a2 u) else J u v) ∧
  p10=(if _:W (a2 (p7)) (p7)<W u v then op (a2 (p7)) (p7) else J u v) ∧
  op u v=(
 if O u v∧W (u) (a1 (a1 v))<W u v∧W (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))<W u v∧W (a1 (a1 v)) (a2 (a1 v))<W u v∧W (a1 v) (u)<W u v∧a2 (a2 (a1 v))=p1∧a2 (a1 v)=p2∧a1 v=p3∧v=p4 then a1 (a1 v)
 else if R u v∧W (u) (a1 (a1 v))<W u v∧W (a2 (p1)) (p1)<W u v∧W (a1 (a1 v)) (a2 (a1 v))<W u v∧W (a1 v) (u)<W u v∧tg (p1)=2∧a2 (a1 v)=p5∧a1 v=p3∧v=p4 then a1 (a1 v)
 else if D u v∧W (u) (a2 (a1 u))<W u v∧W (a2 (a1 u)) (a1 u)<W u v∧W (a1 (a2 u)) (a2 (a2 u))<W u v∧W (a1 u) (a2 u)<W u v∧W (a1 v) (u)<W u v∧J (u) (a2 (a1 u))=p6∧a2 (a2 u)=p7∧a2 u=p8∧u=p9∧a1 v=p7∧v=p4 then a2 (a1 u)
 else if Q u v∧W (u) (a2 (a1 u))<W u v∧W (a2 (a1 u)) (a1 u)<W u v∧W (a2 (p7)) (p7)<W u v∧W (a1 u) (a2 u)<W u v∧W (a1 v) (u)<W u v∧J (u) (a2 (a1 u))=p6∧tg (p7)=2∧a2 u=p10∧u=p9∧a1 v=p7∧v=p4 then a2 (a1 u)
 else J u v
  ):=
 ⟨_,_,_,_,_,_,_,_,_,_,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,rfl,op.eq_1 u v⟩
def X (u v:M):op u v=J u v∨(tg v=2∧a2 v=u ∧
  ((tg (a1 v)=2∧op u v=a1 (a1 v)∧op (a1 (a1 v)) (a2 (a1 v))=a1 v ∧
    ((tg (a2 (a1 v))=2∧op u (a1 (a1 v))=a2 (a2 (a1 v)) ∧
      op (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))=a2 (a1 v)) ∨
     (tg (op u (a1 (a1 v)))=2 ∧
      op (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v)))=a2 (a1 v)))) ∨
   (tg u=2∧tg (a1 u)=2∧op u v=a2 (a1 u)∧op (a2 (a1 u)) (a1 u)=a1 v))):=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,hp1,hp2,hp3,hp4,hp5,hp6,hp7,hp8,hp9,hp10,hop⟩:=
  G u v
 rw[hop]
 split
 ·rename_i h
  have c1:=h.2.2.2.2.2.1
  have c2:=h.2.2.2.2.2.2.1
  have c3:=h.2.2.2.2.2.2.2.1
  rw[dif_pos h.2.1] at hp1
  rw[dif_pos h.2.2.1] at hp2
  rw[dif_pos h.2.2.2.1] at hp3
  rw[hp1] at c1
  rw[hp2] at c2
  rw[hp3] at c3
  exact Or.inr ⟨h.1.1,h.1.2.2.2.symm,Or.inl ⟨h.1.2.1,rfl,c3.symm,
   Or.inl ⟨h.1.2.2.1,c1.symm,c2.symm⟩⟩⟩
 ·split
  ·rename_i h
   have tq:=h.2.2.2.2.2.1
   have c5:=h.2.2.2.2.2.2.1
   have c3:=h.2.2.2.2.2.2.2.1
   have g5:=h.2.2.1
   rw[dif_pos h.2.1] at hp1
   rw[hp1] at tq g5 hp5
   rw[dif_pos g5] at hp5
   rw[hp5] at c5
   rw[dif_pos h.2.2.2.1] at hp3
   rw[hp3] at c3
   exact Or.inr ⟨h.1.1,h.1.2.2.symm,Or.inl ⟨h.1.2.1,rfl,c3.symm,Or.inr ⟨tq,c5.symm⟩⟩⟩
  ·split
   ·rename_i h
    have c7:=h.2.2.2.2.2.2.2.2.2.2.1
    rw[dif_pos h.2.2.1] at hp7
    rw[hp7] at c7
    exact Or.inr ⟨h.1.1,h.1.2.1.symm,Or.inr ⟨h.1.2.2.1,h.1.2.2.2.1,rfl,c7.symm⟩⟩
   ·split
    ·rename_i h
     have c7:=h.2.2.2.2.2.2.2.2.2.2.1
     rw[dif_pos h.2.2.1] at hp7
     rw[hp7] at c7
     exact Or.inr ⟨h.1.1,h.1.2.1.symm,Or.inr ⟨h.1.2.2.1,h.1.2.2.2,rfl,c7.symm⟩⟩
    ·exact Or.inl rfl
def I {u v:M} (h:sz v≤sz u):op u v=J u v:=by
 rcases X u v with hz | ⟨tv,av,-⟩
 ·exact hz
 ·exfalso;have q:=E tv;rw[av] at q;omega
def N {u v:M} (h:op u v≠J u v):sz (op u v)<sz v:=by
 rcases X u v with hz | ⟨tv,av,hd⟩
 ·exact absurd hz h
 ·have q1:=E tv
  rw[av] at q1
  rcases hd with⟨t1,hr,-,-⟩ | ⟨tu,tau,hr,-⟩
  ·rw[hr];have:=Y t1;have:=Y tv;omega
  ·rw[hr];have:=E tau;have:=Y tu;omega
def NY {u w:M} (hw:sz w<sz (a1 u)) (hu:sz (a1 u)<sz u)
  (h:a2 (a2 w)=J u (a1 w)):False:=by
 have e:=congrArg sz h
 simp only[szJ] at e
 have:=T w;have:=T (a2 w);omega
def NX {u w:M} (hw:sz w<sz (a1 u)) (hu:sz (a1 u)<sz u)
  (h:op (a1 w) (J u (a1 w))=a2 w):False:=by
 have b1:=Z w
 have b2:=T w
 rcases X (a1 w) (J u (a1 w)) with hz | ⟨-,-,hA | hB⟩
 ·rw[hz] at h;have e:=congrArg sz h;simp only[szJ] at e;omega
 ·obtain⟨-,hr,-,-⟩:=hA
  simp only[a1_J_eq] at hr
  rw[hr] at h
  have e:=congrArg sz h;omega
 ·obtain⟨-,-,hr,hq⟩:=hB
  simp only[a1_J_eq] at hq
  rw[hr] at h
  rw[h] at hq
  by_cases hz:op (a2 w) (a1 (a1 w))=J (a2 w) (a1 (a1 w))
  ·rw[hz] at hq
   have e:=congrArg a1 hq
   simp only[a1_J_eq] at e
   have e2:=congrArg sz e;omega
  ·have q:=N hz
   rw[hq] at q
   have b3:=Z (a1 w);omega
def A (u v:M) (t0:tg v=2) (t1:tg (a1 v)=2) (t2:tg (a2 (a1 v))=2)
  (hv:a2 v=u)
  (k1:op u (a1 (a1 v))=a2 (a2 (a1 v)))
  (k2:op (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))=a2 (a1 v))
  (k3:op (a1 (a1 v)) (a2 (a1 v))=a1 v)
  (k4:op (a1 v) u=v):op u v=a1 (a1 v):=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,hp1,hp2,hp3,hp4,-,-,-,-,-,-,hop⟩:=
  G u v
 have s0:=Y t0
 have s0':=E t0
 rw[hv] at s0'
 have s1:=Y t1
 have s1':=E t1
 have s2:=Y t2
 have s2':=E t2
 have g1:W u (a1 (a1 v))<W u v:=K (by omega)
 have g2:W (a1 (a2 (a1 v))) (a2 (a2 (a1 v)))<W u v:=K (by omega)
 have g3:W (a1 (a1 v)) (a2 (a1 v))<W u v:=K (by omega)
 have g4:W (a1 v) u<W u v:=K (by omega)
 rw[dif_pos g1] at hp1
 rw[dif_pos g2] at hp2
 rw[dif_pos g3] at hp3
 rw[dif_pos g4] at hp4
 rw[hop]
 split
 ·rfl
 ·rename_i h
  exact absurd ⟨⟨t0,t1,t2,hv.symm⟩,g1,g2,g3,g4,k1.symm.trans hp1.symm,
   k2.symm.trans hp2.symm,k3.symm.trans hp3.symm,k4.symm.trans hp4.symm⟩ h
def B (u v:M) (t0:tg v=2) (t1:tg (a1 v)=2) (hv:a2 v=u)
  (k1':tg (op u (a1 (a1 v)))=2)
  (k0:sz (op u (a1 (a1 v)))<sz v)
  (k2:op (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v)))=a2 (a1 v))
  (k3:op (a1 (a1 v)) (a2 (a1 v))=a1 v)
  (k4:op (a1 v) u=v):op u v=a1 (a1 v):=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,hp1,-,hp3,hp4,hp5,-,-,-,-,-,hop⟩:=
  G u v
 have s0:=Y t0
 have s0':=E t0
 rw[hv] at s0'
 have s1:=Y t1
 have s1':=E t1
 have s6:=T (op u (a1 (a1 v)))
 have g1:W u (a1 (a1 v))<W u v:=K (by omega)
 have g3:W (a1 (a1 v)) (a2 (a1 v))<W u v:=K (by omega)
 have g4:W (a1 v) u<W u v:=K (by omega)
 have g5:W (a2 (op u (a1 (a1 v)))) (op u (a1 (a1 v)))<W u v:=
  K (by omega)
 rw[dif_pos g1] at hp1
 rw[hp1] at hp5
 rw[dif_pos g5] at hp5
 rw[dif_pos g3] at hp3
 rw[dif_pos g4] at hp4
 rw[hop]
 split
 ·rfl
 ·split
  ·rfl
  ·rename_i h1 h2
   exact absurd ⟨⟨t0,t1,hv.symm⟩,g1,(by rw[hp1];exact g5),g3,g4,
    (by rw[hp1];exact k1'),k2.symm.trans hp5.symm,k3.symm.trans hp3.symm,
    k4.symm.trans hp4.symm⟩ h2
def C (u v:M) (t0:tg v=2) (hv:a2 v=u) (t1:tg u=2) (t2:tg (a1 u)=2)
  (t3:tg (a2 u)=2)
  (k1:op u (a2 (a1 u))=J u (a2 (a1 u)))
  (k2:op (a2 (a1 u)) (a1 u)=a2 (a2 u))
  (k3:op (a1 (a2 u)) (a2 (a2 u))=a2 u)
  (k4:op (a1 u) (a2 u)=u)
  (k5:a1 v=a2 (a2 u))
  (k6:op (a1 v) u=v)
  (k7:sz (a1 v)<sz (a1 u)):op u v=a2 (a1 u):=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,hp1,-,-,hp4,hp5,hp6,hp7,hp8,hp9,-,hop⟩:=
  G u v
 have s0:=Y t0
 have s0':=E t0
 rw[hv] at s0'
 have q1:=Y t1
 have q1':=E t1
 have q2:=Y t2
 have q2':=E t2
 have q3:=Y t3
 have q3':=E t3
 have q4:=Z (a1 v)
 have hb:sz (a1 (a1 v))≤sz u:=by omega
 have g6:W u (a2 (a1 u))<W u v:=K (by omega)
 have g7:W (a2 (a1 u)) (a1 u)<W u v:=K (by omega)
 have g8:W (a1 (a2 u)) (a2 (a2 u))<W u v:=K (by omega)
 have g9:W (a1 u) (a2 u)<W u v:=K (by omega)
 have g4:W (a1 v) u<W u v:=K (by omega)
 rw[dif_pos g6] at hp6
 rw[dif_pos g7] at hp7
 rw[dif_pos g8] at hp8
 rw[dif_pos g9] at hp9
 rw[dif_pos g4] at hp4
 rw[hop]
 split
 ·rename_i h
  exfalso
  have c1:=h.2.2.2.2.2.1
  rw[dif_pos h.2.1] at hp1
  rw[hp1,I hb] at c1
  exact NY k7 q1 c1
 ·split
  ·rename_i h
   exfalso
   have c5:=h.2.2.2.2.2.2.1
   have g5:=h.2.2.1
   rw[dif_pos h.2.1] at hp1
   rw[hp1,I hb] at g5 hp5
   rw[dif_pos g5] at hp5
   rw[hp5] at c5
   simp only[a2_J_eq] at c5
   exact NX k7 q1 c5.symm
  ·split
   ·rfl
   ·rename_i h1 h2 h3
    exact absurd ⟨⟨t0,hv.symm,t1,t2,t3⟩,g6,g7,g8,g9,g4,
     k1.symm.trans hp6.symm,k2.symm.trans hp7.symm,k3.symm.trans hp8.symm,
     k4.symm.trans hp9.symm,k5.trans (k2.symm.trans hp7.symm),
     k6.symm.trans hp4.symm⟩ h3
def F (u v:M) (t0:tg v=2) (hv:a2 v=u) (t1:tg u=2) (t2:tg (a1 u)=2)
  (k1:op u (a2 (a1 u))=J u (a2 (a1 u)))
  (k2':tg (op (a2 (a1 u)) (a1 u))=2)
  (k3:op (a2 (op (a2 (a1 u)) (a1 u))) (op (a2 (a1 u)) (a1 u))=a2 u)
  (k4:op (a1 u) (a2 u)=u)
  (k5:a1 v=op (a2 (a1 u)) (a1 u))
  (k6:op (a1 v) u=v)
  (k7:sz (a1 v)<sz (a1 u)):op u v=a2 (a1 u):=by
 obtain⟨p1,p2,p3,p4,p5,p6,p7,p8,p9,p10,hp1,-,-,hp4,hp5,hp6,hp7,-,hp9,hp10,hop⟩:=
  G u v
 have s0:=Y t0
 have s0':=E t0
 rw[hv] at s0'
 have q1:=Y t1
 have q1':=E t1
 have q2:=Y t2
 have q2':=E t2
 have q4:=Z (a1 v)
 have q5:=T (a1 v)
 have hb:sz (a1 (a1 v))≤sz u:=by omega
 have g6:W u (a2 (a1 u))<W u v:=K (by omega)
 have g7:W (a2 (a1 u)) (a1 u)<W u v:=K (by omega)
 have g9:W (a1 u) (a2 u)<W u v:=K (by omega)
 have g4:W (a1 v) u<W u v:=K (by omega)
 have g10:W (a2 (op (a2 (a1 u)) (a1 u))) (op (a2 (a1 u)) (a1 u))<W u v:=by rw[← k5];exact K (by omega)
 rw[dif_pos g6] at hp6
 rw[dif_pos g7] at hp7
 rw[hp7] at hp10
 rw[dif_pos g10] at hp10
 rw[dif_pos g9] at hp9
 rw[dif_pos g4] at hp4
 rw[hop]
 split
 ·rename_i h
  exfalso
  have c1:=h.2.2.2.2.2.1
  rw[dif_pos h.2.1] at hp1
  rw[hp1,I hb] at c1
  exact NY k7 q1 c1
 ·split
  ·rename_i h
   exfalso
   have c5:=h.2.2.2.2.2.2.1
   have g5:=h.2.2.1
   rw[dif_pos h.2.1] at hp1
   rw[hp1,I hb] at g5 hp5
   rw[dif_pos g5] at hp5
   rw[hp5] at c5
   simp only[a2_J_eq] at c5
   exact NX k7 q1 c5.symm
  ·split
   ·rfl
   ·split
    ·rfl
    ·rename_i h1 h2 h3 h4
     exact absurd ⟨⟨t0,hv.symm,t1,t2⟩,g6,g7,(by rw[hp7];exact g10),g9,g4,
      k1.symm.trans hp6.symm,(by rw[hp7];exact k2'),k3.symm.trans hp10.symm,
      k4.symm.trans hp9.symm,k5.trans hp7.symm,k6.symm.trans hp4.symm⟩ h4
def L (x y z s1 s2 s3 s4:M)
  (e1:s1=op y x) (e2:s2=op z s1) (e3:s3=op x s2) (e4:s4=op s3 y) :
  op y s4=x:=by
 by_cases h3:op x s2=J x s2
 ·have E3:s3=J x s2:=e3.trans h3
  by_cases h2:op z s1=J z s1
  ·have E2:s2=J z s1:=e2.trans h2
   have h4:op s3 y=J s3 y:=by
    by_cases hh:op s3 y=J s3 y
    ·exact hh
    ·exfalso
     rcases X s3 y with hz | ⟨ty,ay,-⟩
     ·exact hh hz
     ·have qy:=U y ty
      rw[ay,E3,E2] at qy
      simp only[szJ] at qy
      have w1:=V (a1 y)
      have w2:=V z
      have w3:=V s1
      have w4:=V x
      by_cases h1:op y x=J y x
      ·have E1:s1=J y x:=e1.trans h1
       have e:=congrArg sz E1
       simp only[szJ] at e
       omega
      ·rcases X y x with hz3 | ⟨tx,ax,-⟩
       ·exact h1 hz3
       ·have d:=E tx
        rw[ax] at d
        omega
   rw[e4,h4,E3,E2]
   exact A y (J (J x (J z s1)) y) rfl rfl rfl rfl e1.symm h2
    (by rw[← E2];exact h3) (by rw[← E2,← E3];exact h4)
  ·rcases X z s1 with hz2 | ⟨t1,a1s,hD⟩
   ·exact absurd hz2 h2
   ·have h4:op s3 y=J s3 y:=by
     by_cases hh:op s3 y=J s3 y
     ·exact hh
     ·exfalso
      rcases X s3 y with hz | ⟨ty,ay,-⟩
      ·exact hh hz
      ·have qy:=U y ty
       rw[ay,E3] at qy
       simp only[szJ] at qy
       have w1:=V (a1 y)
       have w4:=V x
       have w5:=V s2
       by_cases h1:op y x=J y x
       ·have E1:s1=J y x:=e1.trans h1
        have hA1:a1 s1=y:=(congrArg a1 E1).trans (a1_J_eq y x)
        have hA2:a2 s1=x:=(congrArg a2 E1).trans (a2_J_eq y x)
        rw[hA2] at a1s
        rcases hD with hA | hB
        ·obtain⟨tv,hres,hfree,hsub⟩:=hA
         rw[hA1] at tv hres hfree hsub
         have hs2:s2=a1 y:=e2.trans hres
         rcases hsub with⟨ti,hi1,hi2⟩ | ⟨ti,hi⟩
         ·rw[← a1s,← hs2,← e3,ay] at hi1
          rw[ay] at ti
          have hd:=E ti
          rw[← hi1] at hd
          omega
         ·rw[← a1s,← hs2,← e3,ay] at hi
          rw[← hs2,ay] at hfree
          have ha2:a2 s3=s2:=(congrArg a2 E3).trans (a2_J_eq x s2)
          rw[ha2] at hi
          have hys:y=s3:=hfree.symm.trans hi
          rw[← hys] at ay
          have e:=congrArg sz ay
          have:=E ty
          omega
        ·obtain⟨tu,tau,hres,hq⟩:=hB
         rw[hA1] at hq
         have hs2:s2=a2 (a1 z):=e2.trans hres
         rw[← hs2] at hq
         rw[← a1s] at tu tau hs2 hq
         have d1:=E tau
         rw[← hs2] at d1
         have d2:=Y tu
         by_cases hf:op s2 (a1 x)=J s2 (a1 x)
         ·rw[hf] at hq
          have e:=congrArg sz hq
          simp only[szJ] at e
          omega
         ·have wq:=N hf
          rw[hq] at wq
          omega
       ·rcases X y x with hz3 | ⟨tx,ax,-⟩
        ·exact h1 hz3
        ·have d:=E tx
         rw[ax] at d
         omega
    have k0:sz s1<sz x+sz s2+sz y+2:=by
     have w5:=V s2
     by_cases h1:op y x=J y x
     ·have E1:s1=J y x:=e1.trans h1
      have e:=congrArg sz E1
      simp only[szJ] at e
      omega
     ·have wq:=N h1
      rw[← e1] at wq
      omega
    rw[e4,h4,E3]
    refine B y (J (J x s2) y) rfl rfl rfl ?_ ?_ ?_ h3 (by rw[← E3];exact h4)
    ·show tg (op y x)=2
     rw[← e1];exact t1
    ·show sz (op y x)<sz (J (J x s2) y)
     rw[← e1];simp only[szJ];omega
    ·show op (a2 (op y x)) (op y x)=s2
     rw[← e1,a1s];exact e2.symm
 ·rcases X x s2 with hz | ⟨t2,a2s,-⟩
  ·exact absurd hz h3
  ·have hL3:sz s3<sz s2:=by rw[e3];exact N h3
   have w3:sz x<sz s2:=by
    have q:=U s2 t2
    rw[a2s] at q
    have:=V (a1 s2)
    omega
   have h2:¬ (op z s1=J z s1):=by
    intro hc
    have E2:s2=J z s1:=e2.trans hc
    rw[E2] at a2s
    simp only[a2_J_eq] at a2s
    rw[a2s] at e1
    by_cases hf:op y x=J y x
    ·rw[hf] at e1
     have e:=congrArg sz e1
     simp only[szJ] at e
     have:=V y
     omega
    ·have q:=N hf
     rw[← e1] at q
     omega
   rcases X z s1 with hz2 | ⟨t1,a1s,hD2⟩
   ·exact absurd hz2 h2
   ·have w2:sz s2<sz s1:=by rw[e2];exact N h2
    have h1:op y x=J y x:=by
     by_cases hf:op y x=J y x
     ·exact hf
     ·exfalso
      have q:=N hf
      rw[← e1] at q
      omega
    have E1:s1=J y x:=e1.trans h1
    have hA1:a1 s1=y:=(congrArg a1 E1).trans (a1_J_eq y x)
    have hA2:a2 s1=x:=(congrArg a2 E1).trans (a2_J_eq y x)
    rw[hA2] at a1s
    rcases hD2 with hA | hB
    ·obtain⟨tv,hres,hfree,hsub⟩:=hA
     rw[hA1] at tv hres hfree hsub
     have hs2:s2=a1 y:=e2.trans hres
     rw[← hs2] at hfree
     rcases hsub with⟨ti,hi1,hi2⟩ | ⟨ti,hi⟩
     ·rw[← a1s,← hs2,← e3] at hi1
      have h4:op s3 y=J s3 y:=by
       by_cases hh:op s3 y=J s3 y
       ·exact hh
       ·exfalso
        rcases X s3 y with hz4 | ⟨ty2,ay,-⟩
        ·exact hh hz4
        ·rw[ay] at hi1 ti
         have hd:=E ti
         rw[← hi1] at hd
         omega
      rw[e4,h4]
      refine (C y (J s3 y) rfl rfl tv (by rw[← hs2];exact t2) ti ?_ ?_ hi2 ?_
       hi1 h4 ?_).trans ?_
      ·rw[← hs2,a2s];exact h1
      ·rw[← hs2,a2s,← e3];exact hi1
      ·rw[← hs2];exact hfree
      ·rw[← hs2];exact hL3
      ·rw[← hs2];exact a2s
     ·rw[← a1s,← hs2,← e3] at ti hi
      have h4:op s3 y=J s3 y:=by
       by_cases hh:op s3 y=J s3 y
       ·exact hh
       ·exfalso
        rcases X s3 y with hz4 | ⟨ty2,ay,-⟩
        ·exact hh hz4
        ·rw[ay] at hi
         by_cases hf2:op (a2 s3) s3=J (a2 s3) s3
         ·rw[hf2] at hi
          have e:=congrArg sz hi
          simp only[szJ] at e
          have:=V (a2 s3)
          omega
         ·have q:=N hf2
          rw[hi] at q
          omega
      rw[e4,h4]
      refine (F y (J s3 y) rfl rfl tv (by rw[← hs2];exact t2) ?_ ?_ ?_ ?_ ?_ h4
       ?_).trans ?_
      ·rw[← hs2,a2s];exact h1
      ·rw[← hs2,a2s,← e3];exact ti
      ·rw[← hs2,a2s,← e3];exact hi
      ·rw[← hs2];exact hfree
      ·rw[← hs2,a2s];exact e3
      ·rw[← hs2];exact hL3
      ·rw[← hs2];exact a2s
    ·obtain⟨tu,tau,hres,-⟩:=hB
     exfalso
     have hs2:s2=a2 (a1 z):=e2.trans hres
     rw[← a1s] at tu tau hs2
     have d1:=E tau
     rw[← hs2] at d1
     have d2:=Y tu
     omega
def law (x y z:M):op (y) (op (op (x) (op (z) (op (y) (x)))) (y))=x:=
 L x y z (op y x) (op z (op y x)) (op x (op z (op y x)))
  (op (op x (op z (op y x))) y) rfl rfl rfl rfl
def lhs:@EquationLHS M inst:=by
 intro x y z
 exact (law x y z).symm
end submission
def submission:Goal:=
 Exists.intro submission.M (Exists.intro submission.inst
  (And.intro submission.lhs submission.rhs))