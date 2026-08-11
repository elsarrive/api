from __future__ import annotations 
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import null

from models.employe import Employe
# from enums.titre import Titre


class EmployeRequestDto(BaseModel):
    first_name : str = Field()
    last_name : str = Field()
    email : EmailStr = Field() 
    salary : Decimal = Field(gt=0, lt=1000000)
    supervisor_id : Optional[int] = Field(default=null)
    titre : Employe.Titre = Field(default=Employe.Titre.DEV)