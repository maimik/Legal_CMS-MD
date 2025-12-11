"""
Pydantic схемы для дел
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class CaseType(str, Enum):
    CIVIL = "civil"
    CRIMINAL = "criminal"
    ADMINISTRATIVE = "administrative"
    INTERNATIONAL = "international"
    ARBITRATION = "arbitration"


class CaseStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    SUSPENDED = "suspended"
    CLOSED = "closed"
    ARCHIVED = "archived"


class CaseBase(BaseModel):
    case_prefix: str = Field(..., max_length=10)
    case_type: CaseType
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    court: Optional[str] = Field(None, max_length=150)
    judge: Optional[str] = Field(None, max_length=150)
    plaintiff: Optional[str] = Field(None, max_length=150)
    defendant: Optional[str] = Field(None, max_length=150)
    case_status: CaseStatus = CaseStatus.NEW
    open_date: date
    close_date: Optional[date] = None
    tags: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}


class CaseCreate(CaseBase):
    @validator('close_date')
    def validate_close_date(cls, v, values):
        if v and 'open_date' in values and v < values['open_date']:
            raise ValueError('Дата закрытия не может быть раньше даты открытия')
        return v


class CaseUpdate(BaseModel):
    case_prefix: Optional[str] = Field(None, max_length=10)
    case_type: Optional[CaseType] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    court: Optional[str] = Field(None, max_length=150)
    judge: Optional[str] = Field(None, max_length=150)
    plaintiff: Optional[str] = Field(None, max_length=150)
    defendant: Optional[str] = Field(None, max_length=150)
    case_status: Optional[CaseStatus] = None
    open_date: Optional[date] = None
    close_date: Optional[date] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class CaseInDB(CaseBase):
    id: int
    case_number: str
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseResponse(CaseInDB):
    pass


class CaseListResponse(BaseModel):
    items: List[CaseResponse]
    total: int
    page: int
    size: int
    pages: int
