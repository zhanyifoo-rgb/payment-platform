import subprocess
import sys


transaction_worker = subprocess.Popen(
    [sys.executable, "-m", "app.workers.transaction_worker"]
)

outbox_worker = subprocess.Popen(
    [sys.executable, "-m", "app.workers.outbox_worker"]
)


try:
    transaction_worker.wait()
    outbox_worker.wait()

finally:
    transaction_worker.terminate()
    outbox_worker.terminate()