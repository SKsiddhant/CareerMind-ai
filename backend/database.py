import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Build the database URL
db_user = os.getenv("POSTGRES_USER", "postgres")
db_pass = os.getenv("POSTGRES_PASSWORD", "password")
db_host = os.getenv("POSTGRES_HOST", "localhost")
db_port = os.getenv("POSTGRES_PORT", "5432")
db_name = os.getenv("POSTGRES_DB", "careermind")

# Fallback to SQLite for development if POSTGRES_HOST is localhost and connection fails, 
# or if explicitly requested. For this project, we prioritize the Production architecture.
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    # Quick check if engine can connect
    with engine.connect() as conn:
        pass
except Exception:
    print("⚠️ PostgreSQL not found. Falling back to local SQLite database for development.")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./careermind.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
