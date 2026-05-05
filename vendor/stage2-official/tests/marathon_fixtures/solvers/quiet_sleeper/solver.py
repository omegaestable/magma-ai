"""Marathon harness fixture: a solver that simply sleeps a few seconds
and exits cleanly with no LLM activity.

Used by ``watchdog_uses_settled_only``: the harness preseeds the proxy's
``_tokens_reserved`` counter to exceed the budget — pre-fix the watchdog
read ``settled + reserved`` and would have SIGTERMed this idle solver
even though no real cost was incurred. With the watchdog reading
``settled`` only, the run completes cleanly.

We do not call the LLM and do not write any answer rows; the assertion
is purely about the runner's lifecycle (exit_code, sigterm_fired,
tokens_exhausted=False).
"""
import time

# Sleep just under the case's wall-clock budget so the runner has
# multiple watchdog ticks to (incorrectly, pre-fix) observe the
# preseeded reservation. 4s is enough for ~8 watchdog polls at the
# 0.5s interval; cases use budget_seconds=10.
time.sleep(4.0)
