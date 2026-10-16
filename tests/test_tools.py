import unittest
from unittest.mock import patch

from campus_cafe.tools import calculator_tool, web_search


class ToolTests(unittest.TestCase):
    def test_crewai_adapter_executes_langchain_calculator(self):
        result = calculator_tool.run(expression="24000 / 4.96")
        self.assertAlmostEqual(float(result), 4838.709677419355)

    def test_search_failure_is_labeled_as_failure(self):
        with patch("campus_cafe.tools._search") as search:
            search.invoke.side_effect = ConnectionError
            result = web_search.invoke({"query": "campus cafe"})
        self.assertTrue(result.startswith("TOOL_FAILED:"))


if __name__ == "__main__":
    unittest.main()