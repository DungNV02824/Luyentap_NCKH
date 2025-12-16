from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Lưu ý: 3 dấu gạch chéo /// (đường dẫn tương đối)
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()