"""
Pydantic схемы для документов
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum


class DocumentType(str, Enum):
    LAWSUIT = "lawsuit"
    MOTION = "motion"
    COMPLAINT = "complaint"
    COURT_DECISION = "court_decision"
    POWER_OF_ATTORNEY = "power_of_attorney"
    CONTRACT = "contract"
    CORRESPONDENCE = "correspondence"
    EVIDENCE = "evidence"
    EXPERT_OPINION = "expert_opinion"
    OTHER = "other"


class DocumentBase(BaseModel):
    case_id: Optional[int] = None
    document_type: DocumentType
    document_date: Optional[date] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    is_template: bool = False


class DocumentCreate(DocumentBase):
    """Создание документа (файл передаётся отдельно через multipart/form-data)"""
    pass


class DocumentUpdate(BaseModel):
    document_type: Optional[DocumentType] = None
    document_date: Optional[date] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    is_template: Optional[bool] = None


class DocumentInDB(DocumentBase):
    id: int
    file_name: str
    original_file_name: str
    file_path: str
    file_size: Optional[int]
    file_format: Optional[str]
    upload_date: datetime
    ocr_text: Optional[str]
    extracted_metadata: Optional[Dict[str, Any]]
    version: int
    created_by: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class DocumentResponse(DocumentInDB):
    pass


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int


class DocumentOCRRequest(BaseModel):
    """Запрос на OCR обработку документа"""
    document_id: int


class DocumentOCRResponse(BaseModel):
    """Результат OCR обработки"""
    document_id: int
    ocr_text: str
    success: bool
