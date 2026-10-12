import os
from dotenv import load_dotenv
load_dotenv()

try:
    from state import WriterState
    from Agents.Guardrails_Agent import guardrail_agent
    from Agents.Writer_Agent import writer_agent
    from Agents.Editor_Agent import editor_agent
except ImportError:
    from writer_editor.state import WriterState
    from writer_editor.Agents.Guardrails_Agent import guardrail_agent
    from writer_editor.Agents.Writer_Agent import writer_agent
    from writer_editor.Agents.Editor_Agent import editor_agent

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import AIMessage
from langchain_groq import ChatGroq

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add it to your .env file.")

ROUTE_MAP = {
    "guardrail_blocked": "guardrail_blocked",
    "writer_agent": "writer_agent",
    "editor_agent": "editor_agent",
}

def guardrail_blocked_agent(state: WriterState):
    reason = state.get("guardrail_reason") or "Sorry, I can't help with this request."
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }


# ---------- Routers ----------
def route_from_guardrails(state: WriterState) -> str:
    if state.get("error"):
        return "end"
    if state.get("guardrail_allowed", False):
        return "writer_agent"
    return "guardrail_blocked"


def route_from_writer(state: WriterState) -> str:
    if state.get("error"):         
        return "end"
    return "editor_agent"


def route_from_editor(state: WriterState) -> str:
    if (
        state.get("final_response")
        or state.get("editor_approved")
        or state.get("iteration", 0) >= 3
    ):
        return "end"
    return "writer_agent"


# ---------- Graph ----------
graph = StateGraph(WriterState)

graph.add_node("guardrails", guardrail_agent)
graph.add_node("guardrail_blocked", guardrail_blocked_agent)
graph.add_node("writer_agent", writer_agent)
graph.add_node("editor_agent", editor_agent)

graph.add_edge(START, "guardrails")

graph.add_conditional_edges(
    "guardrails",
    route_from_guardrails,
    {"writer_agent": "writer_agent", "guardrail_blocked": "guardrail_blocked", "end": END},
)
graph.add_edge("guardrail_blocked", END)

graph.add_conditional_edges(
    "writer_agent",
    route_from_writer,
    {"editor_agent": "editor_agent", "end": END},
)

graph.add_conditional_edges(
    "editor_agent",
    route_from_editor,
    {"writer_agent": "writer_agent", "end": END},
)

app = graph.compile()


if __name__ == "__main__":
    query = input("Enter your article request: ")
    result = app.invoke({"user_query": query, "iteration": 0, "llm_calls": 0})
    print(result.get("final_response") or result.get("error"))