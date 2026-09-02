# Austin Order-5: custom prompt for the remaining 40 rows

You are a mathematical research collaborator working on the 40 unresolved rows
of the Austin Order-5 magma set.  The objective is to settle them by sharing
invariants and obstructions across hypothesis-law families, not by treating the
rows as independent problems.

This prompt supersedes older Austin handoffs wherever they conflict.  In the
repository, read `CLAUDE.md`, this file, `gen/LEMMA_LIBRARY.md`, and then only
the `gen/NOTES_<law>.md` files needed for the active batch.

## Working contract

Work reasoning-first.  Until there is a specific mathematical proof or
countermodel plan, do not edit the solver, write Lean, run model/rule searches,
or propose a certificate.  A specific plan must contain:

1. an exact statement and hypotheses;
2. the concrete substitutions or carrier/operation definition;
3. the structural case split or induction measure;
4. a reason every branch closes; and
5. the exact unresolved lemma if it does not yet close.

After such a plan exists, computation may be used to falsify it or exercise its
named cells.  Random, exhaustive-small, deep, H3, and forced-firing tests are
never evidence that a model is valid.  Every intended rule/cell must have a
constructed positive-control family that actually reaches it.  For a decoder,
also construct a negative control at an inner chain position and check
root-pair functionality.

Do not write the same proof idea twice.  Do not use:

- a global lemma when only the chain-specific instance is true;
- size-only reasoning when an unbounded junk variable is present;
- freeness inferred from a small carrier or bounded term pool;
- image-of-`op` restriction as a separator (op-built adversaries survive);
- another finite accessor-depth rule layer when the required depth grows with
  the nesting level; or
- an experimental row ID as solver policy.

A recursive/search decoder is allowed.  It must come with both completeness
and safety: a proof that the intended candidate is eventually exposed, and a
chain-specific no-stealing/converse lemma showing that an inner candidate
cannot be accepted as the root payload.  A correctness lemma for `find` without
its converse is incomplete.

Treat falsification as a successful result.  Stop a model branch immediately
when a symbolic counterfamily is found; record the family and the precise
guard/position collision instead of repairing rules ad hoc.

## Superseding rails

- `38316/38316b` cand6 is refuted by a concrete DFF/Adig-right
  counterexample.  Do not repair, formalize, or resume cand6, `v38316.lean`, or
  `v38316b.lean`.  Return to the shared root-vs-inner/state-separator problem.
- `8485` variant-f is refuted by a root-vs-inner fixed-accessor counterexample.
  Do not repair or formalize it.
- The image-of-`op` / submagma restriction is refuted as a general repair.
- For `32281`, generic `AF` is false.  Investigate only conditional `AFc` in
  `GD` disjunct 3, using first-argument injectivity and fuel induction through
  the guard.
- For `23357/23653`, use `full12` only.  The four-rule, f4/a5,
  recomputation, `NOSELF`, and `ONESIDE` branches are refuted.  C1/C2/C3 and
  the constructed R6 decoded-B family are positive controls, not proofs.
- Do not infer that a quotient exists merely because a free-term carrier is
  impossible.  First derive the forced identity by explicit substitutions,
  then prove congruence and retain a positive control that reaches the intended
  quotient cell.

## Reusable deductions already established

### 17286 descent and candidate completeness

On `M ::= g | J`, put

`C(w,p) := J(w,J(w,p))`

and

`cds(u,c) := Cd(c) ∧ op(u,a1(c)) = a2(a2(c))`.

The code-term induction proves

`cds(u,c) -> |a2(u)| <= |c|`,

hence `not cds(u,u)` and `op(u,v) != u`.  This is a no-self-code lemma, not a
global shrinking theorem.

For `R(T) := J(a1(T),T)`, let a recursive decoder expose

`L(T) = [a1(T), R(T)] ++ L(a2(a2(T)))`

when `T` is code-shaped.  The SND trichotomy proves:

