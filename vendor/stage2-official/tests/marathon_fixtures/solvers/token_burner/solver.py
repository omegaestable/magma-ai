"""Marathon harness fixture: sleeps; the proxy is preseeded over budget.

The harness sets ``OPENROUTER_API_KEY`` (so the proxy starts) and
``JUDGE_MARATHON_TEST_PRESEED_TOKENS`` (so the proxy's in-memory
counter is preloaded above the budget). The runner watchdog reads
that counter via ``proxy_handle.tokens_used()`` and SIGTERMs.

This replaces the older fixture body that wrote to
``<scratch>/tokens_used.txt`` directly — that file is no longer
consulted by the runner, so writing it is now inert (which is exactly
the trust-boundary fix this fixture pair regression-tests, alongside
``token_tamper_inert``).

Tests:
* runner enforces JUDGE_MARATHON_BUDGET_TOKENS via the proxy's
  authoritative in-memory counter
* ``tokens_exhausted`` flag is set in the run summary
"""
import signal
import sys
import time

signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
while True:
    time.sleep(60)
