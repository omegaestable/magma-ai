#!/bin/bash
cd /c/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata
export PYTHONIOENCODING=utf-8
export PY=/c/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe
run(){ echo "== $1" >> smallcheck_missing.out; timeout 900 "$PY" smallcheck.py "$1" 9 1 2>&1 | tail -1 >> smallcheck_missing.out; }
export -f run
for e in 32281 34889 36524 38565 40037 33020 38316 23354 28626 23357 23653 35836 36487 9663 32294 35036 12883 39214 5837; do echo $e; done | xargs -P 4 -I{} bash -c 'run "$@"' _ {}
echo DONE >> smallcheck_missing.out
