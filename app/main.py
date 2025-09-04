"""Start Application."""
import os

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.responses import Response
from starlette.types import Message

from app.api.errors.http_error import http_error_handler
from app.api.errors.validation_error import http422_error_handler
from app.core.config import ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from app.logger.logger import custom_logger

if PROJECT_NAME:
    from app.api.routes.api import app as api_router


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging All API request."""

    async def set_body(request: Request, body: bytes):

        async def receive() -> Message:
            """Receive body."""
            return {"type": "http.request", "body": body}

        request._receive = receive

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Dispatch."""
        await self.set_body(request)

        # Call the next middleware or route handler
        response = await call_next(request)

        return response

def get_application() -> FastAPI:
    """Get application

    Returns:
        FastAPI Chatbot application
    """

    application = FastAPI(title=PROJECT_NAME, version=VERSION)
    application.add_middleware(LoggingMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # application.add_middleware(GZipMiddleware, minimum_size=1000)
    application.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

    application.include_router(api_router, prefix=API_PREFIX)

    return application


app = get_application()
from app.api.database.create_db import create_db
@app.on_event("startup")
async def on_startup():
    await create_db()

if __name__ == "__main__":
    HOST = os.getenv("APP_HOST")
    PORT = os.getenv("APP_PORT")
    uvicorn.run(app, host=HOST, port=int(PORT))
