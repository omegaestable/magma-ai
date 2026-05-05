"""
Opt-in Docker sandbox integration smoke test.

Not part of the canonical harness (docker daemon required, so it would
make run_harness.py environment-dependent). Run manually after setup:

    python3 scripts/sandbox_smoke.py

Exits 0 when the sandbox image behaves correctly, 1 when any assertion
fails, 2 when docker is unavailable (treated as skip rather than fail).

Tests
-----
1. docker daemon reachable and image ee-solver:latest exists
2. benign solver: trivial stdout write completes
3. network isolation: solver attempting urllib outbound call fails
4. filesystem read-only: solver attempting to write inside mount fails
5. non-root + caps dropped: effective uid != 0 and CapEff bitmap == 0

Each adversarial case mounts a tiny solver.py into the sandbox and
checks that the expected failure mode happens. No host state is
modified beyond a private tempdir.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

IMAGE = "ee-solver:latest"
ROOT = Path(__file__).resolve().parents[1]


def _docker_available() -> bool:
    if not shutil.which("docker"):
        return False
    info = subprocess.run(
        ["docker", "info"], capture_output=True, text=True, timeout=10,
    )
    return info.returncode == 0


def _image_present() -> bool:
    result = subprocess.run(
        ["docker", "image", "inspect", IMAGE],
        capture_output=True, text=True, timeout=10,
    )
    return result.returncode == 0


def _run_sandbox(solver_src: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run solver_src inside the sandbox image and return the completed process."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        (tmp_path / "solver.py").write_text(solver_src, encoding="utf-8")
        container_name = f"ee-solver-smoke-{uuid.uuid4().hex[:12]}"
        argv = [
            "docker", "run", "--rm", "-i",
            "--name", container_name,
            "--network=none",
            "--read-only",
            "--cap-drop=ALL",
            "--security-opt=no-new-privileges:true",
            "--memory=256m",
            "--memory-swap=256m",
            "--cpus=1",
            "--pids-limit=32",
            "--tmpfs", "/tmp:size=8m",
            "-v", f"{tmp_path.resolve()}:/solver:ro",
            "-e", "PYTHONUNBUFFERED=1",
            IMAGE,
        ]
        try:
            return subprocess.run(
                argv, capture_output=True, text=True, timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            # Host docker CLI gets SIGKILL from the timeout, but the container
            # itself is managed by the daemon — kill it explicitly so the
            # smoke run cannot orphan a sandbox on the host.
            subprocess.run(
                ["docker", "kill", container_name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5,
            )
            raise


def test_benign_solver() -> tuple[bool, str]:
    solver_src = (
        "import sys, json\n"
        "print(json.dumps({'ok': True, 'msg': 'hello from sandbox'}), flush=True)\n"
    )
    result = _run_sandbox(solver_src)
    if result.returncode != 0:
        return False, f"expected exit 0, got {result.returncode}; stderr={result.stderr!r}"
    try:
        parsed = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as e:
        return False, f"could not parse stdout: {e}; stdout={result.stdout!r}"
    if parsed.get("ok") is not True:
        return False, f"unexpected payload: {parsed}"
    return True, "benign solver produced expected stdout"


def test_network_isolation() -> tuple[bool, str]:
    solver_src = (
        "import sys\n"
        "try:\n"
        "    import urllib.request\n"
        "    urllib.request.urlopen('http://1.1.1.1', timeout=3)\n"
        "    print('NETWORK_REACHED', flush=True)\n"
        "    sys.exit(0)\n"
        "except Exception as e:\n"
        "    print(f'NETWORK_BLOCKED: {type(e).__name__}', flush=True)\n"
        "    sys.exit(42)\n"
    )
    try:
        result = _run_sandbox(solver_src)
    except subprocess.TimeoutExpired:
        return True, "network call hung (effectively blocked by --network=none)"
    if "NETWORK_BLOCKED" in result.stdout and result.returncode == 42:
        return True, f"urllib raised as expected: {result.stdout.strip()}"
    if "NETWORK_REACHED" in result.stdout:
        return False, f"SECURITY: outbound reached! stdout={result.stdout!r}"
    return False, (
        f"unexpected result: rc={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def test_non_root_and_caps_dropped() -> tuple[bool, str]:
    """Verify the hardening claims that smoke doesn't otherwise exercise.

    Reads the container's effective UID and the ``CapEff`` bitmap from
    ``/proc/self/status``. A silent regression in the Dockerfile ``USER``
    line or the ``--cap-drop=ALL`` flag would flip one of these.
    """
    solver_src = (
        "import os, json\n"
        "status = open('/proc/self/status').read()\n"
        "cap_eff = 'unknown'\n"
        "for line in status.splitlines():\n"
        "    if line.startswith('CapEff:'):\n"
        "        cap_eff = line.split(':', 1)[1].strip()\n"
        "        break\n"
        "print(json.dumps({'euid': os.geteuid(), 'cap_eff': cap_eff}), flush=True)\n"
    )
    result = _run_sandbox(solver_src)
    if result.returncode != 0:
        return False, f"exit {result.returncode}; stderr={result.stderr!r}"
    try:
        parsed = json.loads(result.stdout.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as e:
        return False, f"could not parse stdout: {e}; stdout={result.stdout!r}"
    euid = parsed.get("euid")
    cap_eff = parsed.get("cap_eff", "")
    if euid == 0:
        return False, f"SECURITY: container running as root (euid=0)"
    try:
        cap_eff_int = int(cap_eff, 16)
    except ValueError:
        return False, f"could not parse CapEff {cap_eff!r}"
    if cap_eff_int != 0:
        return False, f"SECURITY: effective capabilities not empty: CapEff=0x{cap_eff}"
    return True, f"non-root (euid={euid}), CapEff=0x{cap_eff} (empty)"


def test_readonly_mount() -> tuple[bool, str]:
    solver_src = (
        "import sys\n"
        "try:\n"
        "    with open('/solver/attack.txt', 'w') as f:\n"
        "        f.write('pwned')\n"
        "    print('WRITE_SUCCEEDED', flush=True)\n"
        "    sys.exit(0)\n"
        "except OSError as e:\n"
        "    print(f'WRITE_BLOCKED: {type(e).__name__}', flush=True)\n"
        "    sys.exit(42)\n"
    )
    result = _run_sandbox(solver_src)
    if "WRITE_BLOCKED" in result.stdout and result.returncode == 42:
        return True, f"write blocked as expected: {result.stdout.strip()}"
    if "WRITE_SUCCEEDED" in result.stdout:
        return False, f"SECURITY: solver wrote to mounted read-only dir"
    return False, (
        f"unexpected result: rc={result.returncode}, "
        f"stdout={result.stdout!r}, stderr={result.stderr!r}"
    )


def main() -> int:
    if not _docker_available():
        print("SKIP: docker daemon not reachable. Start Docker Desktop and retry.")
        return 2
    if not _image_present():
        print(f"FAIL: image {IMAGE!r} not found. Run: bash scripts/setup.sh  (or  docker build -t {IMAGE} .)")
        return 1

    tests = [
        ("benign_solver_runs", test_benign_solver),
        ("network_isolation_blocks_outbound", test_network_isolation),
        ("readonly_mount_blocks_writes", test_readonly_mount),
        ("container_non_root_and_caps_dropped", test_non_root_and_caps_dropped),
    ]

    failures = 0
    for name, fn in tests:
        try:
            ok, detail = fn()
        except Exception as e:
            ok, detail = False, f"exception: {type(e).__name__}: {e}"
        mark = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{mark}] {name} — {detail}")

    if failures:
        print(f"\n{failures}/{len(tests)} failed")
        return 1
    print(f"\nall {len(tests)} sandbox smoke tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
