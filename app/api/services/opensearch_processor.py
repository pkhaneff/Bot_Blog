from __future__ import annotations
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from opensearchpy import OpenSearch                      # NEW
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document            # CHANGED

from app.api.database.dao.imported_document_dao import ImportedDocumentDAO
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.config import OPENAI_API_KEY
from app.core.config import (
    OPENSEARCH_URL, OPENSEARCH_USER, OPENSEARCH_PASSWORD, OPENSEARCH_INDEX,
    OPENSEARCH_USE_SSL, OPENSEARCH_VERIFY_CERTS
)

EMBED_MODEL = "text-embedding-3-small"   # dùng model embedding, KHÔNG dùng gpt-3-turbo
EMBED_DIM   = 1536                       # phải khớp với mapping

class OpenSearchProcessor:
    def __init__(self, db: AsyncSession, index_name: Optional[str] = None):
        self.db = db
        self.dao = ImportedDocumentDAO()
        self.index_name = index_name or OPENSEARCH_INDEX

        # 1) Đảm bảo index tồn tại với mapping đúng
        self._ensure_index()

        # 2) Embedding chuẩn (model + dimension)
        self.emb = OpenAIEmbeddings(
            model=EMBED_MODEL,
            dimensions=EMBED_DIM,
            api_key=OPENAI_API_KEY,
        )

        # 3) Khởi tạo vector store client
        self.vs = OpenSearchVectorSearch(
            embedding_function=self.emb,
            index_name=self.index_name,
            opensearch_url=OPENSEARCH_URL,
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER else None,
            use_ssl=OPENSEARCH_USE_SSL,
            verify_certs=OPENSEARCH_VERIFY_CERTS,
            vector_field="vector",
            text_field="text",
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def _ensure_index(self) -> None:
        client = OpenSearch(
            hosts=[OPENSEARCH_URL],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER else None,
            use_ssl=OPENSEARCH_USE_SSL,
            verify_certs=OPENSEARCH_VERIFY_CERTS,
        )
        if not client.indices.exists(self.index_name):
            body = {
                "settings": {"index": {"knn": True}},
                "mappings": {
                    "properties": {
                        "vector": {
                            "type": "knn_vector",
                            "dimension": EMBED_DIM,
                            "method": {"name": "hnsw", "engine": "nmslib", "space_type": "cosinesimil"},
                        },
                        "text": {"type": "text"},
                        "doc_id": {"type": "keyword"},
                        "file_name": {"type": "keyword"},
                        "chunk": {"type": "integer"},
                    }
                },
            }
            client.indices.create(index=self.index_name, body=body)

    async def process_unprocessed(self, limit: Optional[int] = None):
        try:
            docs = await self.dao.list_unprocessed(self.db, limit=limit)
            if not docs:
                return BaseResponse.success_response(message="No unprocessed documents.")

            indexed_ids: List[str] = []
            for d in docs:
                # Chunking
                chunks = self.splitter.create_documents([d.content])
                doc_objs: List[Document] = []
                for i, ch in enumerate(chunks):
                    doc_objs.append(
                        Document(
                            page_content=ch.page_content,
                            metadata={"doc_id": d.id, "file_name": d.file_name, "chunk": i},
                        )
                    )

                # Index vào OpenSearch (đồng bộ; OK trong async, nhưng sẽ block)
                self.vs.add_documents(doc_objs, vector_field="vector", text_field="text")
                indexed_ids.append(d.id)
                await self.dao.mark_processed(self.db, d.id)

            return BaseResponse.success_response(
                message=f"Indexed {len(indexed_ids)} document(s) to OpenSearch index '{self.index_name}'",
                data={"indexed_ids": indexed_ids},
            )
        except Exception as e:
            custom_logger.error(str(e))
            return BaseResponse.error_response(message=str(e))
