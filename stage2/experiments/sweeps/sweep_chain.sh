#!/usr/bin/env bash
# Sequential deep-sweep chain.
#
# ONE audit at a time (rail 5e) -- never parallelise these. 16-worker pools
# competing for the same cores starve each other and manufacture "losses" that
# are not real. Each step is independent; a completed step is skipped on
# restart, so the chain resumes rather than redoes.
#
# STOPPING IT: TaskStop / Ctrl-C kills the shell but NOT the audit's worker
# pool, and the shell can relaunch a batch before it dies. Kill it like this:
#     powershell -NoProfile -Command "Get-CimInstance Win32_Process | \
#       Where-Object { \$_.CommandLine -like '*sweep_chain.sh*' -and \$_.Name -eq 'bash.exe' } | \
#       ForEach-Object { taskkill /F /T /PID \$_.ProcessId }"
#     powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | \
#       Where-Object { \$_.CommandLine -like '*audit_corpus*' } | \
#       ForEach-Object { taskkill /F /T /PID \$_.ProcessId }"
# then confirm `Get-Process python*` is empty before starting anything else.
#
# Launch detached:  nohup bash stage2/experiments/sweeps/sweep_chain.sh > chain.log 2>&1 &

cd /c/Users/nacho/Documents/GitHub/magma-ai || exit 1
PY=".venv/Scripts/python.exe"
WORKERS="${WORKERS:-20}"   # of 32 logical CPUs; 16 was ~100% sustained, 20 ~88%
export PYTHONIOENCODING=utf-8

run () {  # run <batch-stem> <row-budget-seconds, 0 = unbounded>
  local stem="$1"; shift
  local budget="$1"; shift
  local file="stage2/results/${stem}.jsonl"
  local out="stage2/results/audit-${stem}.json"
  if [ -f "$out" ]; then echo "### SKIP ${stem} (already audited)"; return 0; fi
  if [ ! -f "$file" ]; then echo "### MISSING ${file}"; return 0; fi
  echo "### START ${stem} $(date +%H:%M:%S)"
  local args=(--file "$file" --effort fast --workers "$WORKERS" --out "$out")
  if [ "$budget" != "0" ]; then args+=(--row-budget "$budget"); fi
  "$PY" stage2/experiments/audit_corpus.py "${args[@]}" 2>&1 | grep -Ev "^  ${stem}: [0-9]+/"
  "$PY" stage2/experiments/sweep_report.py --audit "$out" --batch "$file" \
        --out-prefix "stage2/results/${stem}" 2>&1 | head -2
  echo "### DONE ${stem} $(date +%H:%M:%S)"
}

# ---------------------------------------------------------------------------
# 2026-08-27: another 200,000 unseen order-4 rows, twenty 10k batches.
# Seed 20260827, excludes all 330,000 rows measured so far (the four
# 2026-08-20 batches + the 2026-08-25 10k/100k tracks + the 2026-08-26 200k
# batch) -- verified 0 overlap. Unbounded per row (matches every prior
# order-4 sweep, so all 530,000 rows measured across sessions stay ONE
# comparable population -- do not add a --row-budget here without renaming
# the run).
for b in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20; do
  run "etp-sweep-200k-2026-08-27-b${b}" 0
done

echo "### CHAIN COMPLETE $(date +%H:%M:%S)"
