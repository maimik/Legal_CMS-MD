"""
Модель связи дела и законодательного акта
"""
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CaseLegalAct(Base):
    __tablename__ = "case_legal_acts"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    legal_act_id = Column(Integer, ForeignKey("legal_acts.id", ondelete="CASCADE"), nullable=False, index=True)
    relevance_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="case_legal_acts")
    legal_act = relationship("LegalAct", back_populates="case_legal_acts")

    __table_args__ = (
        UniqueConstraint('case_id', 'legal_act_id', name='unique_case_legal_act'),
    )

    def __repr__(self):
        return f"<CaseLegalAct case_id={self.case_id} legal_act_id={self.legal_act_id}>"
