"""
API endpoints для законодательной базы РМ
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from typing import List, Optional
from datetime import datetime, date
from pathlib import Path
import aiofiles
from app.database import get_db
from app.models.user import User
from app.models.legal_act import LegalAct
from app.schemas.legal_act import (
    LegalActCreate, LegalActUpdate, LegalActResponse, LegalActListResponse,
    ActType, ActStatus
)
from app.api.deps import get_current_user
from app.config import settings
import math
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=LegalActListResponse)
async def get_legal_acts(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    act_type: Optional[ActType] = None,
    act_status: Optional[ActStatus] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка законодательных актов с фильтрацией
    """
    query = select(LegalAct)

    if act_type:
        query = query.where(LegalAct.act_type == act_type.value)

    if act_status:
        query = query.where(LegalAct.act_status == act_status.value)

    if search:
        search_filter = or_(
            LegalAct.title.ilike(f"%{search}%"),
            LegalAct.act_number.ilike(f"%{search}%"),
            LegalAct.full_text.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * size
    query = query.offset(offset).limit(size).order_by(LegalAct.created_at.desc())

    result = await db.execute(query)
    legal_acts = result.scalars().all()

    pages = math.ceil(total / size) if total > 0 else 1

    return LegalActListResponse(
        items=legal_acts,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=LegalActResponse, status_code=status.HTTP_201_CREATED)
async def upload_legal_act(
    file: UploadFile = File(...),
    act_type: ActType = Form(...),
    title: str = Form(...),
    act_number: Optional[str] = Form(None),
    act_date: Optional[date] = Form(None),
    tags: Optional[str] = Form(None),
    act_status: ActStatus = Form(ActStatus.ACTIVE),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка законодательного акта
    """
    # Сохранение файла
    storage_path = Path(settings.STORAGE_PATH) / "legal_acts"
    storage_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_filename = file.filename.replace(" ", "_")
    new_filename = f"{timestamp}_{safe_filename}"
    file_path = storage_path / new_filename

    content = await file.read()
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    # Парсинг тегов
    import json
    tags_list = []
    if tags:
        try:
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            tags_list = [tag.strip() for tag in tags.split(',')]

    # Создание записи
    new_legal_act = LegalAct(
        act_type=act_type.value,
        act_number=act_number,
        act_date=act_date,
        title=title,
        file_path=f"legal_acts/{new_filename}",
        file_size=len(content),
        tags=tags_list,
        act_status=act_status.value
    )

    db.add(new_legal_act)
    await db.commit()
    await db.refresh(new_legal_act)

    return new_legal_act


@router.get("/{legal_act_id}", response_model=LegalActResponse)
async def get_legal_act(
    legal_act_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение законодательного акта по ID"""
    result = await db.execute(select(LegalAct).where(LegalAct.id == legal_act_id))
    legal_act = result.scalar_one_or_none()

    if not legal_act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Законодательный акт с ID {legal_act_id} не найден"
        )

    return legal_act


@router.get("/{legal_act_id}/download")
async def download_legal_act(
    legal_act_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Скачивание файла законодательного акта"""
    result = await db.execute(select(LegalAct).where(LegalAct.id == legal_act_id))
    legal_act = result.scalar_one_or_none()

    if not legal_act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Акт не найден")

    file_full_path = Path(settings.STORAGE_PATH) / legal_act.file_path

    if not file_full_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")

    return FileResponse(path=file_full_path, filename=Path(legal_act.file_path).name)


@router.delete("/{legal_act_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legal_act(
    legal_act_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление законодательного акта (только admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Требуются права администратора")

    result = await db.execute(select(LegalAct).where(LegalAct.id == legal_act_id))
    legal_act = result.scalar_one_or_none()

    if not legal_act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Акт не найден")

    # Удаление файла
    try:
        file_full_path = Path(settings.STORAGE_PATH) / legal_act.file_path
        if file_full_path.exists():
            file_full_path.unlink()
    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}")

    await db.execute(delete(LegalAct).where(LegalAct.id == legal_act_id))
    await db.commit()

    return None
