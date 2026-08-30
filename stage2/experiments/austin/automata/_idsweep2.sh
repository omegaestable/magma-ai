#!/bin/bash
cd /c/Users/nacho/Documents/GitHub/magma-ai/stage2/experiments/austin/automata
export PYTHONIOENCODING=utf-8
PY=/c/Users/nacho/Documents/GitHub/magma-ai/.venv/Scripts/python.exe
for e in 12073 27859 21865 22591 9663 10222 12294 21864 24199; do
  timeout 600 "$PY" smallcheck.py $e 9 1 > gen/_id_$e.txt 2>&1
done
echo DONE > gen/_id_DONE
