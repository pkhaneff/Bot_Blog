# pylint: skip-file
"""Conversation Views Model."""

from pydantic import BaseModel


class ConvesationModel(BaseModel):
    """Conversation ViewsModel/Schema"""

    conversation_id: str

    class Config:
        """Config."""

        json_schema_extra = {
            "example": {
                "conversation_id":"1"
            }
        }

class ConvesationDetailModel(BaseModel):
    """Conversation Detail ViewsModel/Schema"""

    message_detail: str
    role: str
    conversation_id: str
    
    class Config:
        """Config."""

        json_schema_extra = {
            "example": {
                "message_detail":"Hello",
                "role": "user",
                "conversation_id":"1"
            }
        }

class PromptRequest(BaseModel):
    """Model for custom prompt request."""

    prompt: str

    class Config:
        """Config."""

        json_schema_extra = {
            "example": {
                "prompt": "Your custom prompt here"
            }
        }
