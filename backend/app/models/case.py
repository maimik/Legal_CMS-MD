"""
Модель дела
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ARRAY, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(50), unique=True, nullable=False, index=True)
    case_prefix = Column(String(10), nullable=False)
    case_type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    court = Column(String(150), nullable=True)
    judge = Column(String(150), nullable=True)
    plaintiff = Column(String(150), nullable=True)
    defendant = Column(String(150), nullable=True)
    case_status = Column(String(30), nullable=False, default="new", index=True)
    open_date = Column(Date, nullable=False, index=True)
    close_date = Column(Date, nullable=True)
    tags = Column(ARRAY(Text), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
    events = relationship("CaseEvent", back_populates="case", cascade="all, delete-orphan")
    case_persons = relationship("CasePerson", back_populates="case", cascade="all, delete-orphan")
    case_legal_acts = relationship("CaseLegalAct", back_populates="case", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Case {self.case_number}: {self.title}>"
