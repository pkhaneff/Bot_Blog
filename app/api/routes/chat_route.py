"""
    Chat API using LangChain and ChatOpenAI
"""
from __future__ import annotations
from starlette import status
import datetime

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from langchain.callbacks import AsyncIteratorCallbackHandler

from app.api.model.request import ChatRequest
from app.api.services.chat_service import ConversationChainService
from app.api.model.streaming_chain import StreamingConversationRetrievalChain
from app.api.responses.base import BaseResponse
from app.logger.logger import custom_logger

router = APIRouter()

callbacks = {}
streaming_conversation_chains = {}
conv_chain_services = {}
conversation_chains = {}

@router.post("/stream_chat/")
async def generate_response(data: ChatRequest):
    """
    Generate streaming response based on user question.
    Note: Must wait for response complete to send another question.
    Input: User question and conversation_id (string)
    Output Chatbot response in streaming format
    """
    try:
        if len(data.conversation_id) != 0:
            if data.conversation_id not in callbacks:   # if conversation_id not exist in callbacks
                # Initialize Streaming Conversation Chain
                create_time = datetime.datetime.now()
                callbacks[data.conversation_id] = {"callback": AsyncIteratorCallbackHandler(),
                                                   "time_created": create_time}
                streaming_conversation_chains[data.conversation_id] = {"conv_chain": StreamingConversationRetrievalChain(callbacks[data.conversation_id]["callback"],
                                                                                                                         conversation_id=data.conversation_id),
                                                                       "time_created": create_time}
                # Initialize ConversationalRetrievalChain Service
                conv_chain_services[data.conversation_id] = ConversationChainService(
                    temperature=streaming_conversation_chains[data.conversation_id]["conv_chain"].temperature,
                    memory=streaming_conversation_chains[data.conversation_id]["conv_chain"].memories[data.conversation_id],
                    streaming_cb=streaming_conversation_chains[data.conversation_id]["conv_chain"].streaming_cb,
                    conv_cb_manager=streaming_conversation_chains[data.conversation_id]["conv_chain"].conv_cb_manager,
                    qa_prompt=streaming_conversation_chains[data.conversation_id]["conv_chain"].chat_prompt_template
                )

                # Create ConversationalRetrievalChain
                conversation_chains[data.conversation_id] = conv_chain_services[data.conversation_id].generate_conv_chain(streaming_conversation_chains[data.conversation_id]["conv_chain"].condense_question_prompt)

                # Delete variables
                del(create_time)
            else:
                current_time = datetime.datetime.now()
                latest_time = callbacks[data.conversation_id]["time_created"]
                if (current_time - latest_time).total_seconds() < 43200:
                    pass
                else:
                    # Initialize Streaming Conversation Chain
                    callbacks[data.conversation_id] = {"callback": AsyncIteratorCallbackHandler(),
                                                       "time_created": current_time}
                    streaming_conversation_chains[data.conversation_id] = {"conv_chain": StreamingConversationRetrievalChain(callbacks[data.conversation_id]["callback"],
                                                                                                                             conversation_id=data.conversation_id),
                                                                           "time_created": current_time}
                                                                           
                    # Initialize ConversationalRetrievalChain Service
                    conv_chain_services[data.conversation_id] = ConversationChainService(
                        temperature=streaming_conversation_chains[data.conversation_id]["conv_chain"].temperature,
                        memory=streaming_conversation_chains[data.conversation_id]["conv_chain"].memories[data.conversation_id],
                        streaming_cb=streaming_conversation_chains[data.conversation_id]["conv_chain"].streaming_cb,
                        conv_cb_manager=streaming_conversation_chains[data.conversation_id]["conv_chain"].conv_cb_manager,
                        qa_prompt=streaming_conversation_chains[data.conversation_id]["conv_chain"].chat_prompt_template
                    )

                    # Create ConversationalRetrievalChain
                    conversation_chains[data.conversation_id] = conv_chain_services[data.conversation_id].generate_conv_chain(streaming_conversation_chains[data.conversation_id]["conv_chain"].condense_question_prompt)

                    # Delete variables
                    del(current_time)
                    del(latest_time)
                    
            try: 
                await streaming_conversation_chains[data.conversation_id]["conv_chain"].generate_response(
                    data.message, 
                    streaming_conversation_chains[data.conversation_id]["conv_chain"].chat_template,
                    conv_chain_services[data.conversation_id], 
                    conversation_chains[data.conversation_id]
                )
            except Exception as e:
                # log error
                custom_logger.error("Error with OpenAI server")
                return BaseResponse.error_response(message="Error with OpenAI server",
                                                   status_code=status.HTTP_400_BAD_REQUEST)

            # Update time
            latest_time = datetime.datetime.now()
            callbacks[data.conversation_id]["time_created"] = latest_time
            streaming_conversation_chains[data.conversation_id]["time_created"] = latest_time

            # Delete variables
            del(latest_time)

            return streaming_conversation_chains[data.conversation_id]["conv_chain"].output
        else:
            # log error
            custom_logger.error("conversation_id is empty")
            return BaseResponse.error_response(message="conversation_id is empty",
                                               status_code=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        # log error
        custom_logger.error(str(e))
        return BaseResponse.error_response(message=str(e),
                                           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)