from django.test import TestCase

from ai_assistant.tools.executor import execute_tool

class ExecuteToolsTests(TestCase):
    
    def test_execute_registered_tool(self):
        result = execute_tool(
            "search_products", {"query": "teclado"},
        )

        self.assertIsInstance(result, list)

    def test_rejects_unknown_tool(self):
        with self.assertRaises(ValueError):
            execute_tool("delete_all_products", {})

    def test_rejects_missing_query(self):
        with self.assertRaises(ValueError):
            execute_tool("search_products", {})

    def test_rejects_empty_query(self):
        with self.assertRaises(ValueError):
            execute_tool("search_products", {"query": "   "})

    def test_rejects_invalide_arguments_type(self):
        with self.assertRaises(ValueError):
            execute_tool("search_products", "teclado")