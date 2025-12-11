"""
API endpoints для управления событиями и календарём
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.database import get_db
from app.models.user import User
from app.models.case_event import CaseEvent
from app.models.case import Case
from app.schemas.case_event import (
    CaseEventCreate, CaseEventUpdate, CaseEventResponse, CaseEventListResponse,
    EventType, EventStatus, CalendarEventResponse
)
from app.api.deps import get_current_user
import math
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=CaseEventListResponse)
async def get_events(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    case_id: Optional[int] = None,
    event_type: Optional[EventType] = None,
    event_status: Optional[EventStatus] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка событий с фильтрацией и пагинацией

    - **page**: номер страницы
    - **size**: количество элементов
    - **case_id**: фильтр по делу
    - **event_type**: фильтр по типу события
    - **event_status**: фильтр по статусу
    - **date_from**: события начиная с даты (YYYY-MM-DD)
    - **date_to**: события до даты (YYYY-MM-DD)
    """
    # Базовый запрос
    query = select(CaseEvent)

    # Фильтры
    if case_id is not None:
        query = query.where(CaseEvent.case_id == case_id)

    if event_type:
        query = query.where(CaseEvent.event_type == event_type.value)

    if event_status:
        query = query.where(CaseEvent.event_status == event_status.value)

    if date_from:
        # Конвертируем date в datetime (начало дня)
        datetime_from = datetime.combine(date_from, datetime.min.time())
        query = query.where(CaseEvent.event_date >= datetime_from)

    if date_to:
        # Конвертируем date в datetime (конец дня)
        datetime_to = datetime.combine(date_to, datetime.max.time())
        query = query.where(CaseEvent.event_date <= datetime_to)

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Сортировка (ближайшие события первыми)
    query = query.order_by(CaseEvent.event_date.asc())

    # Выполнение запроса
    result = await db.execute(query)
    events = result.scalars().all()

    # Расчёт количества страниц
    pages = math.ceil(total / size) if total > 0 else 1

    return CaseEventListResponse(
        items=events,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=CaseEventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_data: CaseEventCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание нового события

    **Автоматически:**
    - Проверяется существование дела
    - Проверяется, что дата события не в прошлом
    """
    # Проверка существования дела
    result = await db.execute(select(Case).where(Case.id == event_data.case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {event_data.case_id} не найдено"
        )

    # Создание события
    new_event = CaseEvent(
        case_id=event_data.case_id,
        event_type=event_data.event_type.value,
        event_date=event_data.event_date,
        description=event_data.description,
        location=event_data.location,
        reminder_days_before=event_data.reminder_days_before,
        event_status=event_data.event_status.value,
        reminder_sent=False,
        created_by=current_user.id
    )

    db.add(new_event)
    await db.commit()
    await db.refresh(new_event)

    logger.info(f"Создано событие {new_event.id} для дела {case.case_number}")

    return new_event


@router.get("/{event_id}", response_model=CaseEventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение события по ID
    """
    result = await db.execute(select(CaseEvent).where(CaseEvent.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    return event


@router.put("/{event_id}", response_model=CaseEventResponse)
async def update_event(
    event_id: int,
    event_data: CaseEventUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление события
    """
    # Проверка существования события
    result = await db.execute(select(CaseEvent).where(CaseEvent.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    # Обновление полей
    update_data = event_data.model_dump(exclude_unset=True)

    # Преобразование enum
    if 'event_type' in update_data and update_data['event_type']:
        update_data['event_type'] = update_data['event_type'].value
    if 'event_status' in update_data and update_data['event_status']:
        update_data['event_status'] = update_data['event_status'].value

    # Если изменилась дата или статус, сбросить reminder_sent
    if 'event_date' in update_data or 'event_status' in update_data:
        update_data['reminder_sent'] = False

    if update_data:
        await db.execute(
            update(CaseEvent)
            .where(CaseEvent.id == event_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(event)

    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление события
    """
    # Проверка существования события
    result = await db.execute(select(CaseEvent).where(CaseEvent.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    # Удаление события
    await db.execute(delete(CaseEvent).where(CaseEvent.id == event_id))
    await db.commit()

    return None


@router.get("/calendar/{year}/{month}")
async def get_calendar(
    year: int = Path(..., ge=2000, le=2100),
    month: int = Path(..., ge=1, le=12),
    event_type: Optional[EventType] = None,
    event_status: Optional[EventStatus] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение событий для календаря (по месяцам)

    - **year**: год (2000-2100)
    - **month**: месяц (1-12)
    - **event_type**: фильтр по типу события
    - **event_status**: фильтр по статусу

    Возвращает события за указанный месяц с информацией о делах
    """
    # Определяем начало и конец месяца
    first_day = datetime(year, month, 1)

    if month == 12:
        last_day = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        last_day = datetime(year, month + 1, 1) - timedelta(seconds=1)

    # Базовый запрос с JOIN на таблицу дел
    query = (
        select(CaseEvent, Case.case_number)
        .join(Case, CaseEvent.case_id == Case.id)
        .where(
            and_(
                CaseEvent.event_date >= first_day,
                CaseEvent.event_date <= last_day
            )
        )
    )

    # Фильтры
    if event_type:
        query = query.where(CaseEvent.event_type == event_type.value)

    if event_status:
        query = query.where(CaseEvent.event_status == event_status.value)

    # Сортировка по дате
    query = query.order_by(CaseEvent.event_date.asc())

    # Выполнение запроса
    result = await db.execute(query)
    events_data = result.all()

    # Формируем ответ
    events = []
    for event, case_number in events_data:
        events.append(CalendarEventResponse(
            id=event.id,
            case_id=event.case_id,
            case_number=case_number,
            event_type=EventType(event.event_type),
            event_date=event.event_date,
            description=event.description,
            location=event.location,
            event_status=EventStatus(event.event_status)
        ))

    return {
        "year": year,
        "month": month,
        "events": events,
        "total": len(events)
    }


@router.get("/upcoming/week")
async def get_upcoming_week(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение предстоящих событий на неделю

    Полезно для дашборда
    """
    now = datetime.now()
    week_later = now + timedelta(days=7)

    query = (
        select(CaseEvent, Case.case_number)
        .join(Case, CaseEvent.case_id == Case.id)
        .where(
            and_(
                CaseEvent.event_date >= now,
                CaseEvent.event_date <= week_later,
                CaseEvent.event_status == EventStatus.SCHEDULED.value
            )
        )
        .order_by(CaseEvent.event_date.asc())
    )

    result = await db.execute(query)
    events_data = result.all()

    # Формируем ответ
    events = []
    for event, case_number in events_data:
        # Вычисляем количество дней до события
        days_until = (event.event_date.date() - now.date()).days

        events.append({
            "id": event.id,
            "case_id": event.case_id,
            "case_number": case_number,
            "event_type": event.event_type,
            "event_date": event.event_date.isoformat(),
            "description": event.description,
            "location": event.location,
            "days_until": days_until,
            "is_today": days_until == 0,
            "is_urgent": days_until <= 1
        })

    return {
        "events": events,
        "total": len(events)
    }


@router.get("/reminders/pending")
async def get_pending_reminders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение событий, для которых нужно отправить напоминания

    Используется для background задачи отправки email напоминаний
    **Требуются права администратора**
    """
    # Проверка прав
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )

    now = datetime.now()

    # Находим события, для которых пора отправить напоминание
    query = (
        select(CaseEvent, Case.case_number)
        .join(Case, CaseEvent.case_id == Case.id)
        .where(
            and_(
                CaseEvent.event_status == EventStatus.SCHEDULED.value,
                CaseEvent.reminder_sent == False,
                CaseEvent.event_date > now  # Событие ещё не прошло
            )
        )
    )

    result = await db.execute(query)
    events_data = result.all()

    # Фильтруем события, для которых пора отправить напоминание
    pending_reminders = []
    for event, case_number in events_data:
        # Вычисляем дату напоминания
        reminder_date = event.event_date - timedelta(days=event.reminder_days_before)

        # Если пора отправить напоминание (reminder_date <= now)
        if reminder_date <= now:
            pending_reminders.append({
                "event_id": event.id,
                "case_id": event.case_id,
                "case_number": case_number,
                "event_type": event.event_type,
                "event_date": event.event_date.isoformat(),
                "description": event.description,
                "location": event.location,
                "reminder_days_before": event.reminder_days_before,
                "reminder_date": reminder_date.isoformat()
            })

    return {
        "pending_reminders": pending_reminders,
        "total": len(pending_reminders)
    }


@router.post("/{event_id}/mark-reminder-sent", status_code=status.HTTP_204_NO_CONTENT)
async def mark_reminder_sent(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Отметить, что напоминание отправлено

    Используется после успешной отправки email напоминания
    **Требуются права администратора**
    """
    # Проверка прав
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора"
        )

    # Проверка существования события
    result = await db.execute(select(CaseEvent).where(CaseEvent.id == event_id))
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    # Обновление флага
    await db.execute(
        update(CaseEvent)
        .where(CaseEvent.id == event_id)
        .values(reminder_sent=True)
    )
    await db.commit()

    logger.info(f"Напоминание отправлено для события {event_id}")

    return None
