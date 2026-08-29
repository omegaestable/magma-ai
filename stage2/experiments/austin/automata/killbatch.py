"""Kill batch.py drivers and their multiprocessing children, never our own shell."""
import subprocess, sys, os
me = {os.getpid(), os.getppid()}
PAT = sys.argv[1] if len(sys.argv) > 1 else 'batch.py'
cmd = "Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'python*' } | ForEach-Object { '{0}|{1}|{2}' -f $_.ProcessId, $_.ParentProcessId, $_.CommandLine }"
r = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, encoding='utf-8', errors='replace')
procs = []
for line in r.stdout.splitlines():
    parts = line.split('|', 2)
    if len(parts) == 3 and parts[0].strip().isdigit():
        procs.append((int(parts[0]), int(parts[1]) if parts[1].strip().isdigit() else 0, parts[2]))
targets = set()
for pid, ppid, cl in procs:
    if pid in me:
        continue
    if PAT in cl and 'killbatch' not in cl:
        targets.add(pid)
# children: multiprocessing spawn workers whose parent is a target (or whose parent no longer exists)
alive = {pid for pid, _, _ in procs}
for pid, ppid, cl in procs:
    if pid in me:
        continue
    if 'spawn_main' in cl and (ppid in targets or ppid not in alive):
        targets.add(pid)
print('python procs:', len(procs), 'targets:', sorted(targets))
for p in sorted(targets):
    subprocess.run(['taskkill', '/F', '/PID', str(p)], capture_output=True)
r = subprocess.run(['powershell', '-NoProfile', '-Command', cmd], capture_output=True, text=True, encoding='utf-8', errors='replace')
left = [l.split('|', 2) for l in r.stdout.splitlines()]
print('remaining python procs:')
for l in left:
    if len(l) == 3:
        print('  ', l[0], l[1], l[2][:100])
