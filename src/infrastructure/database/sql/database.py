from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from src.config.settings import get_settings

settings = get_settings()

# Use SQLite for simplicity, replace with your actual database URL from settings
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_db_and_tables():
    Base.metadata.create_all(bind=engine)
