import pytest

from ai_assistant.services.response_validator import validate_llm_response

def test_accepts_valid_text_response():
    response = {
        "type": "text",
        "content": "Olá, como posso ajudar?",
    }

    assert validate_llm_response(response) is None

def test_accepts_valid_tool_call_response():
    response = {
        "type": "tool_call",
        "tool_name": "search_products",
        "arguments": {"query": "teclado"},
    }

    assert validate_llm_response(response) is None

def test_rejects_non_dictionary_response():
    with pytest.raises(ValueError):
        validate_llm_response("Resposta inválida")


def test_rejects_text_response_without_string_content():
    response = {
        "type": "text",
        "content": 123,
    }

    with pytest.raises(ValueError):
        validate_llm_response(response)

def test_rejects_tool_call_without_valid_name():
    response = {
        "type": "tool_call",
        "tool_name": "   ",
        "arguments": {"query": "teclado"},
    }

    with pytest.raises(ValueError):
        validate_llm_response(response)

def test_rejects_tool_call_with_invalid_argument():
    response = {
        "type": "tool_call",
        "tool_name": "search_products",
        "arguments": "teclado",
    }

    with pytest.raises(ValueError):
        validate_llm_response(response)

def test_rejects_unknown_response_type():
    response = {
        "type": "image",
        "content": "image",
    }

    with pytest.raises(ValueError):
        validate_llm_response(response)