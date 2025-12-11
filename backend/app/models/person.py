"""
Модель персоны
"""
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False, index=True)
    person_type = Column(String(30), nullable=False, index=True)
    idnp = Column(String(13), nullable=True, unique=True, index=True)
    birth_date = Column(Date, nullable=True)
    phone = Column(String(20), nullable=True)
    phone_additional = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address_legal = Column(Text, nullable=True)
    address_actual = Column(Text, nullable=True)
    organization = Column(String(150), nullable=True)
    idno = Column(String(13), nullable=True)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case_persons = relationship("CasePerson", back_populates="person", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Person {self.full_name} ({self.person_type})>"
