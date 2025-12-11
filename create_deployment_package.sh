#!/bin/bash

# Скрипт создания пакета для развёртывания Legal CMS-MD
# Дата: 10.12.2025
# Версия: 1.0.0

set -e

echo "╔═══════════════════════════════════════════════════════╗"
echo "║  Создание пакета развёртывания Legal CMS-MD v1.0.0      ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Переменные
VERSION="1.0.0"
PROJECT_NAME="legal-cms-md"
ARCHIVE_NAME="${PROJECT_NAME}-v${VERSION}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Определить текущую директорию
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$SCRIPT_DIR"

echo "📂 Рабочая директория: $PROJECT_DIR"
echo ""

# Создать временную папку
TEMP_DIR="/tmp/${PROJECT_NAME}_build_${TIMESTAMP}"
mkdir -p "$TEMP_DIR"

echo "🗂️  Копирование файлов проекта..."

# Копировать структуру проекта
rsync -av --progress \
  --exclude 'node_modules' \
  --exclude 'venv' \
  --exclude '__pycache__' \
  --exclude '.git' \
  --exclude '*.pyc' \
  --exclude '.DS_Store' \
  --exclude '.env' \
  --exclude 'dist' \
  --exclude 'build' \
  --exclude '*.log' \
  --exclude 'create_deployment_package.sh' \
  "$PROJECT_DIR/" "$TEMP_DIR/Jurist/"

echo ""
echo "✅ Файлы скопированы"
echo ""

# Создать пустые папки для хранилища
echo "📁 Создание структуры папок..."
mkdir -p "$TEMP_DIR/Jurist/storage/documents"
mkdir -p "$TEMP_DIR/Jurist/storage/templates"
mkdir -p "$TEMP_DIR/Jurist/storage/legal_acts"
mkdir -p "$TEMP_DIR/Jurist/backups"

# Создать .gitkeep для пустых папок
touch "$TEMP_DIR/Jurist/storage/documents/.gitkeep"
touch "$TEMP_DIR/Jurist/storage/templates/.gitkeep"
touch "$TEMP_DIR/Jurist/storage/legal_acts/.gitkeep"
touch "$TEMP_DIR/Jurist/backups/.gitkeep"

echo "✅ Структура папок создана"
echo ""

# Создать README для администратора
cat > "$TEMP_DIR/Jurist/ADMIN_README.txt" << 'EOF'
╔═══════════════════════════════════════════════════════════════╗
║              LEGAL CMS - ИНСТРУКЦИЯ ДЛЯ АДМИНИСТРАТОРА        ║
╚═══════════════════════════════════════════════════════════════╝

🎯 ВЫ АДМИНИСТРАТОР? НАЧНИТЕ ЗДЕСЬ!

1. Прочитайте START_HERE.txt - краткий обзор
2. Следуйте INSTALLATION_GUIDE.md - полная установка (пошагово!)
3. Используйте QUICK_START.md - для ежедневного запуска
4. При проблемах: TROUBLESHOOTING.md - решение 50+ ошибок

═══════════════════════════════════════════════════════════════

📋 ЧТО НУЖНО УСТАНОВИТЬ НА СЕРВЕРЕ:

1. PostgreSQL 15+  (база данных)
2. Python 3.11+    (backend)
3. Node.js 18+     (frontend)
4. Ollama          (AI функции)

═══════════════════════════════════════════════════════════════

⏱️ ВРЕМЯ РАЗВЁРТЫВАНИЯ: 1-2 часа

💻 СИСТЕМНЫЕ ТРЕБОВАНИЯ:
- CPU: 4 ядра (минимум 2)
- RAM: 8 ГБ (минимум 4 ГБ)
- Диск: 50 ГБ SSD (минимум 20 ГБ)
- ОС: MX-Linux (Debian-based)

═══════════════════════════════════════════════════════════════

🚀 БЫСТРАЯ УСТАНОВКА (краткая версия):

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Настроить .env файл
alembic upgrade head
python create_admin.py
uvicorn app.main:app --reload &

cd ../frontend
npm install
npm run dev &

# В третьем окне:
ollama serve &

# Открыть: http://localhost:5173
# Логин: admin / Пароль: admin123

═══════════════════════════════════════════════════════════════

📚 ВСЯ ДОКУМЕНТАЦИЯ:

См. файл DOCS_INDEX.md - там список всех 14 документов!

═══════════════════════════════════════════════════════════════

✅ Удачного развёртывания!
EOF

echo "✅ Создан ADMIN_README.txt"
echo ""

# Создать архив tar.gz
echo "📦 Создание архива tar.gz..."
cd "$TEMP_DIR"
tar -czf "${ARCHIVE_NAME}.tar.gz" Jurist/

# Переместить архив в исходную директорию
mv "${ARCHIVE_NAME}.tar.gz" "$PROJECT_DIR/"

echo "✅ Архив создан: ${ARCHIVE_NAME}.tar.gz"
echo ""

# Создать архив zip (для Windows)
echo "📦 Создание архива zip..."
zip -r "${ARCHIVE_NAME}.zip" Jurist/ -q

# Переместить архив в исходную директорию
mv "${ARCHIVE_NAME}.zip" "$PROJECT_DIR/"

echo "✅ Архив создан: ${ARCHIVE_NAME}.zip"
echo ""

# Показать размеры
echo "📊 Размеры архивов:"
ls -lh "$PROJECT_DIR/${ARCHIVE_NAME}.tar.gz" | awk '{print "  tar.gz:", $5}'
ls -lh "$PROJECT_DIR/${ARCHIVE_NAME}.zip" | awk '{print "  zip:   ", $5}'
echo ""

# Подсчитать количество файлов
FILE_COUNT=$(find "$TEMP_DIR/Jurist" -type f | wc -l)
echo "📁 Файлов в архиве: $FILE_COUNT"
echo ""

# Очистить временную папку
echo "🧹 Очистка временных файлов..."
rm -rf "$TEMP_DIR"
echo "✅ Временные файлы удалены"
echo ""

# Создать чек-сумму
echo "🔐 Создание контрольных сумм..."
cd "$PROJECT_DIR"
sha256sum "${ARCHIVE_NAME}.tar.gz" > "${ARCHIVE_NAME}.tar.gz.sha256"
sha256sum "${ARCHIVE_NAME}.zip" > "${ARCHIVE_NAME}.zip.sha256"
echo "✅ Контрольные суммы созданы"
echo ""

# Итоговый отчёт
echo "╔═══════════════════════════════════════════════════════╗"
echo "║                 ✅ ПАКЕТ ГОТОВ!                       ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""
echo "📦 Созданы файлы:"
echo "  • ${ARCHIVE_NAME}.tar.gz (для Linux)"
echo "  • ${ARCHIVE_NAME}.tar.gz.sha256 (контрольная сумма)"
echo "  • ${ARCHIVE_NAME}.zip (для Windows)"
echo "  • ${ARCHIVE_NAME}.zip.sha256 (контрольная сумма)"
echo ""
echo "📁 Местоположение:"
echo "  $PROJECT_DIR/"
echo ""
echo "📧 Передайте администратору:"
echo "  1. Архив (tar.gz или zip)"
echo "  2. Файл DEPLOYMENT_PACKAGE.md"
echo "  3. Контрольную сумму (.sha256)"
echo ""
echo "🎉 Готово к развёртыванию!"
echo ""
