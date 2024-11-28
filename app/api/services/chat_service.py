"""Chat service"""
from __future__ import annotations

import os
from starlette import status

from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks import AsyncIteratorCallbackHandler

from app.core.config import MODEL_NAME
from app.core.constants import OPENAI_API_KEY
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger

class ConversationChainService:
    """Create ConversationalRetrievalChain Service"""

    def __init__(self, temperature: float,
                 memory: ConversationBufferMemory,
                 streaming_cb: AsyncIteratorCallbackHandler,
                 conv_cb_manager: AsyncCallbackManager,
                 qa_prompt: PromptTemplate) -> None:
        """
        Receive memory, StreamingCallback and ConversationChainCallback
        """
        self.temperature = temperature
        self.memory = memory
        self.streaming_cb = streaming_cb
        self.conv_cb_manager = conv_cb_manager
        self.qa_prompt = qa_prompt
        
        directory = "app/vector_store"
        if not os.path.exists(directory):
            os.makedirs(directory)
        elif len(os.listdir(directory)) == 0:
            custom_logger.error("Could not find vector store")
            raise FileNotFoundError
        else:
            vector_index = FAISS.load_local(directory, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), allow_dangerous_deserialization=True)
            self.retriever = vector_index.as_retriever(search_type="similarity", search_kwargs={"k": 3})

    def generate_conv_chain(self, condense_prompt: PromptTemplate) -> ConversationalRetrievalChain:
        """
        Generates a conversational retrieval chain
        """
        try:
            question_gen_llm = ChatOpenAI(
                model_name=MODEL_NAME,
                max_retries=15,
                temperature=self.temperature,
                # streaming=True,
                request_timeout=100,
                max_tokens=200,
                openai_api_key=OPENAI_API_KEY
            )

            streaming_llm = ChatOpenAI(
                model_name=MODEL_NAME,
                max_retries=15,
                temperature=self.temperature,
                callbacks=[self.streaming_cb],
                streaming=False,
                request_timeout=100,
                max_tokens=350,
                openai_api_key=OPENAI_API_KEY
            )

            question_gen_chain = LLMChain(llm=question_gen_llm, prompt=condense_prompt)  # , callback_manager=manager)

            final_qa_chain = load_qa_chain(
                streaming_llm,
                prompt=self.qa_prompt
            )

            conversation_chain = ConversationalRetrievalChain(
                retriever=self.retriever,
                question_generator=question_gen_chain,
                combine_docs_chain=final_qa_chain,
                memory=self.memory,
                return_source_documents=False,
                max_tokens_limit=2000,
                callback_manager=self.conv_cb_manager,
            )

            return conversation_chain
        except FileNotFoundError:
            custom_logger.error("Could not find vector store")
            return BaseResponse.error_response(message="Could not find vector store",
                                               status_code=status.HTTP_404_INTERNAL_SERVER_ERROR)
