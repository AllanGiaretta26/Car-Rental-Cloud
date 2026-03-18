from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    pass


def _ensure_sqlite_directory(database_url: str) -> None:
    # Garante que a pasta do arquivo SQLite exista antes da conexao.
    url = make_url(database_url)
    if url.drivername.startswith("sqlite") and url.database:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)


settings = get_settings()
_ensure_sqlite_directory(settings.database_url)

# O SQLite precisa desta flag para funcionar bem com a sessao local do FastAPI.
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    # Importa os modelos aqui para garantir que todas as tabelas sejam registradas.
    from app import models

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    # Abre e fecha a sessao automaticamente a cada requisicao.
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
