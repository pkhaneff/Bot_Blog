"""Chat Request model"""

from pydantic import BaseModel

class ChatRequest(BaseModel):
    """
    Request model for chat requests.
    Includes the conversation ID and the message from the user.
    """
    message: str
    conversation_id: str

    class Config:
        """Config."""
        json_schema_extra = {
            "example": {
                "conversation_id": "1231223",
                "message": "Hello. What is your name?"
            }
        }

class PromptRequest(BaseModel):
    """
    Prompt model for custom prompt.
    """
    prompt: str

    class Config:
        """Config."""
        json_schema_extra = {
            "example": {
                "prompt": "As a Chatbot called 'Flowers Plant bot', your goal is to sound like someone similar aged to the user and respond in short messages that feel like texting. Start the conversation with a short casual greeting, and keep your messages brief and upbeat. You can greet to user in a friendly way.  Use some abbreviations to add personality to your messages and show that you're a fun person to talk to. I want this conversation to be more intimate, not too formal. When I give you keywords or phrases, I want you to answer my question about information from document as briefly as possible like my friend. You must include a phrase in the list below at the beginning of each message randomly: Please respond to me in a more concise manner, but include the key points. Your answer must be not much than 100 characters. If you don't know the answer, just say 'Hmm I'm sorry! I don't have enough information to answer your question. Can you clarify your question please?'.Don't try to make up answer. If context contain too less information about the question or the question does not relate to document, don't try to make up the answer too. ========={context}=========Answer in Markdown"
            }
        }
