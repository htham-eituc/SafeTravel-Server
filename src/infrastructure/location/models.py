from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.infrastructure.database.sql.database import Base

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float, nullable=True)
    accuracy = Column(Float, nullable=True)
    recorded_at = Column(DateTime, server_default=func.now())

    user = relationship("User", back_populates="locations")
