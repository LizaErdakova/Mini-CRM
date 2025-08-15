from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.schemas.user import UserOut, UserLogin
from app.dependencies import get_db
from app.auth import authenticate_user, create_session_token, get_current_user
from app.models.user import User

router = APIRouter(tags=["auth"])
security = HTTPBasic()

@router.post("/login")
def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Вход в систему и создание cookie-сессии."""
    user = authenticate_user(user_data.email, user_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Создаём токен сессии
    session_token = create_session_token(user.id)
    
    # Устанавливаем cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=3600 * 24 * 7,  # 7 дней
    )
    
    return {"message": "Вход выполнен успешно"}


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получить информацию о текущем пользователе."""
    return current_user


@router.post("/logout")
def logout(response: Response):
    """Выход из системы (удаление cookie)."""
    response.delete_cookie(key="session_token")
    return {"message": "Выход выполнен успешно"} 