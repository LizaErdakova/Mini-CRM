from fastapi import FastAPI
import logging
from app.core.database import engine, Base
from app.models.user import User  # импортируем модели для создания таблиц
from app.models.course import Course  # импортируем для создания таблицы курсов
from app.routers import users, auth, courses
from app.core.kafka_consumer import start_consumers

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Создание таблиц при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini-CRM (online courses)")

# Подключение роутеров
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(courses.router)


@app.on_event("startup")
async def startup_event():
    """Запуск Kafka consumers при старте приложения."""
    try:
        start_consumers()
        logging.info("✅ Kafka consumers запущены")
    except Exception as e:
        logging.error(f"❌ Ошибка при запуске Kafka consumers: {e}")


@app.get("/ping")
async def ping():
    """Health-check эндпоинт."""
    return {"ok": True} 