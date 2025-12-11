"""
API endpoints для генерации отчётов
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from datetime import datetime, date
from pathlib import Path
import tempfile
from app.database import get_db
from app.models.user import User
from app.models.case import Case
from app.models.document import Document
from app.models.case_event import CaseEvent
from app.api.deps import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/case/{case_id}/pdf")
async def generate_case_report_pdf(
    case_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Генерация PDF карточки дела

    Включает:
    - Основная информация о деле
    - Список персон
    - Список документов
    - События
    """
    # Получение дела
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Дело с ID {case_id} не найдено"
        )

    # Генерация PDF с помощью reportlab
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Создаём временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        pdf_path = tmp_file.name

    # Создаём PDF документ
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()

    # Заголовок
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
    )
    story.append(Paragraph(f"Карточка дела №{case.case_number}", title_style))

    # Основная информация
    info_data = [
        ["Номер дела:", case.case_number],
        ["Префикс:", case.case_prefix],
        ["Тип дела:", case.case_type],
        ["Статус:", case.case_status],
        ["Название:", case.title],
        ["Истец:", case.plaintiff or "-"],
        ["Ответчик:", case.defendant or "-"],
        ["Суд:", case.court or "-"],
        ["Судья:", case.judge or "-"],
        ["Дата открытия:", case.open_date.strftime('%d.%m.%Y') if case.open_date else "-"],
        ["Дата закрытия:", case.close_date.strftime('%d.%m.%Y') if case.close_date else "-"],
    ]

    info_table = Table(info_data, colWidths=[5*cm, 12*cm])
    story.append(info_table)
    story.append(Spacer(1, 1*cm))

    # Описание
    if case.description:
        story.append(Paragraph("<b>Описание:</b>", styles['Heading2']))
        story.append(Paragraph(case.description, styles['BodyText']))
        story.append(Spacer(1, 0.5*cm))

    # Генерация PDF
    doc.build(story)

    return FileResponse(
        path=pdf_path,
        filename=f"case_{case.case_number}.pdf",
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=case_{case.case_number}.pdf"}
    )


@router.get("/statistics")
async def get_statistics(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение статистики по делам

    - Количество дел по статусам
    - Количество дел по типам
    - Количество документов
    - Ближайшие события
    """
    # Базовый запрос
    query = select(Case)

    if date_from:
        datetime_from = datetime.combine(date_from, datetime.min.time())
        query = query.where(Case.created_at >= datetime_from)

    if date_to:
        datetime_to = datetime.combine(date_to, datetime.max.time())
        query = query.where(Case.created_at <= datetime_to)

    # Статистика по статусам
    status_query = select(
        Case.case_status,
        func.count(Case.id)
    ).group_by(Case.case_status)

    if date_from or date_to:
        status_query = query.add_columns(func.count(Case.id)).group_by(Case.case_status)

    status_result = await db.execute(status_query)
    status_stats = {row[0]: row[1] for row in status_result.all()}

    # Статистика по типам
    type_query = select(
        Case.case_type,
        func.count(Case.id)
    ).group_by(Case.case_type)

    type_result = await db.execute(type_query)
    type_stats = {row[0]: row[1] for row in type_result.all()}

    # Общее количество документов
    doc_count_query = select(func.count(Document.id))
    doc_count_result = await db.execute(doc_count_query)
    total_documents = doc_count_result.scalar()

    # Общее количество дел
    case_count_query = select(func.count(Case.id))
    case_count_result = await db.execute(case_count_query)
    total_cases = case_count_result.scalar()

    return {
        "total_cases": total_cases,
        "total_documents": total_documents,
        "cases_by_status": status_stats,
        "cases_by_type": type_stats,
        "date_from": date_from.isoformat() if date_from else None,
        "date_to": date_to.isoformat() if date_to else None
    }


@router.get("/export/cases")
async def export_cases(
    format: str = Query("csv", description="Формат экспорта: csv, excel"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Экспорт списка дел в CSV или Excel

    **В разработке**
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Экспорт находится в разработке"
    )
