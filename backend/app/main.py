"""
Главный файл FastAPI приложения
Legal CMS - Система электронного документооборота юридических дел
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
import logging

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Создание приложения FastAPI
app = FastAPI(
    title="Legal CMS API",
    description="Система электронного документооборота юридических дел",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
from app.api.v1 import (
    auth, cases, persons, documents, events,
    legal_acts, templates, search, reports, admin
)

# Аутентификация
app.include_router(auth.router, prefix="/api/auth", tags=["Аутентификация"])

# Основные модули
app.include_router(cases.router, prefix="/api/cases", tags=["Дела"])
app.include_router(persons.router, prefix="/api/persons", tags=["Персоны"])
app.include_router(documents.router, prefix="/api/documents", tags=["Документы"])
app.include_router(events.router, prefix="/api/events", tags=["События"])

# Законодательство и шаблоны
app.include_router(legal_acts.router, prefix="/api/legal-acts", tags=["Законодательство"])
app.include_router(templates.router, prefix="/api/templates", tags=["Шаблоны"])

# Поиск и отчёты
app.include_router(search.router, prefix="/api/search", tags=["Поиск"])
app.include_router(reports.router, prefix="/api/reports", tags=["Отчёты"])

# Администрирование
app.include_router(admin.router, prefix="/api/admin", tags=["Администрирование"])


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info("Starting Legal CMS API...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Проверка подключения к Ollama
    from app.utils.ollama import ollama_client
    ollama_available = await ollama_client.check_availability()
    if ollama_available:
        logger.info("Ollama API доступен")
    else:
        logger.warning("Ollama API недоступен - AI функции будут отключены")


@app.on_event("shutdown")
async def shutdown_event():
    """Действия при остановке приложения"""
    logger.info("Shutting down Legal CMS API...")


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Legal CMS API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Проверка здоровья приложения"""
    from app.utils.ollama import ollama_client

    ollama_status = await ollama_client.check_availability()

    return {
        "status": "healthy",
        "ollama": "available" if ollama_status else "unavailable"
    }
