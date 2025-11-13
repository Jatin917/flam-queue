

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

    def getKey(self, job_id):
        return f"{self.ns}:job:{job_id}"
    
    def getData(self, job_id):
        key = self.getKey(job_id)
        return self._client.hgetall(key)
    
    def changeState(self, state, payload):
        payload.updated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        payload.state = state
        self._client.hset(self.getKey(payload.id), mapping=payload.__dict__)

    # Entry into the redis queue
    def enqueue(self, job: Job):
        key = self.getKey(job.id)
        self._client.hset(key, mapping=job.__dict__)
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
        print("being processed job ", self._client.hgetall(self.getKey(job.id)))
        return job
    def mark_completed(self, job: Job):
        job.state = "completed"
        self.r.hset(f"{self.ns}:job:{job.id}", mapping=job.__dict__)

if __name__ == "__main__":
    print("main function")
    job = Job.new("echo hi")
    storage = Storage()
    storage.enqueue(job)
    storage.fetchNextJob()