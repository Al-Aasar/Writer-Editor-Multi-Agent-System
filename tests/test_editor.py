import json

import writer_editor.Agents.Editor_Agent as e

DRAFT = "Some article text"


def run_editor(iteration=1):
    return e.editor_agent(
        {"user_query": "Write about cats", "draft": DRAFT, "iteration": iteration, "llm_calls": 1}
    )


def fake_llm_reply(monkeypatch, approved, feedback=""):
    reply = json.dumps({"approved": approved, "feedback": feedback})
    monkeypatch.setattr(e, "_llm_text", lambda *a, **k: reply)


def test_approved_article_is_returned_as_final(monkeypatch):
    fake_llm_reply(monkeypatch, approved=True)
    out = run_editor()

    assert out["editor_approved"] is True
    assert out["final_response"] == DRAFT


def test_rejected_article_returns_feedback_and_no_final(monkeypatch):
    fake_llm_reply(monkeypatch, approved=False, feedback="Add a conclusion.")
    out = run_editor(iteration=1)

    assert out["editor_approved"] is False
    assert out["feedback"] == "Add a conclusion."
    assert "final_response" not in out


def test_rejected_article_is_forced_final_at_max_iterations(monkeypatch):
    fake_llm_reply(monkeypatch, approved=False, feedback="Still weak.")
    out = run_editor(iteration=3)

    assert out["final_response"] == DRAFT


def test_llm_calls_counter_increases_on_success(monkeypatch):
    fake_llm_reply(monkeypatch, approved=True)
    assert run_editor()["llm_calls"] == 2


def test_editor_approves_draft_when_llm_raises(monkeypatch):

    def boom(*args, **kwargs):
        raise RuntimeError("simulated rate limit")

    monkeypatch.setattr(e, "_llm_text", boom)
    out = run_editor()

    assert out["editor_approved"] is True
    assert out["final_response"] == DRAFT


def test_editor_approves_draft_when_reply_is_not_json(monkeypatch):
    monkeypatch.setattr(e, "_llm_text", lambda *a, **k: "Looks fine to me.")
    out = run_editor()

    assert out["editor_approved"] is True
    assert out["final_response"] == DRAFT