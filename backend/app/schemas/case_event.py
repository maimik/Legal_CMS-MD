"""
Pydantic схемы для событий дел
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    COURT_HEARING = "court_hearing"
    DOCUMENT_DEADLINE = "document_deadline"
    CONSULTATION = "consultation"
    PAYMENT_DEADLINE = "payment_deadline"
    CASE_DEADLINE = "case_deadline"
    CUSTOM = "custom"


class EventStatus(str, Enum):
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CaseEventBase(BaseModel):
    case_id: int
    event_type: EventType
    event_date: datetime
    description: str = Field(..., min_length=1)
    location: Optional[str] = Field(None, max_length=255)
    reminder_days_before: int = Field(1, ge=0, le=30)
    event_status: EventStatus = EventStatus.SCHEDULED

    @validator('event_date')
    def validate_event_date(cls, v):
        """Проверка, что дата события не в прошлом (для новых событий)"""
        # Для создания события проверяем, что дата в будущем или сегодня
        # Для обновления это ограничение можно не применять
        return v


class CaseEventCreate(CaseEventBase):
    @validator('event_date')
    def validate_future_date(cls, v):
        if v < datetime.now():
            raise ValueError('Дата события не может быть в прошлом')
        return v


class CaseEventUpdate(BaseModel):
    event_type: Optional[EventType] = None
    event_date: Optional[datetime] = None
    description: Optional[str] = Field(None, min_length=1)
    location: Optional[str] = Field(None, max_length=255)
    reminder_days_before: Optional[int] = Field(None, ge=0, le=30)
    event_status: Optional[EventStatus] = None


class CaseEventInDB(CaseEventBase):
    id: int
    reminder_sent: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseEventResponse(CaseEventInDB):
    pass


class CaseEventListResponse(BaseModel):
    items: List[CaseEventResponse]
    total: int
    page: int
    size: int
    pages: int


class CalendarEventResponse(BaseModel):
    """Упрощённый формат для календаря"""
    id: int
    case_id: int
    case_number: Optional[str] = None
    event_type: EventType
    event_date: datetime
    description: str
    location: Optional[str]
    event_status: EventStatus
