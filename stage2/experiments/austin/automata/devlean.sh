#!/bin/bash
# devlean.sh <file.lean> : compile a certificate against the dev JudgeProblem (5107:22818), fast loop.
D=/c/Users/nacho/Documents/GitHub/magma-ai/vendor/stage2-official/.artifacts/dev5107
cp "$1" "$D/Submission.lean"
cd "$D" || exit 1
export PATH="$HOME/.elan/bin:$PATH"
export LEAN_PATH="$(cygpath -w "$PWD");$(cat leanpath.txt)"
W=$(cygpath -w "$PWD")
S=$(date +%s)
timeout ${T:-300} lean --root="$W" -D linter.defProp=false -o "$W\Submission.olean" Submission.lean 2>&1 | head -c ${C:-12000}
echo; echo "exit=${PIPESTATUS[0]} secs=$(( $(date +%s) - S )) bytes=$(wc -c < "$D/Submission.lean")"
