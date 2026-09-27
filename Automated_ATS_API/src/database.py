import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text
from sqlalchemy.orm import sessionmaker, declarative_base

# Pull the DB connection string from our .env file.
# Defaults to a local SQLite file if missing.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ats_local.db")

# check_same_thread=False is required for SQLite in FastAPI since multiple 
# async workers might try to access the file at the same time.
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class CandidateRecord(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, index=True)
    match_score = Column(Float)
    summary = Column(Text)
    # Storing skills as a stringified JSON array
    skills = Column(Text)

# Dependency injection helper to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
