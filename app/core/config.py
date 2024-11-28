"""Define config for project."""
from __future__ import annotations

import logging
import sys

from dotenv import load_dotenv
from loguru import logger
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings

from app.core.logging import InterceptHandler

load_dotenv('.env')

API_PREFIX = "/api"

VERSION = "0.0.0"

config = Config()

DEBUG: bool = config("DEBUG", cast=bool, default=False)

PROJECT_NAME: str = config("PROJECT_NAME", default="Flowers Blog Chatbot")
ALLOWED_HOSTS: list[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

# logging configuration
LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGERS = ("uvicorn.asgi", "uvicorn.access")

logging.getLogger().handlers = [InterceptHandler()]
for logger_name in LOGGERS:
    logging_logger = logging.getLogger(logger_name)
    logging_logger.handlers = [InterceptHandler(level=LOGGING_LEVEL)]

logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])

# Import configuration
MAX_FILE_SIZE = 5*1024*1024
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# APIKey authen
API_KEY_NAME = "access_token"

# Model name
MODEL_NAME = "gpt-3.5-turbo"