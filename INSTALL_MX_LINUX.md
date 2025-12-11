# 🚀 Установка Legal CMS-MD на MX-Linux

**Для MX-Linux 25 "Infinity" (Debian 13 + SysVinit + Xfce)**

---

## 📋 Системные требования

**Операционная система:**
- MX-Linux 25 "Infinity"
- Базируется на Debian 13
- Система инициализации: **SysVinit** (НЕ systemd!)
- Рабочий стол: Xfce

**Минимальные требования:**
- CPU: 2 ядра
- RAM: 4 ГБ
- Диск: 20 ГБ свободного места
- Сеть: Доступ к серверу Ollama (192.168.0.21)

**Рекомендуемые:**
- CPU: 4 ядра
- RAM: 8 ГБ
- Диск: 50 ГБ SSD

---

## ⚡ Автоматическая установка (РЕКОМЕНДУЕТСЯ)

### Шаг 1: Распаковать проект

```bash
# Перейти в домашнюю директорию
cd /home/maimik

# Создать папку Projects
mkdir -p Projects
cd Projects

# Распаковать архив (если есть)
tar -xzf ~/legal-cms-md-v1.0.0.tar.gz

# ИЛИ клонировать из Git (если настроен)
git clone your-repo-url Legal_CMS-MD

# Перейти в проект
cd Legal_CMS-MD
```

### Шаг 2: Запустить скрипт установки

```bash
# Сделать скрипт исполняемым
chmod +x deployment/install-mx-linux.sh

# Запустить установку (требуются права root!)
sudo deployment/install-mx-linux.sh
```

**Что делает скрипт:**

1. ✅ Обновляет систему (apt update && upgrade)
2. ✅ Устанавливает PostgreSQL 15+
3. ✅ Устанавливает Python 3.11+
4. ✅ Устанавливает Node.js 18+
5. ✅ Устанавливает Nginx
6. ✅ Создаёт пользователя maimik (если не существует)
7. ✅ Создаёт структуру папок проекта
8. ✅ Настраивает PostgreSQL (создаёт БД и пользователя)
9. ✅ Устанавливает зависимости Python (venv + pip)
10. ✅ Создаёт .env файл с настройками
11. ✅ Применяет миграции Alembic
12. ✅ Создаёт администратора (admin/admin123)
13. ✅ Настраивает SysVinit сервис для автозапуска
14. ✅ Собирает Frontend (npm install + build)
15. ✅ Настраивает Nginx как reverse proxy
16. ✅ Запускает все сервисы

**Время установки:** 10-15 минут

### Шаг 3: Проверить установку

```bash
# Проверить статус сервиса
sudo service legal-cms-md-backend status

# Проверить логи
tail -f /var/log/legal-cms-md-backend.log

# Открыть в браузере
firefox http://localhost
```

**Первый вход:**
- URL: http://localhost
- Логин: `admin`
- Пароль: `admin123`

⚠️ **ВАЖНО:** Смените пароль после первого входа!

---

## 🔧 Ручная установка (опционально)

<details>
<summary>Развернуть инструкцию ручной установки</summary>

### 1. Установка зависимостей

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Установить Python 3
sudo apt install -y python3 python3-pip python3-venv

# Установить Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo bash -
sudo apt install -y nodejs

# Установить Nginx
sudo apt install -y nginx

# Установить утилиты
sudo apt install -y git curl poppler-utils libmagic1 build-essential libpq-dev
```

### 2. Настройка PostgreSQL

```bash
# Запустить PostgreSQL (SysVinit)
sudo service postgresql start

# Войти в PostgreSQL
sudo -u postgres psql

# Создать БД и пользователя
CREATE DATABASE legal_cms_md;
CREATE USER legal_cms_md_user WITH PASSWORD 'YourSecurePassword123!';
GRANT ALL PRIVILEGES ON DATABASE legal_cms_md TO legal_cms_md_user;
ALTER DATABASE legal_cms_md OWNER TO legal_cms_md_user;
\q
```

### 3. Настройка Backend

```bash
# Перейти в backend
cd /home/maimik/Projects/Legal_CMS-MD/backend

# Создать виртуальное окружение
python3 -m venv venv

