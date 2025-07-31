from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLITE_URL = "sqlite:///./books.db"

engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base = declarative_base()
