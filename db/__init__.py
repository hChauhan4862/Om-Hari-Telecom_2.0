from distutils.log import debug
from db.config import *
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends



engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


Base.metadata.create_all(engine) # create tables if not exists in db 


SessionLocal  = sessionmaker(autocommit=False, autoflush=False,bind = engine)

def get_db():
    cache_db = SessionLocal()
    try:
        yield cache_db
    finally:
        cache_db.close()