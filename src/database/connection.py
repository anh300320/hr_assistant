from contextlib import contextmanager
from datetime import date
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from src.database import models

SessionLocal = scoped_session(sessionmaker(autoflush=True))


@contextmanager
def get_db():
    session = SessionLocal
    try:
        yield session
    except:
        session.rollback()
        raise
    finally:
        session.close()


db_context = contextmanager(get_db)


def init_database(sqlite_db_url: str) -> None:
    sqlite_local_fp = sqlite_db_url.replace("sqlite:///", "", 1)
    Path(sqlite_local_fp).parent.mkdir(exist_ok=True, parents=True)
    engine = create_engine(
        sqlite_db_url,
        pool_pre_ping=True,
        max_overflow=-1,
        pool_size=128,
        connect_args={"check_same_thread": False},
    )
    models.Base.metadata.create_all(bind=engine)
    SessionLocal.configure(bind=engine)
