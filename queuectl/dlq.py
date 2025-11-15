import queuectl.jobState as jobState
from queuectl.models import Job
class DLQ:
    def __init__(self, storage):
        self.storage = storage


    def list(self):
        return self.storage.listJobs(state="dead")


    def retry(self, job_id):
    # fetch job from DLQ -> reset attempts/state -> put back to pending
        job = self.storage.getData(job_id)
        if not job:
            print(f"[ERROR] Job {job_id} not found in DLQ")
            return
        job = Job(**job)
        job.attempts = 0
        job.state = jobState.JobState.PENDING.value
        self.storage.enqueue(job)
        print(f"[RETRY] Retried job {job_id}")