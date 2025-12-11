"""
API endpoints для управления персонами
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.models.person import Person
from app.models.case_person import CasePerson
from app.models.case import Case
from app.schemas.person import (
    PersonCreate, PersonUpdate, PersonResponse, PersonListResponse, PersonType
)
from app.api.deps import get_current_user
import math


router = APIRouter()


@router.get("/", response_model=PersonListResponse)
async def get_persons(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    person_type: Optional[PersonType] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка персон с фильтрацией и пагинацией

    - **page**: номер страницы (начиная с 1)
    - **size**: количество элементов на странице
    - **person_type**: фильтр по типу персоны
    - **search**: поиск по ФИО, IDNP, телефону, email
    """
    # Базовый запрос
    query = select(Person)

    # Фильтры
    if person_type:
        query = query.where(Person.person_type == person_type.value)

    if search:
        search_filter = or_(
            Person.full_name.ilike(f"%{search}%"),
            Person.idnp.ilike(f"%{search}%"),
            Person.phone.ilike(f"%{search}%"),
            Person.email.ilike(f"%{search}%"),
            Person.organization.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Сортировка (по имени)
    query = query.order_by(Person.full_name.asc())

    # Выполнение запроса
    result = await db.execute(query)
    persons = result.scalars().all()

    # Расчёт количества страниц
    pages = math.ceil(total / size) if total > 0 else 1

    return PersonListResponse(
        items=persons,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
async def create_person(
    person_data: PersonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Создание новой персоны

    Автоматически проверяется уникальность IDNP
    """
    # Проверка уникальности IDNP (если указан)
    if person_data.idnp:
        result = await db.execute(
            select(Person).where(Person.idnp == person_data.idnp)
        )
        existing_person = result.scalar_one_or_none()
        if existing_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Персона с IDNP {person_data.idnp} уже существует"
            )

    # Создание персоны
    new_person = Person(
        full_name=person_data.full_name,
        person_type=person_data.person_type.value,
        idnp=person_data.idnp,
        birth_date=person_data.birth_date,
        phone=person_data.phone,
        phone_additional=person_data.phone_additional,
        email=person_data.email,
        address_legal=person_data.address_legal,
        address_actual=person_data.address_actual,
        organization=person_data.organization,
        idno=person_data.idno,
        notes=person_data.notes,
        metadata=person_data.metadata
    )

    db.add(new_person)
    await db.commit()
    await db.refresh(new_person)

    return new_person


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение персоны по ID
    """
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персона с ID {person_id} не найдена"
        )

    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int,
    person_data: PersonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление персоны
    """
    # Проверка существования персоны
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персона с ID {person_id} не найдена"
        )

    # Проверка уникальности IDNP (если изменяется)
    if person_data.idnp and person_data.idnp != person.idnp:
        result = await db.execute(
            select(Person).where(Person.idnp == person_data.idnp)
        )
        existing_person = result.scalar_one_or_none()
        if existing_person:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Персона с IDNP {person_data.idnp} уже существует"
            )

    # Обновление полей
    update_data = person_data.model_dump(exclude_unset=True)

    # Преобразование enum в значение
    if 'person_type' in update_data and update_data['person_type']:
        update_data['person_type'] = update_data['person_type'].value

    if update_data:
        await db.execute(
            update(Person)
            .where(Person.id == person_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(person)

    return person


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_person(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление персоны

    **Требуются права администратора**
    **ВНИМАНИЕ:** Удаляет персону и все связи с делами
    """
    # Проверка прав (только администратор может удалять персон)
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора для удаления персон"
        )

    # Проверка существования персоны
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персона с ID {person_id} не найдена"
        )

    # Удаление персоны (cascade удалит связанные записи)
    await db.execute(delete(Person).where(Person.id == person_id))
    await db.commit()

    return None


@router.get("/{person_id}/cases")
async def get_person_cases(
    person_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка дел, в которых участвует персона

    Возвращает список дел с указанием роли персоны в каждом деле
    """
    # Проверка существования персоны
    result = await db.execute(select(Person).where(Person.id == person_id))
    person = result.scalar_one_or_none()

    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Персона с ID {person_id} не найдена"
        )

    # Получение дел через связующую таблицу
    query = (
        select(Case, CasePerson.role_in_case, CasePerson.notes)
        .join(CasePerson, Case.id == CasePerson.case_id)
        .where(CasePerson.person_id == person_id)
        .order_by(Case.open_date.desc())
    )

    result = await db.execute(query)
    cases_data = result.all()

    # Формируем ответ
    cases = []
    for case, role, notes in cases_data:
        cases.append({
            "case_id": case.id,
            "case_number": case.case_number,
            "title": case.title,
            "case_type": case.case_type,
            "case_status": case.case_status,
            "open_date": case.open_date.isoformat() if case.open_date else None,
            "close_date": case.close_date.isoformat() if case.close_date else None,
            "role_in_case": role,
            "notes": notes
        })

    return {
        "person_id": person_id,
        "full_name": person.full_name,
        "cases": cases,
        "total_cases": len(cases)
    }
