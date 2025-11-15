

from aiohttp import Payload
from dotenv import get_key
import queuectl.jobState as jobState
from queuectl.models import Job
from queuectl.redisConnection import RedisConnection
import time
class Storage:
    def __init__(self, namespace="queuectl"):
        redisClient = RedisConnection()
        self.ns = namespace
        self._client = redisClient.get_client()
        pass

    def saveState(self, job:Job):
        self._client.hset(self.getKey(job.id), mapping=job.__dict__)

    def getKey(self, job_id):
        return f"{self.ns}:job:{job_id}"
    
    def getData(self, job_id):
        key = self.getKey(job_id)
        return self._client.hgetall(key)

    def incrementAttempts(self, job):
        job.attempts+=1
        job.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    def changeState(self, state, payload):
        payload.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        payload.state = state
        self.saveState(payload)

    # Entry into the redis queue
    def enqueue(self, jobPayload: Job):
        # jobPayload = (Job.new(job)).__dict__
        # key = self.getKey(job.id)
        # self._client.hset(key, mapping=job.__dict__)
        self.saveState(jobPayload)
        self._client.rpush(f"{self.ns}:queue:pending", jobPayload.id)

    # process jobs
    def fetchNextJob(self):
        job_id = self._client.lpop(f"{self.ns}:queue:pending")
        if not job_id:
            return None
        data = self.getData(job_id)
        if not data:
            return
        job = Job(**data)
        self.changeState(jobState.JobState.PROCESSING.value, job)
        return job
    
    # mark completed
    def mark_completed(self, job: Job):
        job.state = jobState.JobState.COMPLETED.value
        # self.r.hset(f"{self.ns}:job:{job.id}", mapping=job.__dict__)
        self.saveState(job)
    
    # failed jobs
    def mark_failed(self, job: Job):
        self.incrementAttempts(job)
        if job.attempts >= int(job.max_retries):
            job.state = "dead"
            self._client.rpush(f"{self.ns}:queue:dead", job.id)
        else:
            job.state = "delayed"
            delay = 2 ** job.attempts
            run_at = int(time.time() + delay)
            self._client.zadd(f"{self.ns}:queue:delayed", {job.id: run_at})
        # self.r.hset(f"{self.ns}:job:{job.id}", mapping=job.__dict__)
        self.saveState(job)

    # delayed jobs to pending jobs
    def moveReadyDelayedJob(self):
        now = int(time.time())
        jobs_ready = self._client.zrangebyscore(f"{self.ns}:queue:delayed", 0, now)
        for job_id in jobs_ready:
            self._client.rpush(f"{self.ns}:queue:pending", job_id)
            self._client.zrem(f"{self.ns}:queue:delayed", job_id)
            self.changeState(jobState.JobState.PENDING.value, job)
    
    def getSummary(self):
        keys = self._client.keys(f"{self.ns}:job:*")
        summary = {}
        for k in keys:
            state = self._client.hget(k, "state")
            summary[state] = summary.get(state, 0) + 1
        return summary

    def listJobs(self, state=None):
        keys = self._client.keys(f"{self.ns}:job:*")
        jobs = []
        for k in keys:
            j = self._client.hgetall(k)
            if state and j.get("state") != state:
                continue
            jobs.append(j)
        return jobs

    # Worker registry methods
    def register_worker(self, worker_id: int, pid: int, parent_pid: int = None):
        """Register a worker in Redis so it can be stopped from any terminal."""
        worker_key = f"{self.ns}:worker:{worker_id}"
        worker_data = {
            "worker_id": str(worker_id),
            "pid": str(pid),
            "parent_pid": str(parent_pid) if parent_pid else "",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self._client.hset(worker_key, mapping=worker_data)
        # Add to set of active workers
        self._client.sadd(f"{self.ns}:workers:active", worker_id)
    
    def unregister_worker(self, worker_id: int):
        """Unregister a worker from Redis."""
        worker_key = f"{self.ns}:worker:{worker_id}"
        self._client.delete(worker_key)
        self._client.srem(f"{self.ns}:workers:active", worker_id)
    
    def list_workers(self):
        """Get list of all registered workers."""
        worker_ids = self._client.smembers(f"{self.ns}:workers:active")
        workers = []
        for worker_id in worker_ids:
            worker_key = f"{self.ns}:worker:{worker_id}"
            worker_data = self._client.hgetall(worker_key)
            if worker_data:
                workers.append(worker_data)
        return workers
    
    def set_stop_signal(self, worker_id: int = None):
        """Set stop signal for a specific worker or all workers."""
        if worker_id:
            self._client.set(f"{self.ns}:worker:{worker_id}:stop", "1", ex=60)  # Expire after 60s
        else:
            # Set stop signal for all workers
            worker_ids = self._client.smembers(f"{self.ns}:workers:active")
            for wid in worker_ids:
                self._client.set(f"{self.ns}:worker:{wid}:stop", "1", ex=60)
    
    def check_stop_signal(self, worker_id: int):
        """Check if stop signal is set for a worker."""
        return self._client.exists(f"{self.ns}:worker:{worker_id}:stop") > 0
    
    def clear_stop_signal(self, worker_id: int):
        """Clear stop signal for a worker."""
        self._client.delete(f"{self.ns}:worker:{worker_id}:stop")

if __name__ == "__main__":
    print("main function")
    job = Job.new("echo hi")
    storage = Storage()
    storage.enqueue(job)
    storage.fetchNextJob()
    storage.mark_completed(job)
    storage.mark_failed(job)
    storage.mark_failed(job)
    print("saved job 0", job)
    storage.mark_failed(job)
    print("saved job", job)
    print("summary is ",  storage.getSummary())
    # print("list is ",  storage.listJobs())