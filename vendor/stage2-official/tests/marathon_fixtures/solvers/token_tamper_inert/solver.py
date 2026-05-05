"""Marathon harness fixture: writes garbage to <scratch>/tokens_used.txt
to attempt the old file-tampering attack, then exits cleanly.

Pre-fix, the runner watchdog read ``<scratch>/tokens_used.txt`` for
authority. A solver could write a number above the budget to spoof
exhaustion (or below to mask real overage). After the fix the runner
reads the proxy's in-memory counter via ``proxy_handle.tokens_used()``
under a lock, and the on-disk telemetry file lives in a runner-private
directory the solver has no env reference to.

This fixture proves the attack is now inert: it writes a value far
above the budget, then exits 0. The harness asserts that
``tokens_exhausted == False`` and ``sigterm_reason != 'tokens'`` —
i.e., the bogus write had no effect on runner behavior.
"""
import os
import time
from pathlib import Path

scratch = Path(os.environ["JUDGE_MARATHON_SCRATCH_DIR"])
scratch.mkdir(parents=True, exist_ok=True)
cap = int(os.environ.get("JUDGE_MARATHON_BUDGET_TOKENS", "0"))

# Old attack vector: write a value that pretends the budget was burned
# many times over. Pre-fix, the runner watchdog would see this and
# SIGTERM with reason="tokens".
(scratch / "tokens_used.txt").write_text(str(cap * 1000 + 1))
# Try a few common typo / sibling variants for paranoia — none should
# fool the post-fix watchdog either.
(scratch / "tokens_used.tmp").write_text(str(cap * 1000 + 1))

# Sleep through a couple of watchdog poll cycles (~0.5 s each) so the
# runner gets multiple chances to inspect the bogus file before we
# exit. Pre-fix this would SIGTERM us with reason="tokens"; post-fix
# the runner reads the proxy's in-memory counter (0) and lets us
# finish.
time.sleep(2.0)

