"""LangChain tools exposed to the CrewAI agents."""

from langchain_community.tools import DuckDuckGoSearchResults
from langchain_core.tools import BaseTool as LangChainBaseTool
from langchain_core.tools import StructuredTool, tool
from pydantic import BaseModel
from crewai.tools import BaseTool as CrewAIBaseTool

from campus_cafe.calculations import calculate


_search = DuckDuckGoSearchResults(max_results=6, output_format="json")


@tool
def web_search(query: str) -> str:
    """Search the public web and return result titles, URLs, and snippets."""
    try:
        return str(_search.invoke({"query": query}))
    except Exception as error:
        return f"TOOL_FAILED: Web search did not return results ({type(error).__name__}). Do not treat this as evidence."


def _calculator(expression: str) -> str:
    try:
        return str(calculate(expression))
    except (SyntaxError, TypeError, ValueError, ZeroDivisionError) as error:
        return f"CALCULATION_FAILED: {error}"


calculator = StructuredTool.from_function(
    func=_calculator,
    name="calculator",
    description="Evaluate a basic arithmetic expression. Use this for every financial calculation; only arithmetic is supported.",
)


class CrewLangChainAdapter(CrewAIBaseTool):
    """Expose a LangChain tool through CrewAI's tool interface."""

    args_schema: type[BaseModel]
    langchain_tool: LangChainBaseTool

    def _run(self, **kwargs: object) -> str:
        return str(self.langchain_tool.invoke(kwargs))


def as_crewai_tool(langchain_tool: LangChainBaseTool) -> CrewLangChainAdapter:
    return CrewLangChainAdapter(
        name=langchain_tool.name,
        description=langchain_tool.description,
        args_schema=langchain_tool.args_schema,
        langchain_tool=langchain_tool,
    )


web_search_tool = as_crewai_tool(web_search)
calculator_tool = as_crewai_tool(calculator)