from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Схема для создания пользователя."""
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=10, le=120)
    password: str = Field(..., min_length=6)
    is_admin: bool = False  # По умолчанию не админ


class UserOut(BaseModel):
    """Схема для вывода пользователя."""
    id: int
    email: EmailStr
    name: str
    age: int
    is_admin: bool

    class Config:
        from_attributes = True  # для SQLAlchemy моделей (ранее orm_mode)


class UserLogin(BaseModel):
    """Схема для входа в систему."""
    email: EmailStr
    password: str