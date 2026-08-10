# SQLAlchemy et Alembic

## Installation

```sh
pip install sqlalchemy alembic psycopg2 python-dotenv
```

- `sqlalchemy` : ORM Python
- `alembic` : gestion des migrations
- `psycopg2` : pilote PostgreSQL
- `python-dotenv` : chargement des variables d'environnement

## Initialisation des modèles

Créer une classe `Base` qui hérite de `DeclarativeBase` :

```python
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass
```

Puis définir les modèles en héritant de `Base` :

```python
from sqlalchemy.orm import Mapped, mapped_column

class Student(Base):
    __tablename__ = "student"
    id: Mapped[int] = mapped_column(primary_key=True)
    # autres colonnes...
```

## Initialisation d'Alembic

1. Générer la structure Alembic :

```sh
alembic init alembic
```

2. Configurer la connexion à la base dans `alembic/env.py` :

```python
import os
from dotenv import load_dotenv
from models import Base

load_dotenv()

def run_migrations_online():
    config.set_main_option("sqlalchemy.url", os.getenv("DB_URL"))
    target_metadata = Base.metadata
    # ... reste de la configuration Alembic
```

> Assurez-vous que `DB_URL` est défini dans `.env`.

## Créer une migration

```sh
alembic revision --autogenerate -m "nom_migration"
```

## Appliquer les migrations

```sh
alembic upgrade head
```

## Base PostgreSQL avec Docker

```sh
docker run --name postgres -p 5432:5432 \
  -e POSTGRES_USER=my_user \
  -e POSTGRES_PASSWORD=my_password \
  -e POSTGRES_DB=my_db \
  -d postgres:latest
```

Exemple de `DB_URL` :

```env
DB_URL=postgresql://my_user:my_password@localhost:5432/my_db
```
