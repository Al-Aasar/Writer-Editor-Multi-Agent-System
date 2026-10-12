from writer_editor.backend import route_from_editor, route_from_writer


def test_editor_route_ends_when_approved():
    assert route_from_editor({"editor_approved": True, "iteration": 1}) == "end"


def test_editor_route_ends_at_max_iterations():
    assert route_from_editor({"editor_approved": False, "iteration": 3}) == "end"


def test_editor_route_ends_when_final_response_set():
    assert route_from_editor({"final_response": "article", "iteration": 1}) == "end"


def test_editor_route_loops_back_when_rejected():
    assert route_from_editor({"editor_approved": False, "iteration": 1}) == "writer_agent"


def test_editor_route_defaults_to_writer_on_empty_state():
    assert route_from_editor({}) == "writer_agent"


def test_writer_route_ends_on_error():
    assert route_from_writer({"error": "Writer failed: x"}) == "end"


def test_writer_route_goes_to_editor():
    assert route_from_writer({"draft": "text"}) == "editor_agent"