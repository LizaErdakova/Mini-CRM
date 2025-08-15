from sqlalchemy import Column, Integer, String, Text, Numeric
from app.core.database import Base


class Course(Base):
    """Модель курса в базе данных."""
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)  # DECIMAL(10,2) в MySQL 