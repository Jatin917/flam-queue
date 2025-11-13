from sklearn.utils import resample
from storage import Storage
import subprocess
import multiprocessing
import time


class Worker:
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

if __name__ == "__main__":
    storage = Storage()
    worker = Worker(storage)
    worker.start()