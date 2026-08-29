# 2026-08-28 — The Austin research set: first models, first accepted certificates

Companion to `2026-08-28-assessment-deterministic-austin-tidy.md` §2 (which
ended the day before at 0/100 with every automated construction dead).
Every number below is measured; the judge is Lean 4.33.1 through
`stage2/experiments/judge_cert_text.py` at the deployed caps.

## Headline

| Metric | Value |
| --- | --- |
| Rows accepted by the real judge | **10 / 100** (was 0): `0009`, `0047`, `0056` (eq1 11116); `0013`, `0090` (5066); `0062` (4952); `0046` (34888, dual of 11116); `0088` (41252, dual of 4952) — tag automata; `0100` (25087) and `0043` (20911, its dual) — piecewise-linear models over ℚ |
| Hypotheses with a verified infinite model | 8 of 69 (11116, 5066, 4952, 34888, 41252, 25087, 20911, and the control 28770 — Kisielewicz's law, whose automaton the search rediscovers, repair included) |
| Certificate size / judge time | 2.7–11.6 KB, 5–46 s (FALSE cap 20,000 B, 300 s) |
| Shipped | all 10 as `false:distilled:aus_e<eq1>_e<eq2>` in `DISTILLED_CERTS`, byte-pinned in `judge_verified_certs.jsonl` (+10 fixture lines carrying their own equations, rail 16) |
| Second construction family | **piecewise-linear over ℚ** (Le Floch's 2025 shape for 13102): 25087 `x = (y◇(x◇(x◇y)))◇(z◇z)` has `x◇y = −x/2+y/2 if y ≤ 0 ∧ x ≤ y; −x/2+y if 0 ≤ y ∧ x ≤ 0; −x+y otherwise` (exact on 30,000 rationals, refutes 4916 at (1,0,0)); the mirrored operation is a model of the dual 20911 refuting 20034. Found by a 3-region sweep with coefficients in {0, ±½, ±1, ±2} over the 69 hypotheses: **1 hit in 69** at that width; a wider sweep is running. Lean: a 4-way *linear-region lemma* for `op x y`, nested `rcases` in evaluation order with `linarith` pruning, refutation by `norm_num`; the carrier must be hidden as `def submission.carrier := ℚ` because `Rat` is not on the judge's allowlist (rail 25) |
| TRUE side (Track C) | Prover9, 300 s, all 169 problems (100 rows + 69 `eq1 ⇒ x = y`): **169 timeouts, 0 proved**. Consistent with Vampire; the rows are on the model side |

These are, to the best of the literature search (ETP blueprint, final ETP
paper Dec 2025, the order-5 Zulip thread), the first infinite models of any
Table-2 law: teorth has a Lean model only for 28770 among the ten Austin laws,
and none for the 96 Table-2 laws.

## The construction: tag automata = term models with a few rules

Carrier: an inductive type `M` with generators `g : Nat → M` and tag
constructors (`J : M → M → M` the free product, `S : M → M` the square, and
any stage tags). `op u v` is an ordered list of pattern rules with equality
guards, default `J u v`. The rules check as *little* as possible about the
off-spine argument — Kisielewicz's `(3^y 5^x) ◇ z = x` ignores `z` — and the
recognisable structure is the term model's own (`S y` for `y ◇ y`, nested
`J`s). Example, 11116 `x = y ◇ ((x ◇ (z ◇ x)) ◇ (y ◇ y))`:

```
u ◇ u                  = S u
u ◇ J (J a b) (S u)    = a
u ◇ v                  = J u v      otherwise
```

Three rules. 5066 `x = y◇(y◇(x◇(y◇(z◇y))))` and 4952 are two-rule models
(root projection + one exception).

## The tooling (scratchpad `engine/`, to be promoted to `stage2/experiments/austin/automata/`)

| Piece | What it does |
| --- | --- |
| `symb.py` | **Complete** symbolic verifier: case splits on constructors, unification with the occurs check (= the "level" argument), deferred equality checks, `AS` whole-subterm bindings. 0 failing leaves is a proof that the law holds for every element of `M` — replaces rail 37's depth-bounded random checker |
| `synth.py` | Seeds (root-rule term models at several depths, stage-tag spine models, squares on/off) + CEGIS repairs (projection at the root, keep-rules blocking wrong firings, *directed* repairs that keep exactly the paths to `x` and to the early-unload payload), global best-first with lazy verification, rule minimisation, dualisation, orientation check |
| `render2.py` | Lean certificate mirroring the verifier's binary case tree: `by_cases h : tg t = k` + `obtain ⟨…, rfl⟩`, `by_cases` on equalities with `subst`/`injection`, leaves closed by `simp (disch := (try simp only [sz]) <;> (try omega)) [op, eqf, *]` where `eqf : sz a ≠ sz b → (a = b) = False` discharges every cyclic equality |
| `pipeline.py` / `ship.py` | one certificate per row, bulk judge, ledger; fixture lines + `DISTILLED_CERTS` entries keyed by the solver's `canonical_eq_text` |

Renderer lessons that cost real judge round-trips: `rcases` n-way splits blow
the tree up (600 KB) where binary tests give 7 KB; `simp [tg]` unfolds a
variable argument into a stuck `match` — expose accessors only through
constructor-case `@[simp]` lemmas; `simp` needs both orientations of every
disequality hypothesis (`Ne.symm h`); the discharger must fail silently
(`try`), else `omega`'s failures are logged as errors; the 20,000-byte FALSE
cap is UTF-8 bytes of source, so the certificate is the *tree*, not the model.

## The hard family, and what is now understood

**Orientation theorem.** A term model with free products can only exist when
the innermost spine product has `x` on the left (`x ◇ y`, `y` bare) or a
compound off-spine term. With `y ◇ x` innermost and `y` bare, the forced
early unload (`x` of root shape ⇒ `y ◇ x` = payload) hits every `x` with that
payload, contradicting the injectivity of `L_y` that the law itself forces.
Ten hypotheses are bad-orientation (32280, 32281, 35836, 36524, 36713, 38565,
39163, 39214, 40909, 40951); they must be solved on the dual and dualised
back (`synthesize_any`).

**Early unloads.** Every failure of a root-rule model is an inner product that
is itself a law instance (e.g. 5107 `x ◇ y` with `y = x◇(x◇(z'◇(x'◇x)))`
returns `x'`), after which the chain seen by the root is shorter and its
bottom is a payload. The exact repair is the critical pair: "the root fires
when the bottom equals the payload stored inside `u`" (ρ₂), then ρ₃ for the
next unload position, … Exact critical-pair completion on 5107 diverges
(rules of depth 20+, trees of 28,000 leaves after 11 rules); the limit object
is the semantic fixed-point model `op u v = x iff v = op(u, op(u, op(z,
op(x, u))))` for some `x, z`, which is definable by well-founded recursion but
needs an *inductive* proof — outside what the symbolic verifier (finite case
analysis) or a 20 KB certificate can carry today.

**Search under load (rail 5e again).** Per-verification wall-clock deadlines
under 12-way parallelism produced spurious "none"s on laws that solve in
seconds in isolation (5066, the 28770 control); verification is now capped by
leaf count, deterministic under load.

## Negative results (do not re-run)

| Idea | Result |
| --- | --- |
| Prover9 300 s on all 169 TRUE-side problems | 169 timeouts |
| Recursive self-consistency check inside the symbolic verifier | unbounded unfolding; bounded unfolding with unknowns reports failures at depth 1–3 (the model as written is incomplete: short chains after two early unloads are not covered) |
| Exact critical-pair completion (5107, 5012, 5837) | diverges; rule depth and tree size grow without bound |
| Blind CEGIS search on the hard family (batches 3–7, 600–900 s per law) | 0 of the all-bare-variable laws; 0 of 5012/5837/6912/… (compound off-spine but early unloads inside the off-spine term) |
