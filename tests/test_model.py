from souriva.model import Evidence, MockModel


def test_mock_model_cites_selected_evidence():
    evidence = [
        Evidence("chunk-1", "First supported fact. Extra detail.", "guide.md", "section 1", 0.8),
        Evidence("chunk-2", "Second supported fact.", "guide.md", "section 2", 0.7),
    ]

    reply = MockModel().answer("What is supported?", evidence)

    assert reply.citation_ids == ("chunk-1", "chunk-2")
    assert reply.text == "First supported fact. [chunk-1] Second supported fact. [chunk-2]"


def test_mock_model_declines_without_evidence():
    reply = MockModel().answer("Unknown?", [])
    assert reply.citation_ids == ()
    assert "enough evidence" in reply.text
