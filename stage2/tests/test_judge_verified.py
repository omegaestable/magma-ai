"""Regression gate for certificates the proof kernel cannot check.

Most TRUE certificates are verified exactly by `ProofKernel`. A minority — the
hand-written `*_block` combinator proofs and the nested-`have` collapse proofs —
fall outside that grammar (`classify_true_certificate` -> "other"). For those,
offline evidence is weak, and for the `*_singleton` / `*_collapse` family it is
absent altogether: those routes assert eq1 forces a one-element magma, and the
trivial magma satisfies every equation, so model-checking them is vacuous by
construction. Measured 2026-07-29: 10 official certificates had *no* offline
verification of any kind.

So they are pinned against the real Lean judge instead. Every entry in
`stage2/fixtures/judge_verified_certs.jsonl` is a certificate that
`judge.verify.verify_answer` returned `accepted` for, stored byte-for-byte. This
test re-solves the row and asserts the builder still produces exactly that text.

If a test here fails, the builder changed. That is not automatically a bug — but
the new certificate has no judge evidence, so re-verify and re-pin:

    python stage2/experiments/judge_rows.py --ids <row-id>
    python stage2/experiments/judge_rows.py --from-audit <audit.json> \
        --shape other --write-fixture

Never edit the fixture by hand: its whole value is that a human did not write it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

import oracles

FIXTURE_PATH = (Path(__file__).resolve().parents[1]
                / "fixtures" / "judge_verified_certs.jsonl")


def _load() -> list[dict]:
    if not FIXTURE_PATH.exists():
        return []
    return [json.loads(line) for line in
            FIXTURE_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]


ENTRIES = _load()


@pytest.mark.skipif(not ENTRIES, reason="no judge-verified certs pinned yet")
@pytest.mark.parametrize(
    "entry", ENTRIES, ids=[f"{e['route']}:{e['id']}" for e in ENTRIES])
def test_judge_verified_cert_unchanged(solver, problems_by_id, entry):
    problem = problems_by_id.get(entry["id"])
    if problem is None:
        pytest.skip(f"problem {entry['id']} not present locally")

    record = solver.solve_problem(problem, false_time_budget=5.0)
    assert record is not None, (
        f"coverage regression: {entry['id']} was solved by {entry['route']} "
        f"and judge-accepted on {entry['verified_on']}, now skipped")

    got_route = str(record["route"])
    code = record["answer"]["code"]

    # Route selection is wall-clock nondeterministic (documented): under load a
    # bespoke route can lose its race to a general closure engine. That produces
    # a different — still oracle-checked — certificate, which is not a
    # regression in the builder this entry pins.
    if got_route != entry["route"]:
        pytest.skip(f"route drifted {entry['route']} -> {got_route} "
                    f"(timing); nothing to compare")

    assert record["answer"]["verdict"] == entry["verdict"]
    # The banned-tactic rule applies here too: a cert that reintroduced `grind`
    # would still be byte-identical only if nothing changed, but be explicit.
    oracles.check_no_banned_tactics(code, got_route)

    assert code == entry["code"], (
        f"{entry['id']}: {got_route} no longer emits the certificate the Lean "
        f"judge accepted on {entry['verified_on']} "
        f"({entry['judge_seconds']}s). The proof kernel cannot check this "
        f"shape, so the new text has no correctness evidence. Re-verify with "
        f"stage2/experiments/judge_rows.py --ids {entry['id']} and re-pin.")


@pytest.mark.skipif(not ENTRIES, reason="no judge-verified certs pinned yet")
def test_pinned_certs_are_all_judge_accepted():
    """The fixture may only contain certificates the real judge accepted."""
    for entry in ENTRIES:
        assert entry["judge_status"] == "accepted", entry["id"]
        assert entry["code"].strip(), entry["id"]
