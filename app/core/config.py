from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""
    
    DB_URL: str = "sqlite:///./test.db"  # по умолчанию SQLite для разработки
    SECRET_KEY: str = "dev-secret"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings() 