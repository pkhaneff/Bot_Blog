from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.api.database.models.base import Base

class CustomPrompt(Base):
    __tablename__ = "custom_prompts"

    id = Column(String, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    