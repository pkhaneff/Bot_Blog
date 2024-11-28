"""Import service."""
from __future__ import annotations
from io import BytesIO
import os
import docx2txt
import PyPDF2

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger
from app.core.config import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.constants import OPENAI_API_KEY

class ImportService:
    """Import Service"""
    def __init__(self, file_stream: BytesIO):
        """Receiv file_stream: BytesIO from processed file uploaded by client"""
        self.file_stream = file_stream
    

    def txt_to_text(self) -> str:
        """TXT to RawText"""
        detected_text = self.file_stream.getvalue().decode() #Convert BytesIO of txtfile--> string
        return detected_text

    def docx_to_text(self) -> str:
        """DOCX to RawText"""
        detected_text = docx2txt.process(self.file_stream) # Convert BytesIO of docxfile --> string
        return detected_text 

    def pdf_to_text(self) -> str:
        """PDF to RawText"""
        pdf_reader = PyPDF2.PdfReader(self.file_stream) # Convert BytesIO of pdffile --> PdfReader
        num_pages = len(pdf_reader.pages)
        detected_text = ""
        for page_num in range(num_pages):
            page_obj = pdf_reader.pages[page_num]
            detected_text += page_obj.extract_text() + "\n\n"
        return detected_text

    def save_vector(self, detected_text: str, file_name: str = 'index'):
        """Save to vector_restore"""
        try:
            # Make list of docs vector from detected_text
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
            texts = text_splitter.create_documents([detected_text])

            directory = "app/vector_store"
            vector_index_new = FAISS.from_documents(texts, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY))
            # Check if vector_store is empty, if True --> create new index else --> concat with old index
            if not os.path.exists(directory):
                os.makedirs(directory)
                vector_index_new.save_local(directory,file_name)
            elif os.listdir(directory):
                vector_index = FAISS.load_local(directory, OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY), index_name=file_name)
                vector_index.merge_from(vector_index_new)
                vector_index.save_local(directory,file_name) 
            else:
                vector_index_new.save_local(directory,file_name)     
            return BaseResponse.success_response(message="Save embedded vector successfully")
        except Exception as e:
            # log error
            custom_logger.error(str(e))
            return BaseResponse.error_response(message=str(e))
