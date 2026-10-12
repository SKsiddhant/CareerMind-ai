import os
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
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
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL") or f"postgresql://{quote_plus(db_user)}:{quote_plus(db_pass)}@{db_host}:{db_port}/{db_name}"
if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):  # SQLAlchemy 1.4+ only accepts "postgresql://"
    SQLALCHEMY_DATABASE_URL = "postgresql://" + SQLALCHEMY_DATABASE_URL[len("postgres://"):]

try:
    # connect_timeout: with the old default an unreachable host could hang start-up for minutes
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"connect_timeout": 5} if SQLALCHEMY_DATABASE_URL.startswith("postgresql") else {})
    # Quick check if engine can connect
    with engine.connect() as conn:
        pass
except Exception:
    print("⚠️ PostgreSQL not found. Falling back to local SQLite database for development.")
    # Keep using an existing local file; otherwise put it in data/, the folder docker-compose persists.
    os.makedirs("data", exist_ok=True)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./careermind.db" if os.path.exists("careermind.db") else "sqlite:///./data/careermind.db"
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
