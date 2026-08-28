"""Run any command under the competition sandbox's *resource* shape on Windows.

The grading sandbox is `python:3.11-slim` with **2 vCPU** and **2048 MB**. Every
local Marathon/Solo run so far has been measured on 32 cores and 33 GB, so a
row that fits the budget here may not fit there. This wrapper reproduces the two
limits that matter, at the process-tree level, before exec-ing the command:

* **CPU**: `SetProcessAffinityMask` on our own process. On Windows a child
  inherits the affinity mask *at creation*, and the official runner spawns the
  solver with plain `subprocess.Popen` (`pipeline/marathon_runner.py` L436), so
  setting it here -- before anything is spawned -- covers the whole tree. Doing
  it with `Start-Process -PassThru; $p.ProcessorAffinity = 0x3` instead races
  the runner: a child created before the assignment keeps the full mask.
* **RAM**: a Job Object with `JOB_OBJECT_LIMIT_PROCESS_MEMORY`. Child processes
  join the job automatically (nested jobs, Win8+), and the limit is per process,
  which is what the container enforces. A process exceeding it fails its next
  allocation -- the same shape as the sandbox OOM the memory guard exists for.

Deliberately NOT used for the scoring phase: Lean is organizer-side and is not
charged to the contestant, so score with `--score-only` outside the wrapper.

    PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe \
      stage2/experiments/sandbox_limits_wrapper.py --cpus 2 --memory-mb 2048 -- \
      ./.venv/Scripts/python.exe tmp_stage2_smoke/real-run-tools/run_marathon_batch.py ...
"""
from __future__ import annotations

import argparse
import ctypes
import os
import subprocess
import sys
from ctypes import wintypes

JobObjectExtendedLimitInformation = 9
JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100


class IO_COUNTERS(ctypes.Structure):
    _fields_ = [(n, ctypes.c_ulonglong) for n in (
        "ReadOperationCount", "WriteOperationCount", "OtherOperationCount",
        "ReadTransferCount", "WriteTransferCount", "OtherTransferCount")]


class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("PerProcessUserTimeLimit", wintypes.LARGE_INTEGER),
        ("PerJobUserTimeLimit", wintypes.LARGE_INTEGER),
        ("LimitFlags", wintypes.DWORD),
        ("MinimumWorkingSetSize", ctypes.c_size_t),
        ("MaximumWorkingSetSize", ctypes.c_size_t),
        ("ActiveProcessLimit", wintypes.DWORD),
        ("Affinity", ctypes.POINTER(wintypes.ULONG)),
        ("PriorityClass", wintypes.DWORD),
        ("SchedulingClass", wintypes.DWORD),
    ]


class JOBOBJECT_EXTENDED_LIMIT_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BasicLimitInformation", JOBOBJECT_BASIC_LIMIT_INFORMATION),
        ("IoInfo", IO_COUNTERS),
        ("ProcessMemoryLimit", ctypes.c_size_t),
        ("JobMemoryLimit", ctypes.c_size_t),
        ("PeakProcessMemoryUsed", ctypes.c_size_t),
        ("PeakJobMemoryUsed", ctypes.c_size_t),
    ]


def _kernel32():
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    # Without an explicit restype the pseudo-handle (-1) is truncated to a
    # c_int and every call fails with ERROR_INVALID_HANDLE.
    k32.GetCurrentProcess.restype = wintypes.HANDLE
    k32.CreateJobObjectW.restype = wintypes.HANDLE
    k32.SetProcessAffinityMask.argtypes = [wintypes.HANDLE, ctypes.c_size_t]
    k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    k32.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int,
                                            ctypes.c_void_p, wintypes.DWORD]
    return k32


def apply_affinity(cpus: int) -> int:
    k32 = _kernel32()
    mask = (1 << cpus) - 1
    if not k32.SetProcessAffinityMask(k32.GetCurrentProcess(), ctypes.c_size_t(mask)):
        raise ctypes.WinError(ctypes.get_last_error())
    return mask


def apply_memory_limit(mb: int):
    k32 = _kernel32()
    job = k32.CreateJobObjectW(None, None)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    info = JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
    info.BasicLimitInformation.LimitFlags = JOB_OBJECT_LIMIT_PROCESS_MEMORY
    info.ProcessMemoryLimit = mb * 1024 * 1024
    if not k32.SetInformationJobObject(
        job, JobObjectExtendedLimitInformation,
        ctypes.byref(info), ctypes.sizeof(info)
    ):
        raise ctypes.WinError(ctypes.get_last_error())
    if not k32.AssignProcessToJobObject(job, k32.GetCurrentProcess()):
        raise ctypes.WinError(ctypes.get_last_error())
    return job  # keep the handle alive for the lifetime of this process


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpus", type=int, default=2)
    ap.add_argument("--memory-mb", type=int, default=2048)
    ap.add_argument("--no-memory-limit", action="store_true")
    ap.add_argument("command", nargs=argparse.REMAINDER)
    args = ap.parse_args()
    cmd = [a for a in args.command if a != "--"]
    if not cmd:
        ap.error("no command given (use `-- <cmd> <args...>`)")
    if os.name != "nt":
        ap.error("Windows only; on Linux use taskset + a cgroup or the real container")
    mask = apply_affinity(args.cpus)
    handle = None if args.no_memory_limit else apply_memory_limit(args.memory_mb)
    print(f"sandbox_limits affinity_mask=0x{mask:x} cpus={args.cpus} "
          f"memory_mb={'off' if handle is None else args.memory_mb}", file=sys.stderr, flush=True)
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
