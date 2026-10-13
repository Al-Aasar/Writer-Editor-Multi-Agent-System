from typing import Any
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)
import os
import json
from langchain_groq import ChatGroq


from langchain_core.language_models import BaseChatModel


def _content_to_text(content) -> str:
    """Normalize LangChain message content (str or list of blocks) to plain text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def _llm_text(user_prompt: str, system_prompt: str, llm: BaseChatModel | None = None) -> str:
    if llm is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")
        llm = ChatGroq(model="qwen/qwen3.8-27b", api_key=api_key)

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return _content_to_text(response.content).strip()


def _json_from_llm(text: str) -> dict[str, Any]:
    """Extract the first complete JSON object returned by the model."""
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")

    return json.loads(text[start : end + 1])


# Alias for backward compatibility
json_from_llm = _json_from_llm

