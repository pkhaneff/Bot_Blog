"""
    Custom Prompt API
"""
from __future__ import annotations
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.model.request import PromptRequest
from app.api.database.models.base import get_db
from app.api.database.dao.conversation_dao import ConversationDAO
from app.api.database.models.custom_prompt import CustomPrompt

router = APIRouter()
dao = ConversationDAO()

@router.post("/custom_prompt")
async def custom_prompt(prompt_request: PromptRequest, db: AsyncSession = Depends(get_db)) -> str:
    """
    Lưu prompt tuỳ chỉnh vào DB. Bản mới nhất sẽ được dùng khi chat.
    """
    cp = CustomPrompt(id=str(uuid.uuid4()), content=prompt_request.prompt)
    await dao.add_custom_prompt(db, cp)
    return prompt_request.prompt
