import pytest

from ai_assistant.services.llm_provider import LLMProvider

def test_cannot_instantiate_abstract_provider():
    with pytest.raises(TypeError):
        LLMProvider()

class FakeLLMProvider(LLMProvider):
    def generate_response(self, messages: list, tools:list):
        return {
            "type": "text",
            "content": "Resposta simulada do modelo."
        }

def test_fake_provider_implements_contract():
    provider = FakeLLMProvider()

    response = provider.generate_response(
        messages=[{"role": "user", "content": "olá"}],
        tools=[]
    )

    assert response["type"] == "text"
    assert response["content"] == "Resposta simulada do modelo."


def test_fake_provider_returns_text_response():
    provider = FakeLLMProvider()

    response = provider.generate_response([], [])

    assert response == {
        "type": "text",
        "content": "Resposta simulada do modelo."
    }

def test_tool_call_response_structure():
    response = {
        "type": "tool_call",
        "tool_name": "search_products",
        "arguments": {"query": "teclado"},
    }

    assert response["type"] == "tool_call"
    assert response["tool_name"] == "search_products"
    assert response["arguments"]["query"] == "teclado"