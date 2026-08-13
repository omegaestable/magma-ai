param(
    [string]$OutPath = "stage2/submissions/solver.py",
    [switch]$SkipTests,
    # Headroom warning, not a de-bloat target: routes are never deleted to save
    # bytes (CLAUDE.md rail 1). This fires when the artifact is within 10% of the
    # hard cap, which is when adding a large distilled certificate needs thought.
    [int]$WarnBytes = 450000
)

$sourcePath = "stage2/solver/solver.py"
$limitBytes = 500000
$python = if (Test-Path ".venv/Scripts/python.exe") { ".venv/Scripts/python.exe" } else { "python" }

if (-not (Test-Path $sourcePath)) {
    throw "Missing solver source: $sourcePath"
}

# Offline correctness gate. The Lean judge is cloud-only, so these oracles
# (proof kernel + finite-model checks + golden routes) are the local guard
# against shipping `incorrect` certificates. Do not package around a failure.
if (-not $SkipTests) {
    Write-Host "Running offline correctness gate..."
    # -n auto: the gate re-solves ~170 real problems, which is ~160 s serially
    # and ~47 s across cores. Speed matters here because a slow gate is a gate
    # people skip. Falls back to serial when pytest-xdist is not installed.
    & $python -m pytest stage2/tests -q -n auto
    if ($LASTEXITCODE -eq 4) {
        Write-Warning "pytest-xdist unavailable; falling back to a serial gate (slower)."
        & $python -m pytest stage2/tests -q
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Offline correctness gate failed; refusing to package. Re-run with -SkipTests only for a deliberate spike."
    }
}

$outDir = Split-Path $OutPath -Parent
if ($outDir) {
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
}

# Build to a temp file, validate, then swap into place. The previous order
# emptied the output directory first and only then ran the minifier, so any
# failure downstream left `stage2/submissions/` with no artifact at all — and
# since `.gitignore` excludes it, there was no copy in git to fall back on.
# The size check had the mirror-image bug: it threw "refusing to package" only
# *after* the oversized file was already sitting at $OutPath, exactly where the
# upload steps in EVAL_WORKFLOW.md tell an operator to pick it up.
#
# Writing the submission with LF line endings and no comments or docstrings is
# pure byte savings the judge does not need: LF instead of the CRLF working tree
# is worth ~2% of the cap, and comments plus docstrings are ~17%.
# `minify_submission.py` proves the artifact parses to the same tree as the
# source before writing it, so this cannot silently change behaviour.
# UTF-8 without BOM: the file contains ◇ and a BOM would be junk to parse.
$staging = Join-Path ([System.IO.Path]::GetTempPath()) ("solver-package-" + [guid]::NewGuid().ToString("N") + ".py")
try {
    & $python stage2/solver/minify_submission.py $sourcePath $staging
    if ($LASTEXITCODE -ne 0) {
        throw "Minifying the submission failed; refusing to package. $OutPath is unchanged."
    }
    $sizeBytes = (Get-Item $staging).Length

    if ($sizeBytes -gt $limitBytes) {
        throw "Packaged solver is $sizeBytes bytes; limit is $limitBytes bytes. $OutPath is unchanged."
    }

    # Only now is the previous artifact replaced. Remove just the file we own,
    # never the directory contents: $OutPath is caller-supplied, and a blind
    # directory wipe keyed off it would happily delete the solver source.
    if (Test-Path $OutPath) { Remove-Item -Force $OutPath }
    Move-Item -Force $staging $OutPath

    # The official Solo runner refuses to execute if the submission directory
    # holds anything besides solver.py, and `__pycache__` appears there by
    # accident easily -- any `py_compile`/`compileall` touching the artifact
    # leaves one. The old blind directory wipe cleaned this as a side effect;
    # now that the wipe is gone, remove it deliberately, then assert the
    # invariant rather than trusting it.
    $stalePycache = Join-Path $outDir "__pycache__"
    if (Test-Path $stalePycache) { Remove-Item -Recurse -Force $stalePycache }

    $expected = Split-Path $OutPath -Leaf
    $strays = Get-ChildItem -Force -Path $outDir | Where-Object { $_.Name -ne $expected }
    if ($strays) {
        throw ("Submission directory $outDir contains entries besides ${expected}: " +
               ($strays.Name -join ', ') + ". The official Solo runner rejects these.")
    }
}
finally {
    if (Test-Path $staging) { Remove-Item -Force $staging }
}

if ($sizeBytes -gt $WarnBytes) {
    Write-Warning "Packaged solver is $sizeBytes bytes, within 10% of the $limitBytes byte hard cap."
}

Write-Host "Packaged $OutPath ($sizeBytes bytes)."
