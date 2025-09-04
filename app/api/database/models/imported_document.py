from __future__ import annotations
from datetime import datetime
from sqlalchemy import String, Boolean, Text, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column
from app.api.database.models.base import Base

class ImportedDocument(Base):
    __tablename__ = "imported_document"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_process: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
