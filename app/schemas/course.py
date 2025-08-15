from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


class CourseCreate(BaseModel):
    """Схема для создания курса."""
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    price: Decimal = Field(..., ge=0)  # цена не может быть отрицательной


class CourseOut(BaseModel):
    """Схема для вывода информации о курсе."""
    id: int
    title: str
    description: Optional[str] = None
    price: Decimal

    class Config:
        from_attributes = True  # для SQLAlchemy моделей 