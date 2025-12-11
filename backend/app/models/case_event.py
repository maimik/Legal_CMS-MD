"""
Модель события дела
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class CaseEvent(Base):
    __tablename__ = "case_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    event_date = Column(DateTime(timezone=True), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=True)
    reminder_days_before = Column(Integer, default=1)
    reminder_sent = Column(Boolean, default=False, index=True)
    event_status = Column(String(20), nullable=False, default="scheduled", index=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    case = relationship("Case", back_populates="events")

    def __repr__(self):
        return f"<CaseEvent {self.event_type} on {self.event_date}>"
