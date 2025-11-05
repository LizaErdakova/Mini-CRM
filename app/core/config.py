from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    # Принудительно используем SQLite, если не указано явно
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret")
    
    # Настройки Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_USER_EVENTS: str = "user-events"
    KAFKA_TOPIC_COURSE_EVENTS: str = "course-events"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Игнорируем переменные окружения системы, если они конфликтуют
        case_sensitive = False


settings = Settings()

# Принудительно устанавливаем SQLite для разработки
if "mysql" in settings.DB_URL.lower():
    settings.DB_URL = "sqlite:///./test.db" 