from sklearn.utils import resample
from storage import Storage
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
            result = subprocess.run(job.command, shell=True)
            if result.returncode == 0:
                self.storage.mark_completed(job)
            else:
                self.storage.mark_failed(job)

    def stop(self):
        self._running = False

class WorkerManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.workers = []

    def start(self, count=1):
        for _ in range(count):
            p = multiprocessing.Process(target=self._worker_proc)
            p.start()
            self.workers.append(p)
        print(f"Started {count} worker(s)")

    def _worker_proc(self):
        WorkerProcess(self.storage).start()

    def stop(self):
        for p in self.workers:
            p.terminate()
        print("Workers stopped")

if __name__ == "__main__":
    storage = Storage()
    worker = WorkerProcess(storage)
    worker.start()