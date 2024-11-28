""" Import_route """
import io
from fastapi import APIRouter, UploadFile, File
from app.api.services.import_service import ImportService
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import MAX_FILE_SIZE

router = APIRouter()

@router.post("/import_data", response_description="import")
async def upload_file(file: UploadFile = File(...)):
    """
    Uploaded file and converted into vector_store.
    Note: Upload each file one at a time.
    Suppport .pdf, .txt, .docx
    """
    try:
        type_available = ["pdf", "txt", "docx"]
        file_type = file.filename.split(".")[-1]

        # Check size of the uploaded file
        if len(await file.read()) > MAX_FILE_SIZE:
            # log error
            error = "Could not upload file with size larger than 20MB."
            custom_logger.error(error)
            return BaseResponse.error_response(message=error, status_code=400)
        
        # Check if the uploaded file extension available
        if not file_type in type_available:
            # log error
            error = f'Uploaded file is not available supported. Supported files are {", ".join(type_available)}'
            custom_logger.error(error)
            return BaseResponse.error_response(message=error, status_code=415)
        
        # Process the uploaded file
        await file.seek(0) # reset cursor to point at the begining of the file after the first read()
        file_bytes = await file.read()
        file_stream = io.BytesIO(file_bytes)

        # Call service to save representative vector
        import_service = ImportService(file_stream)
        import_type_fn = {'pdf': import_service.pdf_to_text,
                          'txt': import_service.txt_to_text,
                          'docx': import_service.docx_to_text}
        texts = import_type_fn[file_type]()
        response_result = import_service.save_vector(texts)
        return response_result
    except Exception as e:
        # log error
        custom_logger.error(str(e))
        return BaseResponse.error_response(message=str(e))
