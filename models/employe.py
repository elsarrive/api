from enum import Enum as PyEnum, auto
from typing import Optional

from sqlalchemy import NUMERIC, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from base import Base 

class Employe(Base):
    __tablename__ = 'employe'

    class Titre(PyEnum):
        PM = auto()
        DEV = auto()
        
    employee_id : Mapped[int] = mapped_column(primary_key=True)
    last_name : Mapped[str] = mapped_column()
    first_name : Mapped[str] = mapped_column()
    email : Mapped[str] = mapped_column()
    salary : Mapped[float] = mapped_column(NUMERIC(7,2))
    titre : Mapped[Titre] = mapped_column(SQLEnum(Titre), nullable=False)
    supervisor_id : Optional[Mapped[int]] = mapped_column(ForeignKey('employe.employee_id'))
    
    superviseur : Mapped[Optional["Employe"]] = relationship("Employe", remote_side=[employee_id], back_populates='employees')
    employees : Mapped[list["Employe"]] = relationship("Employe", back_populates='superviseur')