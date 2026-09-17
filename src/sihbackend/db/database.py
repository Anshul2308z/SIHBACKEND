import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# We default to SQLite for immediate testing, but the app is Postgres-ready
# Provide POSTGRES_URL in .env to use PostgreSQL (e.g. postgresql://user:pass@localhost:5432/sihdb)
SQLALCHEMY_DATABASE_URL = os.environ.get("POSTGRES_URL", "sqlite:///./sih_application.db")

# SQLite requires connect_args={"check_same_thread": False}
connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
