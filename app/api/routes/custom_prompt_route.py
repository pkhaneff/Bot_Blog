"""
    Custom Prompt API
"""
from __future__ import annotations

from fastapi import APIRouter

from app.api.model.request import PromptRequest

router = APIRouter()

@router.post("/custom_prompt")
async def custom_prompt(prompt_request: PromptRequest) -> str:
    """
    Custom your own prompt.
    """
    chat_template = prompt_request.prompt

    # Write prompt data to chat_prompt.txt
    with open(r"app/core/chat_prompt.txt", "w", encoding="utf-8") as file:
        file.write(f'{chat_template}')
    return chat_template
