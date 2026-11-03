import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import database_url


def make_session_factory():
    engine = create_engine(
        database_url(), pool_pre_ping=True,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
        echo=False,
    )
    return sessionmaker(engine, expire_on_commit=False)
    #¿Cuándo se generan los commits?
    # Alta, Baja y Modificación
