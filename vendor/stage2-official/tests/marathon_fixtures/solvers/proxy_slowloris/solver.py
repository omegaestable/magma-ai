"""Marathon harness fixture: slowloris attack against the local proxy.

Pre-fix the marathon proxy used ``ThreadingHTTPServer`` with no
per-connection socket timeout and no concurrency cap. A solver that
opened many TCP connections without sending a body would pin one runner
thread per connection forever — slowloris-class denial of service
against the in-process proxy.

Post-fix the proxy:
  * sets ``timeout = 5.0`` on the request handler so any single
    send/recv that stalls raises and the thread exits;
  * reads the body via ``_read_body_with_deadline`` so a slow-trickle
    feeder cannot keep one thread alive past the deadline;
  * caps concurrent handler threads at 64; excess connections are
    closed immediately on the accept thread.

This fixture opens a burst of partial-HTTP connections (well above the
concurrency cap) that send a ``Content-Length`` promise but never the
body, then closes them. It writes a marker answer so scoring sees a
row. The harness assertion is the run completes cleanly inside the
budget — pre-fix it would either OOM the runner or wedge the proxy
until the wall-budget kill.
"""
import json
import os
import socket
import threading
import time
from urllib.parse import urlparse

# Many more connections than the concurrency cap (64). Excess
# connections must be admitted+closed without piling up threads.
_BURST = 256

# Each slowloris socket promises a 1 MB body but sends no bytes after
# the headers. Pre-fix: each socket pins a runner thread until the
# socket is closed (potentially indefinite). Post-fix: each thread's
# body read raises after 5 s and the thread exits.
_PROMISED_BODY_BYTES = 1024 * 1024


def _slowloris_one(host: str, port: int, secret: str) -> None:
    """Open one connection, send headers + content-length, never send body."""
    try:
        s = socket.create_connection((host, port), timeout=2.0)
    except OSError:
        return
    try:
        # Send a request that promises a body, then stop. We do NOT close
        # the socket — we want to test that the proxy times out the read
        # rather than waiting forever.
        request = (
            f"POST /v1/chat/completions HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            f"Authorization: Bearer {secret}\r\n"
            f"Content-Type: application/json\r\n"
            f"Content-Length: {_PROMISED_BODY_BYTES}\r\n"
            f"\r\n"
        ).encode("utf-8")
        try:
            s.sendall(request)
        except OSError:
            pass
        # Hold the socket open briefly so the runner has time to admit
        # the connection but cannot drain a body. The proxy's body-read
        # deadline (5 s) expires while we're idle here.
        time.sleep(2.0)
    finally:
        try:
            s.close()
        except OSError:
            pass


base_url = os.environ.get("OPENAI_BASE_URL", "")
api_key = os.environ.get("OPENAI_API_KEY", "")
parsed = urlparse(base_url)
host = parsed.hostname or "127.0.0.1"
port = parsed.port or 0

opened = 0
if port:
    threads = []
    for _ in range(_BURST):
        t = threading.Thread(
            target=_slowloris_one, args=(host, port, api_key), daemon=True
        )
        t.start()
        threads.append(t)
        opened += 1
    # Don't wait for all threads — the harness assertion is the runner
    # survives, not that every socket is cleanly torn down. We do give
    # the burst enough time to actually hit the proxy.
    deadline = time.monotonic() + 3.0
    for t in threads:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        t.join(timeout=remaining)

with open(os.environ["JUDGE_MARATHON_OUTPUT"], "a", encoding="utf-8") as fh:
    fh.write(json.dumps({
        "id": "proxy_slowloris_probe",
        "verdict": "true",
        "code": "(slowloris probe)",
        "opened_connections": opened,
    }) + "\n")
