from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserCreatedEvent(BaseModel):
    """Событие создания нового пользователя."""
    event_type: str = "user.created"
    user_id: int
    email: str
    name: str
    age: int
    is_admin: bool
    timestamp: str


class UserLoggedInEvent(BaseModel):
    """Событие входа пользователя в систему."""
    event_type: str = "user.logged_in"
    user_id: int
    email: str
    timestamp: str


class CourseCreatedEvent(BaseModel):
    """Событие создания нового курса."""
    event_type: str = "course.created"
    course_id: int
    title: str
    price: float
    created_by: int  # user_id администратора
    timestamp: str

