from queuectl.storage import Storage
import subprocess
import multiprocessing
import time
import os
import signal
import sys


class WorkerProcess:
    def __init__(self, storage:Storage, worker_id: int):
        self.storage = storage
        self.worker_id = worker_id
        self.pid = os.getpid()

    def start(self):
        # Register this worker in Redis
        self.storage.register_worker(self.worker_id, self.pid)
        print(f"[Worker {self.worker_id}] Started (PID: {self.pid})")
        
        try:
            while True:
                # Check Redis for stop signal
                if self.storage.check_stop_signal(self.worker_id):
                    print(f"[Worker {self.worker_id}] Stop signal received")
                    break
                
                job = self.storage.fetchNextJob()
                if not job:
                    time.sleep(0.5)
                    continue
                
                print(f"[Worker {self.worker_id}] Processing job {job.id}")
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
                            print(f"[Worker {self.worker_id}] Job {job.id} output: {result.stdout}")
                    else:
                        self.storage.mark_failed(job)
                        if result.stderr:
                            print(f"[Worker {self.worker_id}] Job {job.id} error: {result.stderr}")
                except Exception as e:
                    print(f"[Worker {self.worker_id}] Error executing job {job.id}: {e}")
                    self.storage.mark_failed(job)
        finally:
            # Unregister and cleanup
            self.storage.unregister_worker(self.worker_id)
            self.storage.clear_stop_signal(self.worker_id)
            print(f"[Worker {self.worker_id}] Stopped (PID: {self.pid})")
            sys.exit(0)

# Top-level function for multiprocessing (required on Windows)
def _worker_process_entry(worker_id: int):
    """Entry point for worker processes. Each process creates its own Storage instance."""
    worker_storage = Storage()
    worker = WorkerProcess(worker_storage, worker_id)
    worker.start()


class WorkerManager:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.workers = []
        self.worker_ids = []

    def start(self, count=1):
        # Get next available worker IDs
        print("Getting existing workers", len(self.workers))
        existing_workers = self.storage.list_workers()
        existing_ids = {int(w.get("worker_id", 0)) for w in existing_workers}
        next_id = max(existing_ids) + 1 if existing_ids else 1
        
        # Use top-level function instead of bound method for Windows compatibility
        for i in range(count):
            worker_id = next_id + i
            p = multiprocessing.Process(
                target=_worker_process_entry,
                args=(worker_id,)
            )
            p.start()
            self.workers.append(p)
            self.worker_ids.append(worker_id)
        print(f"[Manager] Started {count} worker(s)")

    def stop_all(self):
        """Stop all workers registered in Redis."""
        workers = self.storage.list_workers()
        if not workers:
            print("[Manager] No workers running")
            return
        
        print(f"[Manager] Stopping {len(workers)} worker(s)...")
        # Set stop signal for all workers in Redis
        self.storage.set_stop_signal()
        
        # Wait for workers to stop
        import time
        max_wait = 10  # Maximum wait time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            remaining = self.storage.list_workers()
            if not remaining:
                break
            time.sleep(0.5)
        
        # Check if any workers are still running and force kill them
        remaining = self.storage.list_workers()
        if remaining:
            print(f"[Manager] Force terminating {len(remaining)} worker(s)...")
            for worker in remaining:
                try:
                    pid = int(worker.get("pid", 0))
                    if pid:
                        try:
                            if hasattr(signal, 'SIGTERM'):
                                os.kill(pid, signal.SIGTERM)
                            else:
                                # Windows doesn't have SIGTERM, use SIGKILL or taskkill
                                import platform
                                if platform.system() == 'Windows':
                                    import subprocess
                                    subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                else:
                                    os.kill(pid, signal.SIGKILL)
                        except (ProcessLookupError, OSError):
                            pass  # Process already dead
                        self.storage.unregister_worker(int(worker.get("worker_id", 0)))
                except (ProcessLookupError, OSError):
                    # Process already dead
                    self.storage.unregister_worker(int(worker.get("worker_id", 0)))
                except Exception as e:
                    print(f"[Manager] Error stopping worker {worker.get('worker_id')}: {e}")
        
        print("[Manager] All workers stopped")

    def stop_by_pid(self, pid: int):
        """Stop a specific worker by PID."""
        workers = self.storage.list_workers()
        target_worker = None
        for worker in workers:
            if int(worker.get("pid", 0)) == pid:
                target_worker = worker
                break
        
        if not target_worker:
            print(f"[Manager] No worker found with PID {pid}")
            return
        
        worker_id = int(target_worker.get("worker_id", 0))
        print(f"[Manager] Stopping worker {worker_id} (PID: {pid})...")
        self.storage.set_stop_signal(worker_id)
        
        # Wait for worker to stop
        import time
        max_wait = 5
        start_time = time.time()
        while time.time() - start_time < max_wait:
            remaining = self.storage.list_workers()
            if not any(int(w.get("worker_id", 0)) == worker_id for w in remaining):
                break
            time.sleep(0.5)
        
        # Force kill if still running
        remaining = self.storage.list_workers()
        if any(int(w.get("worker_id", 0)) == worker_id for w in remaining):
            try:
                if hasattr(signal, 'SIGTERM'):
                    os.kill(pid, signal.SIGTERM)
                else:
                    # Windows doesn't have SIGTERM, use taskkill
                    import platform
                    if platform.system() == 'Windows':
                        import subprocess
                        subprocess.run(['taskkill', '/F', '/PID', str(pid)], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    else:
                        os.kill(pid, signal.SIGKILL)
                self.storage.unregister_worker(worker_id)
            except (ProcessLookupError, OSError):
                self.storage.unregister_worker(worker_id)
        
        print(f"[Manager] Worker {worker_id} (PID: {pid}) stopped")

    def list_workers(self):
        """List all running workers."""
        return self.storage.list_workers()

if __name__ == "__main__":
    storage = Storage()
    worker = WorkerProcess(storage, worker_id=1)
    worker.start()