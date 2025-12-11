"""
Pydantic схемы для шаблонов документов
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class DocumentTemplateBase(BaseModel):
    template_name: str = Field(..., min_length=1, max_length=150)
    template_type: str = Field(..., max_length=50)
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = {}


class DocumentTemplateCreate(DocumentTemplateBase):
    """Создание шаблона (файл передаётся отдельно)"""
    pass


class DocumentTemplateUpdate(BaseModel):
    template_name: Optional[str] = Field(None, min_length=1, max_length=150)
    template_type: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class DocumentTemplateInDB(DocumentTemplateBase):
    id: int
    file_path: str
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentTemplateResponse(DocumentTemplateInDB):
    pass


class DocumentTemplateListResponse(BaseModel):
    items: List[DocumentTemplateResponse]
    total: int


class GenerateDocumentRequest(BaseModel):
    """Запрос на генерацию документа из шаблона"""
    template_id: int
    case_id: int
    variables: Dict[str, Any] = {}
    use_ai: bool = False  # Использовать AI для генерации текста
    ai_prompt: Optional[str] = None  # Промпт для AI, если use_ai=True


class GenerateDocumentResponse(BaseModel):
    """Результат генерации документа"""
    document_id: int
    file_path: str
    success: bool
    message: Optional[str] = None
