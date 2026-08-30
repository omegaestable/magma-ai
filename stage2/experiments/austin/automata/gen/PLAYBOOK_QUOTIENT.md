# PLAYBOOK_QUOTIENT — the identity laws

Written 2026-08-29 (deep session 7) by the orchestrator, from the three independent design agents whose
synthesis died on the session limit. Their raw reports are in the workflow journal
`.claude/projects/.../subagents/workflows/wf_511b985a-b21/journal.jsonl`; everything they claimed that is
stated below has been **re-run and reproduced** rather than copied.

An *identity law* is one whose SEMANTIC free model fails — `python smallcheck.py <eq> 9 1` reports failures
on one-generator terms (see `gen/SEMANTIC_TABLE.md`). No rule set can repair it, because the rules only
decide `op`; the carrier itself has to change.

---

## 1. The result: two of the five are solved, three are proved impossible by this route

| law | rows | status |
| --- | --- | --- |
| **12073** | 0007, 0022 | **model validated**, three independent constructions, Lean skeleton compiles — only `theorem law` remains |
| **27859** | 0050, 0099 | **model validated**, Lean skeleton compiles — only `theorem law` remains |
| 21865 | 0039, 0057 | square-collapse **structurally unavailable** (proof below); needs the existential decoder |
| 21866 | 0020, 0028 | same, plus it is the 18,515-failure outlier |
| 22591 | 0017, 0052, 0069 | square-collapse **provably forces the trivial magma** (two-line proof below) |

Reproduced by the orchestrator 2026-08-29: `gen/q12073e.py` and `gen/q27859.py`, exhaustively over all 550
one-generator carrier terms of size <= 9 in both `x` and `y` — **302,500 assignments each, 0 failures**
(`z` is irrelevant: `op(z,z) = E` unconditionally, so it drops out of the law by construction).

---

## 2. The theorem that makes 12073 and 27859 work

Derived by hand, each step a legal instantiation of the law. For 12073, `x = y ◇ (((y◇x)◇x) ◇ (z◇z))`:

write `S_z = z◇z`, `psi_y(x) = (y◇x)◇x`, `E(y,z) = psi_y(y) ◇ S_z`.

* `x := y` gives `psi_y(E) = y`, hence `E(y,z') = y ◇ (y ◇ S_z)` — **E does not depend on z'**.
* instantiating `y` at a square `y = a◇a`, and taking `S_z = y` then `S_z = y◇y`, forces `E_y = y◇E_y = y`,
  hence `y◇y = y` and `y◇S = y` for every square `S`;
* finally `L[y := a◇a, x := b◇b]` collapses `psi` to `y` and gives `b◇b = a◇a`.

**So 12073 implies that all squares are equal and idempotent: `a◇a = e` for one constant `e`**, and the law
is equivalent to `a◇a = e` together with the *two-variable* law `x = y ◇ (((y◇x)◇x) ◇ e)`. That is the whole
trick: the offending variable `z` occurs only inside `z◇z`, the law forces every square to one element, and
once the carrier has that element as a **constructor**, `z` disappears definitionally instead of up to a
congruence — so no quotient type, no `Quot.sound`, no setoid.

27859 (`x = ((y◇(y◇x))◇x)◇(z◇z)`) is the only other open law where `z` occurs solely as `z◇z`, and the same
carrier works.

### The tag must be 0-ary

The handover proposed an argument-carrying tag `K y`. **Measured to cascade** — holes at `Q^3 u`, then
`Q^4 u`, and so on without end (`gen/q12073.py` … `q12073d.py` are that iteration history). The tag that
works is a single **nullary constructor** `E` identified with every square. Because `E` is a constructor
distinct from `g n` and `J _ _`, it is never itself decoded, its decoding is unique and trivial, and being
0-ary it can never grow — which is also what makes the well-founded measure go through.

---

## 3. The three carriers that work, ranked for the Lean proof

All three are validated. Pick by proof cost, not by elegance.

### (a) `gen/q12073e.py` + `gen/qlean12073.lean` — 3 constructors, 6 branches  ← recommended

```
carrier   M ::= g i | E | J u v
measure   msr u v = max (sz u) (sz v)^2 + sz u + sz v          (leangen's own gate)
op u v =
  R1 SQ    u = v                                          -> E
  R2 DEC   v = ((a◇b)◇E),  p := <u,b>,  <p,b> = (a◇b)     -> b
  R3 SELF  v = (d◇E),  u != E,  <E,u> = d                 -> u
  R4 GSC   v = (w◇E),  not (u = E and w = E),  <u,w> = E   -> ((E◇w)◇E)
  R5                                                      -> J u v
        where <a,b> = op a b when msr a b < msr u v, else J u v
```
Four gated nested calls; three of the four gates hold unconditionally on any real reading. R3/R4 are the
degenerate chains (`x = E`; `x` is the self-code of `u`), and they were **derived mechanically**, not
guessed: `gen/qfix.py` / `qfix2.py` saturate the least fixed point of the forced entries `op u (C_u x) = x`
over term pools — 302,522 entries over 550 terms, **zero collisions**, 324,331 of 324,926 generic and the
rest exactly these families. 27859 is the same carrier with 4 branches and 3 nested calls
(`gen/q27859.py`, `gen/qlean27859.lean`, 3,302 B).

### (b) `gen/nf12073.py` + `gen/nf12073.lean` — normal forms, 4 constructors, 8 branches

`M ::= g n | K | E t | J a b`; `op` computes straight into normal form, so the derived identity is true
between constructors. Skeleton is **3,153 B**, leaving ~16.8 KB of the cap for the proof. Its author's
assessment is the useful part: **the law needs NO induction** — it is a finite five-way case split on the
shape of `x` relative to `y`, because R3's guard is discharged by the definition of the middle product.
27859's version is 2,220 B, 4 branches, 2 calls.

