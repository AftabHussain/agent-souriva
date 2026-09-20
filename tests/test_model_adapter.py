import pytest

from souriva.model import MockModel, OpenAICompatibleModel, create_model, parse_citation_ids


def test_model_factory_selects_backends():
    assert isinstance(create_model("mock"), MockModel)
    assert isinstance(
        create_model("openai-compatible", "http://model/v1", "gpt-oss"), OpenAICompatibleModel
    )


def test_model_factory_rejects_unknown_backend():
    with pytest.raises(ValueError, match="Unknown model backend"):
        create_model("missing")


def test_citation_parser_preserves_unknown_ids_for_validation():
    assert parse_citation_ids("Claim [chunk-a] and invention [fake].") == ("chunk-a", "fake")
