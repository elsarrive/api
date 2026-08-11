# from __future__ import annotations -> si on veut ne pas mettre "Employe" entre guillemets dans les relations
from decimal import Decimal
from enum import StrEnum, auto
from typing import Optional
from sqlalchemy import Numeric, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models import Base

from typing import TYPE_CHECKING
if TYPE_CHECKING: # employé import task, task import employé -> permet d'éviter pb d'imports cycliques
    from models.task import Task 

from enums.titre import Titre 

class Employe(Base):
    __tablename__ = 'employe'
    class Titre(StrEnum):
        PM = auto()
        DEV = auto()

    employee_id : Mapped[int] = mapped_column(primary_key=True)
    last_name : Mapped[str] = mapped_column(nullable=False)
    first_name : Mapped[str] = mapped_column(nullable=False)
    email : Mapped[str] = mapped_column(nullable=False, unique=True)
    salary : Mapped[Decimal] = mapped_column(Numeric(8,2), nullable=False)
    titre : Mapped[Titre] = mapped_column(SQLEnum(Titre), nullable=False, default=Titre.DEV)
    supervisor_id : Mapped[Optional[int]] = mapped_column(ForeignKey('employe.employee_id'), nullable=True)

    tasks : Mapped[list["Task"]] = relationship(back_populates='assign_to')
    superviseur : Mapped[Optional["Employe"]] = relationship("Employe", remote_side=[employee_id], back_populates='employees')
    employees : Mapped[Optional[list["Employe"]]] = relationship("Employe", back_populates='superviseur')