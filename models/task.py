from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy.orm import Mapped, mapped_column, sessionmaker
from sqlalchemy import Engine, Enum as SqlEnum, create_engine

from models.base import Base

class Task(Base):
    class Status(StrEnum):
        in_progress = auto()
        done = auto()
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    attribution_email: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[Status] = mapped_column(SqlEnum(Status), nullable=False, default=Status.in_progress)
    start_date: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)
    end_date: Mapped[datetime] = mapped_column(nullable=False)