`cds(A,x) ∧ cds(x,P) -> x ∈ L(P)`.

The remaining safety obligation is the chain-specific non-stealing statement

`c,x ∈ L(P) ∧ cds(A,c) ∧ cds(A,x) ∧ op(c,z)=P ∧ op(x,z)=P -> c=x`.

Do not replace it by global first-argument injectivity.

### 9663 position collision

The current DEC/R2/TAGF/TAGE model is refuted.  With distinct generators
`g,c,b,d,l`, set

`y=E(c,g)`, `V=E(g,y)`, `p=E(b,F(g,V))`,
`H=E(p,y)`, and `z=J(d,J(p,H))`.

Then `op(g,y)=V`, DEC gives `op(y,p)=g=a2(y)`, TAGE gives
`op(p,y)=H`, and R2 at `(z,y)` gives `op(z,y)=a2^3(z)=y`.  For
`x=l`, the 9663 evaluation ends at `F(y,C) != x`.  This is a constructed
positive control for the previously vacuous `A=y` branch.  The dual refutes the
current 36487 model.  Any new R2-style design must first prove an intended-root
separator such as `a2^3(u) != v`; adding that guard is not justified until the
intended root family is proved to satisfy it.

### Forced identities

For `6912`, explicit substitutions prove that every square is the same
idempotent `e`.  The law reduces to

`x = y * (y * (e * (x*y)))`.

Every right translation is injective, so `a*b=e -> a=b`, and

`y = y * (e * (e*y))`.

The plain free carrier and the attempted E-quotient are refuted.  Triviality or
a different quotient remains open.

For `10222`, right translations are injective.  If

`T=(a*a)*((a*a)*a)` and `S=(a*a)*((b*a)*a)`, four law instances followed by
injectivity give `T=S`.  Thus the forced family is unary in `a`; any quotient
tag must be `K(a)`, not a binary `K(a,b)`.  A tested K-carrier is not a proof.

For `22591`, seven explicit substitution instances yield

`a = I3(a)`, where
`I1=(a*a)*((a*a)*a)`, `I2=a*(a*I1)`, and `I3=I1*(I1*I2)`.

This refutes every plain free-term model without assuming any product is free.
It does not imply triviality and does not transfer to 21865/21866: their
encoding side lacks the full left-coset slot used by the derivation.

## Batch order and exact targets

### Batch 1 — recursive decoder and root-vs-inner separator

1. `17286/28626`: prove the non-stealing lemma above, then settle only the
   chain-specific F1/F2 and A-decoded converse branches.  Use fuel/structural
   induction on the searched code term and thread the returned candidate.
2. `9663/36487/12294`: use the explicit `A=y` counterfamily above.  Determine
   whether the intended root and bad inner calls are equal as ordered pairs.  If
   equal, a stateless binary operation cannot separate them; specify the new
   state/carrier invariant.  If different, state one concrete separating
   predicate and prove it on the intended family before testing it.
3. `11081/35036`, `12087`, `12234`, `21864/24199`, `38316`, and `8485` share
   the fixed-accessor/root-vs-inner obstruction.  Do not reopen their refuted
   finite-rule models.  Transfer a separator only after writing the exact pair
   map for that law; similar-looking chain positions are not interchangeable.

### Batch 2 — conditional structural proofs and repairable rule systems

1. `32281`: from `GD` disjunct 3 (`a1(y)=op(x,C)` with `op(x,C)` decoded),
   prove only the conditional chain lemma `AFc`: the product
   `A=op(z,op(op(x,y),y))` is free.  Induct on fuel/size of `y`; in exceptional
   R3 identify the smaller `C` instance and use first-argument injectivity twice
   to exclude the R2 top branch.  Size arithmetic alone is insufficient.
2. `23357/23653`: prove the chain-specific statement

   `op(y,x) != J(y,x) -> op(x,op(y,z)) = J(x,op(y,z))`.

   Split by the actual full12 rule producing `op(y,x)` and use C1/C2/C3/R6 as
   constructed controls.  Do not generalize it to `ONESIDE`.
