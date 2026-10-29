import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv(os.getenv("APP_ENV_FILE") or None)
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()  # the parent class of your table models

engine = None  # the actual connection to Neon postgres
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        pool_timeout=30,
    )
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )  # how Fast api will open and close individual DB conversations per request

def get_db():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()