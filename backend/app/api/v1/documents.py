"""
API endpoints для управления документами
Ключевой модуль: загрузка файлов, OCR, предпросмотр
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, or_
from typing import List, Optional
from datetime import datetime, date
from pathlib import Path
import aiofiles
import mimetypes
import magic
import hashlib
from app.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.case import Case
from app.schemas.document import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentListResponse,
    DocumentType, DocumentOCRResponse
)
from app.api.deps import get_current_user
from app.config import settings
from app.utils.ollama import ollama_client
import math
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Разрешённые форматы файлов
ALLOWED_FORMATS = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/msword': '.doc',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'text/plain': '.txt'
}

# Максимальный размер файла (50 МБ)
MAX_FILE_SIZE = settings.MAX_FILE_SIZE


def get_file_hash(content: bytes) -> str:
    """Получение SHA256 хеша файла"""
    return hashlib.sha256(content).hexdigest()


def validate_file_type(content: bytes, filename: str) -> tuple[str, str]:
    """
    Проверка типа файла по magic bytes (не только по расширению!)
    Возвращает (mime_type, extension)
    """
    # Проверяем magic bytes
    mime = magic.Magic(mime=True)
    detected_mime = mime.from_buffer(content)

    if detected_mime not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла: {detected_mime}. Разрешены: PDF, DOCX, DOC, JPG, PNG, TXT"
        )

    extension = ALLOWED_FORMATS[detected_mime]
    return detected_mime, extension


def get_storage_path(case_id: Optional[int] = None) -> Path:
    """Получение пути к хранилищу документов"""
    storage_path = Path(settings.STORAGE_PATH) / "documents"

    if case_id:
        storage_path = storage_path / f"case_{case_id}"
    else:
        storage_path = storage_path / "general"

    storage_path.mkdir(parents=True, exist_ok=True)
    return storage_path


async def save_uploaded_file(
    file: UploadFile,
    case_id: Optional[int] = None
) -> tuple[str, str, int, str]:
    """
    Сохранение загруженного файла
    Возвращает (relative_path, new_filename, file_size, mime_type)
    """
    # Читаем содержимое файла
    content = await file.read()
    file_size = len(content)

    # Проверка размера
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE / 1024 / 1024:.0f} МБ"
        )

    # Проверка типа файла
    mime_type, extension = validate_file_type(content, file.filename)

    # Генерируем уникальное имя файла
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_hash = get_file_hash(content)[:8]  # Первые 8 символов хеша
    safe_filename = file.filename.replace(" ", "_").replace("/", "_")
    new_filename = f"{timestamp}_{file_hash}_{safe_filename}"

    # Определяем путь сохранения
    storage_path = get_storage_path(case_id)
    file_path = storage_path / new_filename

    # Сохраняем файл
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)

    # Формируем относительный путь
    if case_id:
        relative_path = f"case_{case_id}/{new_filename}"
    else:
        relative_path = f"general/{new_filename}"

    logger.info(f"Файл сохранён: {relative_path} ({file_size} байт)")

    return relative_path, new_filename, file_size, mime_type


@router.get("/", response_model=DocumentListResponse)
async def get_documents(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    case_id: Optional[int] = None,
    document_type: Optional[DocumentType] = None,
    is_template: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение списка документов с фильтрацией и пагинацией

    - **page**: номер страницы
    - **size**: количество элементов
    - **case_id**: фильтр по делу
    - **document_type**: фильтр по типу документа
    - **is_template**: только шаблоны (true) или обычные документы (false)
    - **search**: поиск по имени файла, описанию, OCR тексту
    """
    # Базовый запрос
    query = select(Document)

    # Фильтры
    if case_id is not None:
        query = query.where(Document.case_id == case_id)

    if document_type:
        query = query.where(Document.document_type == document_type.value)

    if is_template is not None:
        query = query.where(Document.is_template == is_template)

    if search:
        search_filter = or_(
            Document.file_name.ilike(f"%{search}%"),
            Document.original_file_name.ilike(f"%{search}%"),
            Document.description.ilike(f"%{search}%"),
            Document.ocr_text.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # Подсчёт общего количества
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Пагинация
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # Сортировка (новые первые)
    query = query.order_by(Document.upload_date.desc())

    # Выполнение запроса
    result = await db.execute(query)
    documents = result.scalars().all()

    # Расчёт количества страниц
    pages = math.ceil(total / size) if total > 0 else 1

    return DocumentListResponse(
        items=documents,
        total=total,
        page=page,
        size=size,
        pages=pages
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    case_id: Optional[int] = Form(None),
    document_type: DocumentType = Form(...),
    document_date: Optional[date] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON строка: '["tag1", "tag2"]'
    is_template: bool = Form(False),
    auto_ocr: bool = Form(True),  # Автоматически запустить OCR
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка документа

    **Multipart/form-data:**
    - **file**: файл для загрузки
    - **case_id**: ID дела (опционально)
    - **document_type**: тип документа
    - **document_date**: дата документа
    - **description**: описание
    - **tags**: теги в формате JSON: ["tag1", "tag2"]
    - **is_template**: это шаблон? (по умолчанию false)
    - **auto_ocr**: автоматически запустить OCR (по умолчанию true)
    """
    # Проверка существования дела (если указан case_id)
    if case_id:
        result = await db.execute(select(Case).where(Case.id == case_id))
        case = result.scalar_one_or_none()
        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Дело с ID {case_id} не найдено"
            )

    # Сохранение файла
    try:
        relative_path, new_filename, file_size, mime_type = await save_uploaded_file(file, case_id)
    except Exception as e:
        logger.error(f"Ошибка при сохранении файла: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )

    # Парсинг тегов
    import json
    tags_list = []
    if tags:
        try:
            tags_list = json.loads(tags)
        except json.JSONDecodeError:
            tags_list = [tag.strip() for tag in tags.split(',')]

    # Создание записи в БД
    new_document = Document(
        case_id=case_id,
        document_type=document_type.value,
        file_name=new_filename,
        original_file_name=file.filename,
        file_path=relative_path,
        file_size=file_size,
        file_format=Path(file.filename).suffix.upper().replace('.', ''),
        upload_date=datetime.now(),
        document_date=document_date,
        description=description,
        tags=tags_list,
        version=1,
        is_template=is_template,
        created_by=current_user.id
    )

    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)

    # Автоматический OCR для PDF файлов
    if auto_ocr and mime_type == 'application/pdf' and settings.OLLAMA_ENABLED:
        try:
            logger.info(f"Запуск автоматического OCR для документа {new_document.id}")
            # OCR запускаем асинхронно (в фоне)
            # TODO: В production использовать Celery или background tasks
            # Пока что синхронно для простоты
            from app.utils.ollama import ollama_client
            file_full_path = Path(settings.STORAGE_PATH) / "documents" / relative_path
            ocr_text = await ollama_client.ocr_document(str(file_full_path))

            if ocr_text:
                await db.execute(
                    update(Document)
                    .where(Document.id == new_document.id)
                    .values(ocr_text=ocr_text)
                )
                await db.commit()
                await db.refresh(new_document)
                logger.info(f"OCR успешно выполнен для документа {new_document.id}")
        except Exception as e:
            logger.error(f"Ошибка при автоматическом OCR: {e}")
            # Не прерываем загрузку, OCR можно запустить позже вручную

    return new_document


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Получение метаданных документа по ID
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    return document


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    document_data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Обновление метаданных документа
    """
    # Проверка существования документа
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    # Обновление полей
    update_data = document_data.model_dump(exclude_unset=True)

    # Преобразование enum
    if 'document_type' in update_data and update_data['document_type']:
        update_data['document_type'] = update_data['document_type'].value

    if update_data:
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(document)

    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Удаление документа

    **Требуются права администратора**
    **ВНИМАНИЕ:** Удаляет документ и файл с диска
    """
    # Проверка прав
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Требуются права администратора для удаления документов"
        )

    # Проверка существования документа
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    # Удаление файла с диска
    try:
        file_full_path = Path(settings.STORAGE_PATH) / "documents" / document.file_path
        if file_full_path.exists():
            file_full_path.unlink()
            logger.info(f"Файл удалён: {file_full_path}")
    except Exception as e:
        logger.error(f"Ошибка при удалении файла: {e}")
        # Продолжаем удаление записи из БД даже если файл не удалился

    # Удаление записи из БД
    await db.execute(delete(Document).where(Document.id == document_id))
    await db.commit()

    return None


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Скачивание документа
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    file_full_path = Path(settings.STORAGE_PATH) / "documents" / document.file_path

    if not file_full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден на диске"
        )

    return FileResponse(
        path=file_full_path,
        filename=document.original_file_name,
        media_type='application/octet-stream'
    )


@router.get("/{document_id}/preview")
async def preview_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Предпросмотр документа (inline)
    Для PDF откроется в браузере
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    file_full_path = Path(settings.STORAGE_PATH) / "documents" / document.file_path

    if not file_full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден на диске"
        )

    # Определяем MIME-тип
    mime_type, _ = mimetypes.guess_type(str(file_full_path))
    if not mime_type:
        mime_type = 'application/octet-stream'

    return FileResponse(
        path=file_full_path,
        media_type=mime_type,
        headers={"Content-Disposition": f"inline; filename={document.original_file_name}"}
    )


@router.post("/{document_id}/ocr", response_model=DocumentOCRResponse)
async def run_ocr(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Запуск OCR обработки документа через Ollama

    Работает только для PDF файлов
    """
    if not settings.OLLAMA_ENABLED:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Ollama API отключен. OCR недоступен."
        )

    # Проверка существования документа
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Документ с ID {document_id} не найден"
        )

    # Проверка формата файла
    if document.file_format.upper() != 'PDF':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OCR доступен только для PDF файлов"
        )

    # Проверка существования файла
    file_full_path = Path(settings.STORAGE_PATH) / "documents" / document.file_path
    if not file_full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден на диске"
        )

    # Запуск OCR
    try:
        logger.info(f"Запуск OCR для документа {document_id}: {document.file_name}")
        ocr_text = await ollama_client.ocr_document(str(file_full_path))

        if not ocr_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OCR не вернул результат"
            )

        # Сохранение результата в БД
        await db.execute(
            update(Document)
            .where(Document.id == document_id)
            .values(ocr_text=ocr_text)
        )
        await db.commit()

        logger.info(f"OCR успешно выполнен для документа {document_id}")

        return DocumentOCRResponse(
            document_id=document_id,
            ocr_text=ocr_text,
            success=True
        )

    except Exception as e:
        logger.error(f"Ошибка при OCR обработке: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при OCR обработке: {str(e)}"
        )
