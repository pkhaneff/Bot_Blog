from __future__ import annotations
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from opensearchpy import OpenSearch
from langchain_community.vectorstores import OpenSearchVectorSearch
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from app.api.database.dao.imported_document_dao import ImportedDocumentDAO
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.config import OPENAI_API_KEY
from app.core.config import (
    OPENSEARCH_URL, OPENSEARCH_USER, OPENSEARCH_PASSWORD, OPENSEARCH_INDEX,
    OPENSEARCH_USE_SSL, OPENSEARCH_VERIFY_CERTS
)

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM   = 1536


def default_index_body(
    *,
    vector_field: str = "vector",
    text_field: str = "text",
    extra_settings: Optional[Dict] = None,
    extra_mappings: Optional[Dict] = None,
) -> Dict:
    """Tạo body settings/mappings mặc định, có thể bổ sung/ghi đè theo từng index."""
    body = {
        "settings": {
            "index": {
                "knn": True,
            }
        },
        "mappings": {
            "properties": {
                vector_field: {
                    "type": "knn_vector",
                    "dimension": EMBED_DIM,
                    "method": {
                        "name": "hnsw",
                        "engine": "lucene",
                        "space_type": "cosinesimil",
                        "parameters": {"ef_construction": 128, "m": 16}
                    }
                },
                text_field: {"type": "text"},
                "doc_id": {"type": "keyword"},
                "file_name": {"type": "keyword"},
                "chunk": {"type": "integer"},
            }
        },
    }
    if extra_settings:
        body["settings"].update(extra_settings)
    if extra_mappings:
        body["mappings"]["properties"].update(extra_mappings)
    return body


class OpenSearchProcessor:
    def __init__(
        self,
        db: AsyncSession,
        index_name: Optional[str] = None,
        *,
        # Cho phép cấu hình theo từng index
        vector_field: str = "vector",
        text_field: str = "text",
        index_body: Optional[Dict] = None,
        create_if_missing: bool = True,
    ):
        self.db = db
        self.dao = ImportedDocumentDAO()
        self.index_name = index_name or OPENSEARCH_INDEX
        self.vector_field = vector_field
        self.text_field = text_field

        # Khởi tạo client 1 lần để tái sử dụng
        self.client = OpenSearch(
            hosts=[OPENSEARCH_URL],
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER else None,
            use_ssl=OPENSEARCH_USE_SSL,
            verify_certs=OPENSEARCH_VERIFY_CERTS,
        )

        # Chỉ tạo index nếu chưa có và cho phép tạo
        if create_if_missing:
            self._ensure_index(
                index_name=self.index_name,
                body=index_body
                or default_index_body(
                    vector_field=self.vector_field,
                    text_field=self.text_field,
                ),
            )

        self.emb = OpenAIEmbeddings(
            model=EMBED_MODEL,
            dimensions=EMBED_DIM,
            api_key=OPENAI_API_KEY,
        )

        self.vs = OpenSearchVectorSearch(
            embedding_function=self.emb,
            index_name=self.index_name,
            opensearch_url=OPENSEARCH_URL,
            http_auth=(OPENSEARCH_USER, OPENSEARCH_PASSWORD) if OPENSEARCH_USER else None,
            use_ssl=OPENSEARCH_USE_SSL,
            verify_certs=OPENSEARCH_VERIFY_CERTS,
            vector_field=self.vector_field,
            text_field=self.text_field,
        )

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

    def _ensure_index(self, *, index_name: str, body: Dict) -> None:
        """Tạo index với cấu hình RIÊNG nếu chưa tồn tại; nếu đã có thì dùng luôn."""
        try:
            exists = self.client.indices.exists(index=index_name)
            if not exists:
                self.client.indices.create(index=index_name, body=body)
        except Exception as e:
            # Nếu race-condition khi nhiều worker cùng tạo, bỏ qua lỗi 'resource_already_exists_exception'
            msg = str(e)
            if "resource_already_exists_exception" not in msg:
                raise

    async def process_unprocessed(self, limit: Optional[int] = None):
        try:
            docs = await self.dao.list_unprocessed(self.db, limit=limit)
            if not docs:
                return BaseResponse.success_response(message="No unprocessed documents.")

            indexed_ids: List[str] = []
            for d in docs:
                chunks = self.splitter.create_documents([d.content])
                doc_objs: List[Document] = []
                for i, ch in enumerate(chunks):
                    doc_objs.append(
                        Document(
                            page_content=ch.page_content,
                            metadata={"doc_id": d.id, "file_name": d.file_name, "chunk": i},
                        )
                    )

                # Đảm bảo trường phải khớp với mapping của index hiện tại
                self.vs.add_documents(doc_objs, vector_field=self.vector_field, text_field=self.text_field)
                indexed_ids.append(d.id)
                await self.dao.mark_processed(self.db, d.id)

            return BaseResponse.success_response(
                message=f"Indexed {len(indexed_ids)} document(s) to OpenSearch index '{self.index_name}'",
                data={"indexed_ids": indexed_ids},
            )
        except Exception as e:
            custom_logger.error(str(e))
            return BaseResponse.error_response(message=str(e))
