# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## Система электронного документооборота юридических дел (Legal Case Management System)

**Версия:** 1.0  
**Дата:** 08.12.2025  
**Статус:** Утверждено к разработке

---

# СОДЕРЖАНИЕ

1. [ОБЩИЕ СВЕДЕНИЯ](#1-общие-сведения)
2. [НАЗНАЧЕНИЕ И ЦЕЛИ](#2-назначение-и-цели-создания-системы)
3. [ХАРАКТЕРИСТИКА ОБЪЕКТОВ АВТОМАТИЗАЦИИ](#3-характеристика-объектов-автоматизации)
4. [ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ](#4-функциональные-требования)
5. [СХЕМА БАЗЫ ДАННЫХ](#5-схема-базы-данных)
6. [API СПЕЦИФИКАЦИЯ](#6-api-спецификация)
7. [ТРЕБОВАНИЯ К ИНТЕРФЕЙСУ](#7-требования-к-интерфейсу)
8. [НЕФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ](#8-нефункциональные-требования)
9. [ИНТЕГРАЦИЯ С OLLAMA](#9-интеграция-с-ollama)
10. [МОЛДАВСКАЯ СПЕЦИФИКА](#10-молдавская-специфика)
11. [ПЛАН РАБОТ И СРОКИ](#11-план-работ-и-сроки)
12. [МИГРАЦИЯ ДАННЫХ](#12-миграция-данных)
13. [РАЗВЁРТЫВАНИЕ](#13-развёртывание)
14. [КРИТЕРИИ ПРИЁМКИ](#14-критерии-приёмки)
15. [СТОИМОСТЬ И ОПЛАТА](#15-стоимость-и-оплата)
16. [ПРИЛОЖЕНИЯ](#16-приложения)

---

## 1. ОБЩИЕ СВЕДЕНИЯ

### 1.1 Полное наименование системы
**Система электронного документооборота юридических дел** (Legal Case Management System, Legal CMS, СЭДЮД)

### 1.2 Краткое описание
Веб-система для автоматизации работы юридической практики, включающая управление делами, документооборот, контроль сроков, интеграцию с локальными AI моделями для OCR и генерации документов.

### 1.3 Заказчик и разработчик
- **Заказчик:** Юридическая практика (Республика Молдова)
- **Пользователи:** 2 человека (юрист + ассистент)
- **Разработчик:** [Указать]
- **Срок:** 3-4 месяца

### 1.4 Юрисдикция
- **Страна:** Республика Молдова
- **Языки:** Русский (основной), Румынский (опционально)
- **Валюта:** MDL
- **Применимое право:** Законодательство РМ

---

## 2. НАЗНАЧЕНИЕ И ЦЕЛИ СОЗДАНИЯ СИСТЕМЫ

### 2.1 Назначение
Комплексная автоматизация юридической практики: управление делами, документооборот, контроль сроков, база законодательных актов РМ.

### 2.2 Цели

**Стратегические:**
- Повышение эффективности работы через автоматизацию
- Снижение рисков пропуска процессуальных сроков
- Улучшение качества обслуживания клиентов
- Обеспечение конфиденциальности (локальное размещение)

**Функциональные:**
- Централизованное хранилище с быстрым поиском
- AI-автоматизация (OCR, генерация документов)
- Контроль сроков с автоматическими напоминаниями
- База законодательства РМ
- Генерация отчётов и карточек дел

**Технические:**
- Масштабируемость до 10,000 дел
- Производительность: поиск <1 сек, загрузка <2 сек
- Интеграция с локальным Ollama
- Надёжное резервное копирование

### 2.3 Пользователи

**Юрист (Администратор):**
- Полный доступ ко всем функциям
- Управление делами, клиентами, настройками

**Ассистент:**
- Ограниченный доступ (без удаления, без настроек)
- Загрузка документов, создание событий

---

## 3. ХАРАКТЕРИСТИКА ОБЪЕКТОВ АВТОМАТИЗАЦИИ

### 3.1 Текущее состояние (AS-IS)

**Хранение дел:** Файловая система
- Структура: `PREFIX_YYYY-MM-DD_Client_Name/`
- Пример: `CS_2025-12-04_Alla_Mogopovoi/`
- Документы: PDF, DOCX, изображения
- Объём: ~20 активных дел, 3-4 новых в неделю

**Проблемы:**
- Нет централизованного поиска
- Сложная навигация
- Нет связей между данными
- Нет контроля сроков
- Ручная обработка документов
- Нет резервного копирования
- Нет аудита действий

### 3.2 Новая система (TO-BE)

**Требования:**
- Веб-доступ через браузер
- Полнотекстовый поиск по всем документам
- Автоматический OCR для PDF
- Календарь с напоминаниями
- Генерация документов по шаблонам
- AI интеграция (OCR, генерация, семантический поиск)
- Теги и фильтрация
- История изменений
- Автоматические бэкапы

---

## 4. ФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 4.1 Модуль "Управление делами"

**Функционал:**
- CRUD операции для дел
- Статусы: Новое, В работе, Приостановлено, Завершено, Архив
- Связь с персонами (многие-ко-многим)
- Теги и категории
- История изменений

**Поля дела:**
```
- ID (автогенерация)
- Номер дела (уникальный)
- Префикс (LS, CR, AD, INT, ARB, GENERAL)
- Тип (civil, criminal, administrative, international, arbitration)
- Название/описание
- Суд, судья
- Истец, ответчик
- Даты (открытия, закрытия)
- Статус
- Теги (массив)
- Метаданные (JSON)
```

**Операции:**
- Быстрый поиск по всем полям
- Фильтрация (статус, тип, даты, теги)
- Сортировка
- Экспорт карточки в PDF/DOCX
- Связывание дел между собой

### 4.2 Модуль "Управление персонами"

**Функционал:**
- CRUD для персон
- Типы: клиент, противник, судья, адвокат, свидетель
- Связь с делами (многие-ко-многим)
- История взаимодействий

**Поля персоны:**
```
- ID
- ФИО
- Тип персоны
- IDNP (молдавский, 13 цифр) - с валидацией
- IDNO (для юрлиц РМ, 13 цифр) - с валидацией
- Дата рождения
- Телефон (основной + дополнительные)
- Email
- Адрес (юридический, фактический)
- Организация (для юрлиц)
- Заметки
- Метаданные (JSON)
```

**Операции:**
- Поиск по ФИО, IDNP, телефону, email
- Просмотр всех дел персоны
- Фильтрация по типам

### 4.3 Модуль "Документооборот" ⭐

**Функционал:**
- Загрузка файлов (drag-and-drop, массовая)
- Автопривязка к делам
- Версионность документов
- **Автоматический OCR** через Ollama deepseek-ocr
- Извлечение метаданных
- **Полнотекстовый поиск** по содержимому (PostgreSQL FTS)
- Предпросмотр в браузере
- Скачивание, печать

**Типы документов:**
- Процессуальные (иски, заявления, жалобы)
- Судебные решения
- Доверенности
- Договоры
- Переписка
- Доказательства
- Экспертные заключения
- Прочие

**Поля документа:**
```
- ID
- ID дела
- Название
- Тип документа
- Путь к файлу
- Оригинальное имя
- Дата загрузки
- Дата документа
- Размер, формат
- OCR текст (проиндексированный)
- Метаданные (JSON)
- Теги
- Версия
- Является шаблоном (boolean)
```

**OCR обработка:**
```python
# Автоматически при загрузке PDF/изображений
# Через Ollama API: deepseek-ocr:latest
# Индексирование текста для поиска
# Сохранение в поле ocr_text
```

### 4.4 Модуль "Генерация документов по шаблонам"

**Функционал:**
- Загрузка шаблонов DOCX с переменными
- Переменные: `{{client_name}}`, `{{case_number}}`, `{{court_name}}` и т.д.
- Подстановка данных из карточки дела
- AI-генерация текста (Ollama qwen2.5:7b) - опционально
- Сохранение в дело

**Шаблоны:**
- Иски, заявления, жалобы
- Договоры, доверенности
- Запросы, ходатайства
- Апелляционные жалобы

**Переменные:**
```
{{case_number}}, {{case_date}}
{{client_name}}, {{client_idnp}}, {{client_address}}
{{defendant_name}}
{{court_name}}, {{judge_name}}
{{current_date}}
{{custom_field_*}}
```

### 4.5 Модуль "События и напоминания"

**Функционал:**
- Календарь событий по делам
- Автоматический расчёт процессуальных сроков (РМ)
- Email напоминания (за 1 день, за 3 часа)
- Telegram бот (опционально)
- История событий

**Типы событий:**
- Судебное заседание
- Срок подачи документа
- Консультация с клиентом
- Срок оплаты госпошлины
- Дедлайн по делу
- Произвольное событие

**Поля события:**
```
- ID
- ID дела
- Тип события
- Дата и время
- Описание
- Место (для заседаний)
- Напоминание (за N дней/часов)
- Отправлено (boolean)
- Статус (запланировано, завершено, отменено)
```

### 4.6 Модуль "Законодательная база"

**Функционал:**
- Хранение законов Республики Молдова
- Полнотекстовый поиск
- Теги и категории
- Связь с делами
- Обновляемая база (ручное добавление)

**Типы актов:**
- Конституция
- Законы
- Кодексы (Гражданский, Уголовный, Административный и т.д.)
- Постановления Правительства
- Решения судов (прецеденты)
- Международные договоры

**Поля акта:**
```
- ID
- Тип акта
- Номер, дата принятия
- Название (полное)
- Путь к файлу
- Теги
- Полный текст (проиндексированный)
- Статус (действует, отменен, изменен)
```

### 4.7 Модуль "Поиск"

**Функционал:**
- **Глобальный поиск** по всей системе
- **Полнотекстовый поиск** PostgreSQL (русский + румынский)
- **Семантический поиск** через Ollama embeddings (опционально)
- Фильтры и сортировка

**Типы поиска:**
1. Быстрый (по названиям и основным полям)
2. Полнотекстовый (по содержимому документов, включая OCR)
3. Расширенный (с множеством фильтров)
4. Семантический (похожие дела через AI)

**Индексы PostgreSQL:**
- Full-Text Search (FTS) для русского/румынского
- GIN индексы для массивов (теги)
- Btree для дат и чисел

### 4.8 Модуль "Отчёты и аналитика"

**Функционал:**
- Генерация карточки дела (PDF/DOCX)
- Статистика по делам (количество, типы, статусы)
- Отчёт по срокам (предстоящие события)
- Экспорт данных

**Виды отчётов:**
- Карточка дела (для клиента)
- Список дел (с фильтрами)
- Статистика по периоду
- Отчёт по персонам
- Календарь событий (на месяц)

**Форматы экспорта:**
- PDF, DOCX, Excel (XLSX), CSV

### 4.9 Модуль "Администрирование"

**Функционал:**
- Управление пользователями
- Роли и права (admin, assistant)
- Аудит действий
- Управление бэкапами
- Настройки системы
- Просмотр логов

**Роли:**
```
1. Администратор (юрист):
   - Полный доступ
   - Управление пользователями
   - Доступ к настройкам

2. Ассистент:
   - Просмотр дел и документов
   - Добавление документов
   - Создание событий
   - НЕТ: удаления дел, доступа к настройкам
```

**Аудит:**
- Логирование всех действий
- История изменений (кто, когда, что)
- Возможность отката (для критичных операций)

---

## 5. СХЕМА БАЗЫ ДАННЫХ

### 5.1 PostgreSQL Schema

```sql
-- =====================================================
-- ПОЛЬЗОВАТЕЛИ
-- =====================================================

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'assistant')),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- =====================================================
-- ДЕЛА
-- =====================================================

CREATE TABLE cases (
    id SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE NOT NULL,
    case_prefix VARCHAR(10) NOT NULL,
    case_type VARCHAR(50) NOT NULL CHECK (case_type IN (
        'civil', 'criminal', 'administrative', 'international', 'arbitration'
    )),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    court VARCHAR(150),
    judge VARCHAR(150),
    plaintiff VARCHAR(150),
    defendant VARCHAR(150),
    case_status VARCHAR(30) NOT NULL CHECK (case_status IN (
        'new', 'in_progress', 'suspended', 'closed', 'archived'
    )) DEFAULT 'new',
    open_date DATE NOT NULL,
    close_date DATE,
    tags TEXT[],
    metadata JSONB,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cases_case_number ON cases(case_number);
CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_cases_case_status ON cases(case_status);
CREATE INDEX idx_cases_tags ON cases USING GIN(tags);
CREATE INDEX idx_cases_dates ON cases(open_date, close_date);
CREATE INDEX idx_cases_metadata ON cases USING GIN(metadata);
CREATE INDEX idx_cases_fulltext ON cases USING GIN(
    to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(description, ''))
);

-- =====================================================
-- ПЕРСОНЫ
-- =====================================================

CREATE TABLE persons (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    person_type VARCHAR(30) NOT NULL CHECK (person_type IN (
        'client', 'defendant', 'judge', 'lawyer', 'witness', 'other'
    )),
    idnp VARCHAR(13),
    birth_date DATE,
    phone VARCHAR(20),
    phone_additional VARCHAR(20),
    email VARCHAR(100),
    address_legal TEXT,
    address_actual TEXT,
    organization VARCHAR(150),
    idno VARCHAR(13),
    notes TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_persons_full_name ON persons(full_name);
CREATE INDEX idx_persons_type ON persons(person_type);
CREATE INDEX idx_persons_idnp ON persons(idnp);
CREATE UNIQUE INDEX idx_persons_idnp_unique ON persons(idnp) WHERE idnp IS NOT NULL;
CREATE INDEX idx_persons_fulltext ON persons USING GIN(
    to_tsvector('russian', coalesce(full_name, '') || ' ' || coalesce(notes, ''))
);

-- =====================================================
-- СВЯЗЬ ДЕЛ И ПЕРСОН
-- =====================================================

CREATE TABLE case_persons (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    person_id INTEGER NOT NULL REFERENCES persons(id) ON DELETE CASCADE,
    role_in_case VARCHAR(50) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, person_id, role_in_case)
);

CREATE INDEX idx_case_persons_case ON case_persons(case_id);
CREATE INDEX idx_case_persons_person ON case_persons(person_id);

-- =====================================================
-- ДОКУМЕНТЫ
-- =====================================================

CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    case_id INTEGER REFERENCES cases(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL CHECK (document_type IN (
        'lawsuit', 'motion', 'complaint', 'court_decision', 'power_of_attorney',
        'contract', 'correspondence', 'evidence', 'expert_opinion', 'other'
    )),
    file_name VARCHAR(255) NOT NULL,
    original_file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    file_format VARCHAR(10),
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    document_date DATE,
    description TEXT,
    ocr_text TEXT,
    extracted_metadata JSONB,
    tags TEXT[],
    version INTEGER DEFAULT 1,
    is_template BOOLEAN DEFAULT FALSE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_case ON documents(case_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_tags ON documents USING GIN(tags);
CREATE INDEX idx_documents_date ON documents(document_date);
CREATE INDEX idx_documents_is_template ON documents(is_template);
CREATE INDEX idx_documents_fulltext ON documents USING GIN(
    to_tsvector('russian', 
        coalesce(file_name, '') || ' ' || 
        coalesce(description, '') || ' ' || 
        coalesce(ocr_text, '')
    )
);

-- =====================================================
-- СОБЫТИЯ
-- =====================================================

CREATE TABLE case_events (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL CHECK (event_type IN (
        'court_hearing', 'document_deadline', 'consultation', 
        'payment_deadline', 'case_deadline', 'custom'
    )),
    event_date TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255),
    reminder_days_before INTEGER DEFAULT 1,
    reminder_sent BOOLEAN DEFAULT FALSE,
    event_status VARCHAR(20) NOT NULL CHECK (event_status IN (
        'scheduled', 'completed', 'cancelled'
    )) DEFAULT 'scheduled',
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_events_case ON case_events(case_id);
CREATE INDEX idx_events_date ON case_events(event_date);
CREATE INDEX idx_events_type ON case_events(event_type);
CREATE INDEX idx_events_status ON case_events(event_status);
CREATE INDEX idx_events_reminder ON case_events(reminder_sent, event_date);

-- =====================================================
-- ЗАКОНОДАТЕЛЬНАЯ БАЗА
-- =====================================================

CREATE TABLE legal_acts (
    id SERIAL PRIMARY KEY,
    act_type VARCHAR(50) NOT NULL CHECK (act_type IN (
        'constitution', 'law', 'code', 'government_decision', 
        'court_decision', 'international_treaty'
    )),
    act_number VARCHAR(50),
    act_date DATE,
    title VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER,
    tags TEXT[],
    full_text TEXT,
    act_status VARCHAR(20) CHECK (act_status IN (
        'active', 'repealed', 'amended'
    )) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_legal_acts_type ON legal_acts(act_type);
CREATE INDEX idx_legal_acts_status ON legal_acts(act_status);
CREATE INDEX idx_legal_acts_tags ON legal_acts USING GIN(tags);
CREATE INDEX idx_legal_acts_fulltext ON legal_acts USING GIN(
    to_tsvector('russian', coalesce(title, '') || ' ' || coalesce(full_text, ''))
);

-- =====================================================
-- СВЯЗЬ ДЕЛ И ЗАКОНОВ
-- =====================================================

CREATE TABLE case_legal_acts (
    id SERIAL PRIMARY KEY,
    case_id INTEGER NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    legal_act_id INTEGER NOT NULL REFERENCES legal_acts(id) ON DELETE CASCADE,
    relevance_note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(case_id, legal_act_id)
);

CREATE INDEX idx_case_legal_case ON case_legal_acts(case_id);
CREATE INDEX idx_case_legal_act ON case_legal_acts(legal_act_id);

-- =====================================================
-- ШАБЛОНЫ ДОКУМЕНТОВ
-- =====================================================

CREATE TABLE document_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(150) NOT NULL UNIQUE,
    template_type VARCHAR(50) NOT NULL,
    file_path TEXT NOT NULL,
    variables JSONB,
    description TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_templates_type ON document_templates(template_type);

-- =====================================================
-- АУДИТ
-- =====================================================

CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_user ON audit_log(user_id);
CREATE INDEX idx_audit_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_date ON audit_log(created_at);

-- =====================================================
-- EMBEDDINGS ДЛЯ СЕМАНТИЧЕСКОГО ПОИСКА
-- =====================================================

CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    embedding_vector FLOAT8[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(document_id)
);

CREATE INDEX idx_embeddings_document ON document_embeddings(document_id);

-- =====================================================
-- НАСТРОЙКИ СИСТЕМЫ
-- =====================================================

CREATE TABLE system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_settings (setting_key, setting_value, description) VALUES
('ollama_url', 'http://localhost:11434', 'URL Ollama сервера'),
('ocr_enabled', 'true', 'Включить автоматический OCR'),
('backup_enabled', 'true', 'Включить автоматическое резервное копирование'),
('backup_time', '03:00', 'Время ежедневного бэкапа'),
('smtp_host', '', 'SMTP сервер для email'),
('smtp_port', '587', 'SMTP порт'),
('reminder_enabled', 'true', 'Включить напоминания');

-- =====================================================
-- ТРИГГЕРЫ ДЛЯ ОБНОВЛЕНИЯ updated_at
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_cases_updated_at BEFORE UPDATE ON cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_persons_updated_at BEFORE UPDATE ON persons
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_events_updated_at BEFORE UPDATE ON case_events
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legal_acts_updated_at BEFORE UPDATE ON legal_acts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON document_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

## 6. API СПЕЦИФИКАЦИЯ

### 6.1 REST API Endpoints

#### Аутентификация
```
POST   /api/auth/login              # Вход (возвращает JWT)
POST   /api/auth/logout             # Выход
POST   /api/auth/refresh            # Обновление access token
GET    /api/auth/me                 # Текущий пользователь
```

#### Дела
```
GET    /api/cases                   # Список дел (фильтры, пагинация)
POST   /api/cases                   # Создать дело
GET    /api/cases/{id}              # Получить дело
PUT    /api/cases/{id}              # Обновить дело
DELETE /api/cases/{id}              # Удалить дело
GET    /api/cases/{id}/timeline     # История событий дела
POST   /api/cases/{id}/link         # Связать с другим делом
```

#### Персоны
```
GET    /api/persons                 # Список персон
POST   /api/persons                 # Создать персону
GET    /api/persons/{id}            # Получить персону
PUT    /api/persons/{id}            # Обновить персону
DELETE /api/persons/{id}            # Удалить персону
GET    /api/persons/{id}/cases      # Дела персоны
```

#### Документы
```
GET    /api/documents               # Список документов
POST   /api/documents               # Загрузить документ
GET    /api/documents/{id}          # Получить документ
PUT    /api/documents/{id}          # Обновить метаданные
DELETE /api/documents/{id}          # Удалить документ
GET    /api/documents/{id}/download # Скачать файл
POST   /api/documents/{id}/ocr      # Запустить OCR
GET    /api/documents/{id}/preview  # Предпросмотр
```

#### События
```
GET    /api/events                  # Список событий
POST   /api/events                  # Создать событие
GET    /api/events/{id}             # Получить событие
PUT    /api/events/{id}             # Обновить событие
DELETE /api/events/{id}             # Удалить событие
GET    /api/events/calendar         # Календарь событий
GET    /api/events/upcoming         # Предстоящие события
```

#### Законодательная база
```
GET    /api/legal-acts              # Список актов
POST   /api/legal-acts              # Загрузить акт
GET    /api/legal-acts/{id}         # Получить акт
PUT    /api/legal-acts/{id}         # Обновить акт
DELETE /api/legal-acts/{id}         # Удалить акт
POST   /api/legal-acts/{id}/link-case  # Связать с делом
```

#### Шаблоны
```
GET    /api/templates               # Список шаблонов
POST   /api/templates               # Загрузить шаблон
GET    /api/templates/{id}          # Получить шаблон
PUT    /api/templates/{id}          # Обновить шаблон
DELETE /api/templates/{id}          # Удалить шаблон
POST   /api/templates/{id}/generate # Генерация документа
```

#### Поиск
```
GET    /api/search?q=текст          # Глобальный поиск
POST   /api/search/semantic         # Семантический поиск
GET    /api/search/cases            # Поиск дел
GET    /api/search/documents        # Поиск документов
GET    /api/search/persons          # Поиск персон
```

#### Отчёты
```
GET    /api/reports/case/{id}       # Карточка дела (PDF)
GET    /api/reports/statistics      # Статистика
GET    /api/reports/calendar        # Календарь событий
```

#### Администрирование
```
GET    /api/admin/users             # Список пользователей
POST   /api/admin/users             # Создать пользователя
PUT    /api/admin/users/{id}        # Обновить пользователя
DELETE /api/admin/users/{id}        # Удалить пользователя
GET    /api/admin/audit             # Аудит действий
GET    /api/admin/settings          # Настройки системы
PUT    /api/admin/settings          # Обновить настройки
POST   /api/admin/backup            # Создать бэкап
POST   /api/admin/restore           # Восстановить из бэкапа
```

---

## 7. ТРЕБОВАНИЯ К ИНТЕРФЕЙСУ

### 7.1 Общие требования
- Адаптивный дизайн (desktop first)
- Поддержка: Chrome 100+, Firefox 100+, Edge 100+
- Язык: русский (румынский опционально)
- Цвета: синий/серый (профессиональная палитра)
- Доступность: WCAG 2.1 уровень AA

### 7.2 Основные экраны

**1. Дашборд**
- Статистика дел по статусам (диаграммы)
- Предстоящие события (на неделю)
- Последние дела
- Глобальный поиск

**2. Список дел**
- Таблица с пагинацией
- Фильтры: статус, тип, даты, теги
- Сортировка
- Действия: просмотр, редактирование, удаление

**3. Карточка дела**
Вкладки:
- Общая информация
- Персоны (участники)
- Документы (список + превью)
- События (календарь)
- Законодательство
- История изменений

**4. Документы**
- Список с превью
- Фильтры
- Drag-and-drop загрузка
- Предпросмотр в модальном окне
- Действия: скачать, OCR, удалить

**5. Календарь**
- Виды: месяц, неделя, день
- Цветовая кодировка по типам
- Создание события (drag на дату)

**6. Поиск**
- Строка в хедере (всегда видна)
- Страница расширенного поиска
- Результаты с подсветкой

**7. Настройки**
- Профиль пользователя
- Настройки уведомлений
- Настройки Ollama
- Резервное копирование
- Управление пользователями (только admin)

---

## 8. НЕФУНКЦИОНАЛЬНЫЕ ТРЕБОВАНИЯ

### 8.1 Производительность
- Загрузка страниц: < 2 сек
- Поиск: < 1 сек
- Загрузка документа (до 10 МБ): < 5 сек
- OCR обработка (1 страница PDF): < 10 сек
- Генерация отчёта: < 5 сек

### 8.2 Масштабируемость
- До 10,000 дел
- До 100,000 документов
- Размер документа: до 50 МБ
- Общий объём: до 500 ГБ
- До 5 одновременных пользователей

### 8.3 Безопасность

**Аутентификация:**
- JWT токены (access: 15 мин, refresh: 7 дней)
- Bcrypt хеширование (12 rounds)

**Авторизация:**
- RBAC (admin, assistant)

**Защита данных:**
- HTTPS (SSL/TLS)
- Защита от SQL injection (ORM)
- Защита от XSS (экранирование)
- CSRF защита
- Ограничение размера файлов
- Проверка типов файлов (magic bytes)

**Аудит:**
- Логирование всех действий
- История изменений
- IP адрес и User-Agent

### 8.4 Резервное копирование
- Ежедневно автоматически (03:00)
- Перед критичными операциями
- Хранение последних 30 копий
- Формат: `backup_YYYYMMDD_HHMMSS.sql.gz`

### 8.5 Надёжность
- Uptime: 99% (до 7.2 часов простоя в месяц)
- Graceful degradation при недоступности Ollama
- Обработка ошибок с понятными сообщениями
- Логирование всех ошибок
- RPO: 24 часа
- RTO: 4 часа

---

## 9. ИНТЕГРАЦИЯ С OLLAMA

### 9.1 Ollama API

**Base URL:** `http://localhost:11434`

**Модели:**
- `deepseek-ocr:latest` (6.7 GB) - OCR
- `qwen2.5:7b` (4.7 GB) - генерация текста
- `nomic-embed-text:latest` (274 MB) - embeddings

### 9.2 Примеры использования

**OCR документа:**
```python
import httpx
import base64

async def ocr_document(pdf_path: str) -> str:
    # Конвертируем PDF в изображения (pdf2image)
    # Для каждой страницы:
    with open(image_path, 'rb') as f:
        image_base64 = base64.b64encode(f.read()).decode()
    
    response = await httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "deepseek-ocr:latest",
            "prompt": "Распознай весь текст на этом изображении",
            "images": [image_base64],
            "stream": False
        },
        timeout=60.0
    )
    
    result = response.json()
    return result["response"]
```

**Генерация текста:**
```python
async def generate_text(prompt: str) -> str:
    response = await httpx.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False
        },
        timeout=30.0
    )
    
    return response.json()["response"]
```

**Embeddings для семантического поиска:**
```python
async def get_embeddings(text: str) -> list:
    response = await httpx.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": "nomic-embed-text:latest",
            "prompt": text
        }
    )
    
    return response.json()["embedding"]
```

### 9.3 Обработка ошибок
- Таймауты для всех запросов
- Retry механизм (3 попытки)
- Graceful degradation (продолжение работы без AI)
- Логирование ошибок Ollama

---

## 10. МОЛДАВСКАЯ СПЕЦИФИКА

### 10.1 Языки
- **Интерфейс:** Русский (основной), Румынский (опционально через i18n)
- **Поиск:** PostgreSQL FTS с конфигурацией `russian` и `romanian`

### 10.2 Валидация молдавских кодов

**IDNP (физические лица):**
```python
import re

def validate_idnp(idnp: str) -> bool:
    """
    IDNP: 13 цифр
    Формат: ГГММДДNNNNНК
    ГГ - год рождения (00-99)
    ММ - месяц (01-12)
    ДД - день (01-31)
    NNNN - порядковый номер
    НК - контрольная цифра
    """
    if not re.match(r'^\d{13}$', idnp):
        return False
    
    # Дополнительная валидация даты
    year = int(idnp[0:2])
    month = int(idnp[2:4])
    day = int(idnp[4:6])
    
    if month < 1 or month > 12:
        return False
    if day < 1 or day > 31:
        return False
    
    return True
```

**IDNO (юридические лица):**
```python
def validate_idno(idno: str) -> bool:
    """
    IDNO: 13 цифр для юрлиц РМ
    """
    return bool(re.match(r'^\d{13}$', idno))
```

### 10.3 Процессуальные сроки РМ
- Автоматический расчёт с учётом праздников РМ
- Список праздничных дней в конфигурации
- Пример: подача апелляции - 15 дней с даты решения

### 10.4 Типы дел РМ
- Гражданские (Codul de procedură civilă)
- Уголовные (Codul de procedură penală)
- Административные (Codul contravențional)
- Арбитражные
- Международные

---

## 11. ПЛАН РАБОТ И СРОКИ

### 11.1 Этапы разработки

**ЭТАП 1: Проектирование (1 неделя)**
- Детализация требований
- UI/UX дизайн (wireframes)
- Финализация схемы БД
- Настройка окружения
- Git репозиторий

**ЭТАП 2: Backend базовый (3 недели)**
- Настройка FastAPI
- Модели SQLAlchemy
- Миграции Alembic
- API для дел, персон, документов
- JWT авторизация
- CRUD операции

**ЭТАП 3: Backend AI (2 недели)**
- Интеграция с Ollama
- OCR сервис
- Полнотекстовый поиск PostgreSQL
- Генерация документов по шаблонам
- Сервис событий и напоминаний

**ЭТАП 4: Frontend (4 недели)**
- Настройка Vue.js + Vuetify
- UI компоненты
- Все страницы (дашборд, дела, документы, календарь)
- Интеграция с Backend API
- Загрузка и предпросмотр документов

**ЭТАП 5: Тестирование (2 недели)**
- Интеграционное тестирование
- UI/UX тестирование
- Исправление багов
- Оптимизация производительности
- Тестирование на реальных данных

**ЭТАП 6: Развёртывание (1 неделя)**
- Установка на сервер MX-Linux
- Настройка PostgreSQL
- Настройка Nginx + SSL
- Автоматические бэкапы
- Миграция 20 дел (готовый скрипт)
- Обучение пользователей

**ЭТАП 7: Поддержка (1 месяц)**
- Мониторинг работы
- Исправление критичных багов
- Мелкие доработки

### 11.2 Общий график

```
Неделя | Этап                       | Результат
-------|----------------------------|---------------------------
1      | Проектирование             | Дизайн, схема БД
2-4    | Backend базовый            | API, CRUD, авторизация
5-6    | Backend AI                 | Ollama, OCR, поиск
7-10   | Frontend                   | UI, все страницы
11-12  | Тестирование               | Стабильная версия
13     | Развёртывание              | Запуск на сервере
14-17  | Поддержка                  | Стабильная работа

ИТОГО: 17 недель (~4 месяца)
```

---

## 12. МИГРАЦИЯ ДАННЫХ

### 12.1 Исходные данные
- **Путь:** `/mnt/data_vl/DOC/MAA/DB/Projects/TelegramBot/CASE`
- **Количество дел:** ~20
- **Структура папок:** `PREFIX_YYYY-MM-DD_Client_Name/` или `YYYY-MM-DD_Client_Name/`

### 12.2 Скрипт миграции
**Файл:** `migrate_old_data.py` (уже готов)

**Функционал:**
1. Сканирование папок с делами
2. Парсинг имени папки (дата, клиент, префикс)
3. Создание записи в `cases`
4. Создание записи в `persons` (клиент)
5. Загрузка документов в `documents`
6. OCR обработка PDF
7. Связывание документов с делами

**Режимы:**
- `DRY_RUN = True` - тестовый прогон без записи в БД
- `DRY_RUN = False` - реальная миграция

### 12.3 Порядок миграции
1. Резервная копия старых данных
2. Установка новой системы
3. Тестовая миграция (2-3 дела)
4. Полная миграция (все 20 дел)
5. Валидация данных

---

## 13. РАЗВЁРТЫВАНИЕ

### 13.1 Сервер

**Операционная система:**
- MX-Linux (Debian-based)
- SysVinit (НЕ systemd)
- Xfce

**Требования:**
```
CPU: 4 ядра (рекомендуется 8)
RAM: 8 ГБ (рекомендуется 16 ГБ)
HDD: 100 ГБ (БД + система) + 500 ГБ (документы)
```

**Установленное ПО:**
- Python 3.11+
- PostgreSQL 15+
- Nginx
- Ollama (уже установлен на порту 11434)

### 13.2 Структура директорий

```
/home/maimik/Projects/legal-cms/
├── backend/
│   ├── app/
│   ├── venv/
│   └── requirements.txt
├── frontend/
│   └── dist/
├── storage/
│   ├── documents/
│   ├── templates/
│   └── legal_acts/
├── backups/
│   ├── daily/
│   └── manual/
├── logs/
└── scripts/
    ├── install.sh
    ├── backup.sh
    └── migrate_old_data.py
```

### 13.3 Установка

**Скрипт:** `install.sh`

```bash
#!/bin/bash
# Автоматическая установка Legal CMS

# 1. Системные пакеты
sudo apt update
sudo apt install python3.11 python3-venv postgresql nginx

# 2. PostgreSQL
sudo -u postgres psql <<EOF
CREATE DATABASE legal_cms;
CREATE USER legal_cms_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE legal_cms TO legal_cms_user;
EOF

# 3. Python окружение
cd /home/maimik/Projects/legal-cms/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Миграции БД
alembic upgrade head

# 5. Nginx конфигурация
# (настройка reverse proxy)

# 6. Systemd сервис (если systemd) или SysVinit скрипт
# (запуск FastAPI как службы)

# 7. Автоматические бэкапы
# (добавление в cron)
```

### 13.4 Доступ

```
Backend API:  http://192.168.X.X:8000/api
Frontend:     http://192.168.X.X:8080
Через Nginx:  https://legal-cms.local
Swagger UI:   http://192.168.X.X:8000/docs
```

---

## 14. КРИТЕРИИ ПРИЁМКИ

### 14.1 Функциональные требования

✅ **Модуль "Дела":**
- Создание, редактирование, удаление дел
- Все поля заполняются и сохраняются
- Фильтрация и поиск работают
- Связь с персонами работает

✅ **Модуль "Персоны":**
- CRUD операции работают
- Валидация IDNP/IDNO работает
- Связь с делами работает

✅ **Модуль "Документы":**
- Загрузка файлов работает (drag-and-drop)
- OCR обрабатывает PDF автоматически
- Полнотекстовый поиск находит документы
- Предпросмотр PDF работает
- Скачивание работает

✅ **Модуль "События":**
- Создание событий работает
- Календарь отображается корректно
- Email напоминания отправляются (если настроено)

✅ **Модуль "Законодательная база":**
- Загрузка актов работает
- Поиск по актам работает
- Связывание с делами работает

✅ **Модуль "Шаблоны":**
- Загрузка шаблонов работает
- Генерация документов работает
- Подстановка переменных корректна

✅ **Модуль "Поиск":**
- Глобальный поиск находит результаты
- Полнотекстовый поиск работает
- Фильтры работают

✅ **Модуль "Отчёты":**
- Карточка дела генерируется в PDF
- Статистика отображается
- Экспорт работает

✅ **Модуль "Администрирование":**
- Управление пользователями работает
- Роли и права применяются
- Аудит логирует действия
- Бэкапы создаются и восстанавливаются

### 14.2 Технические требования

✅ **Производительность:**
- Загрузка страниц < 2 сек
- Поиск < 1 сек
- OCR < 10 сек на страницу

✅ **Безопасность:**
- JWT авторизация работает
- RBAC применяется
- HTTPS работает
- Аудит логирует

✅ **Надёжность:**
- Автоматические бэкапы работают
- Восстановление из бэкапа работает
- Graceful degradation при сбое Ollama

✅ **Интеграция:**
- Ollama OCR работает
- Ollama генерация работает
- PostgreSQL FTS работает

### 14.3 Миграция данных

✅ **Скрипт миграции:**
- Все 20 дел мигрировали
- Все документы скопированы
- Персоны созданы
- Связи установлены
- Нет критичных ошибок

### 14.4 Документация

✅ **Наличие документации:**
- README.md
- API_DOCS.md (или Swagger)
- DATABASE.md
- DEPLOYMENT.md
- USER_GUIDE.md

### 14.5 Обучение

✅ **Обучение пользователей:**
- Демонстрация системы (2-3 часа)
- Ответы на вопросы
- Передача документации

---

## 15. СТОИМОСТЬ И ОПЛАТА

### 15.1 Ориентировочная стоимость

**MVP (базовая версия):**
```
Разработка:              150,000 - 200,000 MDL
Развёртывание:            20,000 -  30,000 MDL
───────────────────────────────────────────
ИТОГО MVP:               170,000 - 230,000 MDL
```

**Полная версия:**
```
MVP:                     170,000 - 230,000 MDL
Дополнительно:            80,000 - 120,000 MDL
(семантический поиск, email, аналитика)
───────────────────────────────────────────
ИТОГО полная:            250,000 - 350,000 MDL
```

**Поддержка:**
```
Месячная поддержка:       10,000 -  15,000 MDL/мес
(багфиксы, консультации, доработки до 8 часов/мес)
```

### 15.2 Условия оплаты (пример)

**Поэтапная оплата:**
```
1. Аванс (30%):          при подписании договора
2. Этап 2 (30%):         Backend готов
3. Этап 4 (30%):         Frontend готов
4. Финал (10%):          после успешного запуска
```

---

## 16. ПРИЛОЖЕНИЯ

### 16.1 Технологический стек (полный список)

**Backend:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
pydantic==2.5.2
pydantic-settings==2.1.0
python-multipart==0.0.6
pyjwt==2.8.0
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
httpx==0.25.2

# Обработка документов
PyPDF2==3.0.1
pdfplumber==0.10.3
python-docx==1.1.0
Pillow==10.1.0
python-magic==0.4.27

# Утилиты
jinja2==3.1.2
python-dateutil==2.8.2
APScheduler==3.10.4

# Email (опционально)
aiosmtplib==3.0.1

# Логирование
python-json-logger==2.0.7

# Тестирование
pytest==7.4.3
pytest-asyncio==0.21.1
```

**Frontend (Vue.js):**
```
vue@3.3.x
vuetify@3.4.x
vue-router@4.2.x
pinia@2.1.x
axios@1.6.x
date-fns@2.30.x
```

### 16.2 Глоссарий

| Термин | Определение |
|--------|-------------|
| **СЭДЮД** | Система электронного документооборота юридических дел |
| **OCR** | Optical Character Recognition — распознавание текста |
| **IDNP** | Молдавский персональный номер (13 цифр) |
| **IDNO** | Номер молдавских юрлиц (13 цифр) |
| **JWT** | JSON Web Token — токен аутентификации |
| **RBAC** | Role-Based Access Control — управление доступом по ролям |
| **ORM** | Object-Relational Mapping — преобразование объектов в SQL |
| **MVP** | Minimum Viable Product — минимальная версия |
| **API** | Application Programming Interface |
| **Ollama** | Локальный сервер для больших языковых моделей |
| **FTS** | Full-Text Search — полнотекстовый поиск |
| **MDL** | Молдавский лей (валюта РМ) |

### 16.3 Список документов

1. ✅ **TZ_Full_Complete.md** - полное ТЗ (этот документ)
2. ✅ **TZ_For_Programmers.md** - краткое ТЗ для разработчиков
3. ✅ **migrate_old_data.py** - скрипт миграции данных
4. 📄 **install.sh** - скрипт установки (создать при развёртывании)
5. 📄 **backup.sh** - скрипт резервного копирования (создать)
6. 📄 **requirements.txt** - Python зависимости (создать)

### 16.4 Контактная информация

**Заказчик:**
- Организация: [Юридическая практика]
- Контактное лицо: [ФИО]
- Email: [email]
- Телефон: [телефон]

**Разработчик:**
- Организация: [Название]
- Контактное лицо: [ФИО]
- Email: [email]
- Телефон: [телефон]

---

## ПРИЛОЖЕНИЕ: ПРИМЕР ФАЙЛА .env

```env
# База данных
DATABASE_URL=postgresql+asyncpg://legal_cms_user:PASSWORD@localhost/legal_cms

# Безопасность
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OCR_MODEL=deepseek-ocr:latest
GENERATION_MODEL=qwen2.5:7b
EMBEDDING_MODEL=nomic-embed-text:latest
OCR_TIMEOUT=60
GENERATION_TIMEOUT=30

# Хранилище
STORAGE_PATH=/home/maimik/Projects/legal-cms/storage
MAX_FILE_SIZE=52428800  # 50 МБ
ALLOWED_EXTENSIONS=pdf,docx,doc,jpg,jpeg,png,txt

# Бэкапы
BACKUP_PATH=/home/maimik/Projects/legal-cms/backups
BACKUP_ENABLED=true
BACKUP_TIME=03:00
BACKUP_KEEP_DAYS=30

# Email (опционально)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=password
SMTP_FROM=legal-cms@example.com
SMTP_TLS=true

# Уведомления
REMINDER_ENABLED=true
REMINDER_DAYS_BEFORE=1
REMINDER_HOURS_BEFORE=3

# Режим
DEBUG=false
LOG_LEVEL=INFO
```

---

## ЗАКЛЮЧЕНИЕ

Данное техническое задание содержит полную спецификацию системы электронного документооборота юридических дел. Система разрабатывается с учётом специфики Республики Молдова, локального размещения данных и интеграции с AI моделями для автоматизации рутинных задач.

Ожидаемый срок разработки: **3-4 месяца**  
Ориентировочная стоимость: **170,000 - 350,000 MDL**  

После успешного внедрения система обеспечит:
- ✅ Повышение эффективности работы на 30-40%
- ✅ Сокращение времени поиска в 10-20 раз
- ✅ Исключение пропуска процессуальных сроков
- ✅ Профессиональный имидж юридической практики
- ✅ Возможность масштабирования бизнеса

---

**Дата составления:** 08.12.2025  
**Версия:** 1.0  
**Статус:** Утверждено к разработке

**Подписи:**

Заказчик: ______________________  
Разработчик: ______________________

---

**КОНЕЦ ДОКУМЕНТА**
