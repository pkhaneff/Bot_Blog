# Condense Prompt Template
_template = """
Given the following conversation and a follow up question to be a standalone question.
You can assume the question about the documents.
If user repeat the question, you must rephrase the same question as before please.
If follow up question is meaningful and related to any information from chat history then rephrase the follow up question to be a standalone question meaningful and related to document or the chat history.
If follow up question is meaningful but not related to any information from documents or chat history then don't rephrase the follow up question to be a standalone question meaningful, just rephrase it to meaningless question.
If follow up question is meaningless (like contain meaningless question or punctuation marks) or question does related to any information of documents, you mustn't try to rephrase that question to be meaningful please.

Chat History:
{chat_history}
Follow Up Question: {question}
Standalone question:
"""