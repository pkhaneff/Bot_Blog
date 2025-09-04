"""Chat service"""
from __future__ import annotations
from starlette import status

# ✅ Dùng wrapper mới
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import OpenSearchVectorSearch

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks import AsyncIteratorCallbackHandler

from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import MODEL_NAME, OPENAI_API_KEY
from app.core.config import (
    OPENSEARCH_URL, OPENSEARCH_USER, OPENSEARCH_PASSWORD, OPENSEARCH_INDEX,
    OPENSEARCH_USE_SSL, OPENSEARCH_VERIFY_CERTS
)

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536

class ConversationChainService:
    def __init__(self,
                 temperature: float,
                 streaming_cb: AsyncIteratorCallbackHandler,
                 conv_cb_manager: AsyncCallbackManager,
                 qa_prompt: PromptTemplate) -> None:
        self.temperature = temperature
        self.streaming_cb = streaming_cb
        self.conv_cb_manager = conv_cb_manager
        self.qa_prompt = qa_prompt

        try:
            embeddings = OpenAIEmbeddings(
                model=EMBED_MODEL,
                dimensions=EMBED_DIM,
                api_key=OPENAI_API_KEY,
            )

            vector_index = OpenSearchVectorSearch(
                embedding_function=embeddings,
                index_name=OPENSEARCH_INDEX,
                opensearch_url=OPENSEARCH_URL,
                http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER else None,
                use_ssl=OPENSEARCH_USE_SSL,
                verify_certs=OPENSEARCH_VERIFY_CERTS,
                vector_field="vector",
                text_field="text"
            )
            self.retriever = vector_index.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3, "vector_field": "vector", "text_field": "text"}
            )
        except Exception as e:
            custom_logger.error(str(e))
            self.retriever = None

    def generate_conv_chain(self, condense_prompt: PromptTemplate | None):
        try:
            if not self.retriever:
                return None

            question_gen_llm = ChatOpenAI(
                model=MODEL_NAME,
                temperature=self.temperature,
                max_retries=15,
                timeout=100,
                max_tokens=200,
                api_key=OPENAI_API_KEY,
                streaming=False,
            )

            streaming_llm = ChatOpenAI(
                model=MODEL_NAME,
                temperature=self.temperature,
                max_retries=15,
                timeout=100,
                max_tokens=350,
                api_key=OPENAI_API_KEY,
                streaming=True,                  
                callbacks=[self.streaming_cb],  
            )

            question_gen_chain = None
            if condense_prompt is not None:
                question_gen_chain = LLMChain(llm=question_gen_llm, prompt=condense_prompt)

            final_qa_chain = load_qa_chain(
                llm=streaming_llm,
                chain_type="stuff",
                prompt=self.qa_prompt,
                callback_manager=self.conv_cb_manager
            )

            conversation_chain = ConversationalRetrievalChain(
                retriever=self.retriever,
                question_generator=question_gen_chain,
                combine_docs_chain=final_qa_chain,
                return_source_documents=False,
                max_tokens_limit=2000,
                callback_manager=self.conv_cb_manager,
            )
            return conversation_chain
        except FileNotFoundError:
            custom_logger.error("Could not find vector store")
            return BaseResponse.error_response(
                message="Could not find vector store",
                status_code=status.HTTP_404_NOT_FOUND
            )
