from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config.settings import get_settings
import mysql.connector

settings = get_settings()

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

def create_database_if_not_exists():
    db_name = SQLALCHEMY_DATABASE_URL.split('/')[-1]
    # Connect to MySQL server without specifying a database
    # This assumes the DATABASE_URL is in the format "mysql+mysqlconnector://user:password@host:port/database_name"
    server_url = SQLALCHEMY_DATABASE_URL.rsplit('/', 1)[0]
    
    temp_engine = create_engine(server_url)
    try:
        with temp_engine.connect() as connection:
            # Use text() for DDL statements with SQLAlchemy 2.0 style
            connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name};"))
            connection.commit()
        print(f"Database '{db_name}' ensured to exist.")
    except Exception as e:
        print(f"Error ensuring database '{db_name}' exists: {e}")
    finally:
        temp_engine.dispose() # Dispose the temporary engine connection

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=15,        # Tăng nhẹ lên 15 vì bạn chỉ có 4 workers
    max_overflow=10,     # Cho phép bung ra thêm 10 kết nối khi cao điểm
    pool_timeout=30,
    pool_pre_ping=True,  # Giúp tự động kết nối lại nếu DB bị ngắt giữa chừng
    pool_recycle=1800    # Quan trọng: Đóng các kết nối cũ sau 30 phút
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    create_database_if_not_exists() # Ensure database exists before creating tables
    Base.metadata.create_all(bind=engine)
