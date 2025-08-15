from fastapi import Depends, HTTPException, status, Cookie
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session
import uuid
from typing import Optional, Dict

from app.dependencies import get_db
from app.models.user import User

# Простое хранилище сессий в памяти (для MVP)
# В реальном проекте лучше использовать Redis или базу данных
active_sessions: Dict[str, int] = {}

security = HTTPBasic()

def authenticate_user(email: str, password: str, db: Session) -> User:
    """Проверяет email и пароль, возвращает пользователя."""
    user = db.query(User).filter(User.email == email).first()
    if not user or user.password != password:  # В MVP простое сравнение, в реальном проекте - bcrypt
        return None
    return user

def create_session_token(user_id: int) -> str:
    """Создаёт новый токен сессии и сохраняет его."""
    token = str(uuid.uuid4())
    active_sessions[token] = user_id
    return token

def get_current_user(
    session_token: Optional[str] = Cookie(None, alias="session_token"),
    db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя по токену сессии."""
    if not session_token or session_token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется аутентификация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = active_sessions[session_token]
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        # Если пользователь удалён, но сессия осталась
        del active_sessions[session_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
        )
    
    return user 