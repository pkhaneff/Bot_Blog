"""
    StreamingChat using LangChain and ChatOpenAI
"""
from __future__ import annotations
from collections.abc import AsyncGenerator
from starlette import status

from langchain.callbacks.manager import AsyncCallbackManager
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain

from app.core.condense_prompt import _template
from app.api.services.custom_prompt_service import CustomPromptService

class StreamingConversationRetrievalChain:
    """
    Class for handling streaming conversation chains.
    It creates and stores memory for each conversation,
    and generates responses using the ChatOpenAI model from LangChain.
    """

    def __init__(self, streaming_cb: AsyncIteratorCallbackHandler,
                 conversation_id: str = "24",
                 temperature: float = 0.0):
        self.memories = {}
        self.temperature = temperature
        self.conversation_id = conversation_id

        # Create Callback Handler
        self.streaming_cb = streaming_cb
        self.conv_cb_manager = AsyncCallbackManager([streaming_cb])

        # Create memory for each conversation_id
        self.memory = self.memories.get(self.conversation_id)
        if self.memory is None:
            self.memory = ConversationBufferWindowMemory(memory_key="chat_history", 
                                                         return_messages=True, 
                                                         output_key="answer",
                                                         k=4)
                                                   
            self.memories[self.conversation_id] = self.memory

        # Load prompt
        with open(r"app/core/chat_prompt.txt", "r", encoding="utf-8") as file:
            template = file.read()
        self.chat_template = f"""{template}"""
        custom_chat_prompt = CustomPromptService(self.chat_template, _template)
        self.chat_prompt_template = custom_chat_prompt.custom_prompt()
        self.condense_question_prompt = custom_chat_prompt.custom_condense_prompt()

        self.output = None

    async def generate_response(
        self, message: str, 
        chat_template: str,
        conv_chain_service: ConversationChainService,
        conversation_chain: ConversationalRetrievalChain
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous function to generate a response for a conversation.
        It creates a new conversation chain for each message and uses a
        callback handler to stream responses as they're generated.
        :param message: The message from the user.
        :param chat_template: Prompt template for system chat.
        :param conv_chain_service: Conversation Chain Service.
        :param conversation_chain: ConversationalRetrievalChain.
        """
        # Load prompt from chat_prompt.txt
        with open(r"app/core/chat_prompt.txt", "r", encoding="utf-8") as file:
            template = file.read()
        current_template = f"""{template}"""

        # Check current prompt with initial prompt
        if current_template == chat_template:
            output = await conversation_chain.acall({"question": message})
            self.output = output['answer']
        else:
            custom_chat_prompt = CustomPromptService(current_template, _template)
            new_chat_prompt_template = custom_chat_prompt.custom_prompt()  
            conv_chain_service.qa_prompt = new_chat_prompt_template

            conversation_chain = conv_chain_service.generate_conv_chain(self.condense_question_prompt)
            if conversation_chain is None:
                answer = "Sorry! I don't have any information about this question. Please provide me document about this."
                self.output = answer
            else:
                output = await conversation_chain.acall({"question": message})
                self.output = output['answer']
