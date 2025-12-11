"""
Pydantic схемы для поиска
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


class SearchType(str, Enum):
    GLOBAL = "global"
    CASES = "cases"
    PERSONS = "persons"
    DOCUMENTS = "documents"
    LEGAL_ACTS = "legal_acts"


class SearchRequest(BaseModel):
    """Запрос глобального поиска"""
    query: str = Field(..., min_length=1, max_length=500)
    search_type: SearchType = SearchType.GLOBAL
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)


class SearchResultItem(BaseModel):
    """Элемент результата поиска"""
    entity_type: str  # case, person, document, legal_act
    entity_id: int
    title: str
    description: Optional[str]
    highlight: Optional[str]  # Подсвеченный фрагмент текста
    relevance_score: Optional[float]  # Релевантность (для FTS)
    metadata: Optional[Dict[str, Any]] = {}


class SearchResponse(BaseModel):
    """Результат поиска"""
    query: str
    total: int
    items: List[SearchResultItem]
    search_type: SearchType
    execution_time: Optional[float]  # Время выполнения в секундах


class SemanticSearchRequest(BaseModel):
    """Запрос семантического поиска (через Ollama embeddings)"""
    query: str = Field(..., min_length=1, max_length=500)
    limit: int = Field(10, ge=1, le=50)
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0)


class AdvancedSearchRequest(BaseModel):
    """Расширенный поиск с фильтрами"""
    query: Optional[str] = None

    # Фильтры для дел
    case_type: Optional[str] = None
    case_status: Optional[str] = None
    case_date_from: Optional[date] = None
    case_date_to: Optional[date] = None

    # Фильтры для документов
    document_type: Optional[str] = None
    document_date_from: Optional[date] = None
    document_date_to: Optional[date] = None

    # Общие
    tags: Optional[List[str]] = None

    # Пагинация
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)
