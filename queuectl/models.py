# models.py
from dataclasses import dataclass, field
from datetime import datetime
import uuid

import queuectl.jobState as jobState

def _get_default_max_retries():
    """Get max_retries from config, with fallback to default."""
    try:
        from queuectl.config import Config
        config = Config.load()
        max_retries = config.get("max_retries")
        # Convert to int if it's a string (from JSON)
        if isinstance(max_retries, str):
            return int(max_retries)
        return int(max_retries) if max_retries is not None else 3
    except Exception:
        return 3

@dataclass
class Job:
    id: str
    command: str
    state: str = jobState.JobState.PENDING.value
    attempts: int = 0
    max_retries: int = field(default_factory=_get_default_max_retries)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")

    @classmethod
    def new(cls, command: str, max_retries: int = None, job_id: str | None = None):
        if max_retries is None:
            max_retries = _get_default_max_retries()
        return cls(id=job_id or str(uuid.uuid4()), command=command, max_retries=max_retries)