import os
from pathlib import Path

import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


# =========================================================
# Environment setup
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


def _require_env(name: str, value: str | None) -> str:
    """Return an environment value or raise a readable setup error."""

    if not value:
        raise RuntimeError(
            f"{name} is missing. "
            f"Add {name}=your_key to the project .env file."
        )

    return value


# =========================================================
# MCP client (Tavily only)
# =========================================================

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": (
                "https://mcp.tavily.com/mcp/"
                f"?tavilyApiKey={TAVILY_API_KEY or ''}"
            ),
        },
    }
)


async def _get_tavily_tool(tool_name: str = "tavily_search"):
    """Load one tool from the Tavily MCP server."""

    _require_env("TAVILY_API_KEY", TAVILY_API_KEY)

    tools = await client.get_tools(server_name="tavily")

    tool = next(
        (item for item in tools if item.name == tool_name),
        None,
    )

    if tool is None:
        available_tools = (
            ", ".join(sorted(item.name for item in tools)) or "none"
        )

        raise RuntimeError(
            f"MCP tool '{tool_name}' was not found "
            f"on server 'tavily'. "
            f"Available tools: {available_tools}"
        )

    return tool


# =========================================================
# Tavily MCP
# =========================================================

async def tavily_mcp_search(query: str):
    search_tool = await _get_tavily_tool("tavily_search")

    return await search_tool.ainvoke(
        {
            "query": query,
        }
    )