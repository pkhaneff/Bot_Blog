"""Import service: extract text -> save RAW to DB (is_process=false)."""
from __future__ import annotations
from io import BytesIO
import uuid
import docx2txt
import PyPDF2

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.api.database.models.imported_document import ImportedDocument
from app.api.database.dao.imported_document_dao import ImportedDocumentDAO


class ImportService:
    def __init__(self, file_stream: BytesIO, db: AsyncSession):
        self.file_stream = file_stream
        self.db = db
        self.dao = ImportedDocumentDAO()

    def pdf_to_text(self) -> str:
        reader = PyPDF2.PdfReader(self.file_stream)
        texts = []
        for page in reader.pages:
            texts.append(page.extract_text() or "")
        return "\n".join(texts)

    def txt_to_text(self) -> str:
        return self.file_stream.read().decode("utf-8")

    def docx_to_text(self) -> str:
        data = self.file_stream.read()
        from tempfile import NamedTemporaryFile
        with NamedTemporaryFile(suffix=".docx") as tmp:
            tmp.write(data)
            tmp.flush()
            return docx2txt.process(tmp.name)

    async def save_raw(self, file_name: str, content: str):
        try:
            new_id = str(uuid.uuid4())
            doc = ImportedDocument(
                id=new_id,
                file_name=file_name,
                content=content,
                is_process=False
            )
            await self.dao.add_document(self.db, doc)
            return BaseResponse.success_response(
                message=f"Saved raw doc to DB with id={new_id}",
                data={"id": new_id}
            )
        except Exception as e:
            custom_logger.error(str(e))
            return BaseResponse.error_response(message=str(e))
