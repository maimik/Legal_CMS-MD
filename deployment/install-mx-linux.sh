#!/bin/bash

# Скрипт автоматической установки Legal CMS-MD на MX-Linux
# Дата: 10.12.2025
# Версия: 1.0.0
# ОС: MX-Linux 25 "Infinity" (Debian 13, SysVinit)

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║  Автоматическая установка Legal CMS-MD v1.0.0                ║"
echo "║  ОС: MX-Linux 25 'Infinity' (Debian 13 + SysVinit)           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Проверка прав root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Ошибка: Запустите скрипт с правами root (sudo)"
    exit 1
fi

# Переменные
PROJECT_DIR="/home/maimik/Projects/Legal_CMS-MD"
USER="maimik"
DB_NAME="legal_cms_md"
DB_USER="legal_cms_md_user"
OLLAMA_SERVER="http://192.168.0.21:11434"

echo "📋 Параметры установки:"
echo "  • Путь проекта: $PROJECT_DIR"
echo "  • Пользователь: $USER"
echo "  • База данных: $DB_NAME"
echo "  • Пользователь БД: $DB_USER"
echo "  • Ollama сервер: $OLLAMA_SERVER"
echo ""

read -p "Продолжить установку? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Установка отменена"
    exit 1
fi

# 1. Обновление системы
echo ""
echo "📦 Шаг 1/10: Обновление системы..."
apt update && apt upgrade -y

# 2. Установка зависимостей
echo ""
echo "📦 Шаг 2/10: Установка системных пакетов..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    poppler-utils \
    libmagic1 \
    build-essential \
    libpq-dev

# 3. Установка Node.js 18+
echo ""
echo "📦 Шаг 3/10: Установка Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
    apt install -y nodejs
fi

NODE_VERSION=$(node --version)
echo "  ✅ Node.js установлен: $NODE_VERSION"

# 4. Создание пользователя (если не существует)
echo ""
echo "👤 Шаг 4/10: Проверка пользователя..."
if ! id "$USER" &>/dev/null; then
    useradd -m -s /bin/bash "$USER"
    echo "  ✅ Пользователь $USER создан"
else
    echo "  ✅ Пользователь $USER уже существует"
fi

# 5. Создание директории проекта
echo ""
echo "📁 Шаг 5/10: Создание структуры проекта..."
mkdir -p "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR/storage/documents"
mkdir -p "$PROJECT_DIR/storage/templates"
mkdir -p "$PROJECT_DIR/storage/legal_acts"
mkdir -p "$PROJECT_DIR/backups"
mkdir -p "$PROJECT_DIR/logs"
chown -R "$USER:$USER" "$PROJECT_DIR"
echo "  ✅ Директории созданы"

# 6. Настройка PostgreSQL
echo ""
echo "🗄️  Шаг 6/10: Настройка PostgreSQL..."

# Запуск PostgreSQL (SysVinit)
service postgresql start

# Ожидание запуска PostgreSQL
sleep 3

# Создание БД и пользователя
su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'\"" | grep -q 1 || \
su - postgres << EOF
psql -c "CREATE DATABASE $DB_NAME;"
psql -c "CREATE USER $DB_USER WITH PASSWORD 'ChangeMeInProduction123!';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
psql -c "ALTER DATABASE $DB_NAME OWNER TO $DB_USER;"
echo "  ✅ База данных $DB_NAME создана"
EOF

# 7. Установка Backend зависимостей
echo ""
echo "🐍 Шаг 7/10: Установка Backend (Python)..."
cd "$PROJECT_DIR/backend"

# Создание виртуального окружения
su - "$USER" -c "cd '$PROJECT_DIR/backend' && python3 -m venv venv"

# Установка зависимостей
su - "$USER" -c "cd '$PROJECT_DIR/backend' && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

echo "  ✅ Backend зависимости установлены"

# 8. Создание .env файла
echo ""
echo "⚙️  Шаг 8/10: Создание конфигурации (.env)..."
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    cp "$PROJECT_DIR/backend/.env.example" "$PROJECT_DIR/backend/.env"

    # Генерация SECRET_KEY
    SECRET_KEY=$(openssl rand -hex 32)

    # Замена значений в .env
    sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql+asyncpg://$DB_USER:ChangeMeInProduction123!@localhost/$DB_NAME|g" "$PROJECT_DIR/backend/.env"
    sed -i "s|SECRET_KEY=.*|SECRET_KEY=$SECRET_KEY|g" "$PROJECT_DIR/backend/.env"
    sed -i "s|OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=$OLLAMA_SERVER|g" "$PROJECT_DIR/backend/.env"
    sed -i "s|STORAGE_PATH=.*|STORAGE_PATH=$PROJECT_DIR/storage|g" "$PROJECT_DIR/backend/.env"
    sed -i "s|BACKUP_PATH=.*|BACKUP_PATH=$PROJECT_DIR/backups|g" "$PROJECT_DIR/backend/.env"

    chown "$USER:$USER" "$PROJECT_DIR/backend/.env"
    echo "  ✅ Файл .env создан и настроен"
