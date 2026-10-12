import pytest

from writer_editor.utils import _json_from_llm


def test_parses_plain_json():
    assert _json_from_llm('{"approved": true}') == {"approved": True}


def test_parses_json_wrapped_in_text_and_fences():
    text = 'Here you go:\n```json\n{"approved": false, "feedback": "Add a conclusion."}\n```'
    assert _json_from_llm(text) == {"approved": False, "feedback": "Add a conclusion."}


def test_raises_when_no_json_present():
    with pytest.raises(ValueError):
        _json_from_llm("I think the article is fine.")


def test_raises_on_malformed_json():
    with pytest.raises(ValueError):
        _json_from_llm('{"approved": true,')