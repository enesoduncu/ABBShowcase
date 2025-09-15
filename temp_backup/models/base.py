from sqlalchemy import Column, Integer, DateTime, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class TimestampMixin:
    """Mixin für created_at und updated_at Felder"""
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

@event.listens_for(TimestampMixin, 'before_update', propagate=True)
def timestamp_before_update(mapper, connection, target):
    """Setzt updated_at vor jedem Update"""
    target.updated_at = datetime.utcnow()
