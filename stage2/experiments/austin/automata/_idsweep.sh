#!/bin/bash
cd /c/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata
export PYTHONIOENCODING=utf-8
export PY=/c/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe
run(){ e=$1; { echo "===== $e plain"; timeout 900 "$PY" smallcheck.py $e 9 1 2>&1 | tail -8; echo "===== $e values"; timeout 900 "$PY" smallcheck.py $e 9 1 --values 2>&1 | tail -8; } >> identities.out; }
export -f run
for e in 12073 27859 21865 22591 9663 10222 12294 24199 21864 21866; do echo $e; done | xargs -P 3 -I{} bash -c 'run "$@"' _ {}
echo DONE >> identities.out
