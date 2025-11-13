# schedulerQueue.py
import time
import threading
from storage import Storage

class SchedulerQueue:
    def __init__(self, storage: Storage, poll_interval=2):
        self.storage = storage
        self.poll_interval = poll_interval
        self._running = False

    def start(self):
        if self._running:
            return
        self._running = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        while self._running:
            self.storage.moveReadyDelayedJob()
            time.sleep(self.poll_interval)

    def stop(self):
        self._running = False
