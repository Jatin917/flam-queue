class DLQ:
    def __init__(self, storage):
        self.storage = storage


    def list(self):
        return self.storage.list(state="dead")


    def retry(self, job_id):
    # fetch job from DLQ -> reset attempts/state -> put back to pending
        pass