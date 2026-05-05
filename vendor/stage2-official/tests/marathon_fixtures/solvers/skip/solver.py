"""Marathon harness fixture: writes nothing, exits cleanly.

Used by the ``skip_path`` case to confirm:
* runner does not crash on an empty solver
* score path reports every problem as ``not_attempted``
"""
import sys
sys.exit(0)
