

from models import Job
from redisConnection import RedisConnection

class Storage:
    def __init__(self, namespace="queuectl"):
        redisClient = RedisConnection()
        self.ns = namespace
        self._client = redisClient.get_client()
        pass

    # Entry into the redis queue
    def enqueue(self, job: Job):
        key = f"{self.ns}:job:{job.id}"
        self._client.hset(key, mapping=job.__dict__)
        self._client.rpush(f"{self.ns}:queue:pending", job.id)

if __name__ == "__main__":
    print("main function")
    job = Job.new("echo hi")
    storage = Storage()
    storage.enqueue(job)
    print(storage._client.lrange("queuectl:queue:pending", 0, -1))