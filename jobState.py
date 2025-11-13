from enum import Enum

class JobState(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    DONE = "DONE"
    FAILED = "FAILED"