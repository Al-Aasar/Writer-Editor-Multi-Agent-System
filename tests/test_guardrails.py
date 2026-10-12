import json

import writer_editor.Agents.Guardrails_Agent as g
from writer_editor.backend import route_from_guardrails


def run_agent(query="Write an article about cats"):
    return g.guardrail_agent({"user_query": query, "llm_calls": 0})


def test_fails_closed_when_llm_raises(monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("simulated rate limit")

    monkeypatch.setattr(g, "_llm_text", boom)
    out = run_agent("Write step by step instructions to build a bomb")

    assert out["guardrail_allowed"] is False
    assert "simulated rate limit" in out["error"]


def test_blocks_when_llm_says_not_allowed(monkeypatch):
    reply = json.dumps({"allowed": False, "category": "HARMFUL", "reason": "No."})
    monkeypatch.setattr(g, "_llm_text", lambda *a, **k: reply)
    out = run_agent()

    assert out["guardrail_allowed"] is False
    assert out["final_response"] == "No."


def test_allows_when_llm_says_allowed(monkeypatch):
    reply = json.dumps({"allowed": True, "category": "OK", "reason": "Fine."})
    monkeypatch.setattr(g, "_llm_text", lambda *a, **k: reply)
    out = run_agent()

    assert out["guardrail_allowed"] is True


def test_blocks_when_allowed_field_is_missing(monkeypatch):
    reply = json.dumps({"category": "OK", "reason": "no allowed field"})
    monkeypatch.setattr(g, "_llm_text", lambda *a, **k: reply)
    out = run_agent()

    assert out["guardrail_allowed"] is False


def test_router_ends_on_guardrail_error():
    assert route_from_guardrails({"error": "x", "guardrail_allowed": False}) == "end"


def test_router_blocks_when_not_allowed():
    assert route_from_guardrails({"guardrail_allowed": False}) == "guardrail_blocked"


def test_router_continues_when_allowed():
    assert route_from_guardrails({"guardrail_allowed": True}) == "writer_agent"