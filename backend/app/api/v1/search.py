"""
API endpoints для глобального поиска
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, text
from typing import Optional, List
from app.database import get_db
from app.models.user import User
from app.models.case import Case
from app.models.person import Person
from app.models.document import Document
from app.models.legal_act import LegalAct
from app.api.deps import get_current_user
from app.utils.ollama import ollama_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def global_search(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    search_type: str = Query("all", description="Тип поиска: all, cases, persons, documents, legal_acts"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Глобальный поиск по всей системе

    - **q**: поисковый запрос (минимум 2 символа)
    - **search_type**: где искать (all, cases, persons, documents, legal_acts)
    - **limit**: максимальное количество результатов в каждой категории
    """
    results = {
        "query": q,
        "cases": [],
        "persons": [],
        "documents": [],
        "legal_acts": [],
        "total": 0
    }

    # Поиск дел
    if search_type in ["all", "cases"]:
        query = select(Case).where(
            or_(
                Case.case_number.ilike(f"%{q}%"),
                Case.title.ilike(f"%{q}%"),
                Case.plaintiff.ilike(f"%{q}%"),
                Case.defendant.ilike(f"%{q}%"),
                Case.description.ilike(f"%{q}%")
            )
        ).limit(limit)

        result = await db.execute(query)
        cases = result.scalars().all()

        results["cases"] = [
            {
                "id": c.id,
                "case_number": c.case_number,
                "title": c.title,
                "case_type": c.case_type,
                "case_status": c.case_status
            } for c in cases
        ]

    # Поиск персон
    if search_type in ["all", "persons"]:
        query = select(Person).where(
            or_(
                Person.full_name.ilike(f"%{q}%"),
                Person.idnp.ilike(f"%{q}%"),
                Person.phone.ilike(f"%{q}%"),
                Person.email.ilike(f"%{q}%"),
                Person.organization.ilike(f"%{q}%")
            )
        ).limit(limit)

        result = await db.execute(query)
        persons = result.scalars().all()

        results["persons"] = [
            {
                "id": p.id,
                "full_name": p.full_name,
                "person_type": p.person_type,
                "idnp": p.idnp
            } for p in persons
        ]

    # Поиск документов
    if search_type in ["all", "documents"]:
        query = select(Document).where(
            or_(
                Document.file_name.ilike(f"%{q}%"),
                Document.original_file_name.ilike(f"%{q}%"),
                Document.description.ilike(f"%{q}%"),
                Document.ocr_text.ilike(f"%{q}%")
            )
        ).limit(limit)

        result = await db.execute(query)
        documents = result.scalars().all()

        results["documents"] = [
            {
                "id": d.id,
                "file_name": d.file_name,
                "document_type": d.document_type,
                "case_id": d.case_id
            } for d in documents
        ]

    # Поиск законодательных актов
    if search_type in ["all", "legal_acts"]:
        query = select(LegalAct).where(
            or_(
                LegalAct.title.ilike(f"%{q}%"),
                LegalAct.act_number.ilike(f"%{q}%"),
                LegalAct.full_text.ilike(f"%{q}%")
            )
        ).limit(limit)

        result = await db.execute(query)
        legal_acts = result.scalars().all()

        results["legal_acts"] = [
            {
                "id": la.id,
                "title": la.title,
                "act_type": la.act_type,
                "act_number": la.act_number
            } for la in legal_acts
        ]

    # Подсчёт общего количества
    results["total"] = (
        len(results["cases"]) +
        len(results["persons"]) +
        len(results["documents"]) +
        len(results["legal_acts"])
    )

    return results


@router.get("/fulltext")
async def fulltext_search(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Полнотекстовый поиск PostgreSQL (FTS)

    Использует to_tsvector и to_tsquery для эффективного поиска
    Поддерживает русский и румынский языки
    """
    # Полнотекстовый поиск по документам
    fts_query = text("""
        SELECT id, file_name, document_type, case_id,
               ts_rank(to_tsvector('russian', COALESCE(ocr_text, '')), query) AS rank
        FROM documents, to_tsquery('russian', :search_query) query
        WHERE to_tsvector('russian', COALESCE(ocr_text, '')) @@ query
        ORDER BY rank DESC
        LIMIT :limit
    """)

    result = await db.execute(
        fts_query,
        {"search_query": q.replace(' ', ' & '), "limit": limit}
    )
    documents = result.fetchall()

    return {
        "query": q,
        "documents": [
            {
                "id": d[0],
                "file_name": d[1],
                "document_type": d[2],
                "case_id": d[3],
                "relevance_score": float(d[4])
            } for d in documents
        ],
        "total": len(documents)
    }


@router.post("/semantic")
async def semantic_search(
    q: str = Query(..., min_length=2, description="Поисковый запрос"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Семантический поиск через Ollama embeddings

    **Экспериментальная функция**
    Использует векторные представления текста для поиска по смыслу
    """
    from app.config import settings

    if not settings.OLLAMA_ENABLED:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama API отключен. Семантический поиск недоступен."
        )

    # Получаем embedding поискового запроса
    query_embedding = await ollama_client.get_embeddings(q)

    if not query_embedding:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить embeddings для запроса"
        )

    # TODO: Реализовать векторный поиск с использованием pgvector
    # Пока возвращаем заглушку
    logger.warning("Семантический поиск находится в разработке")

    return {
        "query": q,
        "message": "Семантический поиск находится в разработке",
        "query_embedding_length": len(query_embedding),
        "results": []
    }