else
    echo "  ⚠️  Файл .env уже существует, пропускаем"
fi

# 9. Применение миграций БД
echo ""
echo "🗄️  Шаг 9/10: Применение миграций базы данных..."
su - "$USER" -c "cd '$PROJECT_DIR/backend' && source venv/bin/activate && alembic upgrade head"
echo "  ✅ Миграции применены"

# 10. Создание администратора
echo ""
echo "👤 Шаг 10/10: Создание администратора..."

cat > /tmp/create_admin.py << 'EOF'
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import sys
sys.path.insert(0, '/home/maimik/Projects/Legal_CMS-MD/backend')
from app.models.user import User
from app.utils.security import get_password_hash
from app.config import settings

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Проверить существует ли admin
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print("  ⚠️  Администратор уже существует")
            return

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
        print("  ✅ Администратор создан!")
        print("     Логин: admin")
        print("     Пароль: admin123")
        print("     ⚠️  ВАЖНО: Смените пароль после первого входа!")

asyncio.run(create_admin())
EOF

su - "$USER" -c "cd '$PROJECT_DIR/backend' && source venv/bin/activate && python /tmp/create_admin.py"
rm /tmp/create_admin.py

# 11. Установка SysVinit сервиса
echo ""
echo "🔧 Настройка автозапуска (SysVinit)..."

# Копирование init скрипта
cp "$PROJECT_DIR/deployment/init.d/legal-cms-md-backend" /etc/init.d/
chmod +x /etc/init.d/legal-cms-md-backend

# Добавление в автозапуск
update-rc.d legal-cms-md-backend defaults

echo "  ✅ Сервис настроен для автозапуска"

# 12. Установка Frontend
echo ""
echo "🌐 Установка Frontend..."
cd "$PROJECT_DIR/frontend"

su - "$USER" -c "cd '$PROJECT_DIR/frontend' && npm install"

# Сборка production версии
su - "$USER" -c "cd '$PROJECT_DIR/frontend' && npm run build"

echo "  ✅ Frontend собран"

# 13. Настройка Nginx
echo ""
echo "🌍 Настройка Nginx..."

# Копирование конфигурации
cp "$PROJECT_DIR/deployment/nginx/legal-cms-md.conf" /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/legal-cms-md.conf /etc/nginx/sites-enabled/

# Удаление default конфига
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации
nginx -t

# Перезапуск Nginx
service nginx restart

echo "  ✅ Nginx настроен"

# 14. Запуск сервисов
echo ""
echo "🚀 Запуск сервисов..."

service legal-cms-md-backend start

echo "  ✅ Backend запущен"

# 15. Проверка статуса
echo ""
echo "✅ УСТАНОВКА ЗАВЕРШЕНА!"
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                    ИНФОРМАЦИЯ ДЛЯ ВХОДА                      ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "🌐 Веб-интерфейс: http://localhost"
echo "📡 API документация: http://localhost/docs"
echo ""
echo "👤 Первый вход:"
echo "   Логин: admin"
echo "   Пароль: admin123"
echo ""
echo "⚠️  ВАЖНО: Смените пароль после первого входа!"
echo ""
echo "📁 Проект установлен в: $PROJECT_DIR"
echo "📊 База данных: $DB_NAME"
echo "🤖 Ollama сервер: $OLLAMA_SERVER"
echo ""
echo "🔧 Управление сервисом:"
echo "   sudo service legal-cms-md-backend start   - Запустить"
echo "   sudo service legal-cms-md-backend stop    - Остановить"
echo "   sudo service legal-cms-md-backend restart - Перезапустить"
echo "   sudo service legal-cms-md-backend status  - Статус"
echo ""
echo "📝 Логи:"
echo "   Backend: /var/log/legal-cms-md-backend.log"
echo "   Nginx: /var/log/nginx/legal-cms-md-*.log"
echo ""
echo "🎉 Готово к работе!"
echo ""
