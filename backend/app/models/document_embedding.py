"""
Модель embeddings для семантического поиска
"""
from sqlalchemy import Column, Integer, DateTime, ForeignKey, ARRAY, Float, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class DocumentEmbedding(Base):
    __tablename__ = "document_embeddings"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    embedding_vector = Column(ARRAY(Float), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    document = relationship("Document", back_populates="embedding")

    __table_args__ = (
        UniqueConstraint('document_id', name='unique_document_embedding'),
    )

    def __repr__(self):
        return f"<DocumentEmbedding document_id={self.document_id}>"
