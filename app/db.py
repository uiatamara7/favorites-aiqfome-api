# Esse arquivo centraliza a conexão com o banco de dados

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .settings import settings

# Cria a base declarativa
class Base(DeclarativeBase):
    pass

# Conecta a API ao banco evitando conexões mortas
engine = create_engine(
    settings.database_url,
    echo=False,
    future=True,
    pool_pre_ping=True,      # Checa conexão antes de usar
    pool_size=5,             # Ajuste conforme necessidade
    max_overflow=10,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

# Cria uma sessão de banco por requisição
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()