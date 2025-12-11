# 🚀 QUICK START - Legal CMS

Быстрый старт для запуска и использования Legal CMS

**Дата:** 09.12.2025
**Версия:** 1.0.0
**Статус:** Backend 100% готов ✅

---

## 📋 Предварительные требования

### Обязательно:
- ✅ Python 3.11+
- ✅ PostgreSQL 15+
- ✅ Ollama (для OCR и AI функций)

### Опционально:
- Node.js 18+ (для frontend, когда будет готов)
- Git

---

## 🔧 ШАГИ УСТАНОВКИ

### 1. Установка PostgreSQL

```bash
# На Windows используйте PostgreSQL installer
# https://www.postgresql.org/download/windows/

# Создание базы данных
psql -U postgres
CREATE DATABASE legal_cms;
CREATE USER legal_cms_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE legal_cms TO legal_cms_user;
\q
```

### 2. Установка Ollama и моделей

```bash
# Ollama уже установлен, проверим модели:
ollama list

# Убедитесь, что есть эти модели (УЖЕ ЕСТЬ):
# ✅ deepseek-ocr:latest      - для OCR
# ✅ qwen2.5:7b               - для генерации текста
# ✅ nomic-embed-text:latest  - для embeddings

# Если какой-то модели нет:
ollama pull deepseek-ocr:latest
ollama pull qwen2.5:7b
ollama pull nomic-embed-text:latest
```

**💡 РЕКОМЕНДУЕМ ДОБАВИТЬ:**
```bash
# Для лучшей работы с русским и румынским языками:
ollama pull bge-m3:latest  # Мультиязычные embeddings (1.2 GB)

# Для анализа сложных юридических дел:
ollama pull deepseek-r1:latest  # Reasoning модель (5.2 GB)

# Для анализа изображений документов:
ollama pull llava-llama3:latest  # Vision модель (5.5 GB)
```

### 3. Установка зависимостей Python

```bash
cd Z:\FQ\Документооборот\Jurist\backend

# Создание виртуального окружения
python -m venv venv

# Активация (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Или (Windows CMD)
venv\Scripts\activate.bat

# Установка зависимостей
pip install -r requirements.txt
```

**⚠️ ВАЖНО для Windows:**

```bash
# Установка python-magic (требует libmagic)
# Скачайте python-magic-bin для Windows:
pip install python-magic-bin

# Установка poppler (для pdf2image)
# Скачайте poppler для Windows:
# https://github.com/oschwartz10612/poppler-windows/releases/
# Распакуйте и добавьте poppler/bin в PATH
```

### 4. Настройка .env файла

```bash
# Копируем пример
cp .env.example .env

# Редактируем .env
notepad .env
```

**Минимальная конфигурация .env:**
```env
# База данных
DATABASE_URL=postgresql+asyncpg://legal_cms_user:your_strong_password@localhost/legal_cms

# Безопасность (ИЗМЕНИТЕ!)
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OCR_MODEL=deepseek-ocr:latest
GENERATION_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text:latest
OLLAMA_ENABLED=true
OCR_TIMEOUT=120.0
GENERATION_TIMEOUT=60.0

# Хранилище
STORAGE_PATH=Z:/FQ/Документооборот/Jurist/storage
MAX_FILE_SIZE=52428800

# Режим
DEBUG=true
LOG_LEVEL=INFO
ENVIRONMENT=development

# CORS (разрешённые источники)
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

**🔐 Генерация SECRET_KEY:**
```bash
# В Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Создание структуры директорий

```bash
# Создаём директории для хранилища
mkdir -p Z:\FQ\Документооборот\Jurist\storage\documents
mkdir -p Z:\FQ\Документооборот\Jurist\storage\templates
mkdir -p Z:\FQ\Документооборот\Jurist\storage\legal_acts
mkdir -p Z:\FQ\Документооборот\Jurist\backups
mkdir -p Z:\FQ\Документооборот\Jurist\backend\logs
```

### 6. Применение миграций БД

