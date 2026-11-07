"""Simple in-memory task registry. Replace with SQLite/Postgres for production."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import uuid

@dataclass
class Job:
    id: str
    description: str
    requester: str
    channel_id: int
    status: str = "queued"
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class JobStore:
    def __init__(self):
        self._jobs: dict[str, Job] = {}

    def create(self, description: str, requester: str, channel_id: int) -> Job:
        job = Job(uuid.uuid4().hex[:8], description, requester, channel_id)
        self._jobs[job.id] = job
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **changes) -> Optional[Job]:
        job = self.get(job_id)
        if job:
            for key, value in changes.items():
                setattr(job, key, value)
        return job