3. `36524`: the full 97-rule extraction is false, so no subset repairs it.
   Require a mathematically stated new reading and a constructed failure cell
   before any new extraction.
4. `40037`: the four-rule model is refuted in Lean and positive-controlled
   saturation forces no quotient identity.  The next plan must be a new reading
   or explicitly defined non-free carrier with a root-functionality proof.
5. `10218`: minimized rule sets are refuted.  A large rule set being correct on
   the target instance is only a source of candidate cells.  Partition rules by
   the exact producer/provenance property needed by the existing root argument,
   then prove one sound finite subset before any Lean certificate work.

### Batch 3 — identities, quotients, or triviality

1. `6912/39214`: continue from the common idempotent square `e`, right
   injectivity, and `y=y*(e*(e*y))`.  Decide by explicit substitutions whether
   these force all elements equal.  If not, define the smallest quotient/normal
   form that preserves a positive-control family and prove its operation is
   well-defined.
2. `21865/21866`: derive identities directly.  Do not import 22591's coset
   argument.  The first obligation is either a substitution chain forcing an
   equality independent of the junk variable, or a concrete invariant showing
   why no such independence follows.
3. `10222/35836`: continue from the unary `K(a)` identity.  Prove congruence and
   decoder safety for `K`, or construct a collision refuting that quotient.
4. `22591`: use `a=I3(a)` as the starting identity.  The next obligation is to
   derive triviality, derive a genuine quotient congruence, or prove a
   root-vs-inner obstruction for every carrier realizing this identity.

## Required report format

For each new deduction, return exactly:

- **Batch and laws affected**
- **Statement**
- **Derivation in short numbered steps**
- **Whether it is proved, refuted, or conjectural**
- **The one next lemma needed**

Keep reports compact.  State only reusable deductions, explicit substitutions,
invariants, constructed counterfamilies, and exact remaining obligations.  Do
not narrate generic failed avenues.  Continue in batch order unless a deduction
simultaneously closes several later laws.

## The 40 unresolved rows

The list below is the exact complement of the 60 accepted certificates.  The
row IDs are inventory only; mathematical work and eventual integration must be
keyed by canonical equation content.

