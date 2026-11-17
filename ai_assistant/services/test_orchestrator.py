import pytest
from unittest.mock import patch
from django.test import SimpleTestCase
from ai_assistant.services.orchestrator import process_tool_call, process_llm_response

class ProcessToolCallTestes(SimpleTestCase):
    @patch("ai_assistant.services.orchestrator.execute_tool")
    def test_process_valid_tool_call(self, mock_execute):
        mock_execute.return_value = [{"sku": "TEC001"}]

        tool_call = {
            "tool_name": "search_products",
            "arguments": {"query": "teclado"},
        }

        result = process_tool_call(tool_call)

        mock_execute.assert_called_once_with(
            "search_products",
            {"query": "teclado"},
        )
        self.assertEqual(result, [{"sku": "TEC001"}])


    def test_rejects_non_dictionary_tool_call(self):
        with self.assertRaises(ValueError):
            process_tool_call("search_products")


    def test_rejects_missing_tool_name(self):
        tool_call = {
            "arguments": {"query": "teclado"},
        }

        with self.assertRaises(ValueError):
            process_tool_call(tool_call)


    def test_rejects_missing_arguments(self):
        tool_call = {
            "tool_name": "search_products",
        }

        with self.assertRaises (ValueError):
            process_tool_call(tool_call)


    @patch ("ai_assistant.services.orchestrator.execute_tool")
    def test_propagates_unknown_tool_error(self, mock_execute):
        mock_execute.side_effect = ValueError(
            "Ferramenta não registrada: delete_all_products"
        )

        tool_call = {
            "tool_name": "delete_all_products",
            "arguments": {},
        }

        with self.assertRaises(ValueError):
            process_tool_call(tool_call)


    def _assert_rejects_tool_name(self, tool_name):
        with patch(
            "ai_assistant.services.orchestrator.execute_tool"
        ) as mock_execute:
            with self.assertRaises(ValueError):
                process_tool_call({
                    "tool_name": tool_name,
                    "arguments": {"query": "teclado"},
                })

            mock_execute.assert_not_called()

    def test_rejects_numeric_tool_name(self):
        self._assert_rejects_tool_name(123)

    def test_rejects_list_tool_name(self):
        self._assert_rejects_tool_name(["search_products"])

    def test_rejects_dictionary_tool_name(self):
        self._assert_rejects_tool_name({"name": "search_products"})

    def test_rejects_whitespace_tool_name(self):
        self._assert_rejects_tool_name("   ")

    def test_process_llm_response_returns_text(self):
        response = {
            "type": "text",
            "content": "Olá, como posso ajudar?",
        }

        with patch(
            "ai_assistant.services.orchestrator.process_tool_call"
        ) as mock_process:
            result = process_llm_response(response)

        self.assertEqual(result, response)
        mock_process.assert_not_called()


    def test_process_llm_response_executes_tool_call(self):
        response = {
            "type": "tool_call",
            "tool_name": "search_products",
            "arguments": {"query": "teclado"},
        }

        expected_result = [{"sku": "TEC001"}]

        with patch (
            "ai_assistant.services.orchestrator.process_tool_call",
            return_value = expected_result,
        ) as mock_process:
            result = process_llm_response(response)

        mock_process.assert_called_once_with({
            "tool_name": "search_products",
            "arguments": {"query": "teclado"},
        })

        self.assertEqual(result, expected_result)


    def test_process_llm_response_rejects_invalid_response(self):
        response = {
            "type": "tool_call",
            "tool_name": "search_products",
            "arguments": "teclado",
        }

        with patch (
            "ai_assistant.services.orchestrator.process_tool_call"
        ) as mock_process:
            with self.assertRaises(ValueError):
                process_llm_response(response)

        mock_process.assert_not_called()