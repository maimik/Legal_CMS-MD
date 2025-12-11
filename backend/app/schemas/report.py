"""
Pydantic схемы для отчётов
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


class ReportFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    XLSX = "xlsx"
    CSV = "csv"


class ReportType(str, Enum):
    CASE_CARD = "case_card"
    CASE_LIST = "case_list"
    STATISTICS = "statistics"
    CALENDAR = "calendar"
    PERSONS_LIST = "persons_list"


class CaseCardReportRequest(BaseModel):
    """Запрос на генерацию карточки дела"""
    case_id: int
    format: ReportFormat = ReportFormat.PDF
    include_documents: bool = True
    include_events: bool = True
    include_persons: bool = True
    include_legal_acts: bool = True


class CaseListReportRequest(BaseModel):
    """Запрос на генерацию списка дел"""
    format: ReportFormat = ReportFormat.PDF
    case_type: Optional[str] = None
    case_status: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    tags: Optional[List[str]] = None


class StatisticsReportRequest(BaseModel):
    """Запрос на генерацию статистики"""
    format: ReportFormat = ReportFormat.PDF
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    group_by: Optional[str] = "status"  # status, type, month


class StatisticsResponse(BaseModel):
    """Статистика по делам"""
    total_cases: int
    cases_by_status: Dict[str, int]
    cases_by_type: Dict[str, int]
    cases_by_month: Optional[Dict[str, int]] = None
    total_documents: int
    total_persons: int
    total_events: int
    upcoming_events: int


class ReportResponse(BaseModel):
    """Результат генерации отчёта"""
    report_type: ReportType
    format: ReportFormat
    file_path: str
    file_size: int
    generated_at: str
    success: bool
