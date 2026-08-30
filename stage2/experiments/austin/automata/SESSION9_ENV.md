# Session 9 environment — READ FIRST (rebuilt 2026-08-30)

`vendor/stage2-official/.artifacts/` was **deleted** since session 8. It has been rebuilt.
Everything below is verified working as of this session's start.

## Compile a certificate (fast loop, ~1-2 s warm)

```bash
cd /c/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata
A=/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official/.artifacts
D=$A/dev_<eq1>_<eq2> bash devlean2.sh gen/<yourfile>.lean
```

Output ends with `exit=0 secs=N bytes=B`. `exit=0` **with only `declaration uses 'sorry'` warnings**
means everything else compiles. Any `error:` line is a real failure.

### Dev dirs already built for you

`dev_38316_22455`, `dev_38316_20034`, `dev_23357_22455`, `dev_23653_22818`,
`dev_17286_20034`, `dev_17286_28770`, `dev_28626_15535`, `dev_28626_22818`,
`dev_32281_41082`, `dev_32281_15535`, `dev_32281_17522`, `dev_5107_22818` (generic).

Need another row's dir:
```bash
export PATH="$HOME/.elan/bin:$PATH"
cd /c/Users/nacho/Documents/GitHub/magma-ai
./.venv/Scripts/python.exe stage2/experiments/austin/automata/devrow.py <eq1> <eq2>
```

## Toolchain gotcha that will waste your time

On Windows `lean` is an elan shim resolving the toolchain **from the working directory**.
Outside `vendor/stage2-official/` it is **4.30.0-rc2**; inside (and inside `.artifacts/*`, which is
under it) it is the pinned **4.33.1**. `devlean2.sh` cds into the dev dir, so it is correct.
Never invoke `lean` from the repo root — you will get 4.30 and `incompatible header` olean errors.

## Judging (the orchestrator does this — you compile, it judges)

Fixed this session: `jlock.judge_env()` now prepends `~/.elan/bin` to PATH. Without it the judge
returns `JudgeInfrastructureError: missing lean binary: lean`, which `verify_certs.py` reported only
as `infra_error` — indistinguishable from a broken certificate. It was latent through session 8
because an interactive shell had already exported elan. `verify_certs.py` now prints the judge's
`error_code` next to any non-accepted row, so an environment failure is one run from diagnosis.

Verified working from a deliberately stripped PATH: `verify_certs.py --only <rows> --workers 2`,
2/2 accepted, 2.6 s and 4.2 s.

**An `exit=0` compile is not acceptance.** The judge is the arbiter for a row; the Lean kernel is
only the arbiter for the proof. Do not report a row as done on a compile alone.

## Byte cap

FALSE certificates: **20,000 bytes hard**, judged on UTF-8 length. The solver ships 500 B under.
`bytes=` in the compile output is the number that matters. `python squeeze.py <file> --rename`
compresses a finished proof; **`squeeze.py` is NOT idempotent** (rail 56b) — squeeze the readable
source once, and compile whatever you judge.

## Method docs, in reading order

1. `gen/LEMMA_LIBRARY.md` (~95 KB) — the twelve-rung oracle ladder, the reusable Lean invariants
   (`FD`, `ND1`, `mx`, `mxl`, `TR`/`SND`, `Z`, `Y`, `ZP`), the carrier designs. Has a TOC keyed to
   what you are doing. **Read the rows of that table that match your task, not the whole file.**
2. `gen/NOTES_<eq>.md` — your law's specific state.
3. `../../../docs/DEEP_SESSION_8_AUSTIN_HANDOVER.md` — score and per-law state.

## Non-negotiables

* **No `sorry` in anything you hand back.** Report honestly if you do not finish.
* **Banned in certificates**: `macro`, `run_cmd`, `run_elab`, `@[init`, `skipKernelTC`,
  `notation`, `notation3`, `infix`, `infixl`, `infixr`, `prefix`, `postfix`. Scanned over raw
  text **including comments**. `simp` and `omega` are fine (many shipped certs use them).
* **A model you did not validate is a false model.** Seven models in session 8 passed ~10^6
  validation chains and were still false. If you change the *model* (not just the proof), you owe
  the oracle ladder in `LEMMA_LIBRARY.md`. If you only write Lean against an already-validated
  model, you do not.
* The Lean kernel is the arbiter for the proof; the real judge is the arbiter for the row.
  **Do not claim a row is done because a proof "should" work — compile it.**

## Reporting back

State: the file path, its `bytes=`, its exact sorry count, and what remains. If you finish, say
`READY: gen/<file>.lean for rows <ids>`. If you do not, say exactly what is left and what you tried.
Write findings into `gen/NOTES_<eq>.md` **as you go**, not at the end.
