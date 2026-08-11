from datetime import datetime
from enum import StrEnum, auto

from sqlalchemy.orm import Mapped, mapped_column, relationship, sessionmaker
from sqlalchemy import Engine, Enum as SqlEnum, ForeignKey, create_engine

from models.base import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from models.employe import Employe

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

    assign_to_id : Mapped[int] = mapped_column(ForeignKey('employe.employee_id'), nullable=True)
    assign_to : Mapped['Employe'] = relationship(back_populates='tasks')