from enum import Enum

class JobState(Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    DELAYED = "DELAYED"
    FAILED = "FAILED"
    DEAD = "DEAD"