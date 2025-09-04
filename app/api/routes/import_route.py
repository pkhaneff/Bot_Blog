""" Import routes """
from __future__ import annotations
import io
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.services.import_service import ImportService
from app.api.services.opensearch_processor import OpenSearchProcessor
from app.api.model.request import ProcessUnprocessedRequest
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import MAX_FILE_SIZE
from app.api.database.models.base import get_db

router = APIRouter()

@router.post("/import_data", response_description="import")
async def upload_file(file: UploadFile = File(...), db: AsyncSession = Depends(get_db)):
    """
    Upload -> extract text -> LƯU RAW vào DB (is_process=false).
    Hỗ trợ .pdf, .txt, .docx
    """
    try:
        file_size = getattr(file, "size", None)
        if file_size and file_size > MAX_FILE_SIZE:
            return BaseResponse.error_response(message="File is too large")

        ext = file.filename.split(".")[-1].lower()
        if ext not in ["pdf", "txt", "docx"]:
            return BaseResponse.error_response(message="Only support .pdf, .txt, .docx")

        await file.seek(0)
        file_bytes = await file.read()
        file_stream = io.BytesIO(file_bytes)

        svc = ImportService(file_stream, db)

        if ext == "pdf":
            text = svc.pdf_to_text()
        elif ext == "txt":
            text = svc.txt_to_text()
        else:
            text = svc.docx_to_text()

        return await svc.save_raw(file.filename, text)

    except Exception as e:
        custom_logger.error(str(e))
        return BaseResponse.error_response(message=str(e))


@router.post("/opensearch/process_unprocessed")
async def process_unprocessed(req: ProcessUnprocessedRequest, db: AsyncSession = Depends(get_db)):
    """
    Đọc các record imported_document có is_process=false,
    chunk + embed + index vào OpenSearch,
    sau đó set is_process=true.
    """
    processor = OpenSearchProcessor(db, index_name=req.index_name)
    return await processor.process_unprocessed(limit=req.batch_size)
