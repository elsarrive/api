from pydantic import BaseModel, EmailStr, Field


class TaskRequestDto(BaseModel):
    name: str = Field()
    attribution_email: EmailStr = Field()
    duration: int = Field(gt=0)