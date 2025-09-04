"""
    Chat API using LangChain and ChatOpenAI (DB history + OpenSearch retriever)
"""
from __future__ import annotations
import datetime
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.callbacks.manager import AsyncCallbackManager

from app.api.model.request import ChatRequest
from app.api.services.chat_service import ConversationChainService
from app.api.model.streaming_chain import StreamingConversationRetrievalChain
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger

from app.api.database.models.base import get_db
from app.api.database.dao.conversation_dao import ConversationDAO
from app.api.services.db_history import DbChatHistory
from app.api.services.custom_prompt_service import CustomPromptService
from app.core.condense_prompt import _template

router = APIRouter()

callbacks: dict[str, dict] = {}
conv_chain_services: dict[str, ConversationChainService] = {}
conversation_chains: dict[str, object] = {}
streaming_conversation_chains: dict[str, StreamingConversationRetrievalChain] = {}

dao = ConversationDAO()

@router.post("/stream_chat/")
async def generate_response(data: ChatRequest, db: AsyncSession = Depends(get_db)):
    """
    Streaming chat. Prompt lấy từ DB. History lưu/đọc từ DB.
    """
    try:
        if not data.conversation_id:
            custom_logger.error("conversation_id is empty")
            return BaseResponse.error_response(message="conversation_id is empty")

        now = datetime.datetime.now()
        if data.conversation_id not in callbacks:
            callbacks[data.conversation_id] = {"cb": AsyncIteratorCallbackHandler(),
                                               "time_created": now}
        else:
            latest = callbacks[data.conversation_id]["time_created"]
            if (now - latest).total_seconds() >= 43200:  # 12h reset
                callbacks[data.conversation_id] = {"cb": AsyncIteratorCallbackHandler(),
                                                   "time_created": now}
        cb: AsyncIteratorCallbackHandler = callbacks[data.conversation_id]["cb"]
        conv_cb_manager = AsyncCallbackManager([cb])

        latest_prompt = await dao.get_prompt(db)
        current_template = latest_prompt.content if latest_prompt else "You are a helpful assistant."

        cps = CustomPromptService(current_template, _template)
        qa_prompt = cps.custom_prompt()
        condense_prompt = cps.custom_condense_prompt()

        if data.conversation_id not in conv_chain_services:
            conv_chain_services[data.conversation_id] = ConversationChainService(
                temperature=0.2,
                streaming_cb=cb,
                conv_cb_manager=conv_cb_manager,
                qa_prompt=qa_prompt
            )
        conv_svc = conv_chain_services[data.conversation_id]

        conv_svc.qa_prompt_text = current_template

        if data.conversation_id not in conversation_chains:
            conversation_chains[data.conversation_id] = conv_svc.generate_conv_chain(condense_prompt)

        history = DbChatHistory(db, data.conversation_id, k=4)
        await history.append_user(data.message)
        chat_history = await history.load_messages()

        if data.conversation_id not in streaming_conversation_chains:
            streaming_conversation_chains[data.conversation_id] = StreamingConversationRetrievalChain(
                conversation_id=data.conversation_id,
                streaming_cb=cb,
                conv_cb_manager=conv_cb_manager,
                qa_prompt=qa_prompt
            )

        async def event_generator():
            async for token in streaming_conversation_chains[data.conversation_id].generate_response(
                message=data.message,
                chat_template=current_template,
                conv_chain_service=conv_svc,
                conversation_chain=conversation_chains[data.conversation_id],
                chat_history=chat_history
            ):
                if isinstance(token, str):
                    yield token

            # Lưu câu trả lời AI vào DB sau khi stream xong
            answer = streaming_conversation_chains[data.conversation_id].output
            if isinstance(answer, str) and answer:
                await history.append_ai(answer)

        return StreamingResponse(event_generator(), media_type="text/plain")

    except Exception as e:
        custom_logger.error(str(e))
        return BaseResponse.error_response(message=str(e))