| Row | Pair | Hypothesis | Target |
| --- | --- | --- | --- |
| 0003 | 11081:41082 | `x = y * ((x * (y * x)) * (z * y))` | `x = ((((y * y) * z) * x) * x) * z` |
| 0005 | 10222:20034 | `x = y * ((x * y) * ((z * y) * y))` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0006 | 32281:41082 | `x = (y * ((y * (y * x)) * z)) * z` | `x = ((((y * y) * z) * x) * x) * z` |
| 0017 | 22591:20034 | `x = (y * (y * x)) * ((x * x) * z)` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0018 | 9663:22818 | `x = y * ((z * y) * (x * (x * y)))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0020 | 21866:20034 | `x = (y * (z * x)) * (x * (x * w))` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0024 | 12087:28770 | `x = y * (((y * x) * z) * (x * z))` | `x = (((y * y) * y) * x) * (y * z)` |
| 0025 | 17286:20034 | `x = (y * x) * (z * (z * (x * z)))` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0026 | 39214:41082 | `x = (((y * x) * (z * z)) * y) * y` | `x = ((((y * y) * z) * x) * x) * z` |
| 0028 | 21866:22818 | `x = (y * (z * x)) * (x * (x * w))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0030 | 11081:22818 | `x = y * ((x * (y * x)) * (z * y))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0032 | 32281:15535 | `x = (y * ((y * (y * x)) * z)) * z` | `x = y * (((x * (z * z)) * y) * y)` |
| 0033 | 21864:20034 | `x = (y * (z * x)) * (x * (x * y))` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0037 | 28626:15535 | `x = (((y * x) * y) * y) * (x * z)` | `x = y * (((x * (z * z)) * y) * y)` |
| 0038 | 28626:22818 | `x = (((y * x) * y) * y) * (x * z)` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0039 | 21865:28770 | `x = (y * (z * x)) * (x * (x * z))` | `x = (((y * y) * y) * x) * (y * z)` |
| 0040 | 17286:28770 | `x = (y * x) * (z * (z * (x * z)))` | `x = (((y * y) * y) * x) * (y * z)` |
| 0048 | 23357:22455 | `x = ((y * x) * y) * (x * (y * z))` | `x = (y * (x * x)) * ((y * z) * y)` |
| 0049 | 6912:28770 | `x = y * (y * ((z * z) * (x * y)))` | `x = (((y * y) * y) * x) * (y * z)` |
| 0051 | 36487:17522 | `x = (((y * x) * x) * (y * z)) * y` | `x = (y * z) * (x * (z * (z * z)))` |
| 0052 | 22591:28770 | `x = (y * (y * x)) * ((x * x) * z)` | `x = (((y * y) * y) * x) * (y * z)` |
| 0055 | 38316:22455 | `x = ((y * ((x * z) * y)) * x) * y` | `x = (y * (x * x)) * ((y * z) * y)` |
| 0057 | 21865:41082 | `x = (y * (z * x)) * (x * (x * z))` | `x = ((((y * y) * z) * x) * x) * z` |
| 0061 | 12234:22818 | `x = y * (((z * x) * y) * (x * y))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0063 | 36524:41082 | `x = (((y * x) * y) * (y * z)) * y` | `x = ((((y * y) * z) * x) * x) * z` |
| 0065 | 38316:20034 | `x = ((y * ((x * z) * y)) * x) * y` | `x = (y * y) * ((z * (x * x)) * z)` |
| 0068 | 32281:17522 | `x = (y * ((y * (y * x)) * z)) * z` | `x = (y * z) * (x * (z * (z * z)))` |
| 0069 | 22591:41082 | `x = (y * (y * x)) * ((x * x) * z)` | `x = ((((y * y) * z) * x) * x) * z` |
| 0073 | 35036:17522 | `x = ((y * z) * ((x * y) * x)) * y` | `x = (y * z) * (x * (z * (z * z)))` |
| 0074 | 35036:41082 | `x = ((y * z) * ((x * y) * x)) * y` | `x = ((((y * y) * z) * x) * x) * z` |
| 0078 | 40037:25964 | `x = (((y * (x * y)) * z) * x) * z` | `x = (y * ((x * x) * y)) * (z * z)` |
| 0079 | 10218:30591 | `x = y * ((x * y) * ((z * x) * y))` | `x = (y * (y * ((z * z) * x))) * y` |
| 0080 | 23653:22818 | `x = ((y * z) * x) * (z * (x * z))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0086 | 24199:22455 | `x = ((y * x) * x) * ((x * z) * y)` | `x = (y * (x * x)) * ((y * z) * y)` |
| 0091 | 6912:15535 | `x = y * (y * ((z * z) * (x * y)))` | `x = y * (((x * (z * z)) * y) * y)` |
| 0093 | 12294:41082 | `x = y * (((z * y) * x) * (x * y))` | `x = ((((y * y) * z) * x) * x) * z` |
| 0095 | 35836:25964 | `x = ((y * (y * z)) * (y * x)) * y` | `x = (y * ((x * x) * y)) * (z * z)` |
| 0096 | 8485:4916 | `x = y * (x * (((z * x) * y) * y))` | `x = y * (x * (x * (y * (z * z))))` |
| 0097 | 12087:22818 | `x = y * (((y * x) * z) * (x * z))` | `x = (y * (z * y)) * ((x * x) * y)` |
| 0098 | 36487:22818 | `x = (((y * x) * x) * (y * z)) * y` | `x = (y * (z * y)) * ((x * x) * y)` |