```bash
cd Z:\FQ\Документооборот\Jurist\backend

# Убедитесь, что виртуальное окружение активировано
.\venv\Scripts\Activate.ps1

# Применяем миграции
alembic upgrade head
```

**Ожидаемый вывод:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 001, Initial migration - create all tables
```

### 7. Создание первого пользователя (admin)

```bash
# Запустите Python интерпретатор
python

# Выполните:
```

```python
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.utils.security import get_password_hash

# Подключение к БД (замените на ваш DATABASE_URL без +asyncpg)
DATABASE_URL = "postgresql://legal_cms_user:your_strong_password@localhost/legal_cms"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

# Создание admin пользователя
admin = User(
    username="admin",
    email="admin@legal-cms.local",
    password_hash=get_password_hash("admin123"),  # ИЗМЕНИТЕ ПАРОЛЬ!
    full_name="Администратор",
    role="admin",
    is_active=True
)

db.add(admin)
db.commit()
print(f"✅ Создан admin пользователь: {admin.username}")
db.close()
exit()
```

---

## 🎯 ЗАПУСК BACKEND

### Вариант 1: Разработка (с автоперезагрузкой)

```bash
cd Z:\FQ\Документооборот\Jurist\backend
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Вариант 2: Production

```bash
cd Z:\FQ\Документооборот\Jurist\backend
.\venv\Scripts\Activate.ps1

uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Ожидаемый вывод:**
```
INFO:     Starting Legal CMS API...
INFO:     Environment: development
INFO:     Debug mode: True
INFO:     Ollama API доступен
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## 🧪 ПРОВЕРКА РАБОТЫ

### 1. Health Check

Откройте браузер: http://localhost:8000/health

Ожидаемый ответ:
```json
{
  "status": "healthy",
  "ollama": "available"
}
```

### 2. Swagger UI (Документация API)

Откройте браузер: http://localhost:8000/api/docs

Здесь вы увидите все 60+ endpoints с интерактивной документацией!

### 3. Тест аутентификации

**Способ 1: Через Swagger UI**
1. Откройте http://localhost:8000/api/docs
2. Найдите `POST /api/auth/login`
3. Нажмите "Try it out"
4. Введите:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. Нажмите "Execute"
6. Вы получите `access_token` и `refresh_token`

**Способ 2: Через curl**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

**Ожидаемый ответ:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 4. Тест создания дела

В Swagger UI:
1. Скопируйте `access_token` из предыдущего шага
2. Нажмите кнопку "Authorize" вверху страницы
3. Введите: `Bearer <your_access_token>`
4. Найдите `POST /api/cases`
5. Попробуйте создать дело:

```json
{
  "case_prefix": "LS",
  "case_type": "civil",
  "title": "Тестовое дело",
  "description": "Это тестовое дело для проверки API",
  "plaintiff": "Иванов И.И.",
  "defendant": "Петров П.П.",
  "case_status": "active",
  "open_date": "2025-12-09",
  "tags": ["тест"]
}
```

### 5. Тест загрузки документа

В Swagger UI:
1. Найдите `POST /api/documents`
2. Загрузите PDF файл
3. Заполните поля:
   - `file`: выберите PDF файл
   - `document_type`: "other"
   - `auto_ocr`: true (автоматический OCR)

Подождите ~10-30 секунд на OCR обработку.

---

## 📚 ОСНОВНЫЕ ЭНДПОИНТЫ

### Аутентификация
```
POST   /api/auth/login      - Вход (получение токенов)
POST   /api/auth/refresh    - Обновление токена
GET    /api/auth/me         - Текущий пользователь
POST   /api/auth/logout     - Выход
```

### Дела
```
GET    /api/cases           - Список дел (с фильтрами)
POST   /api/cases           - Создать дело
GET    /api/cases/{id}      - Получить дело
PUT    /api/cases/{id}      - Обновить дело
DELETE /api/cases/{id}      - Удалить дело (admin)
GET    /api/cases/{id}/timeline - История дела
```

