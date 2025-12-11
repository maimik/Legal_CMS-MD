"""
Модель документа
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Boolean, ARRAY, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=True, index=True)
    document_type = Column(String(50), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    original_file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    file_format = Column(String(10), nullable=True)
    upload_date = Column(DateTime(timezone=True), server_default=func.now())
    document_date = Column(Date, nullable=True, index=True)
    description = Column(Text, nullable=True)
    ocr_text = Column(Text, nullable=True)
    extracted_metadata = Column(JSON, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    version = Column(Integer, default=1)
    is_template = Column(Boolean, default=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="documents")
    embedding = relationship("DocumentEmbedding", back_populates="document", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Document {self.file_name} ({self.document_type})>"
