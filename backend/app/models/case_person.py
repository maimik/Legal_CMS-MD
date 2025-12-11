"""
Модель связи дела и персоны
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CasePerson(Base):
    __tablename__ = "case_persons"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    person_id = Column(Integer, ForeignKey("persons.id", ondelete="CASCADE"), nullable=False, index=True)
    role_in_case = Column(String(50), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    case = relationship("Case", back_populates="case_persons")
    person = relationship("Person", back_populates="case_persons")

    __table_args__ = (
        UniqueConstraint('case_id', 'person_id', 'role_in_case', name='unique_case_person_role'),
    )

    def __repr__(self):
        return f"<CasePerson case_id={self.case_id} person_id={self.person_id} role={self.role_in_case}>"
