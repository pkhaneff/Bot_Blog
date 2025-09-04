"""Conversation Detail class maps to table conversation_details on database"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.api.database.models.base import Base

"""
class ConversationDetail:
    id: str
    time: datetime
    message_detail: str
    role: str
    conversation_id: str (Foreign Key of conversation table)
"""

class ConversationDetail(Base):
    """Conversation Detail class maps to table conversation_details on database"""

    __tablename__ = 'conversation_detail'

    id = Column(String, primary_key=True)
    time = Column(DateTime, default=datetime.utcnow)
    message_detail = Column(String)
    role = Column(String)
    conversation_id = Column(String, ForeignKey('conversation.conversation_id'))
    conversation = relationship("Conversation", backref="conversation_detail")