### (c) `gen/qz_m24.py` + `gen/qz12073_skel.lean` — 4 constructors, 7 branches, the theorem-first build

`M ::= E | g n | P a b | C m` with `C` a **unary code** constructor, built directly on the theorem of §2.
Skeleton is **2,259 B** and compiles against row 0007's real JudgeProblem; the 41082 variant compiles
against row 0022's. Validated to **185,193,000 exhaustive assignments** at size <= 7 / 1 generator. Its
`law` plan: `sqE : op z z = E` (one unfold), `pushC : m != E -> op m E = C m`, reducing the goal to
`op y (C (psi y x)) = x`, then `op_cases` and a four-way split on `op y x`.

**Do not build a fourth.** Three independent designs converged; the remaining work is Lean.

---

## 4. Why 21865, 21866 and 22591 cannot use this — with the proofs

Two agents derived these independently and they agree.

**21865 and 21866: every element is a square.** Substituting every variable by `x` turns the law into
`x = (x◇(x◇x)) ◇ (x◇(x◇x))`, i.e. `x = W◇W` with `W = x◇(x◇x)`. So *every* element of any model is a
square. A carrier with one square constant `E` therefore forces `x = E` for all `x` — the trivial magma.
Square collapse, the mechanism that carries 12073 and 27859, is **structurally unavailable**. A free-magma
carrier is refuted on the spot for the same reason: its generators are not products at all.

**22591: square collapse forces the trivial magma, in two lines.** `x = (y◇(y◇x))◇((x◇x)◇z)`. Assume
`x◇x = e` for all `x`. Put `x = y = e`: `e = (e◇(e◇e))◇((e◇e)◇z) = (e◇e)◇(e◇z) = e◇(e◇z)`, so
**(*) `e◇(e◇z) = e` for every z**. Now put `y = e` with `x` arbitrary:
`x = (e◇(e◇x))◇((x◇x)◇z) = e◇(e◇z) = e`. Every element equals `e`. (22591 also forces every element to be a
square, via `y := x◇x`, `z := (x◇x)◇x`.)

**The natural unary-tag replacement is refuted too, by a conflict no rule can separate.** With a unary tag
`P` and rules `op u (J u q) = P u`, `op u (P a) = a`, `op u (P u) = P u`:
* 21866 at `y = z = g0`, `x = P g0`, `w = g0` gives `P(P g0)` where the law demands `P g0`;
* 21865 at `y = z = g0`, `x = P g0` gives `P(P g0)` where it demands `P g0`;
* 22591 at `y = g0`, `x = g0`, `z = P g0` gives `P g0` where it demands `g0`.

In each case **two instances of the law demand different values of the same product `(u,v)`**, so no
additional rule can fix it — a rule is a function of `(u,v)`.

**The obstruction has a name, and it is shared with Track B.** Both agents identified it as an
**existential decoder**: the payload has been destroyed on both sides at once because a term is
simultaneously a legal A-term and a legal B-term, so recovering it needs a rule that quantifies over a
forgotten witness rather than reading it out of the term. For 22591 the concrete refutation of the
two-sided-reading model (`gen/q22591b.py`, which survives 1,061,208 exhaustive assignments at size <= 7 and
5,722,200 with `y <= 9`) is
```
x = ((g0◇g0)◇((g0◇g0)◇g0)),  y = (g0◇(g0◇g0)),  any z   ->   got (((g0◇(g0◇g0))◇g0)◇(g0◇z)),  want x
```
because `op(y,x) = g0` and `op(x,x) = g0` are BOTH forced readings.

**This is the same mechanism Track B's 23357/23653 and 21864/24199 need** (the handover names it there as
"the existential decoder for both-compound laws"). Build it once, properly, and it is worth
**7 + 4 = 11 rows** — the single highest-leverage piece of mathematics left in this problem.

---

## 5. The validation standard for a quotient carrier

Everything in `WAVE2_PROMPT.md` §1, plus two tests that this session proved are necessary:

1. **The case tree** (from law 38565, session 7): enumerate the `2^k` free/decoded combinations of the `k`
   products in the law's own evaluation chain and construct one instance per reachable cell by chained
   encoding. Random and fuzz testing reach only the one or two shallow cells — 38565's hole occurred **0
   times in 30,000 random draws**.
2. **`qz_lib.identity_probe`** — build `x` out of the model's own codes, three levels deep. This killed
   four carriers (`gen/qz_m15/16/17/18.py`) that had each already passed 132,651–4,019,679 exhaustive
   assignments and 240,000 random tests, in **under 0.1 s**. The witnesses have size 23–35 and an exact
   internal shape, so no depth-bounded or random test can reach them. The theorem behind it also refutes,
   a priori, **any 12073 model whose carrier has two distinct squares**.

And the exhaustive check must run over the **whole inductive carrier** — `E`, `K`, `C` and all — not only
over `J`-terms. The `--values` restriction is useless at these sizes: the one-generator pool of terms of
size <= 9 in the *free* magma has 23 elements and all of them are values (measured).

---

## 6. What to do first

`gen/qlean27859.lean` (3,302 B, 4 branches, 3 nested calls) before `gen/qlean12073.lean`: both of 27859's
degenerate cases collapse into a single lemma — DEC and SELF both return `a2 u` — so its `law` case tree is
two leaves wide, and it de-risks the proof shape for 12073 at half the cost. Then 12073, whose four case
leaves are already named and each has a concrete witness family from the fixed-point probe, so the
"which coincidence can happen here" question that normally eats the iterations is already answered by data.

Four rows (0050, 0099, 0007, 0022), two `law` proofs, three compiling skeletons to choose from, and
~17 KB of byte budget free in each. This is proof work, not research.
