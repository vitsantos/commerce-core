from abc import ABC, abstractmethod
from typing import Literal, TypedDict

class TextResponse(TypedDict):
    type: Literal["text"]
    content: str

class ToolCallResponse(TypedDict):
    type: Literal["tool_call"]
    tool_name: str
    arguments: dict

LLMResponse = TextResponse | ToolCallResponse


class LLMProvider(ABC):
    @abstractmethod
    def generate_response(self, messages: list, tools: list) -> LLMResponse:
        #gera uma resposta do modelo ou uma solicitação de ferramenta.
        pass