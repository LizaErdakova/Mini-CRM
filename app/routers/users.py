from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.user import UserCreate, UserOut
from app.schemas.events import UserCreatedEvent
from app.models.user import User
from app.dependencies import get_db
from app.core.kafka_producer import send_event
from app.core.config import settings


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Создать нового пользователя."""
    # Проверка на существующий email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован"
        )
    
    # Создание пользователя
    db_user = User(**user_data.dict())
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Отправка события в Kafka
    event = UserCreatedEvent(
        user_id=db_user.id,
        email=db_user.email,
        name=db_user.name,
        age=db_user.age,
        is_admin=db_user.is_admin,
        timestamp=datetime.now().isoformat()
    )
    send_event(settings.KAFKA_TOPIC_USER_EVENTS, event.dict())
    
    return db_user


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Получить пользователя по ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    
    return user


@router.get("", response_model=list[UserOut])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Получить список пользователей с пагинацией."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users 