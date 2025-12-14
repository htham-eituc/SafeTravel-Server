from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.sql import func
from src.infrastructure.database.sql.database import Base


class UserReportIncident(Base):
    __tablename__ = "user_report_incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # e.g. crime, disaster, accident, scam
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    severity = Column(Integer, nullable=True)  # 0-100 (higher = worse)
    status = Column(String(20), default="active")  # active/resolved/invalid
    created_at = Column(DateTime, server_default=func.now())

