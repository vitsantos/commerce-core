from unittest.mock import patch
from django.test import SimpleTestCase
from ai_assistant.services.orchestrator import process_tool_call

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