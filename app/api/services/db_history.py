from __future__ import annotations
import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.schema import BaseMessage
from langchain.schema.messages import HumanMessage, AIMessage

from app.api.database.models.conversation import Conversation
from app.api.database.models.conversation_detail import ConversationDetail

class DbChatHistory:
    def __init__(self, db: AsyncSession, conversation_id: str, k: int = 4):
        self.db = db
        self.conversation_id = conversation_id
        self.k = k

    async def ensure_conversation(self):
        conv = await self.db.get(Conversation, self.conversation_id)
        if not conv:
            self.db.add(Conversation(conversation_id=self.conversation_id))
            await self.db.commit()

    async def load_messages(self) -> List[BaseMessage]:
        stmt = select(ConversationDetail)\
            .where(ConversationDetail.conversation_id == self.conversation_id)\
            .order_by(ConversationDetail.time.asc())
        rows = (await self.db.execute(stmt)).scalars().all()
        rows = rows[-self.k*2:]
        msgs: List[BaseMessage] = []
        for r in rows:
            if r.role == "user":
                msgs.append(HumanMessage(content=r.message_detail))
            else:
                msgs.append(AIMessage(content=r.message_detail))
        return msgs

    async def append_user(self, text: str):
        await self.ensure_conversation()
        self.db.add(ConversationDetail(
            id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            role="user",
            message_detail=text
        ))
        await self.db.commit()

    async def append_ai(self, text: str):
        self.db.add(ConversationDetail(
            id=str(uuid.uuid4()),
            conversation_id=self.conversation_id,
            role="assistant",
            message_detail=text
        ))
        await self.db.commit()
