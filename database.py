import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

Base = declarative_base()  # the parent class of your table models

engine = None  # the actual connection to Neon postgres
SessionLocal = None

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine
    )  # how Fast api will open and close individual DB conversations per request