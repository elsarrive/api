from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from models.task import Task


class TaskFilterRequestDto(BaseModel):
    email: Optional[EmailStr] = Field(default=None)
    status: Optional[Task.Status] = Field(default=None)
    limit: int = Field(default=10, gt=0, le=100)
    page: int = Field(default=1, gt=0)