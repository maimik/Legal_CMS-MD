"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения из .env файла"""

    # База данных
    DATABASE_URL: str

    # Безопасность
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Ollama (на отдельном сервере в локальной сети)
    OLLAMA_BASE_URL: str = "http://192.168.0.21:11434"
    OCR_MODEL: str = "deepseek-ocr:latest"
    GENERATION_MODEL: str = "qwen2.5:7b"
    EMBEDDING_MODEL: str = "nomic-embed-text:latest"
    OCR_TIMEOUT: int = 60
    GENERATION_TIMEOUT: int = 30
    OLLAMA_ENABLED: bool = True

    # Хранилище
    STORAGE_PATH: str
    MAX_FILE_SIZE: int = 52428800  # 50 МБ
    ALLOWED_EXTENSIONS: str = "pdf,docx,doc,jpg,jpeg,png,txt"

    # Резервное копирование
    BACKUP_PATH: str
    BACKUP_ENABLED: bool = True
    BACKUP_TIME: str = "03:00"
    BACKUP_KEEP_DAYS: int = 30

    # Email
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "legal-cms@example.com"
    SMTP_TLS: bool = True

    # Напоминания
    REMINDER_ENABLED: bool = True
    REMINDER_DAYS_BEFORE: int = 1
    REMINDER_HOURS_BEFORE: int = 3

    # Режим работы
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "production"

    # CORS
    CORS_ORIGINS: str = "http://localhost:8080,http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def allowed_extensions_list(self) -> List[str]:
        """Список разрешённых расширений файлов"""
        return [ext.strip() for ext in self.ALLOWED_EXTENSIONS.split(',')]

    @property
    def cors_origins_list(self) -> List[str]:
        """Список разрешённых CORS origins"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(',')]


# Глобальный объект настроек
settings = Settings()
