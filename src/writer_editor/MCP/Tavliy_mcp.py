import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
from langchain_tavily import TavilySearch

# Load .env from project root or environment
load_dotenv(find_dotenv(usecwd=True))

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
_search_tool: TavilySearch | None = None


def _get_search_tool() -> TavilySearch:
    global _search_tool
    if _search_tool is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "TAVILY_API_KEY is missing. "
                "Add TAVILY_API_KEY=your_key to the project .env file."
            )
        _search_tool = TavilySearch(api_key=api_key, max_results=5)
    return _search_tool


async def tavily_mcp_search(query: str) -> str:
    """Execute web search using Tavily and return formatted string of results."""
    try:
        tool = _get_search_tool()
        results = await tool.ainvoke({"query": query})
        if isinstance(results, list):
            formatted_chunks = []
            for item in results:
                if isinstance(item, dict):
                    title = item.get("title", "")
                    url = item.get("url", "")
                    content = item.get("content", "")
                    formatted_chunks.append(f"Title: {title}\nURL: {url}\nContent: {content}\n")
                else:
                    formatted_chunks.append(str(item))
            return "\n---\n".join(formatted_chunks)
        return str(results)
    except Exception as exc:
        print(f"Tavily search error: {exc}")
        return ""