### Документы
```
GET    /api/documents                - Список документов
POST   /api/documents                - Загрузить документ
GET    /api/documents/{id}/download  - Скачать файл
GET    /api/documents/{id}/preview   - Просмотр
POST   /api/documents/{id}/ocr       - Запустить OCR
```

### Календарь
```
GET    /api/events/calendar/{year}/{month}  - События за месяц
GET    /api/events/upcoming/week             - События на неделю
```

### Поиск
```
GET    /api/search?q=текст              - Глобальный поиск
GET    /api/search/fulltext?q=текст     - Полнотекстовый поиск
```

### Админ
```
GET    /api/admin/users         - Список пользователей
POST   /api/admin/backup        - Создать backup БД
GET    /api/admin/system-info   - Информация о системе
```

**Полная документация:** http://localhost:8000/api/docs

---

## 🔧 НАСТРОЙКА OLLAMA ДЛЯ ОПТИМАЛЬНОЙ РАБОТЫ

### Текущая конфигурация (.env):
```env
OCR_MODEL=deepseek-ocr:latest
GENERATION_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text:latest
```

### 🎯 РЕКОМЕНДУЕМАЯ конфигурация:

```env
# OCR - распознавание текста
OCR_MODEL=deepseek-ocr:latest

# Генерация текста - для шаблонов
GENERATION_MODEL=qwen2.5:7b

# Embeddings - ЗАМЕНИТЬ на мультиязычную модель
EMBEDDING_MODEL=bge-m3:latest  # Лучше для русского + румынского!

# НОВЫЕ модели (добавить в config.py):
VISION_MODEL=llava-llama3:latest        # Анализ изображений документов
REASONING_MODEL=deepseek-r1:latest      # Анализ юридических дел
ADVANCED_MODEL=command-r:35b            # Сложные юридические документы (опционально, большая)
```

### Обновление config.py:

```python
# Добавить в app/config.py:
class Settings(BaseSettings):
    # ... существующие настройки ...

    # Ollama models
    OCR_MODEL: str = "deepseek-ocr:latest"
    GENERATION_MODEL: str = "qwen2.5:7b"
    EMBEDDING_MODEL: str = "bge-m3:latest"  # ИЗМЕНЕНО!

    # Новые модели
    VISION_MODEL: str = "llava-llama3:latest"
    REASONING_MODEL: str = "deepseek-r1:latest"
    ADVANCED_MODEL: str = "command-r:35b"
```

### Какая модель для чего:

| Модель | Размер | Назначение | Использование в проекте |
|--------|--------|------------|-------------------------|
| **deepseek-ocr** | 6.7 GB | OCR текста из PDF/изображений | ✅ Автоматическое распознавание документов |
| **qwen2.5:7b** | 4.7 GB | Генерация текста | ✅ Заполнение шаблонов документов |
| **bge-m3** ⭐ | 1.2 GB | Мультиязычные embeddings | ✅ Семантический поиск (русский+румынский) |
| **nomic-embed-text** | 274 MB | Embeddings | ❌ Заменить на bge-m3 |
| **llava-llama3** ⭐ | 5.5 GB | Vision анализ | 💡 Анализ сканов, извлечение структуры |
| **deepseek-r1** ⭐ | 5.2 GB | Reasoning (рассуждения) | 💡 Анализ дел, поиск противоречий |
| **command-r:35b** | 18 GB | Сложные задачи | 💡 Генерация исковых заявлений (опционально) |
| **deepseek-coder** | 3.8 GB | Кодогенерация | ❌ Не нужна для документов |
| **mistral/gemma/llama** | - | Общие модели | ❌ Не нужны (есть специализированные) |

**⭐ = Рекомендуем добавить**

---

## 🐛 TROUBLESHOOTING (Решение проблем)

### Проблема 1: Alembic не может подключиться к БД

