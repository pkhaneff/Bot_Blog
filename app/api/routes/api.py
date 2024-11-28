"""API Routes."""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from app.api.routes import import_route, chat_route, custom_prompt_route

app = APIRouter()

app.include_router(
    import_route.router,
    tags=["Import Data"],
    prefix="/bot",
)

# Stream chat route
app.include_router(
    chat_route.router,
    tags=["Chat"],
    prefix="/bot",
)

# Custome prompt route
app.include_router(
    custom_prompt_route.router,
    tags=["Custom Prompt"],
    prefix="/bot",
)
