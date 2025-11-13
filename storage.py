

from aiohttp import Payload
from dotenv import get_key
import jobState
from models import Job
from redisConnection import RedisConnection
import time
class Storage:
    def __init__(self, namespace="queuectl"):
        redisClient = RedisConnection()
        self.ns = namespace
        self._client = redisClient.get_client()
        pass

    def saveState(self, job):
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
    def enqueue(self, job: Job):
        # key = self.getKey(job.id)
        # self._client.hset(key, mapping=job.__dict__)
        self.saveState(job)
        self._client.rpush(f"{self.ns}:queue:pending", job.id)

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
    print("list is ",  storage.listJobs())