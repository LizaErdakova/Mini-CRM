from fastapi import FastAPI
from app.core.database import engine, Base
from app.models.user import User  # импортируем модели для создания таблиц
from app.models.course import Course  # импортируем для создания таблицы курсов
from app.routers import users, auth, courses

# Создание таблиц при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini-CRM (online courses)")

# Подключение роутеров
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(courses.router)


@app.get("/ping")
async def ping():
    """Health-check эндпоинт."""
    return {"ok": True} 