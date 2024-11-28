"""
    Custom Prompt Service
"""

from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
    PromptTemplate
)

class CustomPromptService:
    """Custom Prompt Service"""
    def __init__(self, template, _template, human_template: str = "Question: {question}") -> None:
        self.prompt_template = template
        self.human_template = human_template
        self._template = _template

    def custom_prompt(self) -> ChatPromptTemplate:
        """Custom chat prompt"""
        chat_prompt_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    f"""{self.prompt_template}"""
                ),
                # MessagesPlaceholder(variable_name="prompt"),
                HumanMessagePromptTemplate.from_template(self.human_template),
            ]
        )
        return chat_prompt_template
    
    def custom_condense_prompt(self):
        """Custom condense prompt"""
        # condense_prompt_Template = PromptTemplate.from_template(self._template)
        condense_prompt_Template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    f"""{self._template}"""
                ),
                # MessagesPlaceholder(variable_name="chat_history"),
                HumanMessagePromptTemplate.from_template("Follow Up Question: {question}"),
            ]
        )
        return condense_prompt_Template

    def custom_language_detect_prompt(self, language_template):
        """Custom language detect prompt"""
        language_dectect_template = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate.from_template(
                    f"""{language_template}"""
                ),
                HumanMessagePromptTemplate.from_template(self.human_template),
            ]
        )
        return language_dectect_template
