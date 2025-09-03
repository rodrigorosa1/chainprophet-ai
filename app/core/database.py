from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import Settings, get_settings


def get_db(settings: Settings = Depends(get_settings)):
    engine = create_engine(settings.DATABASE_URL)
    sessionlocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    db: Session = sessionlocal()
    try:
        yield db
    finally:
        db.close()