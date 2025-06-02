from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from app.database import Base


class Aircraft(Base):
    __tablename__ = "aircraft"

    serial_number = Column(String, primary_key=True, index=True)
    manufacturer = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
