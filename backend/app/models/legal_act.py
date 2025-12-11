"""
Модель законодательного акта
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class LegalAct(Base):
    __tablename__ = "legal_acts"

    id = Column(Integer, primary_key=True, index=True)
    act_type = Column(String(50), nullable=False, index=True)
    act_number = Column(String(50), nullable=True)
    act_date = Column(Date, nullable=True)
    title = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    full_text = Column(Text, nullable=True)
    act_status = Column(String(20), default="active", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case_legal_acts = relationship("CaseLegalAct", back_populates="legal_act", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<LegalAct {self.act_type}: {self.title}>"