**Ошибка:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Решение:**
1. Проверьте, что PostgreSQL запущен
2. Проверьте DATABASE_URL в .env
3. Попробуйте подключиться вручную:
   ```bash
   psql -U legal_cms_user -d legal_cms
   ```

### Проблема 2: Ollama недоступен

**Ошибка в логах:**
```
Ollama API недоступен - AI функции будут отключены
```

**Решение:**
1. Проверьте, что Ollama запущен:
   ```bash
   ollama list
   ```
2. Проверьте OLLAMA_BASE_URL в .env (должен быть http://localhost:11434)
3. Попробуйте:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Проблема 3: OCR не работает

**Ошибка:**
```
Ошибка при OCR обработке PDF
```

**Решение:**
1. Проверьте, что установлен poppler (для pdf2image):
   - Windows: скачайте poppler-windows и добавьте в PATH
   - Проверка: `where poppler` или `where pdftoppm`

2. Проверьте, что модель загружена:
   ```bash
   ollama list | grep deepseek-ocr
   ```

### Проблема 4: Ошибка импорта magic

**Ошибка:**
```
ImportError: failed to find libmagic
```

**Решение (Windows):**
```bash
pip uninstall python-magic
pip install python-magic-bin
```

### Проблема 5: Slow performance (медленно работает)

**Решение:**
1. Используйте меньшие модели для разработки
2. Увеличьте timeout в .env:
   ```env
   OCR_TIMEOUT=300.0
   GENERATION_TIMEOUT=120.0
   ```
3. Отключите автоматический OCR:
   - При загрузке документа установите `auto_ocr=false`

---

## 📦 МИГРАЦИЯ СТАРЫХ ДАННЫХ

Если у вас есть 20 дел в старой системе:

```bash
cd Z:\FQ\Документооборот\Jurist

# Отредактируйте migrate_old_data.py:
# - Установите DRY_RUN = False
# - Проверьте OLD_DATA_PATH
# - Проверьте DATABASE_URL

# Запустите миграцию
python migrate_old_data.py
```

**Ожидается:**
- Миграция 20 дел
- Создание персон
- Копирование документов
- Подробный лог в `logs/migration.log`

---

## 🎯 СЛЕДУЮЩИЕ ШАГИ

### 1. Создание дополнительных пользователей

Через Swagger UI (`POST /api/auth/register`) или админку (`POST /api/admin/users`)

### 2. Загрузка шаблонов документов

```
POST /api/templates
```
Загрузите DOCX файлы с переменными типа `{{case_number}}`, `{{plaintiff}}` и т.д.

### 3. Загрузка законодательной базы РМ

```
POST /api/legal-acts
```
Загрузите PDF файлы с законами, кодексами, постановлениями

### 4. Настройка автоматических backup

Добавьте в Windows Task Scheduler:
```bash
curl -X POST "http://localhost:8000/api/admin/backup" \
  -H "Authorization: Bearer <admin_token>"
```

### 5. Разработка Frontend

Следующий этап - Vue.js 3 + Vuetify 3 интерфейс

---

## 📖 ДОПОЛНИТЕЛЬНАЯ ДОКУМЕНТАЦИЯ

- **Полное ТЗ:** `TZ_Full_Complete.md`
- **ТЗ для разработчиков:** `TZ_For_Programmers.md`
- **Прогресс разработки:** `PROGRESS.md`
- **Контекст для AI:** `CLAUDE.MD`
- **Итоги разработки:** `SUMMARY.md`
- **API Swagger:** http://localhost:8000/api/docs
- **API ReDoc:** http://localhost:8000/api/redoc

---

## 🆘 ПОДДЕРЖКА

При возникновении проблем:

1. Проверьте логи: `backend/logs/`
2. Проверьте Swagger UI: http://localhost:8000/api/docs
3. Проверьте health: http://localhost:8000/health
4. Проверьте конфигурацию в `.env`

---

## 🎉 ГОТОВО!

Backend Legal CMS полностью готов к использованию!

**Версия:** 1.0.0
**Дата:** 09.12.2025
**Статус:** Production Ready ✅
