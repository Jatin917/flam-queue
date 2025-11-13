# models.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

import jobState

@dataclass
class Job:
    id: str
    command: str
    state: str = jobState.JobState.PENDING.value
    attempts: int = 0
    max_retries: int = 3
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @classmethod
    def new(cls, command: str, max_retries: int = 3, job_id: str | None = None):
        return cls(id=job_id or str(uuid.uuid4()), command=command, max_retries=max_retries)