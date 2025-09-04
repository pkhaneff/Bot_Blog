"""
    StreamingChat using LangChain and ChatOpenAI (no in-RAM memory)
"""
from __future__ import annotations
from collections.abc import AsyncGenerator
from starlette import status

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.chains import ConversationalRetrievalChain

from app.core.condense_prompt import _template
from app.api.services.custom_prompt_service import CustomPromptService
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger


class StreamingConversationRetrievalChain:
    """
    Streaming, không dùng ConversationBufferWindowMemory.
    Lịch sử chat được truyền qua tham số `chat_history` (nạp từ DB).
    Prompt lấy từ DB, không đọc file.
    """

    def __init__(self,
                 conversation_id: str,
                 streaming_cb: AsyncIteratorCallbackHandler,
                 conv_cb_manager: AsyncCallbackManager,
                 qa_prompt) -> None:
        self.conversation_id = conversation_id
        self.streaming_cb = streaming_cb
        self.conv_cb_manager = conv_cb_manager
        self.qa_prompt = qa_prompt
        self.output = None

    def _build_prompts(self, current_template: str):
        cps = CustomPromptService(current_template, _template)
        chat_prompt_template = cps.custom_prompt()
        condense_question_prompt = cps.custom_condense_prompt()
        return chat_prompt_template, condense_question_prompt

    async def generate_response(
        self,
        message: str,
        chat_template: str,
        conv_chain_service,
        conversation_chain: ConversationalRetrievalChain,
        chat_history=None
    ) -> AsyncGenerator[str, None]:
        try:
            if chat_template == getattr(conv_chain_service, "qa_prompt_text", None):
                if chat_history is not None:
                    output = await conversation_chain.acall({"question": message, "chat_history": chat_history})
                else:
                    output = await conversation_chain.acall({"question": message})
                self.output = output["answer"]
                yield self.output
                return

            new_chat_prompt_template, condense_prompt = self._build_prompts(chat_template)
            conv_chain_service.qa_prompt = new_chat_prompt_template
            conv_chain_service.qa_prompt_text = chat_template
            conversation_chain = conv_chain_service.generate_conv_chain(condense_prompt)
            if conversation_chain is None:
                self.output = "Sorry! I don't have any information about this question. Please provide me document about this."
                yield self.output
                return

            if chat_history is not None:
                output = await conversation_chain.acall({"question": message, "chat_history": chat_history})
            else:
                output = await conversation_chain.acall({"question": message})
            self.output = output["answer"]
            yield self.output

        except Exception as e:
            custom_logger.error(str(e))
            yield BaseResponse.error_response(message=str(e), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
