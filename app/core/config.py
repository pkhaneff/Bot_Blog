# app/core/config.py
from __future__ import annotations
import logging, sys
from loguru import logger as loguru_logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

# Đọc .env (prod có thể set ENV, vẫn OK)
config = Config(".env")

# ===== App meta =====
API_PREFIX: str = "/api"
VERSION: str = "0.0.0"
PROJECT_NAME: str = config("PROJECT_NAME", default="Flowers Blog Chatbot")
DEBUG: bool = config("DEBUG", cast=bool, default=False)
ALLOWED_HOSTS: list[str] = config("ALLOWED_HOSTS", cast=CommaSeparatedStrings, default="")

# ===== Logging =====
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
for name in ("uvicorn.asgi", "uvicorn.access"):
    logging.getLogger(name).handlers = []
root = logging.getLogger()
root.handlers = []
loguru_logger.remove()
loguru_logger.add(sys.stderr, level=LOGGING_LEVEL)

# ===== Limits / Model =====
MAX_FILE_SIZE: int = config("MAX_FILE_SIZE", cast=int, default=5 * 1024 * 1024)
CHUNK_SIZE: int = config("CHUNK_SIZE", cast=int, default=1000)
CHUNK_OVERLAP: int = config("CHUNK_OVERLAP", cast=int, default=200)
MODEL_NAME: str = config("MODEL_NAME", default="gpt-3.5-turbo")

# ===== API key auth =====
API_KEY_NAME: str = config("API_KEY_NAME", default="access_token")
API_KEY: str = config("API_KEY", default="")  # nếu dùng

# ===== OpenAI =====
OPENAI_API_KEY: str = config("OPENAI_API_KEY", default="")

# ===== Misc app =====
LOCAL_HOST: str = config("LOCAL_HOST", default="127.0.0.1")

# ===== OpenSearch =====
OPENSEARCH_URL: str = config("OPENSEARCH_URL", default="http://127.0.0.1:9200")
OPENSEARCH_USER: str = config("OPENSEARCH_USER", default="")
OPENSEARCH_PASSWORD: str = config("OPENSEARCH_PASSWORD", default="")
OPENSEARCH_INDEX: str = config("OPENSEARCH_INDEX", default="chatbot_docs")
OPENSEARCH_USE_SSL: bool = config("OPENSEARCH_USE_SSL", cast=bool, default=False)
OPENSEARCH_VERIFY_CERTS: bool = config("OPENSEARCH_VERIFY_CERTS", cast=bool, default=False)

# ===== (Tùy chọn) DB =====
POSTGRES_DETAILS: str = config("POSTGRES_DETAILS", default="")
