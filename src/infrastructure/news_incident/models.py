from sqlalchemy import Column, Integer, String, DateTime, Float, Text, UniqueConstraint
from sqlalchemy.sql import func
from src.infrastructure.database.sql.database import Base


class NewsIncident(Base):
    __tablename__ = "news_incidents"
    __table_args__ = (UniqueConstraint("source_url_hash", name="uq_news_incidents_source_url_hash"),)

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    summary = Column(Text, nullable=True)
    category = Column(String(50), nullable=True)  # e.g. crime, disaster, accident, epidemic
    location_name = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    source_url = Column(Text, nullable=False)
    source_url_hash = Column(String(64), nullable=False)
    published_at = Column(DateTime, nullable=True)
    severity = Column(Integer, nullable=True)  # 0-100 (higher = worse)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
