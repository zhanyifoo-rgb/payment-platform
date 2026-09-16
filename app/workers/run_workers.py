import subprocess
import sys

payments_worker = subprocess.Popen(
    [sys.executable, "-m", "app.workers.payments_worker"]
)

outboxs_worker = subprocess.Popen(
    [sys.executable, "-m", "app.workers.outboxs_worker"]
)

try:
    payments_worker.wait()
    outboxs_worker.wait()
finally:
    payments_worker.terminate()
    outboxs_worker.terminate()