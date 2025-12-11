"""
API endpoints для администрирования
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List
from datetime import datetime
from pathlib import Path
import subprocess
from app.database import get_db
from app.models.user import User
from app.models.system_setting import SystemSetting
from app.models.audit_log import AuditLog
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.admin import SystemSettingResponse, SystemSettingUpdate, AuditLogResponse
from app.api.deps import get_current_user
from app.utils.security import get_password_hash
from app.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def require_admin(current_user: User):
    """Проверка прав администратора"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )


# =============================================================================
# УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ
# =============================================================================

@router.get("/users", response_model=List[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка всех пользователей (только admin)"""
    require_admin(current_user)

    result = await db.execute(select(User).order_by(User.created_at.desc()))
    users = result.scalars().all()

    return users


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание нового пользователя (только admin)"""
    require_admin(current_user)

    # Проверка существования username
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )

    # Проверка существования email
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже используется"
        )

    # Создание пользователя
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role.value,
        is_active=True
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    logger.info(f"Создан пользователь {new_user.username} администратором {current_user.username}")

    return new_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление пользователя (только admin)"""
    require_admin(current_user)

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    # Обновление полей
    update_data = user_data.model_dump(exclude_unset=True, exclude={'password'})

    # Хеширование пароля, если он указан
    if user_data.password:
        update_data['password_hash'] = get_password_hash(user_data.password)

    # Преобразование enum
    if 'role' in update_data and update_data['role']:
        update_data['role'] = update_data['role'].value

    if update_data:
        await db.execute(
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Деактивация пользователя (не удаление!) (только admin)"""
    require_admin(current_user)

    # Нельзя деактивировать самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя деактивировать самого себя"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    # Деактивация (не удаление!)
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(is_active=False)
    )
    await db.commit()

    logger.info(f"Пользователь {user.username} деактивирован администратором {current_user.username}")

    return None


# =============================================================================
# СИСТЕМНЫЕ НАСТРОЙКИ
# =============================================================================

@router.get("/settings", response_model=List[SystemSettingResponse])
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение всех системных настроек (только admin)"""
    require_admin(current_user)

    result = await db.execute(select(SystemSetting))
    settings_list = result.scalars().all()

    return settings_list


@router.put("/settings/{key}", response_model=SystemSettingResponse)
async def update_setting(
    key: str,
    setting_data: SystemSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление системной настройки (только admin)"""
    require_admin(current_user)

    result = await db.execute(select(SystemSetting).where(SystemSetting.key == key))
    setting = result.scalar_one_or_none()

    if not setting:
        # Создать новую настройку
        new_setting = SystemSetting(
            key=key,
            value=setting_data.value,
            description=setting_data.description
        )
        db.add(new_setting)
        await db.commit()
        await db.refresh(new_setting)
        return new_setting

    # Обновить существующую
    await db.execute(
        update(SystemSetting)
        .where(SystemSetting.key == key)
        .values(
            value=setting_data.value,
            description=setting_data.description
        )
    )
    await db.commit()
    await db.refresh(setting)

    return setting


# =============================================================================
# ЖУРНАЛ АУДИТА
# =============================================================================

@router.get("/audit-log", response_model=List[AuditLogResponse])
async def get_audit_log(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение журнала аудита (только admin)"""
    require_admin(current_user)

    result = await db.execute(
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    return logs


# =============================================================================
# РЕЗЕРВНОЕ КОПИРОВАНИЕ
# =============================================================================

@router.post("/backup")
async def create_backup(
    current_user: User = Depends(get_current_user)
):
    """
    Создание резервной копии БД (только admin)

    Использует pg_dump для создания backup
    """
    require_admin(current_user)

    try:
        # Создаём директорию для backups
        backup_dir = Path(settings.STORAGE_PATH).parent / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Генерируем имя файла backup
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f"backup_{timestamp}.sql.gz"
        backup_path = backup_dir / backup_filename

        # Получаем параметры подключения к БД из DATABASE_URL
        # Формат: postgresql+asyncpg://user:password@host/dbname
        import re
        match = re.match(r'postgresql\+asyncpg://([^:]+):([^@]+)@([^/]+)/(.+)', settings.DATABASE_URL)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось распарсить DATABASE_URL"
            )

        user, password, host, dbname = match.groups()

        # Запускаем pg_dump
        cmd = f'PGPASSWORD="{password}" pg_dump -h {host} -U {user} {dbname} | gzip > {backup_path}'

        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 минут таймаут
        )

        if result.returncode != 0:
            logger.error(f"Ошибка при создании backup: {result.stderr}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании backup: {result.stderr}"
            )

        # Получаем размер backup
        backup_size = backup_path.stat().st_size

        logger.info(f"Создан backup: {backup_filename} ({backup_size} байт)")

        return {
            "success": True,
            "filename": backup_filename,
            "size": backup_size,
            "path": str(backup_path),
            "created_at": datetime.now().isoformat()
        }

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Таймаут при создании backup (более 5 минут)"
        )
    except Exception as e:
        logger.error(f"Ошибка при создании backup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании backup: {str(e)}"
        )


# =============================================================================
# СИСТЕМНАЯ ИНФОРМАЦИЯ
# =============================================================================

@router.get("/system-info")
async def get_system_info(
    current_user: User = Depends(get_current_user)
):
    """Получение информации о системе (только admin)"""
    require_admin(current_user)

    from app.utils.ollama import ollama_client

    # Проверка Ollama
    ollama_status = await ollama_client.check_availability()

    # Статистика БД
    from app.database import get_db
    async for db in get_db():
        # Подсчёт записей в таблицах
        from app.models.case import Case
        from app.models.person import Person
        from app.models.document import Document

        cases_count = await db.execute(select(func.count(Case.id)))
        persons_count = await db.execute(select(func.count(Person.id)))
        documents_count = await db.execute(select(func.count(Document.id)))

        return {
            "version": "1.0.0",
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "ollama": {
                "enabled": settings.OLLAMA_ENABLED,
                "available": ollama_status,
                "url": settings.OLLAMA_BASE_URL
            },
            "database": {
                "total_cases": cases_count.scalar(),
                "total_persons": persons_count.scalar(),
                "total_documents": documents_count.scalar()
            },
            "storage": {
                "path": settings.STORAGE_PATH,
                "max_file_size": settings.MAX_FILE_SIZE
            }
        }
