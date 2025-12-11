#!/usr/bin/env python3
"""
Скрипт миграции существующих дел в новую систему Legal CMS
Версия: 1.0
Автор: Legal CMS Team
Дата: 2025-12-08
"""

import os
import sys
import re
import asyncio
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging

# Добавляем путь к backend для импорта моделей
sys.path.insert(0, '/home/maimik/Projects/legal-cms/backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.case import Case
from app.models.person import Person
from app.models.document import Document
from app.models.case_persons import case_persons

# ============================================================
# НАСТРОЙКИ
# ============================================================

# Путь к папке со старыми делами
OLD_DATA_PATH = "/mnt/data_vl/DOC/MAA/DB/Projects/TelegramBot/CASE"  # ИЗМЕНИТЬ при необходимости

# База данных
DATABASE_URL = "postgresql://legal_cms_user:PASSWORD@localhost/legal_cms"  # ИЗМЕНИТЬ пароль

# Режим работы
DRY_RUN = True  # True = не записывать в БД, только логи; False = записывать

# Путь для копирования документов
STORAGE_PATH = "/home/maimik/Projects/legal-cms/storage/documents"

# Логирование
LOG_FILE = "/home/maimik/Projects/legal-cms/logs/migration.log"

# ============================================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# ============================================================
# СТАТИСТИКА
# ============================================================

stats = {
    "cases_total": 0,
    "cases_success": 0,
    "cases_failed": 0,
    "persons_created": 0,
    "documents_total": 0,
    "documents_success": 0,
    "documents_failed": 0,
    "errors": []
}

# ============================================================
# МАППИНГ ПРЕФИКСОВ НА ТИПЫ ДЕЛ
# ============================================================

PREFIX_TO_CASE_TYPE = {
    "LS": "civil",           # Гражданское дело
    "CR": "criminal",        # Уголовное дело
    "AD": "administrative",  # Административное дело
    "INT": "international",  # Международное дело
    "ARB": "arbitration",    # Арбитраж
    "GENERAL": "civil"       # По умолчанию
}

# ============================================================
# МАППИНГ РАСШИРЕНИЙ НА ТИПЫ ДОКУМЕНТОВ
# ============================================================

FILENAME_TO_DOCUMENT_TYPE = {
    "cerere": "lawsuit",           # Исковое заявление
    "cererea": "lawsuit",
    "hotarare": "court_decision",  # Решение суда
    "decizie": "court_decision",   # Решение
    "sentinta": "court_decision",  # Приговор
    "procura": "power_of_attorney", # Доверенность
    "contract": "contract",        # Договор
    "dovada": "evidence",          # Доказательство
    "dovezi": "evidence",
    "copia": "evidence",           # Копия (обычно доказательство)
    "plangere": "complaint",       # Жалоба
    "raspuns": "correspondence",   # Ответ
    "adresa": "correspondence",    # Адрес/письмо
    "scrisoare": "correspondence", # Письмо
    "cerinta": "motion",           # Ходатайство
    "expertiza": "expert_opinion", # Экспертное заключение
}

# ============================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================================

def parse_folder_name(folder_name: str) -> Optional[Dict]:
    """
    Парсинг имени папки: 2025-12-04_Alla_Mogopovoi или LS_2025-12-04_Client
    Возвращает: {date: datetime.date, client_name: str, prefix: str}
    """
    # Паттерн с префиксом: PREFIX_YYYY-MM-DD_Name
    pattern_with_prefix = r'^([A-Z]+)_(\d{4}-\d{2}-\d{2})_(.+)$'
    # Паттерн без префикса: YYYY-MM-DD_Name
    pattern_no_prefix = r'^(\d{4}-\d{2}-\d{2})_(.+)$'
    
    match_prefix = re.match(pattern_with_prefix, folder_name)
    if match_prefix:
        prefix = match_prefix.group(1)
        date_str = match_prefix.group(2)
        client_name = match_prefix.group(3).replace('_', ' ')
    else:
        match_no_prefix = re.match(pattern_no_prefix, folder_name)
        if match_no_prefix:
            prefix = "GENERAL"
            date_str = match_no_prefix.group(1)
            client_name = match_no_prefix.group(2).replace('_', ' ')
        else:
            logger.warning(f"Не удалось распарсить имя папки: {folder_name}")
            return None
    
    try:
        open_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        logger.warning(f"Некорректная дата в имени папки: {folder_name}")
        return None
    
    return {
        "prefix": prefix,
        "open_date": open_date,
        "client_name": client_name
    }


def get_case_folders(base_path: str) -> List[Path]:
    """Получение списка папок с делами"""
    path = Path(base_path)
    if not path.exists():
        logger.error(f"Путь не существует: {base_path}")
        sys.exit(1)
    
    folders = [f for f in path.iterdir() if f.is_dir() and not f.name.startswith('.')]
    logger.info(f"Найдено папок с делами: {len(folders)}")
    return folders


def guess_document_type(filename: str) -> str:
    """
    Определение типа документа по имени файла
    """
    filename_lower = filename.lower()
    
    # Проверяем по ключевым словам
    for keyword, doc_type in FILENAME_TO_DOCUMENT_TYPE.items():
        if keyword in filename_lower:
            return doc_type
    
    # По умолчанию
    return "other"


def get_document_files(folder: Path) -> List[Path]:
    """
    Получение списка файлов документов из папки дела
    """
    allowed_extensions = ['.pdf', '.docx', '.doc', '.jpg', '.jpeg', '.png', '.txt']
    files = []
    
    for file in folder.iterdir():
        if file.is_file() and file.suffix.lower() in allowed_extensions:
            files.append(file)
    
    logger.info(f"   Найдено файлов в папке: {len(files)}")
    return files


def copy_document_to_storage(source_file: Path, case_id: int) -> Tuple[str, str]:
    """
    Копирование документа в хранилище
    Возвращает: (relative_path, new_filename)
    """
    import shutil
    
    # Создаём папку для дела в хранилище
    case_storage_dir = Path(STORAGE_PATH) / f"case_{case_id}"
    case_storage_dir.mkdir(parents=True, exist_ok=True)
    
    # Генерируем уникальное имя файла (timestamp + оригинальное имя)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{timestamp}_{source_file.name}"
    destination = case_storage_dir / new_filename
    
    # Копируем файл
    shutil.copy2(source_file, destination)
    
    # Возвращаем относительный путь
    relative_path = f"case_{case_id}/{new_filename}"
    return relative_path, new_filename


# ============================================================
# ОСНОВНЫЕ ФУНКЦИИ МИГРАЦИИ
# ============================================================

def create_or_get_person(db: Session, full_name: str, person_type: str = "client") -> Person:
    """
    Создание или получение существующей персоны
    """
    # Проверяем, существует ли персона
    existing_person = db.query(Person).filter(Person.full_name == full_name).first()
    
    if existing_person:
        logger.info(f"   ✓ Персона уже существует: {full_name}")
        return existing_person
    
    # Создаём новую персону
    new_person = Person(
        full_name=full_name,
        person_type=person_type,
        notes=f"Импортировано из старой системы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    
    if not DRY_RUN:
        db.add(new_person)
        db.flush()  # Получаем ID без commit
        logger.info(f"   ✓ Создана новая персона: {full_name} (ID: {new_person.id})")
    else:
        logger.info(f"   [DRY-RUN] Создана бы персона: {full_name}")
    
    stats["persons_created"] += 1
    return new_person


def create_case(db: Session, parsed_data: Dict) -> Optional[Case]:
    """
    Создание дела в БД
    """
    prefix = parsed_data["prefix"]
    open_date = parsed_data["open_date"]
    client_name = parsed_data["client_name"]
    
    # Генерируем номер дела
    case_number = f"{prefix}-{open_date.strftime('%Y%m%d')}"
    
    # Определяем тип дела
    case_type = PREFIX_TO_CASE_TYPE.get(prefix, "civil")
    
    # Создаём дело
    new_case = Case(
        case_number=case_number,
        case_prefix=prefix,
        case_type=case_type,
        title=f"Дело {client_name}",
        description=f"Импортировано из старой системы. Клиент: {client_name}",
        plaintiff=client_name,
        case_status="archived",  # Старые дела помечаем как архивные
        open_date=open_date,
        tags=["импорт", "старая_система"],
        metadata={
            "imported_at": datetime.now().isoformat(),
            "original_folder": parsed_data.get("folder_name", "")
        }
    )
    
    if not DRY_RUN:
        db.add(new_case)
        db.flush()  # Получаем ID
        logger.info(f"   ✓ Создано дело: {case_number} (ID: {new_case.id})")
    else:
        logger.info(f"   [DRY-RUN] Создано бы дело: {case_number}")
        new_case.id = 9999  # Фиктивный ID для dry-run
    
    return new_case


def create_document(db: Session, case_id: int, file_path: Path) -> Optional[Document]:
    """
    Создание документа в БД
    """
    try:
        # Копируем файл в хранилище
        if not DRY_RUN:
            relative_path, new_filename = copy_document_to_storage(file_path, case_id)
        else:
            relative_path = f"case_{case_id}/{file_path.name}"
            new_filename = file_path.name
        
        # Определяем тип документа
        document_type = guess_document_type(file_path.name)
        
        # Определяем MIME-тип
        mime_type, _ = mimetypes.guess_type(file_path.name)
        file_format = file_path.suffix.upper().replace('.', '')
        
        # Получаем размер файла
        file_size = file_path.stat().st_size
        
        # Создаём запись в БД
        new_document = Document(
            case_id=case_id,
            document_type=document_type,
            file_name=new_filename,
            original_file_name=file_path.name,
            file_path=relative_path,
            file_size=file_size,
            file_format=file_format,
            upload_date=datetime.now(),
            description=f"Импортировано из старой системы",
            tags=["импорт"],
            version=1,
            is_template=False
        )
        
        if not DRY_RUN:
            db.add(new_document)
            db.flush()
            logger.info(f"      ✓ Документ: {file_path.name} → {document_type}")
        else:
            logger.info(f"      [DRY-RUN] Документ: {file_path.name} → {document_type}")
        
        stats["documents_success"] += 1
        return new_document
        
    except Exception as e:
        logger.error(f"      ✗ Ошибка при создании документа {file_path.name}: {e}")
        stats["documents_failed"] += 1
        stats["errors"].append(f"Document: {file_path.name} - {str(e)}")
        return None


def migrate_case(db: Session, folder: Path) -> bool:
    """
    Миграция одного дела
    """
    folder_name = folder.name
    logger.info(f"\n{'='*70}")
    logger.info(f"📂 Обработка папки: {folder_name}")
    logger.info(f"{'='*70}")
    
    stats["cases_total"] += 1
    
    # Парсинг имени папки
    parsed = parse_folder_name(folder_name)
    if not parsed:
        logger.error(f"❌ Не удалось распарсить имя папки: {folder_name}")
        stats["cases_failed"] += 1
        stats["errors"].append(f"Folder parse error: {folder_name}")
        return False
    
    parsed["folder_name"] = folder_name
    
    logger.info(f"   📋 Префикс: {parsed['prefix']}")
    logger.info(f"   📅 Дата открытия: {parsed['open_date']}")
    logger.info(f"   👤 Клиент: {parsed['client_name']}")
    
    try:
        # 1. Создаём дело
        case = create_case(db, parsed)
        if not case:
            raise Exception("Не удалось создать дело")
        
        # 2. Создаём/получаем персону (клиент)
        person = create_or_get_person(db, parsed["client_name"], "client")
        
        # 3. Связываем персону с делом
        if not DRY_RUN and case.id and person.id:
            db.execute(
                case_persons.insert().values(
                    case_id=case.id,
                    person_id=person.id,
                    role_in_case="plaintiff",
                    notes="Клиент (истец)"
                )
            )
            logger.info(f"   ✓ Связь дело-персона создана")
        
        # 4. Обрабатываем документы
        document_files = get_document_files(folder)
        stats["documents_total"] += len(document_files)
        
        logger.info(f"\n   📄 Обработка документов ({len(document_files)} файлов):")
        for doc_file in document_files:
            create_document(db, case.id, doc_file)
        
        # 5. Commit транзакции
        if not DRY_RUN:
            db.commit()
            logger.info(f"\n✅ Дело успешно мигрировано: {case.case_number}")
        else:
            logger.info(f"\n✅ [DRY-RUN] Дело обработано: {parsed['prefix']}-{parsed['open_date']}")
        
        stats["cases_success"] += 1
        return True
        
    except Exception as e:
        if not DRY_RUN:
            db.rollback()
        logger.error(f"\n❌ Ошибка при миграции дела {folder_name}: {e}")
        stats["cases_failed"] += 1
        stats["errors"].append(f"Case: {folder_name} - {str(e)}")
        return False


# ============================================================
# ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """
    Главная функция миграции
    """
    logger.info("\n" + "="*70)
    logger.info("  МИГРАЦИЯ ДЕЛ В LEGAL CMS")
    logger.info("="*70)
    logger.info(f"Режим: {'DRY-RUN (тестовый)' if DRY_RUN else 'РЕАЛЬНАЯ МИГРАЦИЯ'}")
    logger.info(f"Путь к данным: {OLD_DATA_PATH}")
    logger.info(f"База данных: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")
    logger.info("="*70 + "\n")
    
    # Проверка пути к данным
    if not Path(OLD_DATA_PATH).exists():
        logger.error(f"❌ Путь к данным не существует: {OLD_DATA_PATH}")
        sys.exit(1)
    
    # Проверка хранилища
    if not DRY_RUN:
        Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Хранилище документов: {STORAGE_PATH}\n")
    
    # Подключение к БД
    try:
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        logger.info("✓ Подключение к базе данных установлено\n")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        sys.exit(1)
    
    # Получаем список папок с делами
    folders = get_case_folders(OLD_DATA_PATH)
    
    if not folders:
        logger.warning("⚠️  Папок для миграции не найдено!")
        sys.exit(0)
    
    # Подтверждение перед миграцией
    if not DRY_RUN:
        logger.info(f"\n⚠️  ВЫ СОБИРАЕТЕСЬ МИГРИРОВАТЬ {len(folders)} ДЕЛ В БАЗУ ДАННЫХ!")
        response = input("   Продолжить? (yes/no): ").strip().lower()
        if response not in ['yes', 'y', 'да']:
            logger.info("❌ Миграция отменена пользователем")
            sys.exit(0)
        logger.info("")
    
    # Миграция каждого дела
    start_time = datetime.now()
    
    for folder in folders:
        migrate_case(db, folder)
    
    # Закрываем соединение
    db.close()
    
    # Итоговая статистика
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info("\n" + "="*70)
    logger.info("  СТАТИСТИКА МИГРАЦИИ")
    logger.info("="*70)
    logger.info(f"Режим: {'DRY-RUN' if DRY_RUN else 'РЕАЛЬНАЯ МИГРАЦИЯ'}")
    logger.info(f"Время выполнения: {duration:.2f} секунд")
    logger.info(f"\n📁 ДЕЛ:")
    logger.info(f"   Всего обработано: {stats['cases_total']}")
    logger.info(f"   Успешно: {stats['cases_success']}")
    logger.info(f"   Ошибок: {stats['cases_failed']}")
    logger.info(f"\n👤 ПЕРСОН:")
    logger.info(f"   Создано: {stats['persons_created']}")
    logger.info(f"\n📄 ДОКУМЕНТОВ:")
    logger.info(f"   Всего: {stats['documents_total']}")
    logger.info(f"   Успешно: {stats['documents_success']}")
    logger.info(f"   Ошибок: {stats['documents_failed']}")
    
    if stats["errors"]:
        logger.info(f"\n❌ СПИСОК ОШИБОК ({len(stats['errors'])}):")
        for i, error in enumerate(stats["errors"][:10], 1):  # Показываем первые 10
            logger.info(f"   {i}. {error}")
        if len(stats["errors"]) > 10:
            logger.info(f"   ... и ещё {len(stats['errors']) - 10} ошибок")
    
    logger.info("\n" + "="*70)
    
    if DRY_RUN:
        logger.info("\n⚠️  Это был ТЕСТОВЫЙ запуск (DRY-RUN)")
        logger.info("   Для реальной миграции измените DRY_RUN = False в скрипте")
    else:
        logger.info("\n✅ МИГРАЦИЯ ЗАВЕРШЕНА!")
        logger.info(f"   Лог сохранён: {LOG_FILE}")
    
    logger.info("="*70 + "\n")


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Миграция прервана пользователем (Ctrl+C)")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Критическая ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)