from queuectl.storage import Storage
import subprocess
import multiprocessing
import time


class WorkerProcess:
    def __init__(self, storage:Storage):
        self.storage = storage
        self.running = True

    def start(self):
        while self.running:
            job = self.storage.fetchNextJob()
            if not job:
                time.sleep(0.5)
                continue
            print("processing job ", job.id)
            # Redirect stdout, stderr, and stdin to prevent Windows PRN device errors
            try:
                result = subprocess.run(
                    job.command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.DEVNULL,
                    text=True,
                    timeout=None
                )
                if result.returncode == 0:
                    self.storage.mark_completed(job)
                    if result.stdout:
                        print(f"Job {job.id} output: {result.stdout}")
                else:
                    self.storage.mark_failed(job)
                    if result.stderr:
                        print(f"Job {job.id} error: {result.stderr}")
            except Exception as e:
                print(f"Error executing job {job.id}: {e}")
                self.storage.mark_failed(job)

    def stop(self):
        self.running = False


# Top-level function for multiprocessing (required on Windows)
def _worker_process_entry():
    """Entry point for worker processes. Each process creates its own Storage instance."""
    worker_storage = Storage()
    worker = WorkerProcess(worker_storage)
    worker.start()


class WorkerManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.workers = []

    def start(self, count=1):
        # Use top-level function instead of bound method for Windows compatibility
        for _ in range(count):
            p = multiprocessing.Process(target=_worker_process_entry)
            p.start()
            self.workers.append(p)
        print(f"Started {count} worker(s)")

    def stop(self):
        for p in self.workers:
            p.terminate()
        print("Workers stopped")

if __name__ == "__main__":
    storage = Storage()
    worker = WorkerProcess(storage)
    worker.start()