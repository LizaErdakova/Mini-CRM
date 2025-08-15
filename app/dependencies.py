from sqlalchemy.orm import Session
from app.core.database import SessionLocal


def get_db() -> Session:
    """Зависимость для получения сессии базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 