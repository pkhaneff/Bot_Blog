from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from app.api.database.models.conversation_detail import ConversationDetail
from app.api.database.models.custom_prompt import CustomPrompt
from app.api.database.models.conversation import Conversation

class ConversationDAO:
    """Conversation Data Access Object"""

    async def get_all(self, async_session: async_sessionmaker[AsyncSession]):
        """Get all Conversation from database"""
        async with async_session() as session:
            statement = select(Conversation).order_by(Conversation.conversation_id)
            result = await session.execute(statement)
            return result.scalars().all()
        
    async def get_by_id(self, async_session: async_sessionmaker[AsyncSession], id: str):
        """Get Conversation's Information by id"""
        async with async_session() as session:
            statement = select(Conversation).filter(Conversation.conversation_id == id)
            result = await session.execute(statement)
            return result.scalars().all()
        
    async def get_detail_by_id(self, async_session: async_sessionmaker[AsyncSession], id: str):
        """Get Conversation Detail by id"""
        async with async_session() as session:
            statement = select(ConversationDetail).filter(ConversationDetail.conversation_id == id)
            result = await session.execute(statement)
            return result.scalars().all()
        
    async def add_conversation(self, async_session: async_sessionmaker[AsyncSession], conversation: Conversation):
        """Add Conversation to database"""
        async with async_session() as session:
            session.add(conversation)
            await session.commit()
        return conversation
    
    async def add_conversation_detail(self, async_session: async_sessionmaker[AsyncSession], conversation_detail: ConversationDetail):                                      
        """Add Conversation Detail to database with conversation_id"""
        async with async_session() as session:
            session.add(conversation_detail)
            await session.commit()
        return conversation_detail
        
    async def delete_conversation(self, async_session: async_sessionmaker[AsyncSession], conversation: Conversation):
        """Delete Conversation """
        async with async_session() as session:
            await session.delete(conversation)
            await session.commit()
        return conversation

    async def add_custom_prompt(self, db: AsyncSession, custom_prompt: CustomPrompt):
        """Add Custom Prompt to database"""
        async with db.begin():  
            db.add(custom_prompt)
            await db.commit()
        return custom_prompt

    async def get_prompt(self, db: AsyncSession):
        """Get the latest Custom Prompt from database"""
        async with db.begin():
            statement = select(CustomPrompt).order_by(desc(CustomPrompt.created_at)).limit(1)
            result = await db.execute(statement)
            return result.scalar_one_or_none()
