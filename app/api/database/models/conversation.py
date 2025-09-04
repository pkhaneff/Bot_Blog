"""Conversation class maps to table conversation on database"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime
from app.api.database.models.base import Base

"""
class Conversation:
    conversation_id: str
    time_start: datetime
"""

class Conversation(Base):
    """Conversation class maps to table conversation on database"""

    __tablename__ = 'conversation'

    conversation_id = Column(String, primary_key=True)
    time_start = Column(DateTime, default=datetime.utcnow)
