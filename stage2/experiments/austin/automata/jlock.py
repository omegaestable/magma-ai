"""jlock.py -- cross-process semaphore + JUDGE_LEAN_PATH injection for parallel judge calls.

The judge's `_get_lake_lean_path` shells out to `lake env` (30 s timeout) unless
JUDGE_LEAN_PATH is set; under parallel load that times out (CLAUDE.md, environment
gotchas).  We pin it from the cached leanpath.txt instead, and cap the number of
concurrent Lean judge processes so several proof agents can judge without
starving each other (rail 5e / rail 22: your own parallel jobs are the load).
"""
import os, sys, time, errno

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
LEANPATH = os.path.join(ROOT, 'vendor', 'stage2-official', '.artifacts', 'dev5107', 'leanpath.txt')
LOCKDIR = os.path.join(HERE, '.judgelocks')
SLOTS = int(os.environ.get('JUDGE_SLOTS', '5'))


def judge_env(env=None):
    env = dict(os.environ if env is None else env)
    env.setdefault('PYTHONIOENCODING', 'utf-8')
    if 'JUDGE_LEAN_PATH' not in env and os.path.exists(LEANPATH):
        env['JUDGE_LEAN_PATH'] = open(LEANPATH, encoding='utf-8').read().strip()
    return env


class Slot:
    """Acquire one of SLOTS judge slots; stale slots (> 900 s) are reclaimed."""

    def __init__(self, timeout=3600.0):
        self.timeout = timeout
        self.path = None

    def __enter__(self):
        os.makedirs(LOCKDIR, exist_ok=True)
        t0 = time.time()
        while True:
            for i in range(SLOTS):
                p = os.path.join(LOCKDIR, 'slot%d' % i)
                try:
                    fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                    os.write(fd, str(os.getpid()).encode())
                    os.close(fd)
                    self.path = p
                    return self
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                    try:
                        if time.time() - os.path.getmtime(p) > 900:
                            os.remove(p)
                    except OSError:
                        pass
            if time.time() - t0 > self.timeout:
                sys.stderr.write('jlock: timed out waiting for a judge slot; proceeding anyway\n')
                return self
            time.sleep(2.0)

    def __exit__(self, *a):
        if self.path:
            try:
                os.remove(self.path)
            except OSError:
                pass
        return False
