"""
Pydantic схемы для законодательных актов
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum


class ActType(str, Enum):
    CONSTITUTION = "constitution"
    LAW = "law"
    CODE = "code"
    GOVERNMENT_DECISION = "government_decision"
    COURT_DECISION = "court_decision"
    INTERNATIONAL_TREATY = "international_treaty"


class ActStatus(str, Enum):
    ACTIVE = "active"
    REPEALED = "repealed"
    AMENDED = "amended"


class LegalActBase(BaseModel):
    act_type: ActType
    act_number: Optional[str] = Field(None, max_length=50)
    act_date: Optional[date] = None
    title: str = Field(..., min_length=1, max_length=255)
    tags: Optional[List[str]] = []
    full_text: Optional[str] = None
    act_status: ActStatus = ActStatus.ACTIVE


class LegalActCreate(LegalActBase):
    """Создание законодательного акта (файл передаётся отдельно)"""
    pass


class LegalActUpdate(BaseModel):
    act_type: Optional[ActType] = None
    act_number: Optional[str] = Field(None, max_length=50)
    act_date: Optional[date] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    tags: Optional[List[str]] = None
    full_text: Optional[str] = None
    act_status: Optional[ActStatus] = None


class LegalActInDB(LegalActBase):
    id: int
    file_path: str
    file_size: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LegalActResponse(LegalActInDB):
    pass


class LegalActListResponse(BaseModel):
    items: List[LegalActResponse]
    total: int
    page: int
    size: int
    pages: int


class CaseLegalActLink(BaseModel):
    """Связь дела с законодательным актом"""
    case_id: int
    legal_act_id: int
    relevance_note: Optional[str] = None


class CaseLegalActResponse(BaseModel):
    id: int
    case_id: int
    legal_act_id: int
    relevance_note: Optional[str]
    legal_act: LegalActResponse
    created_at: datetime

    class Config:
        from_attributes = True
