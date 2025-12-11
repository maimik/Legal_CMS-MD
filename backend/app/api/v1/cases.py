"""
API endpoints для управления делами
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.case import Case
from app.schemas.case import (
    CaseCreate, CaseUpdate, CaseResponse, CaseListResponse, CaseStatus, CaseType
)
from app.api.deps import get_current_user
import math

router = APIRouter()


@router.get("/", response_model=CaseListResponse)
async def get_cases(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    case_type: Optional[CaseType] = None,
    case_status: Optional[CaseStatus] = None,
    search: Optional[str] = None,
    tags: Optional[List[str]] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка дел с фильтрацией и пагинацией

    - **page**: номер страницы (начиная с 1)
    - **size**: количество элементов на странице
    - **case_type**: фильтр по типу дела
    - **case_status**: фильтр по статусу
    - **search**: поиск по номеру дела, названию, истцу, ответчику
    - **tags**: фильтр по тегам
    """
    # Базовый запрос
    query = select(Case)

    # Фильтры
    if case_type:
        query = query.where(Case.case_type == case_type.value)

    if case_status:
        query = query.where(Case.case_status == case_status.value)

    if search:
        search_filter = or_(
            Case.case_number.ilike(f"%{search}%"),
            Case.title.ilike(f"%{search}%"),
            Case.plaintiff.ilike(f"%{search}%"),
            Case.defendant.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    if tags:
        # Фильтр по тегам (PostgreSQL array contains)
        for tag in tags:
            query = query.where(Case.tags.contains([tag]))

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Сортировка (по дате открытия, новые первые)
    query = query.order_by(Case.open_date.desc())

    # Выполнение запроса
    result = await db.execute(query)
    cases = result.scalars().all()

    # Расчёт количества страниц
    pages = math.ceil(total / size) if total > 0 else 1

    return CaseListResponse(
        items=cases,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание нового дела

    Автоматически генерируется case_number в формате: PREFIX-YYYYMMDD-NNN
    """
    # Генерация уникального номера дела
    date_str = case_data.open_date.strftime('%Y%m%d')
    base_number = f"{case_data.case_prefix}-{date_str}"

    # Поиск последнего дела с таким префиксом и датой
    result = await db.execute(
        select(Case)
        .where(Case.case_number.like(f"{base_number}%"))
        .order_by(Case.case_number.desc())
    )
    last_case = result.scalar_one_or_none()

    if last_case:
        # Извлекаем последний порядковый номер
        try:
            last_seq = int(last_case.case_number.split('-')[-1])
            seq = last_seq + 1
        except (ValueError, IndexError):
            seq = 1
    else:
        seq = 1

    case_number = f"{base_number}-{seq:03d}"

    # Создание дела
    new_case = Case(
        case_number=case_number,
        case_prefix=case_data.case_prefix,
        case_type=case_data.case_type.value,
        title=case_data.title,
        description=case_data.description,
        court=case_data.court,
        judge=case_data.judge,
        plaintiff=case_data.plaintiff,
        defendant=case_data.defendant,
        case_status=case_data.case_status.value,
        open_date=case_data.open_date,
        close_date=case_data.close_date,
        tags=case_data.tags,
        metadata=case_data.metadata,
        created_by=current_user.id
    )

    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)

    return new_case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение дела по ID
    """
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {case_id} не найдено"
        )

    return case


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление дела
    """
    # Проверка существования дела
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {case_id} не найдено"
        )

    # Обновление полей
    update_data = case_data.model_dump(exclude_unset=True)

    # Преобразование enum в значения
    if 'case_type' in update_data and update_data['case_type']:
        update_data['case_type'] = update_data['case_type'].value
    if 'case_status' in update_data and update_data['case_status']:
        update_data['case_status'] = update_data['case_status'].value

    if update_data:
        await db.execute(
            update(Case)
            .where(Case.id == case_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(case)

    return case


@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_case(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление дела

    **Требуются права администратора**
    **ВНИМАНИЕ:** Удаляет дело и все связанные данные (документы, события, связи)
    """
    # Проверка прав (только администратор может удалять дела)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора для удаления дел"
        )

    # Проверка существования дела
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {case_id} не найдено"
        )

    # Удаление дела (cascade удалит связанные записи)
    await db.execute(delete(Case).where(Case.id == case_id))
    await db.commit()

    return None


@router.get("/{case_id}/timeline")
async def get_case_timeline(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение временной шкалы дела (история событий)

    Возвращает хронологический список всех событий дела:
    - Создание дела
    - Загрузка документов
    - Судебные заседания
    - Изменения статуса
    """
    # Проверка существования дела
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {case_id} не найдено"
        )

    # TODO: Реализовать сбор событий из разных таблиц
    # Пока возвращаем базовую информацию
    timeline = [
        {
            "date": case.created_at.isoformat(),
            "event_type": "case_created",
            "description": f"Дело создано: {case.title}",
            "user_id": case.created_by
        }
    ]

    return {
        "case_id": case_id,
        "case_number": case.case_number,
        "timeline": timeline
    }
