from dataclasses import Field, dataclass, field
from datetime import datetime, timedelta

from models.task import Task


@dataclass
class TaskResponseDto:
    
    id: int
    name: str
    attribution_email: str
    start_date: datetime
    end_date: datetime
    status: Task.Status

    @classmethod
    def from_entity(cls, task: Task):
        return cls(
            id=task.id,
            name=task.name,
            status=task.status,
            start_date=task.start_date, 
            end_date=task.end_date,
            attribution_email=task.attribution_email, 
            duration=(task.end_date - task.start_date).days
        )
        