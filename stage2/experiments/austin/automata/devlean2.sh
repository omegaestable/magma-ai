#!/bin/bash
# D=<dev dir from devrow.py> bash devlean2.sh <file.lean> : fast local compile of a certificate against that row's JudgeProblem.
[ -z "$D" ] && { echo "set D=<dev dir>"; exit 1; }
cp "$1" "$D/Submission.lean"
cd "$D" || exit 1
export PATH="$HOME/.elan/bin:$PATH"
export LEAN_PATH="$(cygpath -w "$PWD");$(cat leanpath.txt)"
W=$(cygpath -w "$PWD")
S=$(date +%s)
timeout ${T:-300} lean --root="$W" -D linter.defProp=false -o "$W\Submission.olean" Submission.lean 2>&1 | head -c ${C:-12000}
echo; echo "exit=${PIPESTATUS[0]} secs=$(( $(date +%s) - S )) bytes=$(wc -c < "$D/Submission.lean")"