# Активировать
source venv/bin/activate

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Создать .env файл

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать (используйте nano или vim)
nano .env
```

**Обязательно изменить:**
```env
DATABASE_URL=postgresql+asyncpg://legal_cms_md_user:YourSecurePassword123!@localhost/legal_cms_md
SECRET_KEY=<сгенерировать через: openssl rand -hex 32>
OLLAMA_BASE_URL=http://192.168.0.21:11434
STORAGE_PATH=/home/maimik/Projects/Legal_CMS-MD/storage
BACKUP_PATH=/home/maimik/Projects/Legal_CMS-MD/backups
```

### 5. Применить миграции

```bash
cd /home/maimik/Projects/Legal_CMS-MD/backend
source venv/bin/activate
alembic upgrade head
```

### 6. Создать администратора

Создать файл `create_admin_manual.py`:

```python
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        admin = User(
            username="admin",
            email="admin@legal-cms-md.local",
            full_name="Администратор",
            hashed_password=get_password_hash("admin123"),
            role="admin",
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("✅ Администратор создан: admin/admin123")

asyncio.run(create_admin())
```

Запустить:
```bash
python create_admin_manual.py
```

### 7. Установить Frontend

```bash
cd /home/maimik/Projects/Legal_CMS-MD/frontend

# Установить зависимости
npm install

# Собрать production версию
npm run build
```

### 8. Настроить Nginx

```bash
# Скопировать конфигурацию
sudo cp deployment/nginx/legal-cms-md.conf /etc/nginx/sites-available/

# Создать симлинк
sudo ln -sf /etc/nginx/sites-available/legal-cms-md.conf /etc/nginx/sites-enabled/

# Удалить default
sudo rm /etc/nginx/sites-enabled/default

# Проверить конфигурацию
sudo nginx -t

# Перезапустить Nginx
sudo service nginx restart
```

### 9. Настроить автозапуск (SysVinit)

```bash
# Скопировать init скрипт
sudo cp deployment/init.d/legal-cms-md-backend /etc/init.d/

# Сделать исполняемым
sudo chmod +x /etc/init.d/legal-cms-md-backend

# Добавить в автозапуск
sudo update-rc.d legal-cms-md-backend defaults

# Запустить сервис
sudo service legal-cms-md-backend start
```

### 10. Проверить

```bash
# Статус сервиса
sudo service legal-cms-md-backend status

# Логи
tail -f /var/log/legal-cms-md-backend.log

# Открыть браузер
firefox http://localhost
```

</details>

---

## 🔐 Важные настройки

### 1. Сменить пароль БД

**В файле .env:**
```env
DATABASE_URL=postgresql+asyncpg://legal_cms_md_user:NEW_PASSWORD@localhost/legal_cms_md
```

**В PostgreSQL:**
```sql
sudo -u postgres psql
ALTER USER legal_cms_md_user WITH PASSWORD 'NEW_PASSWORD';
\q
```

### 2. Сменить SECRET_KEY

**Сгенерировать:**
```bash
openssl rand -hex 32
```

**В файле .env:**
```env
SECRET_KEY=<вставить сгенерированный ключ>
```

### 3. Сменить пароль администратора

После первого входа:
1. Войти как admin/admin123
2. Перейти в профиль
3. Сменить пароль

---

## 🔧 Управление сервисами

### Backend (SysVinit)

```bash
# Запустить
sudo service legal-cms-md-backend start

# Остановить
sudo service legal-cms-md-backend stop

# Перезапустить
sudo service legal-cms-md-backend restart

# Статус
sudo service legal-cms-md-backend status

# Логи
tail -f /var/log/legal-cms-md-backend.log
```

### Nginx

```bash
# Запустить
sudo service nginx start

# Остановить
sudo service nginx stop

# Перезапустить
sudo service nginx restart

# Проверить конфигурацию
sudo nginx -t

# Логи
tail -f /var/log/nginx/legal-cms-md-access.log
tail -f /var/log/nginx/legal-cms-md-error.log
```

### PostgreSQL

```bash
# Запустить
sudo service postgresql start

# Остановить
sudo service postgresql stop

# Перезапустить
sudo service postgresql restart

# Статус
sudo service postgresql status
```

---

## 📁 Структура проекта

```
/home/maimik/Projects/Legal_CMS-MD/
├── backend/                    - Backend (FastAPI)
│   ├── venv/                   - Виртуальное окружение Python
│   ├── app/                    - Код приложения
│   ├── alembic/                - Миграции БД
│   ├── .env                    - Конфигурация (создаётся при установке)
│   └── requirements.txt        - Зависимости Python
├── frontend/                   - Frontend (Vue.js)
│   ├── dist/                   - Собранная версия (после npm run build)
│   ├── src/                    - Исходники
│   └── package.json            - Зависимости Node.js
├── storage/                    - Загруженные файлы
│   ├── documents/              - Документы дел
│   ├── templates/              - Шаблоны DOCX
│   └── legal_acts/             - Законы РМ
├── backups/                    - Резервные копии БД
├── logs/                       - Логи приложения
└── deployment/                 - Скрипты развёртывания
    ├── init.d/                 - SysVinit скрипты
    ├── nginx/                  - Конфигурация Nginx
    └── install-mx-linux.sh     - Автоматическая установка
```

---

## 🌐 Доступ к системе

**После установки:**

- **Веб-интерфейс:** http://localhost
- **API документация (Swagger):** http://localhost/docs
- **Админ панель:** http://localhost/admin

**Ollama API:**
- Сервер: http://192.168.0.21:11434
- Проверка: `curl http://192.168.0.21:11434/api/tags`

---

## 🐛 Устранение проблем

### Backend не запускается

```bash
# Проверить логи
tail -f /var/log/legal-cms-md-backend.log

# Проверить .env файл
cat /home/maimik/Projects/Legal_CMS-MD/backend/.env

# Проверить БД доступна
sudo -u postgres psql -l | grep legal_cms_md

# Запустить вручную
cd /home/maimik/Projects/Legal_CMS-MD/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Nginx показывает 502 Bad Gateway

```bash
# Проверить Backend запущен
sudo service legal-cms-md-backend status

# Проверить порт 8000 слушается
netstat -tlnp | grep 8000

# Проверить логи Nginx
tail -f /var/log/nginx/legal-cms-md-error.log
```

### Ollama недоступен

```bash
# Проверить доступность сервера
ping 192.168.0.21

# Проверить API
curl http://192.168.0.21:11434/api/tags

# Если не доступен - проверить firewall и сеть
```

---

## 💾 Резервное копирование

### Автоматический backup БД (cron)

Создать файл `/etc/cron.d/legal-cms-md-backup`:

```bash
# Ежедневный backup в 3:00
0 3 * * * maimik /home/maimik/Projects/Legal_CMS-MD/deployment/backup.sh
```

### Ручной backup

```bash
# База данных
pg_dump -U legal_cms_md_user legal_cms_md > backup_$(date +\%Y\%m\%d).sql

# Файлы
tar -czf documents_backup_$(date +\%Y\%m\%d).tar.gz /home/maimik/Projects/Legal_CMS-MD/storage/
```

---

## ✅ Чеклист после установки

- [ ] Backend запущен и доступен
- [ ] Nginx запущен
- [ ] PostgreSQL запущен
- [ ] Вход в систему работает (admin/admin123)
- [ ] Пароль администратора изменён
- [ ] SECRET_KEY сгенерирован новый
- [ ] Пароль БД изменён
- [ ] Ollama сервер доступен (192.168.0.21:11434)
- [ ] Создано первое дело (тест)
- [ ] Загружен первый документ (тест)
- [ ] OCR работает
- [ ] Настроен автоматический backup
- [ ] Проверены логи (нет ошибок)

---

## 🎉 Готово!

Система установлена и готова к работе!

**Следующие шаги:**
1. Войти в систему (admin/admin123)
2. Сменить пароль администратора
3. Создать нового пользователя (assistant)
4. Создать первое дело
5. Загрузить законодательную базу РМ
6. Создать шаблоны документов

**Документация:**
- См. QUICK_START.md - ежедневное использование
- См. TROUBLESHOOTING.md - решение проблем
- См. DOCS_INDEX.md - вся документация

---

**Дата:** 10.12.2025
**Версия:** 1.0.0
**ОС:** MX-Linux 25 "Infinity"
