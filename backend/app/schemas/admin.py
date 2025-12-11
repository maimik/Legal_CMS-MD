"""
Pydantic схемы для администрирования
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class SystemSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None


class SystemSettingCreate(SystemSettingBase):
    pass


class SystemSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None


class SystemSettingResponse(SystemSettingBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    """Запись журнала аудита"""
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    entity_type: str
    entity_id: Optional[int]
    old_value: Optional[Dict[str, Any]]
    new_value: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int


class BackupRequest(BaseModel):
    """Запрос на создание резервной копии"""
    include_documents: bool = True
    compress: bool = True


class BackupResponse(BaseModel):
    """Результат создания резервной копии"""
    backup_file: str
    backup_size: int
    created_at: datetime
    success: bool
    message: Optional[str] = None


class SystemHealthResponse(BaseModel):
    """Статус здоровья системы"""
    status: str  # healthy, degraded, unhealthy
    database: str  # connected, disconnected
    ollama: str  # available, unavailable
    storage_space_gb: float
    uptime_seconds: int
    version: str
