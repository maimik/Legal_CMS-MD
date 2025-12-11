"""
Интеграция с Ollama API
"""
import httpx
import base64
import logging
from typing import Optional, List
from app.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Клиент для работы с Ollama API"""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.enabled = settings.OLLAMA_ENABLED

    async def check_availability(self) -> bool:
        """Проверка доступности Ollama"""
        if not self.enabled:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/api/tags", timeout=5.0)
                return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama недоступен: {e}")
            return False

    async def ocr_image(self, image_path: str) -> Optional[str]:
        """OCR распознавание текста из изображения"""
        if not self.enabled:
            logger.warning("Ollama отключен в настройках")
            return None

        try:
            # Читаем изображение и конвертируем в base64
            with open(image_path, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode()

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": settings.OCR_MODEL,
                        "prompt": "Распознай весь текст на этом изображении. Верни только текст без комментариев.",
                        "images": [image_base64],
                        "stream": False
                    },
                    timeout=settings.OCR_TIMEOUT
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Ошибка OCR: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Ошибка при OCR распознавании: {e}")
            return None

    async def generate_text(self, prompt: str, max_tokens: int = 500) -> Optional[str]:
        """Генерация текста через Ollama"""
        if not self.enabled:
            logger.warning("Ollama отключен в настройках")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": settings.GENERATION_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "num_predict": max_tokens
                        }
                    },
                    timeout=settings.GENERATION_TIMEOUT
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    logger.error(f"Ошибка генерации: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Ошибка при генерации текста: {e}")
            return None

    async def get_embeddings(self, text: str) -> Optional[List[float]]:
        """Получение embeddings для семантического поиска"""
        if not self.enabled:
            logger.warning("Ollama отключен в настройках")
            return None

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": settings.EMBEDDING_MODEL,
                        "prompt": text
                    },
                    timeout=30.0
                )

                if response.status_code == 200:
                    result = response.json()
                    return result.get("embedding", [])
                else:
                    logger.error(f"Ошибка получения embeddings: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Ошибка при получении embeddings: {e}")
            return None

    async def ocr_document(self, pdf_path: str) -> Optional[str]:
        """
        OCR распознавание PDF документа
        Конвертирует PDF в изображения и распознаёт каждую страницу
        """
        if not self.enabled:
            logger.warning("Ollama отключен в настройках")
            return None

        try:
            from pdf2image import convert_from_path
            import tempfile
            import os

            logger.info(f"Начало OCR обработки PDF: {pdf_path}")

            # Конвертируем PDF в изображения
            with tempfile.TemporaryDirectory() as temp_dir:
                # Конвертация PDF в изображения (300 DPI для качественного OCR)
                images = convert_from_path(pdf_path, dpi=300, output_folder=temp_dir)
                logger.info(f"PDF конвертирован в {len(images)} изображений")

                # OCR каждой страницы
                full_text = []
                for i, image in enumerate(images, 1):
                    # Сохраняем изображение во временный файл
                    temp_image_path = os.path.join(temp_dir, f"page_{i}.jpg")
                    image.save(temp_image_path, 'JPEG')

                    # Распознаём текст
                    logger.info(f"OCR страницы {i}/{len(images)}")
                    page_text = await self.ocr_image(temp_image_path)

                    if page_text:
                        full_text.append(f"=== Страница {i} ===\n{page_text}")

                # Объединяем текст всех страниц
                result = "\n\n".join(full_text)
                logger.info(f"OCR завершён. Распознано {len(result)} символов")
                return result

        except Exception as e:
            logger.error(f"Ошибка при OCR обработке PDF: {e}")
            return None


# Глобальный экземпляр клиента
ollama_client = OllamaClient()
