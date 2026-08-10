from base import Base 
from SQLAlchemy import mapped_column

class Employe(Base):
    __tablename__ = 'employe'
    id : int
    last_name : str
    first_name : str
    email : str
    salary : Mapped[float] = mapped_column(decimal)
    titre : Enum (PM, DEV)
    supervisor_id : int | null (référence vers un autre employé)