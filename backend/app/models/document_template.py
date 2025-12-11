"""
Модель шаблона документа
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.database import Base


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id = Column(Integer, primary_key=True, index=True)
    template_name = Column(String(150), nullable=False, unique=True)
    template_type = Column(String(50), nullable=False, index=True)
    file_path = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<DocumentTemplate {self.template_name} ({self.template_type})>"
