"""
Pydantic схемы для персон
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from enum import Enum
import re


class PersonType(str, Enum):
    CLIENT = "client"
    DEFENDANT = "defendant"
    JUDGE = "judge"
    LAWYER = "lawyer"
    WITNESS = "witness"
    OTHER = "other"


class PersonBase(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=150)
    person_type: PersonType
    idnp: Optional[str] = Field(None, max_length=13)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_additional: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address_legal: Optional[str] = None
    address_actual: Optional[str] = None
    organization: Optional[str] = Field(None, max_length=150)
    idno: Optional[str] = Field(None, max_length=13)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

    @validator('idnp')
    def validate_idnp(cls, v):
        """Валидация молдавского IDNP (13 цифр)"""
        if v is None:
            return v

        if not re.match(r'^\d{13}$', v):
            raise ValueError('IDNP должен содержать ровно 13 цифр')

        # Проверка даты в IDNP (ГГ ММ ДД)
        year = int(v[0:2])
        month = int(v[2:4])
        day = int(v[4:6])

        if month < 1 or month > 12:
            raise ValueError('Некорректный месяц в IDNP')
        if day < 1 or day > 31:
            raise ValueError('Некорректный день в IDNP')

        return v

    @validator('idno')
    def validate_idno(cls, v):
        """Валидация молдавского IDNO для юрлиц (13 цифр)"""
        if v is None:
            return v

        if not re.match(r'^\d{13}$', v):
            raise ValueError('IDNO должен содержать ровно 13 цифр')

        return v


class PersonCreate(PersonBase):
    pass


class PersonUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    person_type: Optional[PersonType] = None
    idnp: Optional[str] = Field(None, max_length=13)
    birth_date: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=20)
    phone_additional: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    address_legal: Optional[str] = None
    address_actual: Optional[str] = None
    organization: Optional[str] = Field(None, max_length=150)
    idno: Optional[str] = Field(None, max_length=13)
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PersonInDB(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PersonResponse(PersonInDB):
    pass


class PersonListResponse(BaseModel):
    items: List[PersonResponse]
    total: int
    page: int
    size: int
    pages: int
